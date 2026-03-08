"""
Shared database and utilities for Titelli routers.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException, Header
import os
import jwt
import bcrypt
import uuid
from datetime import datetime, timezone, timedelta

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Config
JWT_SECRET = os.environ.get('JWT_SECRET', 'titelli_jwt_secret_key_2024')
JWT_ALGORITHM = "HS256"

# Stripe Config
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')

# Titelli Fees Configuration
TITELLI_FEES = {
    'management_fee': 0.10,      # 10% frais de gestion
    'transaction_fee': 0.029,    # 2.9% frais de transaction
    'investment_commission': 0.12  # 12% commission sur profits d'investissement
}

# Premium plans configuration
PREMIUM_PLANS = {
    'free': {
        'name': 'Gratuit',
        'price': 0,
        'cashback_rate': 0.01,  # 1%
        'features': ['Accès aux prestataires', 'Mode de vie basique', 'Notifications']
    },
    'premium': {
        'name': 'Premium',
        'price': 9.99,
        'cashback_rate': 0.10,  # 10%
        'features': ['10% cashback', 'Accès prioritaire', 'Offres exclusives', 'Support prioritaire']
    },
    'vip': {
        'name': 'VIP',
        'price': 19.99,
        'cashback_rate': 0.15,  # 15%
        'features': ['15% cashback', 'Accès VIP', 'Événements privés', 'Conciergerie personnelle', 'Cadeaux surprises']
    }
}



def verify_password(password: str, stored_password: str) -> bool:
    return password == stored_password


def create_token(user_id: str, user_type: str) -> str:
    payload = {
        'user_id': user_id,
        'user_type': user_type,
        'exp': datetime.now(timezone.utc) + timedelta(days=30)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token manquant")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = await db.users.find_one({"id": payload['user_id']}, {"_id": 0, "password": 0})
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")


async def get_user_cashback_rate(user_id: str) -> float:
    """Get the user's cashback rate based on their subscription plan."""
    subscription = await db.subscriptions.find_one({
        "user_id": user_id,
        "status": "active"
    })
    
    if subscription:
        plan = subscription.get('plan', 'free')
        return PREMIUM_PLANS.get(plan, PREMIUM_PLANS['free'])['cashback_rate']
    
    user = await db.users.find_one({"id": user_id})
    if user:
        plan = user.get('premium_plan', 'free')
        if user.get('is_premium') and plan in ['premium', 'vip']:
            return PREMIUM_PLANS.get(plan, PREMIUM_PLANS['free'])['cashback_rate']
    
    return PREMIUM_PLANS['free']['cashback_rate']


async def get_user_plan(user_id: str) -> str:
    """Get user's current subscription plan"""
    subscription = await db.subscriptions.find_one({
        "user_id": user_id,
        "status": "active"
    })
    return subscription.get('plan', 'free') if subscription else 'free'
