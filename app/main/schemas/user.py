from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr, validator


class UserBase(BaseModel):
    name: str
    picture: str
    email: EmailStr    

class UserCreate(UserBase):
    password: str

    @validator('password')
    def check_password_or_token(cls, v, values, **kwargs):
        password_value = values.get('password')
        social_token_value = v

        if (not password_value) and (not social_token_value):
            raise ValueError(f'password must be filled in')
        
        return v

class User(UserBase):
    id: int        
    is_active: bool
    updated_at: datetime

    class Config:
        orm_mode = True