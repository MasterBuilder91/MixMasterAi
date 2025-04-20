"""
MixMaster AI - Payment Processor with Platform Adaptations

This module provides functionality for integrating with Stripe for payment processing
across different deployment platforms, including handling subscriptions, one-time payments, and webhooks.
"""

import os
import stripe
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

from .stripe_config import get_stripe_config

# Setup logging
logger = logging.getLogger(__name__)

# Initialize Stripe with API key from configuration
stripe_config = get_stripe_config()
stripe.api_key = stripe_config.api_key

# Webhook secret for verifying Stripe webhook events
STRIPE_WEBHOOK_SECRET = stripe_config.webhook_secret

# Product and price IDs
PRODUCT_IDS = {
    "credit": None,  # Will be set dynamically for pay-per-use
    "monthly_subscription": stripe_config.monthly_subscription_price_id,
    "lifetime_access": stripe_config.lifetime_access_price_id
}

# Import user management functions
from ..auth.db_interface import (
    get_user, update_user, get_user_by_stripe_id, update_user_stripe_id
)

# Models for payment data
class PaymentIntent:
    """Model for payment intent data."""
    def __init__(self, payment_intent_id: str, amount: int, currency: str, 
                 customer_id: str, status: str, metadata: Dict[str, Any]):
        self.id = payment_intent_id
        self.amount = amount
        self.currency = currency
        self.customer_id = customer_id
        self.status = status
        self.metadata = metadata

class Subscription:
    """Model for subscription data."""
    def __init__(self, subscription_id: str, customer_id: str, status: str,
                 current_period_start: int, current_period_end: int, 
                 cancel_at_period_end: bool, metadata: Dict[str, Any]):
        self.id = subscription_id
        self.customer_id = customer_id
        self.status = status
        self.current_period_start = datetime.fromtimestamp(current_period_start)
        self.current_period_end = datetime.fromtimestamp(current_period_end)
        self.cancel_at_period_end = cancel_at_period_end
        self.metadata = metadata

# Payment processing functions
def create_stripe_customer(user_id: str, email: str, name: str) -> Optional[str]:
    """
    Create a Stripe customer for a user.
    
    Args:
        user_id: The user's ID in our system
        email: The user's email address
        name: The user's name
    
    Returns:
        The Stripe customer ID if successful, None otherwise
    """
    if not stripe_config.is_configured():
        logger.error("Stripe is not properly configured. Cannot create customer.")
        return None
        
    try:
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={"user_id": user_id}
        )
        
        # Update user with Stripe customer ID
        update_user_stripe_id(user_id, customer.id)
        
        return customer.id
    except Exception as e:
        logger.error(f"Error creating Stripe customer for user {user_id}: {str(e)}")
        return None

def create_payment_intent(user_id: str, amount: int, currency: str = "usd", 
                         payment_type: str = "credit", metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
    """
    Create a payment intent for a one-time payment.
    
    Args:
        user_id: The user's ID in our system
        amount: The amount to charge in cents (e.g., 500 for $5.00)
        currency: The currency to use (default: usd)
        payment_type: The type of payment (credit, lifetime_access)
        metadata: Additional metadata to store with the payment
    
    Returns:
        Payment intent details if successful, None otherwise
    """
    if not stripe_config.is_configured():
        logger.error("Stripe is not properly configured. Cannot create payment intent.")
        return None
        
    try:
        user = get_user(user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            return None
        
        stripe_customer_id = user.get("stripeCustomerId")
        if not stripe_customer_id:
            # Create Stripe customer if not exists
            stripe_customer_id = create_stripe_customer(
                user_id, user.get("email"), user.get("name")
            )
            if not stripe_customer_id:
                logger.error(f"Failed to create Stripe customer for user {user_id}")
                return None
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "user_id": user_id,
            "payment_type": payment_type,
            "platform": os.environ.get("DEPLOYMENT_PLATFORM", "docker")
        })
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            customer=stripe_customer_id,
            metadata=metadata,
            payment_method_types=["card"],
        )
        
        return {
            "clientSecret": intent.client_secret,
            "paymentIntentId": intent.id,
            "amount": intent.amount,
            "currency": intent.currency
        }
    except Exception as e:
        logger.error(f"Error creating payment intent for user {user_id}: {str(e)}")
        return None

def create_subscription(user_id: str, price_id: str = None, 
                       metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
    """
    Create a subscription for a user.
    
    Args:
        user_id: The user's ID in our system
        price_id: The Stripe price ID for the subscription
        metadata: Additional metadata to store with the subscription
    
    Returns:
        Subscription details if successful, None otherwise
    """
    if not stripe_config.is_configured():
        logger.error("Stripe is not properly configured. Cannot create subscription.")
        return None
        
    try:
        user = get_user(user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            return None
        
        # Use default monthly subscription price if not specified
        if price_id is None:
            price_id = PRODUCT_IDS.get("monthly_subscription")
            if not price_id:
                logger.error("Monthly subscription price ID not configured")
                return None
        
        stripe_customer_id = user.get("stripeCustomerId")
        if not stripe_customer_id:
            # Create Stripe customer if not exists
            stripe_customer_id = create_stripe_customer(
                user_id, user.get("email"), user.get("name")
            )
            if not stripe_customer_id:
                logger.error(f"Failed to create Stripe customer for user {user_id}")
                return None
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "user_id": user_id,
            "platform": os.environ.get("DEPLOYMENT_PLATFORM", "docker")
        })
        
        # Create subscription
        subscription = stripe.Subscription.create(
            customer=stripe_customer_id,
            items=[
                {"price": price_id},
            ],
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"],
            metadata=metadata
        )
        
        return {
            "subscriptionId": subscription.id,
            "clientSecret": subscription.latest_invoice.payment_intent.client_secret,
            "subscriptionStatus": subscription.status
        }
    except Exception as e:
        logger.error(f"Error creating subscription for user {user_id}: {str(e)}")
        return None

def cancel_subscription(subscription_id: str, cancel_immediately: bool = False) -> bool:
    """
    Cancel a subscription.
    
    Args:
        subscription_id: The Stripe subscription ID
        cancel_immediately: Whether to cancel immediately or at the end of the period
    
    Returns:
        True if successful, False otherwise
    """
    if not stripe_config.is_configured():
        logger.error("Stripe is not properly configured. Cannot cancel subscription.")
        return False
        
    try:
        if cancel_immediately:
            # Cancel immediately
            stripe.Subscription.delete(subscription_id)
        else:
            # Cancel at period end
            stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
        
        return True
    except Exception as e:
        logger.error(f"Error canceling subscription {subscription_id}: {str(e)}")
        return False

def get_subscription_details(subscription_id: str) -> Optional[Subscription]:
    """
    Get details of a subscription.
    
    Args:
        subscription_id: The Stripe subscription ID
    
    Returns:
        Subscription details if successful, None otherwise
    """
    if not stripe_config.is_configured():
        logger.error("Stripe is not properly configured. Cannot get subscription details.")
        return None
        
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        return Subscription(
            subscription_id=subscription.id,
            customer_id=subscription.customer,
            status=subscription.status,
            current_period_start=subscription.current_period_start,
            current_period_end=subscription.current_period_end,
            cancel_at_period_end=subscription.cancel_at_period_end,
            metadata=subscription.metadata
        )
    except Exception as e:
        logger.error(f"Error getting subscription details {subscription_id}: {str(e)}")
        return None

def get_payment_intent_details(payment_intent_id: str) -> Optional[PaymentIntent]:
    """
    Get details of a payment intent.
    
    Args:
        payment_intent_id: The Stripe payment intent ID
    
    Returns:
        Payment intent details if successful, None otherwise
    """
    if not stripe_config.is_configured():
        logger.error("Stripe is not properly configured. Cannot get payment intent details.")
        return None
        
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        return PaymentIntent(
            payment_intent_id=payment_intent.id,
            amount=payment_intent.amount,
            currency=payment_intent.currency,
            customer_id=payment_intent.customer,
            status=payment_intent.status,
            metadata=payment_intent.metadata
        )
    except Exception as e:
        logger.error(f"Error getting payment intent details {payment_intent_id}: {str(e)}")
        return None

def process_successful_payment(payment_intent: Dict[str, Any]) -> bool:
    """
    Process a successful payment by updating user credits or subscription.
    
    Args:
        payment_intent: The Stripe payment intent object
    
    Returns:
        True if successful, False otherwise
    """
    try:
        metadata = payment_intent.get("metadata", {})
        user_id = metadata.get("user_id")
        payment_type = metadata.get("payment_type")
        
        if not user_id:
            # Try to find user by Stripe customer ID
            customer_id = payment_intent.get("customer")
            if customer_id:
                user = get_user_by_stripe_id(customer_id)
                if user:
                    user_id = user.get("userId")
        
        if not user_id:
            logger.error(f"User ID not found in payment intent {payment_intent.get('id')}")
            return False
        
        user = get_user(user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            return False
        
        # Process based on payment type
        if payment_type == "credit":
            # Calculate number of credits based on amount
            amount = payment_intent.get("amount", 0)
            credits_purchased = amount // 500  # $5 per credit
            
            # Update user credits
            current_credits = user.get("credits", 0)
            new_credits = current_credits + credits_purchased
            
            update_data = {
                "credits": new_credits,
                "accountType": "pay-per-use"
            }
            
            # Record transaction
            transaction = {
                "type": "credit_purchase",
                "amount": amount,
                "credits": credits_purchased,
                "paymentIntentId": payment_intent.get("id"),
                "timestamp": datetime.utcnow().isoformat(),
                "platform": metadata.get("platform", "docker")
            }
            
            # Add transaction to user's transaction history
            transactions = user.get("transactions", [])
            transactions.append(transaction)
            update_data["transactions"] = transactions
            
            # Update user
            update_user(user_id, update_data)
            
            logger.info(f"Added {credits_purchased} credits to user {user_id}")
            return True
            
        elif payment_type == "lifetime_access":
            # Update user account type to lifetime
            update_data = {
                "accountType": "lifetime"
            }
            
            # Record transaction
            transaction = {
                "type": "lifetime_purchase",
                "amount": payment_intent.get("amount", 0),
                "paymentIntentId": payment_intent.get("id"),
                "timestamp": datetime.utcnow().isoformat(),
                "platform": metadata.get("platform", "docker")
            }
            
            # Add transaction to user's transaction history
            transactions = user.get("transactions", [])
            transactions.append(transaction)
            update_data["transactions"] = transactions
            
            # Update user
            update_user(user_id, update_data)
            
            logger.info(f"Upgraded user {user_id} to lifetime access")
            return True
            
        else:
            logger.warning(f"Unknown payment type: {payment_type}")
            return False
            
    except Exception as e:
        logger.error(f"Error processing successful payment: {str(e)}")
        return False

def process_successful_subscription(subscription: Dict[str, Any]) -> bool:
    """
    Process a successful subscription by updating user subscription details.
    
    Args:
        subscription: The Stripe subscription object
    
    Returns:
        True if successful, False otherwise
    """
    try:
        metadata = subscription.get("metadata", {})
        user_id = metadata.get("user_id")
        
        if not user_id:
            # Try to find user by Stripe customer ID
            customer_id = subscription.get("customer")
            if customer_id:
                user = get_user_by_stripe_id(customer_id)
                if user:
                    user_id = user.get("userId")
        
        if not user_id:
            logger.error(f"User ID not found in subscription {subscription.get('id')}")
            return False
        
        user = get_user(user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            return False
        
        # Calculate subscription period
        current_period_start = datetime.fromtimestamp(subscription.get("current_period_start", 0))
        current_period_end = datetime.fromtimestamp(subscription.get("current_period_end", 0))
        
        # Update user subscription details
        subscription_details = {
            "subscriptionId": subscription.get("id"),
            "status": subscription.get("status"),
            "startDate": current_period_start.isoformat(),
            "endDate": current_period_end.isoformat(),
            "cancelAtPeriodEnd": subscription.get("cancel_at_period_end", False),
            "platform": metadata.get("platform", "docker")
        }
        
        update_data = {
            "accountType": "subscription",
            "subscriptionDetails": subscription_details
        }
        
        # Record transaction
        transaction = {
            "type": "subscription_payment",
            "subscriptionId": subscription.get("id"),
            "period": {
                "start": current_period_start.isoformat(),
                "end": current_period_end.isoformat()
            },
            "timestamp": datetime.utcnow().isoformat(),
            "platform": metadata.get("platform", "docker")
        }
        
        # Add transaction to user's transaction history
        transactions = user.get("transactions", [])
        transactions.append(transaction)
        update_data["transactions"] = transactions
        
        # Update user
        update_user(user_id, update_data)
        
        logger.info(f"Updated subscription for user {user_id}")
        return True
            
    except Exception as e:
        logger.error(f"Error processing successful subscription: {str(e)}")
        return False

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """
    Verify the signature of a Stripe webhook event.
    
    Args:
        payload: The raw request payload
        signature: The Stripe signature header
    
    Returns:
        True if signature is valid, False otherwise
    """
    if not STRIPE_WEBHOOK_SECRET:
        logger.warning("STRIPE_WEBHOOK_SECRET not set. Webhook verification disabled.")
        return True
    
    try:
        stripe.Webhook.construct_event(
            payload, signature, STRIPE_WEBHOOK_SECRET
        )
        return True
    except Exception as e:
        logger.error(f"Webhook signature verification failed: {str(e)}")
        return False

def handle_webhook_event(event_type: str, event_data: Dict[str, Any]) -> bool:
    """
    Handle a Stripe webhook event.
    
    Args:
        event_type: The type of event (e.g., payment_intent.succeeded)
        event_data: The event data
    
    Returns:
        True if handled successfully, False otherwise
    """
    try:
        if event_type == "payment_intent.succeeded":
            return process_successful_payment(event_data.get("object", {}))
            
        elif event_type == "customer.subscription.created" or event_type == "customer.subscription.updated":
            return process_successful_subscription(event_data.get("object", {}))
            
        elif event_type == "customer.subscription.deleted":
            # Handle subscription cancellation
            subscription = event_data.get("object", {})
            metadata = subscription.get("metadata", {})
            user_id = metadata.get("user_id")
            
            if not user_id:
                # Try to find user by Stripe customer ID
                customer_id = subscription.get("customer")
                if customer_id:
                    user = get_user_by_stripe_id(customer_id)
                    if user:
                        user_id = user.get("userId")
            
            if user_id:
                # Update user subscription status
                user = get_user(user_id)
                if user:
                    subscription_details = user.get("subscriptionDetails", {})
                    if subscription_details:
                        subscription_details["status"] = "canceled"
                        update_user(user_id, {"subscriptionDetails": subscription_details})
                        
                        # If this was their only subscription, revert to free tier
                        if user.get("accountType") == "subscription":
                            update_user(user_id, {"accountType": "free"})
                        
                        logger.info(f"Subscription canceled for user {user_id}")
                        return True
            
            logger.warning(f"User not found for subscription {subscription.get('id')}")
            return False
            
        else:
            logger.info(f"Unhandled webhook event type: {event_type}")
            return True  # Return true for events we don't need to handle
            
    except Exception as e:
        logger.error(f"Error handling webhook event {event_type}: {str(e)}")
        return False
