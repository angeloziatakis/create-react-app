from pydantic import BaseModel, EmailStr
from enum import Enum

class Role(str, Enum):
    teacher = "teacher"
    student = "student"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Role

class LoginForm(BaseModel):
    email: EmailStr
    password: str
