from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression
from sqlalchemy.sql.sqltypes import TIMESTAMP

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default=expression.true(), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user = relationship('User')
    
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=expression.text('now()'))
    

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default='player')
    avatar_url = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=expression.text('now()'))
    updated_at = Column(TIMESTAMP(timezone=False), nullable=False,
                        server_default=expression.text('now()'),
                        onupdate=expression.text('now()'))
    
    
class Vote(Base):
    __tablename__ = 'votes'
    
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id', ondelete='CASCADE'), primary_key=True)