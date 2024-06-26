from pydantic import BaseModel, EmailStr
import uuid


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ApproveUserRequest(BaseModel):
    email: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    role: str
    approved: bool

    class Config:
        from_attributes = True

