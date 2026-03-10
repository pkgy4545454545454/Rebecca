"""
Client Premium subscription routes
Handles premium plans, checkout, confirmation, and cancellation
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta

from stripe_helper import StripeCheckout, CheckoutSessionRequest
import stripe
import uuid
import os
import logging

router = APIRouter(prefix="/client/premium", tags=["Client Premium"])

logger = logging.getLogger(__name__)

# Database and config - injected from main
db = None
STRIPE_API_KEY = None

PREMIUM_PLANS = {
    "free": {
        "name": "Gratuit",
        "price": 0.0,
        "cashback_rate": 0.01,  # 1%
        "features": [
            "Accès aux images de base",
            "acces a tout services et produits gratuits",
            "0% cashback"
        ]
    },
    "premium": {
        "name": "Premium",
        "price": 29.99,
        "cashback_rate": 0.10,  # 10%
        "features": [
            "Accès illimité aux vidéos et images exclusives",
            "Messagerie illimitée",
            "10% cashback",
            "Accés a ma gallerie vidéos privées limitées / films SOFT en illimité",
            "Support prioritaire",
            "Badge Premium"
        ]
    },
    "vip": {
        "name": "VIP",
        "price": 69.99,
        "cashback_rate": 0.15,  # 15%
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

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
def set_config(database, stripe_key):
    """Set database and Stripe configuration"""
    global db, STRIPE_API_KEY
    db = database
    STRIPE_API_KEY = stripe_key


# Import get_current_user from auth module
async def get_current_user(authorization=None):
    from routers.auth import get_current_user as auth_get_current_user
    return await auth_get_current_user(authorization)


@router.get("")
async def get_premium_status(current_user: dict = Depends(get_current_user)):
    """Get client's premium subscription status and benefits"""
    user = await db.users.find_one({"id": current_user['id']}, {"_id": 0})
    
    subscription = await db.subscriptions.find_one(
        {"user_id": current_user['id'], "status": "active"},
        {"_id": 0}
    )
    
    if subscription:
        current_plan = subscription.get('plan', 'free')
    else:
        current_plan = user.get('premium_plan', 'free') if user else 'free'
        if user and user.get('is_premium') and current_plan == 'free':
            current_plan = 'premium'
    
    cashback_rate = PREMIUM_PLANS.get(current_plan, PREMIUM_PLANS['free'])['cashback_rate']
    
    return {
        "current_plan": current_plan,
        "is_premium": current_plan in ['premium', 'vip'],
        "subscription": subscription,
        "benefits": PREMIUM_PLANS,
        "user_since": user.get('created_at') if user else None,
        "cashback_rate": int(cashback_rate * 100),
        "has_active_subscription": subscription is not None
    }


@router.post("/checkout")
async def create_premium_checkout(plan: str, current_user: dict = Depends(get_current_user)):
    """Create Stripe checkout session for premium subscription"""
    if plan not in ['premium', 'vip']:
        raise HTTPException(status_code=400, detail="Plan invalide. Choisissez 'premium' ou 'vip'")
    
    plan_info = PREMIUM_PLANS[plan]
    
    try:
        checkout = StripeCheckout(api_key=STRIPE_API_KEY)
        
        session_request = CheckoutSessionRequest(
            amount=plan_info['price'],
            currency="chf",
            quantity=1,
            success_url=f"{os.environ.get('FRONTEND_URL', 'https://esclavaescort.ch')}/dashboard/client?tab=premium&success=true&plan={plan}",
            cancel_url=f"{os.environ.get('FRONTEND_URL', 'https://esclavaescort.ch')}/dashboard/client?tab=premium&cancelled=true",
            metadata={
                "plan": plan,
                "user_id": current_user['id'],
                "product_name": f"Titelli {plan_info['name']} - Abonnement mensuel"
            }
        )
        
        session_response = await checkout.create_checkout_session(session_request)
        
        pending_sub = {
            "id": str(uuid.uuid4()),
            "user_id": current_user['id'],
            "plan": plan,
            "stripe_session_id": session_response.session_id,
            "status": "pending",
            "price": plan_info['price'],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.pending_subscriptions.insert_one(pending_sub)
        
        return {
            "checkout_url": session_response.url,
            "session_id": session_response.session_id
        }
    except Exception as e:
        logger.error(f"Stripe checkout error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur paiement: {str(e)}")


@router.post("/confirm")
async def confirm_premium_subscription(session_id: str, current_user: dict = Depends(get_current_user)):
    """Confirm premium subscription after successful Stripe payment"""
    pending = await db.pending_subscriptions.find_one({
        "user_id": current_user['id'],
        "stripe_session_id": session_id,
        "status": "pending"
    })
    
    if not pending:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    try:
        checkout = StripeCheckout(api_key=STRIPE_API_KEY)
        status = await checkout.get_checkout_status(session_id)
        
        if status.status != "complete":
            raise HTTPException(status_code=400, detail="Paiement non complété")
        
        plan = pending['plan']
        
        # Create subscription record
        sub = {
            "id": str(uuid.uuid4()),
            "user_id": current_user['id'],
            "plan": plan,
            "status": "active",
            "price": pending['price'],
            "stripe_session_id": session_id,
            "stripe_subscription_id": status.payment_intent if hasattr(status, 'payment_intent') else None,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "next_billing": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        }
        await db.subscriptions.insert_one(sub)
        
        # Update user
        await db.users.update_one(
            {"id": current_user['id']},
            {"$set": {
                "is_premium": True,
                "premium_plan": plan,
                "premium_since": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # Update pending status
        await db.pending_subscriptions.update_one(
            {"id": pending['id']},
            {"$set": {"status": "confirmed"}}
        )
        
        return {
            "success": True,
            "plan": plan,
            "message": f"Bienvenue  {PREMIUM_PLANS[plan]['name']} !"
        }
    except Exception as e:
        logger.error(f"Subscription confirmation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur confirmation: {str(e)}")


@router.post("/cancel")
async def cancel_premium_subscription(current_user: dict = Depends(get_current_user)):
    """Cancel premium subscription - removes all benefits immediately"""
    user = await db.users.find_one({"id": current_user['id']})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    is_premium = user.get('is_premium', False)
    current_plan = user.get('premium_plan', 'free')
    
    subscription = await db.subscriptions.find_one({
        "user_id": current_user['id'],
        "status": "active"
    })
    
    if not subscription and not is_premium and current_plan == 'free':
        raise HTTPException(status_code=404, detail="Aucun abonnement actif à annuler")
    
    plan_name = current_plan if current_plan != 'free' else (subscription.get('plan', 'premium') if subscription else 'premium')
    
    # Cancel on Stripe if applicable
    if subscription:
        stripe_sub_id = subscription.get('stripe_subscription_id')
        if stripe_sub_id:
            try:
                stripe.api_key = STRIPE_API_KEY
                stripe.Subscription.cancel(stripe_sub_id)
                logger.info(f"Stripe subscription {stripe_sub_id} cancelled")
            except Exception as e:
                logger.warning(f"Could not cancel Stripe subscription: {str(e)}")
        
        await db.subscriptions.update_one(
            {"id": subscription['id']},
            {"$set": {
                "status": "cancelled",
                "cancelled_at": datetime.now(timezone.utc).isoformat()
            }}
        )
    
    # Cancel all active subscriptions
    await db.subscriptions.update_many(
        {"user_id": current_user['id'], "status": "active"},
        {"$set": {
            "status": "cancelled",
            "cancelled_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Remove all premium benefits
    await db.users.update_one(
        {"id": current_user['id']},
        {"$set": {
            "is_premium": False, 
            "premium_plan": "free",
            "premium_since": None,
            "stripe_customer_id": None,
            "stripe_subscription_id": None
        }}
    )
    
    # Delete pending subscriptions
    await db.pending_subscriptions.delete_many({"user_id": current_user['id']})
    
    # Create notification
    notification = {
        "id": str(uuid.uuid4()),
        "user_id": current_user['id'],
        "title": "Abonnement annulé",
        "message": f"Votre abonnement {plan_name.capitalize()} a été annulé. Vous êtes maintenant sur le plan gratuit avec 1% de cashback.",
        "notification_type": "subscription",
        "is_read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.notifications.insert_one(notification)
    
    return {
        "success": True,
        "message": "Abonnement annulé avec succès. Tous les avantages premium ont été retirés.",
        "new_plan": "free",
        "new_cashback_rate": 1
    }


@router.get("/history")
async def get_subscription_history(current_user: dict = Depends(get_current_user)):
    """Get user's subscription history"""
    subscriptions = await db.subscriptions.find(
        {"user_id": current_user['id']},
        {"_id": 0}
    ).sort("started_at", -1).to_list(50)
    
    return {"subscriptions": subscriptions}

