from fastapi import status, HTTPException, Depends, APIRouter
from app.schemas import TokenData
from sqlalchemy import desc
from sqlalchemy.orm import Session
from typing import List, Optional
from app import oauth2, schemas, models
from app.dabase import engine, get_db


router = APIRouter(
    prefix="/likes", 
    tags=['Likes']
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def like_post(like: schemas.Like, db: Session = Depends(get_db), oauth_token: TokenData = Depends(oauth2.get_current_user)):
    
    post = db.query(models.Post).filter(models.Post.id == like.post_id).first()
    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"Post does not exist!")
    
    like_query = db.query(models.Like).filter(models.Like.post_id == like.post_id, models.Like.user_id == oauth_token.id)
    
    found_like = like_query.first()
    
    if not found_like:
        new_like = models.Like(post_id = like.post_id, user_id = oauth_token.id)
        db.add(new_like)
        db.commit()
        return {"message": "Successfully Liked!"}
    else:
        like_query.delete(synchronize_session= False)
        db.commit()
    return {"message": "Successfully Unlike!"}