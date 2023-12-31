from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    online: bool
    unread:int


class TokenData(BaseModel):
    user_id: Optional[str] = None


class LoginResponse(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    access_token: str
    token_type: str


class MessageCreate(BaseModel):
    sender_id:int
    receiver_id:int
    content:str

class Message(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    type: str
    created_at: datetime
    content: str

class UpdateCount(BaseModel):
    sender_id :int
    receiver_id:int
    count:int
