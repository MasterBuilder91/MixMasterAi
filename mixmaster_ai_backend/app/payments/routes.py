"""
MixMaster AI - Payment API Routes

This module provides API routes for payment processing, including
credit purchases, subscriptions, and webhook handling.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from typing import Dict, Any, Optional, List
import logging
import json
from pydantic import BaseModel, Field

from ..auth.auth import get_current_user
from ..auth.middleware import get_current_active_user
from .payment_processor import (
    create_payment_intent, create_subscription, cancel_subscription,
    get_subscription_details, verify_webhook_signature, handle_webhook_event
)

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/payments",
    tags=["payments"],
    responses={404: {"description": "Not found"}},
)

# Models
class CreditPurchaseRequest(BaseModel):
    credits: int = Field(..., gt=0, description="Number of credits to purchase")

class SubscriptionRequest(BaseModel):
    plan: str = Field(..., description="Subscription plan (monthly)")

class WebhookEvent(BaseModel):
    id: str
    type: str
    data: Dict[str, Any]

# Routes
@router.post("/credits/purchase", response_model=Dict[str, Any])
async def purchase_credits(
    request: CreditPurchaseRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Create a payment intent for purchasing credits.
    
    Returns client secret for completing the payment on the frontend.
    """
    # Calculate amount based on number of credits
    amount = request.credits * 500  # $5.00 per credit = 500 cents
    
    # Create payment intent
    payment_intent = create_payment_intent(
        user_id=current_user["userId"],
        amount=amount,
        payment_type="credit",
        metadata={"credits": request.credits}
    )
    
    if not payment_intent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment intent"
        )
    
    return payment_intent

@router.post("/subscription/create", response_model=Dict[str, Any])
async def create_user_subscription(
    request: SubscriptionRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Create a subscription for the user.
    
    Returns client secret for completing the subscription payment on the frontend.
    """
    # Determine price ID based on plan
    price_id = None
    if request.plan == "monthly":
        import os
        price_id = os.environ.get("STRIPE_MONTHLY_SUBSCRIPTION_PRICE_ID")
    
    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid subscription plan: {request.plan}"
        )
    
    # Create subscription
    subscription = create_subscription(
        user_id=current_user["userId"],
        price_id=price_id
    )
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subscription"
        )
    
    return subscription

@router.post("/lifetime/purchase", response_model=Dict[str, Any])
async def purchase_lifetime_access(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Create a payment intent for purchasing lifetime access.
    
    Returns client secret for completing the payment on the frontend.
    """
    # Fixed amount for lifetime access
    amount = 50000  # $500.00 = 50000 cents
    
    # Create payment intent
    payment_intent = create_payment_intent(
        user_id=current_user["userId"],
        amount=amount,
        payment_type="lifetime_access"
    )
    
    if not payment_intent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment intent"
        )
    
    return payment_intent

@router.post("/subscription/cancel")
async def cancel_user_subscription(
    cancel_immediately: bool = False,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Cancel the user's subscription.
    
    By default, cancels at the end of the current billing period.
    Set cancel_immediately=true to cancel immediately.
    """
    subscription_details = current_user.get("subscriptionDetails")
    if not subscription_details:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription found"
        )
    
    subscription_id = subscription_details.get("subscriptionId")
    if not subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subscription details"
        )
    
    # Cancel subscription
    success = cancel_subscription(subscription_id, cancel_immediately)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )
    
    return {"message": "Subscription canceled successfully"}

@router.get("/subscription/details", response_model=Dict[str, Any])
async def get_user_subscription_details(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get details of the user's subscription.
    """
    subscription_details = current_user.get("subscriptionDetails")
    if not subscription_details:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription found"
        )
    
    subscription_id = subscription_details.get("subscriptionId")
    if not subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subscription details"
        )
    
    # Get subscription details from Stripe
    subscription = get_subscription_details(subscription_id)
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get subscription details"
        )
    
    return {
        "id": subscription.id,
        "status": subscription.status,
        "currentPeriodStart": subscription.current_period_start.isoformat(),
        "currentPeriodEnd": subscription.current_period_end.isoformat(),
        "cancelAtPeriodEnd": subscription.cancel_at_period_end
    }

@router.post("/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events.
    """
    # Get the signature from the headers
    signature = request.headers.get("stripe-signature")
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature"
        )
    
    # Get the raw request body
    payload = await request.body()
    
    # Verify the signature
    if not verify_webhook_signature(payload, signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Stripe signature"
        )
    
    # Parse the event
    try:
        event = json.loads(payload)
        event_type = event.get("type")
        event_data = event.get("data", {})
        
        # Handle the event
        success = handle_webhook_event(event_type, event_data)
        
        if not success:
            logger.warning(f"Failed to handle webhook event: {event_type}")
            # Don't return an error to Stripe, as they will retry
        
        return {"status": "success"}
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        # Don't return an error to Stripe, as they will retry
        return {"status": "error", "message": str(e)}

@router.get("/transactions", response_model=List[Dict[str, Any]])
async def get_user_transactions(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get the user's transaction history.
    """
    transactions = current_user.get("transactions", [])
    
    # Sort transactions by timestamp (newest first)
    transactions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return transactions
