from datetime import datetime
from typing import Optional, Annotated
from pydantic import BaseModel, ConfigDict, EmailStr, Field, constr


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str = 'player'
    avatar_url: Optional[str] = None
    created_at: datetime


class TestUser(UserResponse):
    password: str


class UserLogin(BaseModel):
    email: EmailStr = Field(..., min_length=5)
    password: str = Field(..., min_length=5)


class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=5)
    email: EmailStr = Field(..., min_length=5)
    password: str = Field(..., min_length=5)
    role: str = 'player'
    avatar_url: Optional[str] = None


class PostBase(BaseModel):
    title: str = Field(..., min_length=5)
    content: str = Field(..., min_length=10)
    published: Optional[bool] = True


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
