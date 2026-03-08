"""
Client routes module
Handles wishlist, providers, agenda, finances, donations
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/client", tags=["Client"])

db = None


def set_database(database):
    global db
    db = database


# Import auth dependency
async def get_current_user(authorization=None):
    from routers.auth import get_current_user as auth_get_current_user
    return await auth_get_current_user(authorization)


# ============ WISHLIST ============

class WishlistItem(BaseModel):
    item_id: str
    item_type: str
    item_name: str
    item_price: float
    item_image: Optional[str] = ""
    enterprise_id: str
    enterprise_name: str


@router.get("/wishlist")
async def get_wishlist(current_user: dict = Depends(get_current_user)):
    """Get user's wishlist"""
    items = await db.wishlist.find(
        {"user_id": current_user['id']},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return {"items": items}


@router.post("/wishlist")
async def add_to_wishlist(item: WishlistItem, current_user: dict = Depends(get_current_user)):
    """Add item to wishlist"""
    existing = await db.wishlist.find_one({
        "user_id": current_user['id'],
        "item_id": item.item_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="Déjà dans la liste de souhaits")
    
    wishlist_item = {
        "id": str(uuid.uuid4()),
        "user_id": current_user['id'],
        **item.model_dump(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.wishlist.insert_one(wishlist_item)
    wishlist_item.pop('_id', None)
    return wishlist_item


@router.get("/wishlist/check/{item_id}")
async def check_wishlist(item_id: str, current_user: dict = Depends(get_current_user)):
    """Check if item is in wishlist"""
    item = await db.wishlist.find_one({
        "user_id": current_user['id'],
        "item_id": item_id
    })
    return {"in_wishlist": item is not None}


@router.delete("/wishlist/{item_id}")
async def remove_from_wishlist(item_id: str, current_user: dict = Depends(get_current_user)):
    """Remove item from wishlist"""
    result = await db.wishlist.delete_one({
        "user_id": current_user['id'],
        "item_id": item_id
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item non trouvé")
    return {"success": True}


# ============ PROVIDERS ============

class ProviderAdd(BaseModel):
    enterprise_id: str
    enterprise_name: str
    category: Optional[str] = None
    city: Optional[str] = None
    rating: Optional[float] = 0
    logo: Optional[str] = None


@router.get("/providers")
async def get_providers(current_user: dict = Depends(get_current_user)):
    """Get user's personal providers list"""
    providers = await db.client_providers.find(
        {"user_id": current_user['id']},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return {"providers": providers}


@router.post("/providers")
async def add_provider(provider: ProviderAdd, current_user: dict = Depends(get_current_user)):
    """Add enterprise to personal providers"""
    existing = await db.client_providers.find_one({
        "user_id": current_user['id'],
        "enterprise_id": provider.enterprise_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="Prestataire déjà ajouté")
    
    provider_doc = {
        "id": str(uuid.uuid4()),
        "user_id": current_user['id'],
        **provider.model_dump(),
        "enterprise_logo": provider.logo,
        "notes": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.client_providers.insert_one(provider_doc)
    provider_doc.pop('_id', None)
    return provider_doc


@router.delete("/providers/{provider_id}")
async def remove_provider(provider_id: str, current_user: dict = Depends(get_current_user)):
    """Remove provider from personal list"""
    result = await db.client_providers.delete_one({
        "user_id": current_user['id'],
        "id": provider_id
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Prestataire non trouvé")
    return {"success": True}


# ============ AGENDA ============

class AgendaEvent(BaseModel):
    title: str
    event_type: str = "appointment"  # appointment, meeting, reminder
    date: str
    time: str
    location: Optional[str] = None
    description: Optional[str] = None


@router.get("/agenda")
async def get_agenda(current_user: dict = Depends(get_current_user)):
    """Get user's agenda events"""
    events = await db.agenda.find(
        {"user_id": current_user['id']},
        {"_id": 0}
    ).sort("date", 1).to_list(100)
    return {"events": events}


@router.post("/agenda")
async def create_agenda_event(event: AgendaEvent, current_user: dict = Depends(get_current_user)):
    """Create agenda event"""
    event_doc = {
        "id": str(uuid.uuid4()),
        "user_id": current_user['id'],
        **event.model_dump(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.agenda.insert_one(event_doc)
    event_doc.pop('_id', None)
    return event_doc


@router.delete("/agenda/{event_id}")
async def delete_agenda_event(event_id: str, current_user: dict = Depends(get_current_user)):
    """Delete agenda event"""
    result = await db.agenda.delete_one({
        "user_id": current_user['id'],
        "id": event_id
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    return {"success": True}


# ============ FINANCES ============

@router.get("/finances")
async def get_finances(current_user: dict = Depends(get_current_user)):
    """Get user's financial summary"""
    # Get orders
    orders = await db.orders.find(
        {"user_id": current_user['id']},
        {"_id": 0, "total": 1, "status": 1, "created_at": 1}
    ).to_list(1000)
    
    completed_orders = [o for o in orders if o.get('status') in ['completed', 'delivered']]
    total_spent = sum(o.get('total', 0) for o in completed_orders)
    
    # Get training purchases
    enrollments = await db.training_enrollments.find(
        {"user_id": current_user['id'], "status": "active"},
        {"_id": 0, "price_paid": 1}
    ).to_list(100)
    training_spent = sum(e.get('price_paid', 0) for e in enrollments)
    
    # Get cashback
    user = await db.users.find_one({"id": current_user['id']})
    cashback_rate = 0.01  # Default 1%
    if user.get('premium_plan') == 'premium':
        cashback_rate = 0.10
    elif user.get('premium_plan') == 'vip':
        cashback_rate = 0.15
    
    cashback_available = await db.cashback.find_one(
        {"user_id": current_user['id']},
        {"_id": 0, "balance": 1}
    )
    
    cashback_earned = (total_spent + training_spent) * cashback_rate
    
    return {
        "total_spent": round(total_spent + training_spent, 2),
        "orders_total": round(total_spent, 2),
        "trainings_total": round(training_spent, 2),
        "orders_count": len(completed_orders),
        "trainings_count": len(enrollments),
        "cashback_rate": int(cashback_rate * 100),
        "cashback_earned": round(cashback_earned, 2),
        "cashback_available": round(cashback_available.get('balance', 0), 2) if cashback_available else 0,
        "savings_percentage": round((cashback_earned / (total_spent + training_spent) * 100), 1) if (total_spent + training_spent) > 0 else 0
    }


# ============ DONATIONS ============

class DonationCreate(BaseModel):
    amount: float
    recipient: str
    message: Optional[str] = None
    anonymous: bool = False


@router.get("/donations")
async def get_donations(current_user: dict = Depends(get_current_user)):
    """Get user's donations"""
    donations = await db.donations.find(
        {"user_id": current_user['id']},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    total = sum(d.get('amount', 0) for d in donations)
    return {"donations": donations, "total": total, "count": len(donations)}


@router.post("/donations")
async def create_donation(donation: DonationCreate, current_user: dict = Depends(get_current_user)):
    """Create a donation"""
    donation_doc = {
        "id": str(uuid.uuid4()),
        "user_id": current_user['id'],
        "donor_name": f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}" if not donation.anonymous else "Anonyme",
        **donation.model_dump(),
        "status": "completed",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.donations.insert_one(donation_doc)
    donation_doc.pop('_id', None)
    return donation_doc
