from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP, Boolean,  String

from .dabase import Base

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True, nullable= False)
    owner_id = Column(Integer,ForeignKey("users.id"), nullable= True)
    title = Column(String, nullable= False)
    content = Column(String, nullable= False)
    published = Column(Boolean, server_default='TRUE', nullable= False)
    created_at = Column(TIMESTAMP(timezone= True), nullable= False, server_default=text('now()'))
    rating = Column(Integer,default=True,server_default='0', nullable= False)
    
    owner = relationship("User", back_populates="posts")
    
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key= True, nullable= False)
    is_active = Column(Boolean, nullable= False,server_default='TRUE')
    email = Column(String, nullable= False, unique= True)
    password = Column(String, nullable= False)
    role = Column(String, nullable= False)
    created_at = Column(TIMESTAMP(timezone= True), nullable= False, server_default=text('now()'))
    
    posts= relationship("Post", back_populates="owner")
    
class Like(Base):
    
    __tablename__ = 'likes'
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key= True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key= True)
