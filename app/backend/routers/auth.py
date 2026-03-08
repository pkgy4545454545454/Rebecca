"""
Authentication routes for Titelli.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from datetime import datetime, timezone

from .shared import (
    db,  verify_password, create_token, 
    get_current_user, JWT_SECRET, JWT_ALGORITHM
)
import jwt

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============ MODELS ============

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    user_type: str = "client"
    social_accounts: Optional[dict] = None
    niche: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    user_type: str
    profile_image: Optional[str] = None
    is_premium: Optional[bool] = False
    premium_plan: Optional[str] = None


# ============ ROUTES ============

@router.post("/register")
async def register(user_data: UserCreate):
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    user_dict = {
        "id": str(uuid.uuid4()),
        "email": user_data.email,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "phone": user_data.phone,
        "user_type": user_data.user_type,
        "profile_image": None,
        "is_premium": False,
        "premium_plan": None,
        "is_active": True,
        "password": user_data.password,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Add influencer-specific fields
    if user_data.user_type == 'influencer':
        user_dict['social_accounts'] = user_data.social_accounts or {}
        user_dict['niche'] = user_data.niche
        # Create influencer profile
        influencer_profile = {
            "id": str(uuid.uuid4()),
            "user_id": user_dict['id'],
            "social_accounts": user_data.social_accounts or {},
            "niche": user_data.niche,
            "followers_count": 0,
            "engagement_rate": 0.0,
            "collaborations": [],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.influencer_profiles.insert_one(influencer_profile)
    
    await db.users.insert_one(user_dict)
    
    token = create_token(user_dict['id'], user_dict['user_type'])
    user_response = {k: v for k, v in user_dict.items() if k != 'password'}
    return {"token": token, "user": user_response}


@router.post("/login")
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user or not verify_password(credentials.password, user['password']):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    token = create_token(user['id'], user['user_type'])
    user_response = {k: v for k, v in user.items() if k != 'password'}
    return {"token": token, "user": user_response}


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    # Add cashback balance
    current_user['cashback_balance'] = current_user.get('cashback_balance', 0)
    
    # Get subscription info
    subscription = await db.subscriptions.find_one({
        "user_id": current_user['id'],
        "status": "active"
    }, {"_id": 0})
    
    current_user['subscription'] = subscription
    return current_user


@router.put("/profile")
async def update_profile(
    updates: dict,
    current_user: dict = Depends(get_current_user)
):
    allowed_fields = ['first_name', 'last_name', 'phone', 'profile_image', 'bio', 'address', 'preferences']
    update_data = {k: v for k, v in updates.items() if k in allowed_fields}
    
    if update_data:
        await db.users.update_one(
            {"id": current_user['id']},
            {"$set": update_data}
        )
    
    user = await db.users.find_one({"id": current_user['id']}, {"_id": 0, "password": 0})
    return user


@router.put("/password")
async def change_password(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        raise HTTPException(status_code=400, detail="Mot de passe actuel et nouveau requis")
    
    # Get user with password
    user = await db.users.find_one({"id": current_user['id']})
    if not verify_password(current_password, user['password']):
        raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect")
    
    await db.users.update_one(
        {"id": current_user['id']},
        {"$set": {"password": new_password}}
    )
    
    return {"message": "Mot de passe mis à jour"}


@router.post("/validate-token")
async def validate_token(authorization: str = None):
    """Validate a JWT token."""
    if not authorization or not authorization.startswith("Bearer "):
        return {"valid": False, "error": "Token manquant"}
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = await db.users.find_one({"id": payload['user_id']}, {"_id": 0, "password": 0})
        if not user:
            return {"valid": False, "error": "Utilisateur non trouvé"}
        return {"valid": True, "user": user}
    except jwt.ExpiredSignatureError:
        return {"valid": False, "error": "Token expiré"}
    except jwt.InvalidTokenError:
        return {"valid": False, "error": "Token invalide"}
