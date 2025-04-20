"""
MixMaster AI - Authentication Routes

This module provides API routes for user authentication, including
registration, login, token refresh, and user profile management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any
import logging

from .auth import (
    UserCreate, UserLogin, Token,
    create_new_user, authenticate_user, create_access_token,
    get_current_user, update_user_last_login,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from datetime import timedelta

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={404: {"description": "Not found"}},
)

@router.post("/register", response_model=Dict[str, Any])
async def register(user_data: UserCreate):
    """
    Register a new user account.
    
    Returns user data excluding sensitive information.
    """
    try:
        user = create_new_user(user_data)
        return user
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering user: {str(e)}"
        )

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and provide access token.
    
    This endpoint is used for OAuth2 password flow.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login timestamp
    update_user_last_login(user["userId"])
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["userId"]},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Dict[str, Any])
async def login(login_data: UserLogin):
    """
    Login user and provide access token and user data.
    
    This is a more user-friendly endpoint that returns both the token and user data.
    """
    user = authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login timestamp
    update_user_last_login(user["userId"])
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["userId"]},
        expires_delta=access_token_expires
    )
    
    # Return token and user data (excluding sensitive information)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "userId": user["userId"],
            "email": user["email"],
            "name": user["name"],
            "accountType": user["accountType"],
            "freeCreditsUsed": user.get("freeCreditsUsed", 0),
            "credits": user.get("credits", 0),
            "totalSongsProcessed": user.get("totalSongsProcessed", 0),
            "subscriptionDetails": user.get("subscriptionDetails")
        }
    }

@router.get("/me", response_model=Dict[str, Any])
async def read_users_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user profile.
    
    Requires authentication.
    """
    # Return user data (excluding sensitive information)
    return {
        "userId": current_user["userId"],
        "email": current_user["email"],
        "name": current_user["name"],
        "accountType": current_user["accountType"],
        "freeCreditsUsed": current_user.get("freeCreditsUsed", 0),
        "credits": current_user.get("credits", 0),
        "totalSongsProcessed": current_user.get("totalSongsProcessed", 0),
        "subscriptionDetails": current_user.get("subscriptionDetails"),
        "createdAt": current_user.get("createdAt"),
        "lastLogin": current_user.get("lastLogin")
    }

@router.post("/logout")
async def logout():
    """
    Logout user.
    
    Note: Since we're using JWT tokens, actual logout happens on the client side
    by removing the token. This endpoint is provided for API completeness.
    """
    return {"message": "Successfully logged out"}
