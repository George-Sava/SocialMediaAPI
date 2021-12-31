from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app import schemas
from .config import settings

# OAuth 2.0 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


# SECRET_KEY
# Algorithm
# Expiration time

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy()
    
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_token

# 
def verify_access_token(token: str, credentials_exception):
    
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        id:str = payload.get("user_id")
        role:str = payload.get("role")
        if id is None and role is None:
            raise credentials_exception
        
        token_data = schemas.TokenData(id=id,role=role)
    except JWTError:
        raise credentials_exception
    
    print("Token Data Verify Func: ", token_data)
    
    return token_data
    
def get_current_user(token: str = Depends(oauth2_scheme) ):
    print("Token Data: ", token)
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials!", headers={ "WWW-Authenticate": "Bearer"})
    
    return verify_access_token(token, credentials_exception)