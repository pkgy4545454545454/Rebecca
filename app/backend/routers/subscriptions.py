"""
Client Premium subscription routes
Handles premium plans (Premium/VIP), checkout, confirmation
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta
import stripe
import uuid
import os
import logging


from .shared import db, get_current_user, STRIPE_API_KEY

router = APIRouter(prefix="/api/client-subscriptions", tags=["Client Premium"])
logger = logging.getLogger(__name__)

# Stripe config
stripe.api_key = STRIPE_API_KEY
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

SUBSCRIPTION_PLANS = {
    "premium": {
        "name": "Premium",
        "price": 29.99,
        "cashback_rate": 0.10,
        "features": [
     "Accès aux images de base",
            "acces a tout services et produits gratuits",
            "0% cashback"
        ]
    },
    "vip": {
        "name": "VIP",
        "price": 69.99,
        "cashback_rate": 0.15,
        "features": [
             "Tout Premium +",
            "15% cashback",
            "Accés a tout les services , videos, films, scénarios en illimité",
            "Accès événements VIP",
            "Réductions partenaires",
            "Badge VIP exclusif"
        ]
    }
}

@router.get("/plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    return {
        "plans": SUBSCRIPTION_PLANS,
        "currency": "CHF"
    }


@router.get("/status")
async def get_subscription_status(current_user: dict = Depends(get_current_user)):
    """Get client's current subscription status"""
    subscription = await db.subscriptions.find_one(
        {"user_id": current_user['id'], "status": "active"},
        {"_id": 0}
    )
    
    current_plan = "free"
    if subscription:
        current_plan = subscription.get('plan', 'free')
    elif current_user.get('is_premium'):
        current_plan = current_user.get('premium_plan', 'premium')
    
    return {
        "current_plan": current_plan,
        "is_premium": current_plan in ['premium', 'vip'],
        "subscription": subscription,
        "available_plans": SUBSCRIPTION_PLANS
    }


@router.post("/checkout")
async def create_subscription_checkout(
    plan_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Create Stripe checkout session for subscription"""
    if plan_id not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=400, detail="Plan invalide")
    
    plan = SUBSCRIPTION_PLANS[plan_id]
    
    try:
        subscription_id = str(uuid.uuid4())
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'chf',
                    'product_data': {
                        'name': f'Esclava {plan["name"]}',
                        'description': f'Abonnement {plan["name"]} - {int(plan["cashback_rate"]*100)}% cashback'
                    },
                    'unit_amount': int(plan["price"] * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
           success_url=f"{FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{FRONTEND_URLl}/payment/cancel",
            metadata={
                'type': plan_id,
                'subscription_id': subscription_id,
                'user_id': current_user['id']
            }
        )
        
        # Store pending subscription
        pending = {
            "id": subscription_id,
            "user_id": current_user['id'],
            "plan": plan_id,
            "price": plan["price"],
            "status": "pending",
            "checkout_session_id": checkout_session.id,
            "created_at": datetime.now(timezone.utc)
        }
        await db.subscriptions.insert_one(pending)
        
        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id,
            "subscription_id": subscription_id
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=500, detail="Erreur de paiement")


@router.post("/confirm/{subscription_id}")
async def confirm_subscription(
    subscription_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Confirm subscription after successful payment"""
    subscription = await db.subscriptions.find_one({
        "id": subscription_id,
        "user_id": current_user['id'],
        "status": "pending"
    })
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Abonnement non trouvé")
    
    # Activate subscription
    await db.subscriptions.update_one(
        {"id": subscription_id},
        {"$set": {
            "status": "active",
            "activated_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(days=30)
        }}
    )
    
    # Update user premium status
    await db.users.update_one(
        {"id": current_user['id']},
        {"$set": {
            "is_premium": True,
            "premium_plan": subscription['plan']
        }}
    )
    
    plan_name = SUBSCRIPTION_PLANS.get(subscription['plan'], {}).get('name', 'Premium')
    
    return {
        "message": f"Abonnement {plan_name} activé !",
        "plan": subscription['plan'],
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    }


@router.post("/cancel")
async def cancel_subscription(current_user: dict = Depends(get_current_user)):
    """Cancel current subscription"""
    result = await db.subscriptions.update_many(
        {"user_id": current_user['id'], "status": "active"},
        {"$set": {
            "status": "cancelled",
            "cancelled_at": datetime.now(timezone.utc)
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Aucun abonnement actif")
    
    # Update user
    await db.users.update_one(
        {"id": current_user['id']},
        {"$set": {"is_premium": False, "premium_plan": "free"}}
    )
    
    return {"message": "Abonnement annulé"}
