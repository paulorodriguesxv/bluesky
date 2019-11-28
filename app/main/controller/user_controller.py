import jwt
import socket
import aiohttp
from aiohttp.resolver import AsyncResolver
from aiohttp import web
from jwt import PyJWTError
from typing import List, AnyStr
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.database import get_db
from app.config import BaseConfig, get_config
from ..services import user_service
from ..schemas import user as user_schema
from ..schemas import token as token_schema
from ..schemas import jwks as jwks_schema

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_token_data(token: str, config: BaseConfig):
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = jwt.decode(token,
                         config.ACCESS_TOKEN_PUBLIC_KEY,
                         algorithms=[config.ACCESS_TOKEN_ALGORITHM])

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    token_data = token_schema.TokenData(username=username)

    return token_data


async def get_current_user(db: Session = Depends(get_db),
                           token: str = Depends(oauth2_scheme),
                           config: BaseConfig = Depends(get_config)):
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token,
                             config.ACCESS_TOKEN_PUBLIC_KEY,
                             algorithms=[config.ACCESS_TOKEN_ALGORITHM])

        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = token_schema.TokenData(username=username)
    except PyJWTError as err:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(err)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = user_service.get_user(db, email=token_data.username)

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
        current_user: user_schema.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Inactive user")
    return current_user


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(db, username: str, password: str):
    user = user_service.get_user(db, username)
    if not user:
        return False

    # if not verify_password(password, user.password):
    if not user.password == password:
        return False
    return user


async def check_facebook_token_is_valid(token):
    base_url = 'https://graph.facebook.com'
    url = f"{base_url}/me?access_token={token}&fields=id,email"

    data = {}

    async with aiohttp.ClientSession(connector=None) as session:
        async with session.get(url) as response:
            headers = response.headers
            data = await response.json()

    # return  {'id': '110071200461759', 'email': 'codekraftofficial@gmail.com'}

    return data


def create_token(*,
                 data: dict,
                 expires_delta: timedelta = None,
                 config: BaseConfig):

    token = user_service.create_token(data, expires_delta, config)
    return token


def create_full_token(user: user_schema.User, config: BaseConfig):
    access_token_expires = timedelta(
        minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token_data = {
        'sub': user.email,
        'name': user.name,
        'picture': user.picture,
    }

    access_token = create_token(data=access_token_data,
                                expires_delta=access_token_expires,
                                config=config)

    refresh_token_expires = timedelta(
        minutes=config.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_token(data={"sub": user.email},
                                 expires_delta=refresh_token_expires,
                                 config=config)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/users/", response_model=List[user_schema.User])
async def read_users(db: Session = Depends(get_db),
                     token: str = Depends(oauth2_scheme)):
    return user_service.get_users(db)


@router.post("/users/", response_model=user_schema.User)
def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Email already registered")
    return user_service.create_user(db=db, user=user)


@router.post("/refresh-token", response_model=token_schema.Token)
async def get_access_token_from_refresh_token(
        token: token_schema.RefreshToken,
        db: Session = Depends(get_db),
        config: BaseConfig = Depends(get_config)):

    token_data = get_token_data(token.refresh_token, config)

    user = user_service.get_user(db, email=token_data.username)

    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return create_full_token(user, config)


@router.post("/token", response_model=token_schema.Token)
async def login_for_access_token(
        db: Session = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends(),
        config: BaseConfig = Depends(get_config)):

    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return create_full_token(user, config)


@router.post("/swap-social-token", response_model=token_schema.Token)
async def swap_social_token_for_access_token(
        social_token: token_schema.FacebookToken,
        db: Session = Depends(get_db),
        config: BaseConfig = Depends(get_config)):

    try:
        data = await check_facebook_token_is_valid(social_token.token)
        user = user_service.get_user(db, email=data['email'])
    except Exception as err:
        print(err)
        user = None

    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return create_full_token(user, config)


@router.get("/users/me", response_model=user_schema.User)
async def read_users_me(
        current_user: user_schema.User = Depends(get_current_active_user)):
    return current_user


@router.get("/.well-known/jwks.json", response_model=jwks_schema.Jwks)
async def jwks(config: BaseConfig = Depends(get_config)):
    public_key = config.ACCESS_TOKEN_PUBLIC_KEY.split('\n')
    public_key = public_key[1:8]

    key_item = dict(alg=config.ACCESS_TOKEN_ALGORITHM,
                    kid='3q1sysizPaTHQhb+xErwIZfZymN+46UmssneP0vPkes=',
                    kty='RSA',
                    n=''.join(public_key),
                    use='sig')

    results = dict(keys=[key_item])

    return results
