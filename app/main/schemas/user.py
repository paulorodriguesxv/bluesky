from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    name: str
    email: EmailStr
    

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int    
    is_active: bool
    updated_at: datetime

    class Config:
        orm_mode = True