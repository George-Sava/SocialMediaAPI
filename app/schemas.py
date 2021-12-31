from datetime import datetime
from pydantic import BaseModel, BaseSettings
from typing import List, Optional

from pydantic.networks import EmailStr
from pydantic.types import conint

#Custom schema for validating data
class PostBase(BaseModel): 
    title: str
    content: str
    
class PatchedPost(BaseModel):
    title: Optional[str]
    content: Optional[str]
    published: Optional[bool]
    rating: Optional[int]
    
class CreatedPost(PostBase):
    published: Optional[bool] = True
    rating: Optional[int] = 0
    
class ReplacePost(PostBase):
    pass


class Post(PostBase): 
    id: int
    owner_id: Optional[int]
    published: Optional[bool] = True
    rating: Optional[int] = 0
    created_at: Optional[datetime]
    
    class Config:
        orm_mode = True
        
class PostOut(BaseModel):
    Post: Post
    likes: int
    
    class Config:
        orm_mode = True

class UserBase(BaseModel): 
    email: EmailStr
    
class UserCreate(UserBase):
    password: str
    role: str

class UserCreateMin(UserBase):
    password: str

    
class User(UserBase):
    id: int
    is_active: bool = True
    role: str
    posts: List[Post] = []
    
    class Config:
        orm_mode = True

class UserMin(UserBase):
    id: int
    is_active: bool = True
    role: str
    
    class Config:
        orm_mode = True
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    id: Optional[str] = None
    role: Optional[str] = None
    
class Like(BaseModel):
    post_id: int
    # liked:  bool
