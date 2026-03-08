"""
Payment routes for Titelli (Stripe integration).
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import uuid
import os
from datetime import datetime, timezone

from .shared import db, get_current_user, TITELLI_FEES, STRIPE_API_KEY
from stripe_helper import StripeCheckout, CheckoutSessionRequest

router = APIRouter(prefix="/payments", tags=["Payments"])


# ============ MODELS ============

class CheckoutRequest(BaseModel):
    package_type: str
    amount: Optional[float] = None


class SubscriptionCheckoutRequest(BaseModel):
    plan_id: str


# ============ ROUTES ============

@router.post("/checkout")
async def create_checkout_session(
    package_type: str,
    amount: Optional[float] = None,
    current_user: dict = Depends(get_current_user)
):
    """Create a Stripe checkout session for various purchases."""
    
    packages = {
        "premium": {"name": "Abonnement Premium", "price": 9.99},
        "vip": {"name": "Abonnement VIP", "price": 19.99},
        "boost_100": {"name": "Boost Marketing 100 CHF", "price": 100},
        "boost_500": {"name": "Boost Marketing 500 CHF", "price": 500},
    }
    
    if package_type in packages:
        final_amount = packages[package_type]['price']
        name = packages[package_type]['name']
    elif amount:
        final_amount = amount
        name = f"Paiement personnalisé {amount} CHF"
    else:
        raise HTTPException(status_code=400, detail="Package ou montant invalide")
    
    # Calculate with transaction fee
    transaction_fee = round(final_amount * TITELLI_FEES['transaction_fee'], 2)
    total_with_fee = round(final_amount + transaction_fee, 2)
    
    frontend_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:3000')
    
    checkout = StripeCheckout(api_key=STRIPE_API_KEY)
    request = CheckoutSessionRequest(
        line_items=[{
            "price_data": {
                "currency": "chf",
                "product_data": {"name": name},
                "unit_amount": int(total_with_fee * 100)
            },
            "quantity": 1
        }],
        mode="payment",
        success_url=f"{frontend_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{frontend_url}/payment/cancel"
    )
    
    response = await checkout.create_session(request)
    
    # Record the payment attempt
    payment_record = {
        "id": str(uuid.uuid4()),
        "user_id": current_user['id'],
        "session_id": response.id,
        "package_type": package_type,
        "amount": final_amount,
        "transaction_fee": transaction_fee,
        "total": total_with_fee,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.payments.insert_one(payment_record)
    
    return {"url": response.url, "session_id": response.id}


@router.get("/status/{session_id}")
async def get_payment_status(session_id: str):
    """Get the status of a payment session."""
    try:
        checkout = StripeCheckout(api_key=STRIPE_API_KEY)
        status = await checkout.get_session_status(session_id)
        return {
            "status": status.status,
            "payment_status": status.payment_status,
            "amount_total": status.amount_total,
            "currency": status.currency
        }
    except Exception as e:
        # Return a safe error response instead of crashing
        return {
            "status": "error",
            "payment_status": "unknown",
            "error": str(e)
        }


@router.post("/webhook")
async def stripe_webhook(request_body: dict):
    """Handle Stripe webhook events."""
    event_type = request_body.get('type')
    data = request_body.get('data', {}).get('object', {})
    
    if event_type == 'checkout.session.completed':
        session_id = data.get('id')
        
        # Update payment record
        await db.payments.update_one(
            {"session_id": session_id},
            {"$set": {"status": "completed", "completed_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        # Process subscription if applicable
        payment = await db.payments.find_one({"session_id": session_id})
        if payment and payment.get('package_type') in ['premium', 'vip']:
            # Activate subscription
            subscription = {
                "id": str(uuid.uuid4()),
                "user_id": payment['user_id'],
                "plan": payment['package_type'],
                "status": "active",
                "start_date": datetime.now(timezone.utc).isoformat(),
                "payment_id": payment['id']
            }
            await db.subscriptions.insert_one(subscription)
            
            # Update user
            await db.users.update_one(
                {"id": payment['user_id']},
                {"$set": {"is_premium": True, "premium_plan": payment['package_type']}}
            )
    
    return {"received": True}
