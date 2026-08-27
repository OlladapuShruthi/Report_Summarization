from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=200)
    password: str = Field(min_length=6, max_length=200)


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    user_id: str
    full_name: str
    email: str
    created_at: str
