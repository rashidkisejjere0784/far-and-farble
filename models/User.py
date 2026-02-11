# models/user.py

from sqlalchemy import Column, Float, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(200))
    country_id = Column(Integer,index=True) 
    user_image = Column(String(100), default="default.png")  
    is_suspended = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    credits = Column(Float, default=5.0)