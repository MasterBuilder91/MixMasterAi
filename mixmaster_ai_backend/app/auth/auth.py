"""
MixMaster AI - User Authentication System

This module provides user authentication functionality for the MixMaster AI platform,
including user registration, login, token generation, and password management.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, validator
import uuid
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-for-development")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

# Database interface (to be replaced with actual implementation)
from .db_interface import get_user_by_email, get_user, save_user, update_user

# Models
class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

# Password functions
def verify_password(plain_password, hashed_password):
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Generate a password hash."""
    return pwd_context.hash(password)

# Authentication functions
def authenticate_user(email: str, password: str):
    """Authenticate a user by email and password."""
    user = get_user_by_email(email)
    if not user:
        return False
    if not verify_password(password, user["passwordHash"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get the current user from a JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    user = get_user(token_data.user_id)
    if user is None:
        raise credentials_exception
    return user

# User management functions
def create_new_user(user_data: UserCreate) -> Dict[str, Any]:
    """Create a new user account."""
    # Check if user already exists
    existing_user = get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user object
    user_id = str(uuid.uuid4())
    user = {
        "userId": user_id,
        "email": user_data.email,
        "passwordHash": hashed_password,
        "name": user_data.name,
        "createdAt": datetime.utcnow().isoformat(),
        "lastLogin": datetime.utcnow().isoformat(),
        "accountType": "free",
        "freeCreditsUsed": 0,
        "credits": 0,
        "totalSongsProcessed": 0,
        "stripeCustomerId": None,
        "subscriptionDetails": None,
        "paymentMethods": []
    }
    
    # Save user to database
    save_user(user_id, user)
    
    # Return user data (excluding sensitive information)
    return {
        "userId": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "accountType": "free",
        "createdAt": user["createdAt"]
    }

def update_user_last_login(user_id: str):
    """Update the last login timestamp for a user."""
    update_user(user_id, {"lastLogin": datetime.utcnow().isoformat()})

def update_user_account_type(user_id: str, account_type: str):
    """Update a user's account type."""
    valid_types = ["free", "pay-per-use", "subscription", "lifetime"]
    if account_type not in valid_types:
        raise ValueError(f"Invalid account type. Must be one of: {', '.join(valid_types)}")
    
    update_user(user_id, {"accountType": account_type})

def update_user_subscription_details(user_id: str, subscription_details: Dict[str, Any]):
    """Update a user's subscription details."""
    update_user(user_id, {"subscriptionDetails": subscription_details})

def update_user_credits(user_id: str, credits: int):
    """Update a user's credit balance."""
    if credits < 0:
        raise ValueError("Credits cannot be negative")
    
    update_user(user_id, {"credits": credits})

def increment_free_credits_used(user_id: str):
    """Increment the free credits used counter for a user."""
    user = get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    update_user(user_id, {"freeCreditsUsed": user.get("freeCreditsUsed", 0) + 1})

def increment_total_songs_processed(user_id: str):
    """Increment the total songs processed counter for a user."""
    user = get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    update_user(user_id, {"totalSongsProcessed": user.get("totalSongsProcessed", 0) + 1})

def check_processing_eligibility(user: Dict[str, Any]):
    """Check if a user is eligible to process a song based on their account type and credits."""
    if user["accountType"] == "free":
        if user.get("freeCreditsUsed", 0) >= 1:
            return False, "Free credit used. Please upgrade to process more songs."
    
    elif user["accountType"] == "pay-per-use":
        if user.get("credits", 0) <= 0:
            return False, "No credits remaining. Please purchase more credits."
    
    elif user["accountType"] == "subscription":
        # Check if subscription is active
        subscription_details = user.get("subscriptionDetails", {})
        if not subscription_details:
            return False, "No active subscription found."
        
        end_date_str = subscription_details.get("endDate")
        if not end_date_str:
            return False, "Invalid subscription details."
        
        try:
            end_date = datetime.fromisoformat(end_date_str)
            if datetime.utcnow() > end_date:
                return False, "Subscription expired. Please renew your subscription."
        except (ValueError, TypeError):
            return False, "Invalid subscription date format."
    
    # Lifetime users always have access
    return True, ""
