from typing import List
from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.functions import add_refreshed_entry, create_user_post, get_user, get_user_by_email, get_users, verify_if_admin, verify_user_permission
from app import models, oauth2, schemas, functions
from app.dabase import engine, get_db



router = APIRouter(
    prefix="/users",
    tags=['User']
)

#Endopint for returning One User

@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Endpoint for creating users

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
async def create_user(user: schemas.UserCreateMin,db: Session = Depends(get_db)):
    db_entry = get_user_by_email(db, user.email)
    
    new_user_schema: schemas.UserCreate = schemas.UserCreate(email=user.email,password=user.password, role='user')
    
    # user = schemas.UserCreate(user_min.email, user_min.password,'user')

    if db_entry:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = functions.hash(user.password)
    new_user_schema.password = hashed_password
    new_user = models.User(**new_user_schema.dict())
    
    add_refreshed_entry(new_user, db)
    return new_user

# Endpoint for creating admins

@router.post("/admin", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
async def create_admin(user: schemas.UserCreateMin,db: Session = Depends(get_db)):
    db_entry = get_user_by_email(db, user.email)
    
    new_user_schema: schemas.UserCreate = schemas.UserCreate(email=user.email,password=user.password, role='admin')
    if db_entry:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = functions.hash(user.password)
    new_user_schema.password = hashed_password
    new_user = models.User(**new_user_schema.dict())
    
    add_refreshed_entry(new_user, db)
    return new_user



#Endpoint for creating individual user posts 

@router.post("/{user_id}/post/", response_model=schemas.Post)
def create_post_for_user_by_id(
    user_id:int, post: schemas.CreatedPost, db: Session = Depends(get_db), oauth_token: schemas.TokenData = Depends(oauth2.get_current_user)
):
    
    verify_user_permission(user_id=user_id,oauth_token=oauth_token)
    
    return create_user_post(db=db, post=post, user_id=user_id)


# Endpoint for returning All users

@router.get("/", response_model=List[schemas.User])
def read_all_users(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    users = get_users(db, skip=skip, limit=limit)
    return users

# DELETE method, url: "/post/{id}" --> removes Post by Id

@router.delete("/{user_id}/post/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_post_by_id(user_id: int,id: int, db: Session = Depends(get_db), oauth_token: schemas.TokenData = Depends(oauth2.get_current_user)):
    
    verify_user_permission(user_id=user_id,oauth_token=oauth_token)
    
    db_entry = get_user(db, user_id)
    if db_entry:
        raise HTTPException(status_code=400, detail="Not a valid user ID!")
    
    post_querry = db.query(models.Post).filter(models.Post.id == id, models.Post.owner_id == user_id)
    
    if post_querry.first() == None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id}, does not exist!")
    post_querry.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Endpoint for suspending user --- ADMIN OPERATION --- 

@router.patch("/{id}/suspend", response_model=schemas.UserMin)
async def suspend_user(user_id: int, db: Session = Depends(get_db), oauth_token: schemas.TokenData = Depends(oauth2.get_current_user) ):
    
    verify_if_admin(oauth_token)
    
    user_querry = db.query(models.User).filter(models.User.id == user_id)
    
    updated_user = user_querry.first()
    
    if updated_user == None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"User with id: {user_id}, does not exist!")
    
    if updated_user.is_active == False:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"User already suspended!")
    
    user_querry.update({models.User.is_active: False}, synchronize_session=False)
    
    db.commit()
    
    db.refresh(updated_user)
    
    return updated_user

# Endpoint for activating user --- ADMIN OPERATION --- 

@router.patch("/{id}/activate", response_model=schemas.UserMin)
async def activate_user(user_id: int, db: Session = Depends(get_db), oauth_token: schemas.TokenData = Depends(oauth2.get_current_user) ):
    
    verify_if_admin(oauth_token)
    
    user_querry = db.query(models.User).filter(models.User.id == user_id)
    
    updated_user = user_querry.first()
    
    if updated_user == None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"User with id: {user_id}, does not exist!")
    
    if updated_user.is_active == True:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"User already active!")
    
    user_querry.update({models.User.is_active: True}, synchronize_session=False)
    
    db.commit()
    
    db.refresh(updated_user)
    
    return updated_user