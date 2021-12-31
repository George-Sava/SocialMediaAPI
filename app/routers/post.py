from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.sql.functions import func
from app.schemas import PatchedPost, Post, PostOut, ReplacePost
from sqlalchemy import desc
from sqlalchemy.orm import Session
from typing import List, Optional
from app import oauth2, schemas, models
from app.dabase import engine, get_db
from app.functions import  cleanNullTerms, create_user_post, get_all_posts_and_likes, verify_if_admin , verify_user_permission_for_post

router = APIRouter(
    prefix="/posts", 
    tags=['Posts']
)

# Endpoint for getting all posts
# @router.get("/all", response_model=List[schemas.PostOut])
@router.get("/all", response_model=List[PostOut])
def read_all_posts(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), search: Optional[str] = ""):
    posts = get_all_posts_and_likes(db, skip=skip, limit=limit, search=search)
    return posts

# Request GET method, url: "/posts/{id}" --> returns one Post by Id

@router.get("/{id}", response_model=schemas.PostOut)
async def get_post_by_id(id: int, db: Session = Depends(get_db)):
    
    post = db.query(models.Post, func.count(models.Like.post_id).label("likes")).join(models.Like, models.Like.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id}, was not found!")
        
    return post


# Request GET method, url: "/posts" --> returns all posts for logged user

@router.get("/", response_model=List[schemas.PostOut])
async def get_posts_for_logged_user(skip: int = 0, limit: int = 50,db: Session = Depends(get_db), oauth_token: schemas.TokenData = Depends(oauth2.get_current_user), search: Optional[str] = ""):
    
    # posts = db.query(models.Post).filter(models.Post.owner_id == oauth_token.id).all()
    
    data = db.query(models.Post, func.count(models.Like.post_id).label("likes")).join(models.Like, models.Like.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search),models.Post.owner_id == oauth_token.id).offset(skip).limit(limit).all()
    
    verify_user_permission_for_post(data[0][0],oauth_token)

    return data


# Request GET method, url: "/posts/latest" --> returns latest Post of Logged user

@router.get("/latest", response_model=schemas.PostOut)
async def get_latest_post_for_logged_user(db: Session = Depends(get_db), oauth_token: schemas.TokenData = Depends(oauth2.get_current_user)):
#     post = cur.execute("""SELECT * FROM posts ORDER BY created_at DESC
#   LIMIT 1 """).fetchone()
    post_data = db.query(models.Post, func.count(models.Like.post_id).label("likes")).join(models.Like, models.Like.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.owner_id == oauth_token.id).order_by(desc(models.Post.created_at)).first()
    
    verify_user_permission_for_post(post_data,oauth_token)
    
    return post_data


# Endpoint for creating post for the current logged user
# @router.get("/all", response_model=List[schemas.PostOut])
@router.post("/", response_model=Post)
def create_post_for_logged_user( post: schemas.CreatedPost, db: Session = Depends(get_db), oauth_token: schemas.TokenData = Depends(oauth2.get_current_user)):
    post = create_user_post(db,post,oauth_token.id)
    return post

# Method PATCH, url: "/posts/{id}" --> update a post by id

@router.patch("/{id}", response_model=schemas.PostOut)
async def update_post_of_logged_user(id: int, post: PatchedPost, db: Session = Depends(get_db), oauth_token: schemas.TokenData = Depends(oauth2.get_current_user) ):
    
    post_querry = db.query(models.Post).filter(models.Post.id == id)
    
    updated_post = post_querry.first()
    
    if updated_post == None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id}, does not exist!")
    
    verify_user_permission_for_post(updated_post,oauth_token)
    
    post_update_attrs = cleanNullTerms(post.dict())
    
    post_querry.update(post_update_attrs , synchronize_session=False)
    
    db.commit()
    
    post_data = db.query(models.Post, func.count(models.Like.post_id).label("likes")).join(models.Like, models.Like.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    
    return post_data
    
    
# Method PUT, url: "/posts/{id}" --> replace a post by id

@router.put("/{id}", response_model= schemas.PostOut)
async def replace_post_of_logged_user(id: int, post: ReplacePost, db: Session = Depends(get_db), oauth_token: schemas.TokenData = Depends(oauth2.get_current_user)):
    
    post_querry = db.query(models.Post).filter(models.Post.id == id)
    
    updated_post = post_querry.first()
    
    if updated_post == None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id}, does not exist!")
    
    verify_user_permission_for_post(updated_post,oauth_token)
    
    post_querry.update(post.dict(), synchronize_session=False)
    
    db.commit()
    
    db.refresh(updated_post)
    
    db.query(models.Like).filter(models.Like.post_id == updated_post.id, models.Like.user_id == oauth_token.id).delete(synchronize_session= False)
    
    db.commit()
    
    post_data = db.query(models.Post, func.count(models.Like.post_id).label("likes")).join(models.Like, models.Like.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    
    return post_data
    
