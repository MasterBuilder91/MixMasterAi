"""
MixMaster AI - Database Interface for Authentication

This module provides database interface functions for the authentication system,
supporting both MongoDB and Replit Database as storage options.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Setup logging
logger = logging.getLogger(__name__)

# Determine which database to use based on environment variable
DB_TYPE = os.environ.get("DB_TYPE", "mongodb").lower()

# MongoDB setup
if DB_TYPE == "mongodb":
    import pymongo
    from pymongo import MongoClient
    
    # Get MongoDB connection string from environment variable
    MONGODB_URI = os.environ.get("MONGODB_URI")
    if not MONGODB_URI:
        logger.warning("MONGODB_URI not set. Using default connection string.")
        MONGODB_URI = "mongodb://localhost:27017/"
    
    # Connect to MongoDB
    try:
        client = MongoClient(MONGODB_URI)
        db = client.mixmaster_db
        users_collection = db.users
        # Create indexes for faster queries
        users_collection.create_index("email", unique=True)
        users_collection.create_index("userId", unique=True)
        logger.info("Connected to MongoDB successfully")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise

# Replit Database setup
elif DB_TYPE == "replit":
    try:
        from replit import db
        logger.info("Using Replit Database")
    except ImportError:
        logger.error("Replit Database module not found. Make sure you're running on Replit.")
        raise

else:
    logger.error(f"Unsupported database type: {DB_TYPE}")
    raise ValueError(f"Unsupported database type: {DB_TYPE}")

# User database functions
def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Get a user by ID."""
    try:
        if DB_TYPE == "mongodb":
            user = users_collection.find_one({"userId": user_id})
            return user
        elif DB_TYPE == "replit":
            user_key = f"user_{user_id}"
            if user_key in db:
                return db[user_key]
            return None
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {str(e)}")
        return None

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get a user by email."""
    try:
        if DB_TYPE == "mongodb":
            user = users_collection.find_one({"email": email})
            return user
        elif DB_TYPE == "replit":
            # Replit DB doesn't support querying by field, so we need to iterate
            for key in db.keys():
                if key.startswith("user_"):
                    user = db[key]
                    if user.get("email") == email:
                        return user
            return None
    except Exception as e:
        logger.error(f"Error getting user by email {email}: {str(e)}")
        return None

def save_user(user_id: str, user_data: Dict[str, Any]) -> bool:
    """Save a user to the database."""
    try:
        if DB_TYPE == "mongodb":
            result = users_collection.update_one(
                {"userId": user_id},
                {"$set": user_data},
                upsert=True
            )
            return result.acknowledged
        elif DB_TYPE == "replit":
            user_key = f"user_{user_id}"
            db[user_key] = user_data
            return True
    except Exception as e:
        logger.error(f"Error saving user {user_id}: {str(e)}")
        return False

def update_user(user_id: str, update_data: Dict[str, Any]) -> bool:
    """Update a user in the database."""
    try:
        if DB_TYPE == "mongodb":
            result = users_collection.update_one(
                {"userId": user_id},
                {"$set": update_data}
            )
            return result.acknowledged and result.modified_count > 0
        elif DB_TYPE == "replit":
            user_key = f"user_{user_id}"
            if user_key in db:
                user = db[user_key]
                for key, value in update_data.items():
                    user[key] = value
                db[user_key] = user
                return True
            return False
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        return False

def delete_user(user_id: str) -> bool:
    """Delete a user from the database."""
    try:
        if DB_TYPE == "mongodb":
            result = users_collection.delete_one({"userId": user_id})
            return result.acknowledged and result.deleted_count > 0
        elif DB_TYPE == "replit":
            user_key = f"user_{user_id}"
            if user_key in db:
                del db[user_key]
                return True
            return False
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        return False

def list_users(limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
    """List users from the database."""
    try:
        if DB_TYPE == "mongodb":
            users = list(users_collection.find({}).skip(skip).limit(limit))
            return users
        elif DB_TYPE == "replit":
            users = []
            count = 0
            for key in db.keys():
                if key.startswith("user_"):
                    count += 1
                    if count > skip:
                        users.append(db[key])
                        if len(users) >= limit:
                            break
            return users
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        return []

def update_user_stripe_id(user_id: str, stripe_customer_id: str) -> bool:
    """Update a user's Stripe customer ID."""
    try:
        if DB_TYPE == "mongodb":
            result = users_collection.update_one(
                {"userId": user_id},
                {"$set": {"stripeCustomerId": stripe_customer_id}}
            )
            return result.acknowledged and result.modified_count > 0
        elif DB_TYPE == "replit":
            user_key = f"user_{user_id}"
            if user_key in db:
                user = db[user_key]
                user["stripeCustomerId"] = stripe_customer_id
                db[user_key] = user
                return True
            return False
    except Exception as e:
        logger.error(f"Error updating Stripe ID for user {user_id}: {str(e)}")
        return False

def get_user_by_stripe_id(stripe_customer_id: str) -> Optional[Dict[str, Any]]:
    """Get a user by Stripe customer ID."""
    try:
        if DB_TYPE == "mongodb":
            user = users_collection.find_one({"stripeCustomerId": stripe_customer_id})
            return user
        elif DB_TYPE == "replit":
            for key in db.keys():
                if key.startswith("user_"):
                    user = db[key]
                    if user.get("stripeCustomerId") == stripe_customer_id:
                        return user
            return None
    except Exception as e:
        logger.error(f"Error getting user by Stripe ID {stripe_customer_id}: {str(e)}")
        return None
