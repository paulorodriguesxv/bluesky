import jwt
from datetime import datetime, timedelta
from http import HTTPStatus
from starlette.status import HTTP_401_UNAUTHORIZED
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.main.model.user import User
from app.main.schemas import user as user_schema
from app.config import BaseConfig


def get_users(db: Session):
    return db.query(User).all()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: user_schema.UserCreate):
    db_user = User(name=user.name,
                   email=user.email,
                   password=user.password,
                   picture=user.picture)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user(db: Session, email: str = None):
    return get_user_by_email(db, email)


def create_token(data: dict,
                 expires_delta: timedelta = None,
                 config: BaseConfig = None):
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
