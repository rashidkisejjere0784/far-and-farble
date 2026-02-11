# models/user.py

from sqlalchemy import Column, Float, Integer, String, Boolean
from sqlalchemy.orm import relationship
from database import Base

class PetImage(Base):
    __tablename__ = "pet_images"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String(200), nullable=False)
    generated_images_folder_path = Column(String(200), nullable=True)
    is_payed = Column(Boolean, default=False)
    stripe_payment_id = Column(String(200), nullable=True, unique=True)
    