"""
Orders Router - Gestion des commandes Titelli
Routes pour les commandes, paiements, historique
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import logging
import uuid
import os
import stripe

from .shared import db, get_current_user, TITELLI_FEES, get_user_cashback_rate

router = APIRouter(prefix="/api", tags=["Commandes"])
logger = logging.getLogger(__name__)

# Stripe config
stripe.api_key = os.environ.get('STRIPE_API_KEY')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://titelli.ch')


# ============ PYDANTIC MODELS ============

class OrderItem(BaseModel):
    item_id: str
    name: str
    price: float
    quantity: int = 1


class OrderCreate(BaseModel):
    enterprise_id: str
    items: List[OrderItem]
    delivery_address: Optional[str] = None
    notes: Optional[str] = None


class OrderCheckoutRequest(BaseModel):
    enterprise_id: str
    items: List[dict]
    delivery_address: Optional[str] = None
    delivery_option: Optional[str] = "pickup"
    notes: Optional[str] = None
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    client_phone: Optional[str] = None


# ============ ORDERS ROUTES ============

@router.post("/orders")
async def create_order(data: OrderCreate, current_user: dict = Depends(get_current_user)):
    """Create a new order"""
    # Verify enterprise exists
    enterprise = await db.enterprises.find_one({"id": data.enterprise_id}, {"_id": 0})
    if not enterprise:
        raise HTTPException(status_code=404, detail="Entreprise non trouvée")
    
    # Calculate totals
    subtotal = sum(item.price * item.quantity for item in data.items)
    
    # Apply Titelli fees
    platform_fee = round(subtotal * TITELLI_FEES["platform_fee_percent"], 2)
    delivery_fee = TITELLI_FEES["delivery_fee"] if data.delivery_address else 0
    total = subtotal + platform_fee + delivery_fee
    
    order_id = str(uuid.uuid4())
    order = {
        "id": order_id,
        "client_id": current_user["id"],
        "client_name": current_user.get("name", current_user.get("email", "").split("@")[0]),
        "enterprise_id": data.enterprise_id,
        "enterprise_name": enterprise.get("business_name") or enterprise.get("name", "Entreprise"),
        "items": [item.model_dump() for item in data.items],
        "subtotal": subtotal,
        "platform_fee": platform_fee,
        "delivery_fee": delivery_fee,
        "total": total,
        "delivery_address": data.delivery_address,
        "notes": data.notes,
        "status": "pending",
        "payment_status": "pending",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db.orders.insert_one(order)
    order.pop('_id', None)
    
    return order


@router.get("/orders")
async def get_orders(
    current_user: dict = Depends(get_current_user),
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """Get orders for current user"""
    # Build query based on user type
    if current_user.get("user_type") in ["enterprise", "entreprise"]:
        query = {"enterprise_id": current_user.get("enterprise_id")}
    else:
        query = {"client_id": current_user["id"]}
    
    if status:
        query["status"] = status
    
    orders = await db.orders.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.orders.count_documents(query)
    
    return {"orders": orders, "total": total}


@router.get("/orders/{order_id}")
async def get_order(order_id: str, current_user: dict = Depends(get_current_user)):
    """Get order by ID"""
    order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    # Verify access
    if order["client_id"] != current_user["id"] and order.get("enterprise_id") != current_user.get("enterprise_id"):
        if current_user.get("user_type") != "admin":
            raise HTTPException(status_code=403, detail="Non autorisé")
    
    return order


@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    status: str,
    current_user: dict = Depends(get_current_user)
):
    """Update order status"""
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    # Only enterprise or admin can update status
    if order.get("enterprise_id") != current_user.get("enterprise_id"):
        if current_user.get("user_type") != "admin":
            raise HTTPException(status_code=403, detail="Non autorisé")
    
    valid_statuses = ["pending", "confirmed", "preparing", "ready", "delivered", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Statut invalide. Valides: {valid_statuses}")
    
    await db.orders.update_one(
        {"id": order_id},
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc)}}
    )
    
    return {"message": f"Statut mis à jour: {status}"}


# ============ ORDER CHECKOUT WITH STRIPE ============

@router.post("/orders/checkout")
async def create_order_checkout(
    data: OrderCheckoutRequest,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Create Stripe checkout for order"""
    # Get enterprise
    enterprise = await db.enterprises.find_one({"id": data.enterprise_id}, {"_id": 0})
    if not enterprise:
        raise HTTPException(status_code=404, detail="Entreprise non trouvée")
    
    # Calculate totals
    subtotal = sum(item.get("price", 0) * item.get("quantity", 1) for item in data.items)
    platform_fee = round(subtotal * TITELLI_FEES["platform_fee_percent"], 2)
    delivery_fee = TITELLI_FEES["delivery_fee"] if data.delivery_option == "delivery" else 0
    total = subtotal + platform_fee + delivery_fee
    
    # Create order
    order_id = str(uuid.uuid4())
    order = {
        "id": order_id,
        "client_id": current_user["id"],
        "client_name": data.client_name or current_user.get("name", "Client"),
        "client_email": data.client_email or current_user.get("email"),
        "enterprise_id": data.enterprise_id,
        "enterprise_name": enterprise.get("business_name") or enterprise.get("name", "Entreprise"),
        "items": data.items,
        "subtotal": subtotal,
        "platform_fee": platform_fee,
        "delivery_fee": delivery_fee,
        "total": total,
        "delivery_address": data.delivery_address,
        "delivery_option": data.delivery_option,
        "notes": data.notes,
        "status": "pending",
        "payment_status": "pending",
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.orders.insert_one(order)
    
    # Create Stripe checkout
    try:
        line_items = [{
            "price_data": {
                "currency": "chf",
                "unit_amount": int(total * 100),  # Stripe uses cents
                "product_data": {
                    "name": f"Commande - {enterprise.get('business_name') or enterprise.get('name', 'Entreprise')}",
                    "description": f"{len(data.items)} article(s)"
                }
            },
            "quantity": 1
        }]
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=f"{FRONTEND_URL}/orders?success=true&order_id={order_id}",
            cancel_url=f"{FRONTEND_URL}/orders?cancelled=true",
            metadata={
                "order_id": order_id,
                "type": "order"
            }
        )
        
        # Update order with stripe session
        await db.orders.update_one(
            {"id": order_id},
            {"$set": {"stripe_session_id": checkout_session.id}}
        )
        
        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id,
            "order_id": order_id
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=500, detail="Erreur de paiement")


@router.get("/orders/{order_id}/payment-status")
async def get_order_payment_status(order_id: str, current_user: dict = Depends(get_current_user)):
    """Get payment status for an order"""
    order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    return {
        "order_id": order_id,
        "payment_status": order.get("payment_status", "unknown"),
        "status": order.get("status", "pending")
    }
