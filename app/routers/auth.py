from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from ..dabase import get_db
from .. import schemas, models, functions, oauth2

router = APIRouter(
    prefix="/login",
    tags=['Authentication']
)

@router.post("/", response_model=schemas.Token)
async def user_login(user_credentials: OAuth2PasswordRequestForm = Depends() , db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials!")
    if not functions.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials!")
    if user.role == 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid account type!")
    
    access_token = oauth2.create_access_token(data= { "user_id": user.id, "role": user.role})
    
    return {"access_token":access_token, "token_type": "Bearer"}

@router.post("/admin", response_model=schemas.Token)
async def admin_login(user_credentials: OAuth2PasswordRequestForm = Depends() , db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials!")
    if not functions.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials!")
    if user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User not Admin!")
    
    access_token = oauth2.create_access_token(data= { "user_id": user.id, "role": user.role})
    
    return {"access_token":access_token, "token_type": "Bearer"}