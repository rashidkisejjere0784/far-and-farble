from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import timedelta

from schemas.user import UserCreate, LoginSchema, UserResponseSchema
from utils.auth import send_verification_email, generate_verification_token
from database import SessionLocal
from models.User import User as UserModel
from utils.auth import get_password_hash, verify_password, create_access_token, verify_token

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    # Hash the password
    hashed_password = get_password_hash(user_data.password)

    # Create a new user instance
    new_user = UserModel(
        name=user_data.name,
        email=user_data.email,
        is_verified=False  # Set the initial verification status
    )

    try:
        # Add and commit the new user to the database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Generate a verification token
    verification_token = create_access_token(data={"sub": new_user.email}, expires_delta=timedelta(days=1))

    # Send the verification email
    send_verification_email(new_user.email, verification_token, new_user.name)

    # Prepare user response data
    user_response = UserResponseSchema(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        is_suspended=new_user.is_suspended,
        image=new_user.user_image,
        credits=new_user.credits,
        country_id=new_user.country_id,
        is_verified=new_user.is_verified,  # Include the verification status
    )

    return user_response

@router.get("/verify", status_code=status.HTTP_200_OK)
def verify_account(token: str, db: Session = Depends(get_db)):
    email = verify_token(token)
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Verify the user
    user.is_verified = True
    db.commit()
    db.refresh(user)

    return {"message": "Account verified successfully"}

@router.post("/login", response_model=dict, status_code=status.HTTP_200_OK)
def login(login_data: LoginSchema, db: Session = Depends(get_db)):
    # Find the user by email
    user = db.query(UserModel).filter(UserModel.email == login_data.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    # Verify the password
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    # Create an access token
    access_token = create_access_token(data={"sub": user.email})

    # Prepare user response data (excluding sensitive information)
    user_response = UserResponseSchema(
        id=user.id,
        email=user.email,
        name=user.name,
        is_suspended=user.is_suspended,
        image=user.user_image,
        credits=user.credits,
        country_id=user.country_id,
        is_verified=user.is_verified,  # Include the verification status
        role=user.role
    )

    return {
        "access_token": access_token,
        "user": user_response
    }