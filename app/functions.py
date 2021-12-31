from typing import Optional
from fastapi import HTTPException, status
from app import models, schemas
from sqlalchemy.orm import Session
import hashlib
from sqlalchemy import func
from passlib.context import CryptContext
from app.schemas import PatchedPost, Post, TokenData


# Encryption Context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Utils

# Hashing function
def hash(password):
    return pwd_context.hash(password)

# Compare Hashes function
def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password) 

# Fucntion Tools

def update_sql_data(data: dict, id):
    return_data = []
    
    for key in data: 
        return_data.append(data[key])
    
    return_data.append(id)
    
    return tuple(return_data)

def update_sql_string(data: dict):
    valid_keys = ("title","content","published", "rating")
    counter = 0
    arg = ""
    argEndStr = "= %s"
    last_key = list(data.keys())[-1]
    
    for vk in valid_keys:
        for key in data:
            if key == vk:
                counter += 1
    
    if counter == 0:
        raise HTTPException(status_code= status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Please enter a valid key! Choose between 'title', 'content', 'published', 'rating")

    for key in data:
        if key == last_key and vk :
            arg += key + argEndStr
        else:
            arg += key + argEndStr+ "," 

    return "UPDATE posts SET " +arg+ " WHERE id = %s RETURNING *"

def add_refreshed_entry(record, db):
    db.add(record)
    db.commit()
    db.refresh(record)
    
def cleanNullTerms(dictionary):
    return {
        key: value
        for key, value in dictionary.items()
        if value is not None
    }
    
def encrypt_string(string):
    sha_signature = hashlib.sha256(string.encode()).hexdigest()
    return sha_signature

# Database operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user_post(db: Session,post: schemas.CreatedPost, user_id: int):
    db_post = models.Post(**post.dict(), owner_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()
    
def get_all_posts_and_likes(db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = ""):
    return db.query(models.Post, func.count(models.Like.post_id).label("likes")).join(models.Like, models.Like.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).offset(skip).limit(limit).all()



# Authorization functions

def verify_user_permission(user_id: int, oauth_token: TokenData):
    if user_id != int(oauth_token.id) and oauth_token.role != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"You do not have permission!")

def verify_user_permission_for_post(post: schemas.Post, oauth_token: TokenData):
    if post.owner_id != int(oauth_token.id) and oauth_token.role != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"You do not have permission!")
    
def verify_if_admin( oauth_token: TokenData):
    if oauth_token.role != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"You do not have permission! Admin Operation!")
