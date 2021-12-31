from fastapi import FastAPI
from app.config import settings
from .dabase import engine
from .routers import post, user, auth, likes
from fastapi.middleware.cors import CORSMiddleware


# Creates tables
# models.Base.metadata.create_all(bind=engine)

# FastAPI App instance
app = FastAPI()

# Allowed sites
origins = ["*"]

# CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# @app.get('/')
# def hello():
#     return {"message": "Hello ANA!"}

app.include_router(post.router)
app.include_router(user.router)
app.include_router(likes.router)
app.include_router(auth.router)


