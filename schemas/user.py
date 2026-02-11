from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    """
    Base user model with common fields.
    """
    name: str
    email: str
    country_id: int


class UserCreate(UserBase):
    """
    User model for creation with password.
    """
    password: str

class User(UserBase):
    """
    User model with additional ID field.
    """
    id: int
    

    class Config:
        """
        Pydantic configuration to use attributes from model.
        """
        from_attributes = True
class UserResponseSchema(BaseModel):
    id: int
    email: EmailStr
    name: str
    is_suspended: bool
    image: str
    credits: float
    country_id: int
    is_verified: bool
      
    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    """
    Schema for user login with email and password.
    """
    email: str
    password: str

    class Config:
        """
        Pydantic configuration to use attributes from model.
        """
        from_attributes = True