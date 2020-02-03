import logging
import jwt
from jwt import PyJWTError
from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST
from app.database import get_db
from app.config import BaseConfig, get_config
from ..services import user_service
from ..schemas import user as user_schema
from ..schemas import token as token_schema

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

logger = logging.getLogger(__name__)


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


@router.get("/", response_model=List[user_schema.User], tags=['users'])
async def read_users(db: Session = Depends(get_db),
                     token: str = Depends(oauth2_scheme)):
    return user_service.get_users(db)


@router.post("/", response_model=user_schema.User, tags=['users'])
def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Email already registered")
    return user_service.create_user(db=db, user=user)


@router.get("/me", response_model=user_schema.User, tags=['users'])
async def read_users_me(
        current_user: user_schema.User = Depends(get_current_active_user)):
    return current_user
