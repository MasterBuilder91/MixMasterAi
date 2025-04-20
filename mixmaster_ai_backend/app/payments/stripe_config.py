"""
MixMaster AI - Stripe Configuration for Alternative Platforms

This module provides configuration and helper functions for Stripe integration
across different deployment platforms.
"""

import os
import logging
from typing import Dict, Any, Optional

# Setup logging
logger = logging.getLogger(__name__)

class StripeConfig:
    """
    Stripe configuration handler for different deployment environments.
    Ensures proper configuration across various deployment platforms.
    """
    
    def __init__(self):
        # Get Stripe API keys from environment variables
        self.api_key = os.environ.get("STRIPE_API_KEY")
        self.webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
        self.publishable_key = os.environ.get("NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY")
        
        # Get product IDs from environment variables
        self.monthly_subscription_price_id = os.environ.get("STRIPE_MONTHLY_SUBSCRIPTION_PRICE_ID")
        self.lifetime_access_price_id = os.environ.get("STRIPE_LIFETIME_ACCESS_PRICE_ID")
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate Stripe configuration and log warnings for missing values."""
        if not self.api_key:
            logger.warning("STRIPE_API_KEY not set. Payment processing will not work.")
        
        if not self.webhook_secret:
            logger.warning("STRIPE_WEBHOOK_SECRET not set. Webhook verification disabled.")
        
        if not self.publishable_key:
            logger.warning("NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY not set. Frontend payment integration will not work.")
        
        if not self.monthly_subscription_price_id:
            logger.warning("STRIPE_MONTHLY_SUBSCRIPTION_PRICE_ID not set. Monthly subscription option will not work.")
        
        if not self.lifetime_access_price_id:
            logger.warning("STRIPE_LIFETIME_ACCESS_PRICE_ID not set. Lifetime access option will not work.")
    
    def get_config(self) -> Dict[str, Any]:
        """Get Stripe configuration as a dictionary."""
        return {
            "api_key": self.api_key,
            "webhook_secret": self.webhook_secret,
            "publishable_key": self.publishable_key,
            "product_ids": {
                "monthly_subscription": self.monthly_subscription_price_id,
                "lifetime_access": self.lifetime_access_price_id
            }
        }
    
    def is_configured(self) -> bool:
        """Check if Stripe is properly configured."""
        return bool(self.api_key and self.publishable_key)
    
    def get_webhook_url(self, base_url: Optional[str] = None) -> str:
        """
        Get the webhook URL for the current deployment.
        
        Args:
            base_url: Base URL of the application. If not provided, will try to determine from environment.
        
        Returns:
            Webhook URL string
        """
        if not base_url:
            # Try to determine base URL from environment
            domain = os.environ.get("DOMAIN_NAME")
            if domain:
                base_url = f"https://{domain}"
            else:
                # Default to localhost for development
                base_url = "http://localhost:8000"
        
        return f"{base_url}/api/payments/webhook"
    
    def get_frontend_config(self) -> Dict[str, Any]:
        """Get Stripe configuration for the frontend."""
        return {
            "publishableKey": self.publishable_key,
            "productIds": {
                "monthlySubscription": self.monthly_subscription_price_id,
                "lifetimeAccess": self.lifetime_access_price_id
            }
        }

# Create a singleton instance
stripe_config = StripeConfig()

def get_stripe_config() -> StripeConfig:
    """Get the Stripe configuration singleton."""
    return stripe_config
