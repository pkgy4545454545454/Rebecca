"""
Stripe Webhooks Router - Real-time payment event handling
"""
from fastapi import APIRouter, HTTPException, Request, Header
from datetime import datetime, timezone, timedelta
import logging
import os
import stripe
import json

from .shared import db

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])
logger = logging.getLogger(__name__)

# Stripe config
stripe.api_key = os.environ.get('STRIPE_API_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')

# Import email service
try:
    from services.email_service import send_payment_confirmation, send_payment_failed
    EMAIL_SERVICE_AVAILABLE = True
except ImportError:
    EMAIL_SERVICE_AVAILABLE = False
    logger.warning("Email service not available for webhook notifications")


async def process_checkout_completed(session_data: dict):
    """Process checkout.session.completed event"""
    session_id = session_data.get('id')
    metadata = session_data.get('metadata', {})
    payment_type = metadata.get('type')
    user_id = metadata.get('user_id')
    
    logger.info(f"Processing payment completion: type={payment_type}, session={session_id}")
    
    if not user_id:
        logger.warning(f"No user_id in metadata for session {session_id}")
        return
    
    # Get user info for email
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    
    if payment_type == 'titelli_pro':
        # Activate Pro++ subscription
        subscription_id = metadata.get('subscription_id')
        await db.pro_subscriptions.update_one(
            {"id": subscription_id},
            {"$set": {
                "status": "active",
                "activated_at": datetime.now(timezone.utc),
                "expires_at": datetime.now(timezone.utc) + timedelta(days=30)
            }}
        )
        logger.info(f"✅ Pro++ subscription activated: {subscription_id}")
        
        if EMAIL_SERVICE_AVAILABLE and user:
            try:
                await send_payment_confirmation(
                    user.get('email'),
                    user.get('first_name', 'Client'),
                    "Titelli Pro++",
                    199.0
                )
            except Exception as e:
                logger.error(f"Email error: {e}")
    
    elif payment_type == 'lifestyle_pass':
        # Activate lifestyle pass
        subscription_id = metadata.get('subscription_id')
        pass_type = metadata.get('pass_type')
        
        await db.lifestyle_subscriptions.update_one(
            {"id": subscription_id},
            {"$set": {
                "status": "active",
                "activated_at": datetime.now(timezone.utc),
                "expires_at": datetime.now(timezone.utc) + timedelta(days=30)
            }}
        )
        logger.info(f"✅ Lifestyle pass activated: {pass_type}, subscription: {subscription_id}")
        
        # Determine price based on pass type
        pass_prices = {"healthy": 99, "better_you": 149, "mvp": 299}
        price = pass_prices.get(pass_type, 99)
        
        if EMAIL_SERVICE_AVAILABLE and user:
            try:
                await send_payment_confirmation(
                    user.get('email'),
                    user.get('first_name', 'Client'),
                    f"Lifestyle Pass - {pass_type.title()}",
                    price
                )
            except Exception as e:
                logger.error(f"Email error: {e}")
    
    elif payment_type == 'romantic_subscription':
        # Activate romantic subscription
        subscription_id = metadata.get('subscription_id')
        
        await db.romantic_subscriptions.update_one(
            {"id": subscription_id},
            {"$set": {
                "status": "active",
                "activated_at": datetime.now(timezone.utc),
                "expires_at": datetime.now(timezone.utc) + timedelta(days=30)
            }}
        )
        logger.info(f"✅ Romantic subscription activated: {subscription_id}")
        
        if EMAIL_SERVICE_AVAILABLE and user:
            try:
                await send_payment_confirmation(
                    user.get('email'),
                    user.get('first_name', 'Client'),
                    "Abonnement Romantique RDV Titelli",
                    200.0
                )
            except Exception as e:
                logger.error(f"Email error: {e}")
    
    elif payment_type == 'rdv_invitation':
        # Activate invitation
        invitation_id = metadata.get('invitation_id')
        
        await db.shared_invitations.update_one(
            {"id": invitation_id},
            {"$set": {
                "status": "accepted",
                "paid": True,
                "paid_at": datetime.now(timezone.utc)
            }}
        )
        logger.info(f"✅ RDV invitation accepted: {invitation_id}")
    
    elif payment_type == 'premium' or payment_type == 'vip':
        # Activate premium/VIP subscription
        await db.subscriptions.update_one(
            {"checkout_session_id": session_id},
            {"$set": {
                "status": "active",
                "activated_at": datetime.now(timezone.utc)
            }}
        )
        
        # Update user premium status
        await db.users.update_one(
            {"id": user_id},
            {"$set": {
                "is_premium": True,
                "premium_plan": payment_type
            }}
        )
        logger.info(f"✅ Premium subscription activated: {payment_type} for user {user_id}")


async def process_payment_failed(session_data: dict):
    """Process payment_intent.payment_failed event"""
    metadata = session_data.get('metadata', {})
    user_id = metadata.get('user_id')
    payment_type = metadata.get('type')
    
    logger.warning(f"Payment failed: type={payment_type}, user={user_id}")
    
    if not user_id:
        return
    
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    
    if EMAIL_SERVICE_AVAILABLE and user:
        try:
            await send_payment_failed(
                user.get('email'),
                user.get('first_name', 'Client'),
                payment_type or 'abonnement'
            )
        except Exception as e:
            logger.error(f"Failed to send payment failed email: {e}")


async def process_subscription_cancelled(subscription_data: dict):
    """Process customer.subscription.deleted event"""
    metadata = subscription_data.get('metadata', {})
    user_id = metadata.get('user_id')
    subscription_type = metadata.get('type')
    
    logger.info(f"Subscription cancelled: type={subscription_type}, user={user_id}")
    
    if not user_id:
        return
    
    # Cancel in our database based on type
    if subscription_type == 'titelli_pro':
        await db.pro_subscriptions.update_many(
            {"user_id": user_id, "status": "active"},
            {"$set": {"status": "cancelled", "cancelled_at": datetime.now(timezone.utc)}}
        )
    
    elif subscription_type == 'lifestyle_pass':
        pass_type = metadata.get('pass_type')
        await db.lifestyle_subscriptions.update_many(
            {"user_id": user_id, "pass_type": pass_type, "status": "active"},
            {"$set": {"status": "cancelled", "cancelled_at": datetime.now(timezone.utc)}}
        )
    
    elif subscription_type == 'romantic_subscription':
        await db.romantic_subscriptions.update_many(
            {"user_id": user_id, "status": "active"},
            {"$set": {"status": "cancelled", "cancelled_at": datetime.now(timezone.utc)}}
        )
    
    elif subscription_type in ['premium', 'vip']:
        await db.subscriptions.update_many(
            {"user_id": user_id, "status": "active"},
            {"$set": {"status": "cancelled"}}
        )
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"is_premium": False, "premium_plan": "free"}}
        )


async def process_refund(refund_data: dict):
    """Process charge.refunded event"""
    payment_intent_id = refund_data.get('payment_intent')
    amount_refunded = refund_data.get('amount_refunded', 0) / 100  # Convert from cents
    
    logger.info(f"Refund processed: {amount_refunded} CHF for payment {payment_intent_id}")
    
    # Update any related payment records
    await db.payments.update_one(
        {"stripe_payment_intent_id": payment_intent_id},
        {"$set": {
            "refunded": True,
            "refund_amount": amount_refunded,
            "refunded_at": datetime.now(timezone.utc)
        }}
    )


@router.post("/stripe")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None, alias="Stripe-Signature")):
    """
    Handle Stripe webhook events in real-time.
    
    Supported events:
    - checkout.session.completed: Payment successful
    - payment_intent.payment_failed: Payment failed
    - customer.subscription.deleted: Subscription cancelled
    - charge.refunded: Refund processed
    """
    payload = await request.body()
    
    # Verify webhook signature if secret is configured
    if STRIPE_WEBHOOK_SECRET and stripe_signature:
        try:
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {e}")
            raise HTTPException(status_code=400, detail="Invalid signature")
    else:
        # Parse without verification (development mode)
        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid payload")
    
    event_type = event.get('type')
    data = event.get('data', {}).get('object', {})
    
    logger.info(f"Webhook received: {event_type}")
    
    try:
        if event_type == 'checkout.session.completed':
            await process_checkout_completed(data)
        
        elif event_type == 'payment_intent.payment_failed':
            await process_payment_failed(data)
        
        elif event_type == 'customer.subscription.deleted':
            await process_subscription_cancelled(data)
        
        elif event_type == 'charge.refunded':
            await process_refund(data)
        
        else:
            logger.info(f"Unhandled webhook event: {event_type}")
    
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        # Don't raise - return 200 to prevent Stripe retries
    
    return {"received": True, "event_type": event_type}


@router.get("/health")
async def webhook_health():
    """Check webhook endpoint health"""
    return {
        "status": "healthy",
        "webhook_secret_configured": bool(STRIPE_WEBHOOK_SECRET),
        "email_service_available": EMAIL_SERVICE_AVAILABLE,
        "supported_events": [
            "checkout.session.completed",
            "payment_intent.payment_failed",
            "customer.subscription.deleted",
            "charge.refunded"
        ]
    }
