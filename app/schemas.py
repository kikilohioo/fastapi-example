from datetime import datetime
from typing import Optional, Annotated
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    user_id: int
    user: UserResponse
    created_at: datetime

class PostOut(BaseModel):
    Post: PostResponse
    votes: int
    
    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str = 'player'
    avatar_url: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str = 'player'
    avatar_url: Optional[str] = None
    created_at: datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None


class LoginResponse(Token):
    user: UserResponse
    
class Vote(BaseModel):
    post_id: int
    dir: Annotated[int, Field(le=1, ge=0)]  # 1 for upvote, 0 for remove vote
