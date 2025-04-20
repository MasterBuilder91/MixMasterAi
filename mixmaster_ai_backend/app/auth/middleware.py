"""
MixMaster AI - Authentication Middleware

This module provides middleware functions for checking user authentication,
subscription status, and credit usage before processing requests.
"""

from fastapi import Depends, HTTPException, status
from typing import Dict, Any, Optional, Callable
import logging
from datetime import datetime

from .auth import get_current_user

# Setup logging
logger = logging.getLogger(__name__)

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get the current active user.
    
    Raises an exception if the user is inactive or deleted.
    """
    if current_user.get("isActive") is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    return current_user

async def check_free_tier_eligibility(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Check if a user on the free tier is eligible to process a song.
    
    Free tier users can only process 1 song total.
    """
    if current_user["accountType"] != "free":
        return current_user
    
    if current_user.get("freeCreditsUsed", 0) >= 1:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Free credit used. Please upgrade to process more songs.",
            headers={"X-Upgrade-Required": "true"}
        )
    
    return current_user

async def check_pay_per_use_eligibility(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Check if a pay-per-use user has available credits.
    
    Pay-per-use users need at least 1 credit to process a song.
    """
    if current_user["accountType"] != "pay-per-use":
        return current_user
    
    if current_user.get("credits", 0) <= 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="No credits remaining. Please purchase more credits.",
            headers={"X-Purchase-Required": "true"}
        )
    
    return current_user

async def check_subscription_eligibility(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Check if a subscription user has an active subscription.
    
    Subscription users need an active subscription that hasn't expired.
    """
    if current_user["accountType"] != "subscription":
        return current_user
    
    subscription_details = current_user.get("subscriptionDetails", {})
    if not subscription_details:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="No active subscription found. Please subscribe to continue.",
            headers={"X-Subscribe-Required": "true"}
        )
    
    end_date_str = subscription_details.get("endDate")
    if not end_date_str:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Invalid subscription details. Please contact support.",
            headers={"X-Subscribe-Required": "true"}
        )
    
    try:
        end_date = datetime.fromisoformat(end_date_str)
        if datetime.utcnow() > end_date:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Subscription expired. Please renew your subscription.",
                headers={"X-Renew-Required": "true"}
            )
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Invalid subscription date format. Please contact support.",
            headers={"X-Subscribe-Required": "true"}
        )
    
    return current_user

async def check_processing_eligibility(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Check if a user is eligible to process a song based on their account type.
    
    This is a unified middleware that handles all account types.
    """
    account_type = current_user["accountType"]
    
    if account_type == "free":
        # Free tier: Check if free credit is used
        if current_user.get("freeCreditsUsed", 0) >= 1:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Free credit used. Please upgrade to process more songs.",
                headers={"X-Upgrade-Required": "true"}
            )
    
    elif account_type == "pay-per-use":
        # Pay-per-use: Check if user has credits
        if current_user.get("credits", 0) <= 0:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="No credits remaining. Please purchase more credits.",
                headers={"X-Purchase-Required": "true"}
            )
    
    elif account_type == "subscription":
        # Subscription: Check if subscription is active
        subscription_details = current_user.get("subscriptionDetails", {})
        if not subscription_details:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="No active subscription found. Please subscribe to continue.",
                headers={"X-Subscribe-Required": "true"}
            )
        
        end_date_str = subscription_details.get("endDate")
        if not end_date_str:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Invalid subscription details. Please contact support.",
                headers={"X-Subscribe-Required": "true"}
            )
        
        try:
            end_date = datetime.fromisoformat(end_date_str)
            if datetime.utcnow() > end_date:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="Subscription expired. Please renew your subscription.",
                    headers={"X-Renew-Required": "true"}
                )
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Invalid subscription date format. Please contact support.",
                headers={"X-Subscribe-Required": "true"}
            )
    
    elif account_type == "lifetime":
        # Lifetime: Always allowed
        pass
    
    else:
        # Unknown account type
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown account type: {account_type}"
        )
    
    return current_user

def create_admin_dependency(admin_emails: Optional[list] = None) -> Callable:
    """
    Create a dependency for admin-only routes.
    
    Args:
        admin_emails: List of email addresses that have admin access.
                     If None, defaults to the ADMIN_EMAILS environment variable.
    
    Returns:
        A dependency function that checks if the current user is an admin.
    """
    import os
    
    if admin_emails is None:
        # Get admin emails from environment variable
        admin_emails_str = os.environ.get("ADMIN_EMAILS", "")
        admin_emails = [email.strip() for email in admin_emails_str.split(",") if email.strip()]
    
    async def is_admin(current_user: Dict[str, Any] = Depends(get_current_active_user)):
        if current_user.get("isAdmin") is True:
            return current_user
        
        if current_user.get("email") in admin_emails:
            return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return is_admin
