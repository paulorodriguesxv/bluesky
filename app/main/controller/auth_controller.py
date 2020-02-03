import logging
import jwt
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED
from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import timedelta
from app.database import get_db
from app.config import BaseConfig, get_config
from ..services import user_service
from ..schemas import user as user_schema
from ..schemas import token as token_schema
from ..schemas import jwks as jwks_schema

from ..services.social_login_service import SocialLoginService

router = APIRouter()

logger = logging.getLogger(__name__)


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


def authenticate_user(db, username: str, password: str):
    user = user_service.get_user(db, username)
    if not user:
        return False

    if not user.password == password:
        return False
    return user


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
        social_token: token_schema.SocialToken,
        db: Session = Depends(get_db),
        config: BaseConfig = Depends(get_config),
        social_login_service=Depends(SocialLoginService)):

    errMsg = None
    try:
        user = await social_login_service.get_user(db, social_token)
    except Exception as err:
        errMsg = str(err)
        user = None
        logger.error(errMsg)

    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"{errMsg}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return create_full_token(user, config)


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
