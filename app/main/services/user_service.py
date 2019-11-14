from sqlalchemy.orm import Session
from app.main.model.user import User
from app.main.schemas import user as user_schema
from http import HTTPStatus
from starlette.status import HTTP_401_UNAUTHORIZED
from fastapi import HTTPException


def get_users(db: Session):
    return db.query(User).all()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: user_schema.UserCreate):
    db_user = User(name=user.name, email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user(db: Session, email: str = None):
    return get_user_by_email(db, email)
