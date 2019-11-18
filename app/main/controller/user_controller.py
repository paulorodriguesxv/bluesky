import jwt
from jwt import PyJWTError
from typing import List
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


def create_access_token(*,
                        data: dict,
                        expires_delta: timedelta = None,
                        config: BaseConfig):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        config.ACCESS_TOKEN_PRIVATE_KEY,
        algorithm=config.ACCESS_TOKEN_ALGORITHM,
        headers={'kid': '3q1sysizPaTHQhb+xErwIZfZymN+46UmssneP0vPkes='})

    return encoded_jwt


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
    access_token_expires = timedelta(
        minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email},
                                       expires_delta=access_token_expires,
                                       config=config)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=user_schema.User)
async def read_users_me(
        current_user: user_schema.User = Depends(get_current_active_user)):
    return current_user


@router.get("/.well-known/jwks.json", response_model=jwks_schema.Jwks)
async def jwks(config: BaseConfig = Depends(get_config)):
    public_key = config.ACCESS_TOKEN_PUBLIC_KEY.split('\n')
    public_key = public_key[1:8]
    print(public_key)

    key_item = dict(alg=config.ACCESS_TOKEN_ALGORITHM,
                    kid='3q1sysizPaTHQhb+xErwIZfZymN+46UmssneP0vPkes=',
                    kty='RSA',
                    n=''.join(public_key),
                    use='sig')

    results = dict(keys=[key_item])

    return results
