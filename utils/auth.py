from fastapi import HTTPException, status, BackgroundTasks, Request
from pydantic import EmailStr
from jose import jwt
from dotenv import load_dotenv
import os
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
import pytz

from utils.mailconfig import render_template, send_email

load_dotenv()

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    utc_timezone = pytz.UTC
    if expires_delta:
        expire = datetime.now(utc_timezone) + expires_delta
    else:
        expire = datetime.now(utc_timezone) + timedelta(days=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

def generate_verification_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    utc_timezone = pytz.UTC
    if expires_delta:
        expire = datetime.now(utc_timezone) + expires_delta
    else:
        expire = datetime.now(utc_timezone) + timedelta(days=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email = payload.get("sub")
        return email
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def send_verification_email(email: EmailStr, token: str, name: str):
    domain =  os.environ.get("APP_HOST")
    verification_url = f"{domain}/api/v1/users/verify?token={token}"
    subject = "Fur and Furble Account Verification"
    html_content = render_template('verification_email.html', name=name, verification_url=verification_url)
    
    send_email(email, subject, html_content, name)