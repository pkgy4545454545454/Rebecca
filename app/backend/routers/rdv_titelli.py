"""
Rdv chez Titelli - Social Booking & Dating Feature
- Shared offers for 2 people (activities, restaurants, etc.)
- Friendly vs Romantic mode
- Real-time chat between participants
- Pricing: Free for friendly, 200 CHF/month for romantic, 2 CHF to accept invitation
"""
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import asyncio
import logging
import jwt
import uuid
import os
import stripe

from .shared import db, get_current_user, JWT_SECRET, JWT_ALGORITHM
from .websocket import ws_manager

# Import email service
try:
    from services.email_service import send_payment_confirmation
    EMAIL_SERVICE_AVAILABLE = True
except ImportError:
    EMAIL_SERVICE_AVAILABLE = False

router = APIRouter(prefix="/api/rdv", tags=["Rdv chez Titelli"])
logger = logging.getLogger(__name__)

# Stripe configuration
stripe.api_key = os.environ.get('STRIPE_API_KEY')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://titelli.ch')

# Gamification helper
async def award_gamification_points(user_id: str, action: str):
    """Award gamification points for RDV actions"""
    try:
        from .gamification import award_points
        await award_points(user_id, action)
    except Exception as e:
        logger.warning(f"Could not award points: {e}")


# ============ PYDANTIC MODELS ============

class SharedOfferCreate(BaseModel):
    """Create a shared offer for 2 people"""
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    offer_type: str = Field(..., pattern="^(friendly|romantic)$")  # friendly or romantic
    category: str = Field(..., min_length=2)  # restaurant, activity, wellness, etc.
    service_id: Optional[str] = None  # Link to existing service/product
    enterprise_id: Optional[str] = None
    location: Optional[str] = None
    proposed_date: Optional[datetime] = None
    price_per_person: float = 0.0
    max_participants: int = 2
    additional_info: Optional[str] = None


class SharedOfferResponse(BaseModel):
    id: str
    creator_id: str
    creator_name: str
    creator_image: Optional[str]
    title: str
    description: Optional[str]
    offer_type: str
    category: str
    service_id: Optional[str]
    enterprise_id: Optional[str]
    enterprise_name: Optional[str]
    location: Optional[str]
    proposed_date: Optional[datetime]
    price_per_person: float
    status: str  # open, pending, confirmed, completed, cancelled
    participants: List[dict]
    created_at: datetime


class InvitationCreate(BaseModel):
    """Send invitation to join an offer"""
    offer_id: str
    invitee_id: str
    message: Optional[str] = None


class InvitationResponse(BaseModel):
    id: str
    offer_id: str
    inviter_id: str
    inviter_name: str
    invitee_id: str
    invitee_name: str
    message: Optional[str]
    status: str  # pending, accepted, declined
    payment_status: str  # pending, paid, not_required
    created_at: datetime


class UserAvailabilityCreate(BaseModel):
    """Register as available for activities"""
    availability_type: str = Field(..., pattern="^(friendly|romantic|both)$")
    interests: List[str] = []
    bio: Optional[str] = None
    preferred_categories: List[str] = []
    available_days: List[str] = []  # monday, tuesday, etc.
    age_range_min: Optional[int] = None
    age_range_max: Optional[int] = None


class ChatMessageCreate(BaseModel):
    """Send a chat message"""
    content: str = Field(..., min_length=1, max_length=2000)


class RomanticSubscriptionCreate(BaseModel):
    """Subscribe to romantic mode"""
    payment_method_id: Optional[str] = None


# ============ PRICING CONSTANTS ============
ROMANTIC_SUBSCRIPTION_PRICE = 200.00  # CHF per month
INVITATION_ACCEPTANCE_FEE = 2.00  # CHF to accept an invitation


# ============ CHAT CONNECTION MANAGER ============

class ChatConnectionManager:
    """Manages WebSocket connections for chat rooms"""
    def __init__(self):
        self.rooms: Dict[str, Dict[str, WebSocket]] = {}  # room_id -> {user_id: websocket}
        self.lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, room_id: str, user_id: str):
        await websocket.accept()
        async with self.lock:
            if room_id not in self.rooms:
                self.rooms[room_id] = {}
            self.rooms[room_id][user_id] = websocket
        logger.info(f"User {user_id} connected to chat room {room_id}")
    
    async def disconnect(self, room_id: str, user_id: str):
        async with self.lock:
            if room_id in self.rooms and user_id in self.rooms[room_id]:
                del self.rooms[room_id][user_id]
                if not self.rooms[room_id]:
                    del self.rooms[room_id]
        logger.info(f"User {user_id} disconnected from chat room {room_id}")
    
    async def send_to_room(self, room_id: str, message: dict, exclude_user: str = None):
        if room_id in self.rooms:
            dead_connections = []
            for user_id, ws in self.rooms[room_id].items():
                if user_id != exclude_user:
                    try:
                        await ws.send_json(message)
                    except Exception as e:
                        logger.error(f"Error sending to {user_id} in room {room_id}: {e}")
                        dead_connections.append(user_id)
            
            for user_id in dead_connections:
                await self.disconnect(room_id, user_id)
    
    async def send_to_user(self, room_id: str, user_id: str, message: dict):
        if room_id in self.rooms and user_id in self.rooms[room_id]:
            try:
                await self.rooms[room_id][user_id].send_json(message)
            except Exception:
                pass


chat_manager = ChatConnectionManager()


# ============ HELPER FUNCTIONS ============

async def get_user_basic_info(user_id: str) -> dict:
    """Get basic user info for display"""
    user = await db.users.find_one(
        {"id": user_id},
        {"_id": 0, "id": 1, "first_name": 1, "last_name": 1, "profile_image": 1, "email": 1}
    )
    if user:
        return {
            "id": user["id"],
            "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or "Utilisateur",
            "image": user.get("profile_image")
        }
    return {"id": user_id, "name": "Utilisateur", "image": None}


async def check_romantic_subscription(user_id: str) -> bool:
    """Check if user has active romantic subscription"""
    subscription = await db.romantic_subscriptions.find_one({
        "user_id": user_id,
        "status": "active",
        "expires_at": {"$gt": datetime.now(timezone.utc)}
    })
    return subscription is not None


async def create_chat_room(offer_id: str, participant_ids: List[str]) -> str:
    """Create a chat room for an offer"""
    room_id = str(uuid.uuid4())
    chat_room = {
        "id": room_id,
        "offer_id": offer_id,
        "participants": participant_ids,
        "created_at": datetime.now(timezone.utc),
        "last_message_at": datetime.now(timezone.utc)
    }
    await db.chat_rooms.insert_one(chat_room)
    return room_id


# ============ SHARED OFFERS ENDPOINTS ============

@router.post("/offers", response_model=dict)
async def create_shared_offer(
    offer_data: SharedOfferCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new shared offer for 2 people"""
    user_id = current_user["id"]
    
    # Check romantic subscription if romantic offer
    if offer_data.offer_type == "romantic":
        has_subscription = await check_romantic_subscription(user_id)
        if not has_subscription:
            raise HTTPException(
                status_code=402,
                detail="Abonnement romantique requis (200 CHF/mois) pour créer des offres romantiques"
            )
    
    # Get creator info
    creator_info = await get_user_basic_info(user_id)
    
    # Get enterprise info if provided
    enterprise_name = None
    if offer_data.enterprise_id:
        enterprise = await db.enterprises.find_one(
            {"id": offer_data.enterprise_id},
            {"_id": 0, "business_name": 1, "name": 1}
        )
        if enterprise:
            enterprise_name = enterprise.get("business_name") or enterprise.get("name")
    
    offer_id = str(uuid.uuid4())
    offer = {
        "id": offer_id,
        "creator_id": user_id,
        "creator_name": creator_info["name"],
        "creator_image": creator_info["image"],
        "title": offer_data.title,
        "description": offer_data.description,
        "offer_type": offer_data.offer_type,
        "category": offer_data.category,
        "service_id": offer_data.service_id,
        "enterprise_id": offer_data.enterprise_id,
        "enterprise_name": enterprise_name,
        "location": offer_data.location,
        "proposed_date": offer_data.proposed_date,
        "price_per_person": offer_data.price_per_person,
        "max_participants": offer_data.max_participants,
        "additional_info": offer_data.additional_info,
        "status": "open",
        "participants": [{"user_id": user_id, "name": creator_info["name"], "image": creator_info["image"], "role": "creator"}],
        "chat_room_id": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db.shared_offers.insert_one(offer)
    
    # Remove _id before returning (MongoDB adds it)
    offer.pop('_id', None)
    
    # Award gamification points
    await award_gamification_points(user_id, "rdv_offer_created")
    
    return {"message": "Offre créée avec succès", "offer_id": offer_id, "offer": offer}


@router.get("/offers", response_model=dict)
async def get_shared_offers(
    offer_type: Optional[str] = Query(None, pattern="^(friendly|romantic)$"),
    category: Optional[str] = None,
    status: str = Query("open"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get available shared offers"""
    user_id = current_user["id"]
    
    # Build query
    query = {"status": status}
    
    if offer_type:
        # Check subscription for romantic offers
        if offer_type == "romantic":
            has_subscription = await check_romantic_subscription(user_id)
            if not has_subscription:
                raise HTTPException(
                    status_code=402,
                    detail="Abonnement romantique requis pour voir les offres romantiques"
                )
        query["offer_type"] = offer_type
    
    if category:
        query["category"] = category
    
    # Exclude user's own offers
    query["creator_id"] = {"$ne": user_id}
    
    offers = await db.shared_offers.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.shared_offers.count_documents(query)
    
    return {
        "offers": offers,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/offers/my", response_model=dict)
async def get_my_offers(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get current user's created offers"""
    query = {"creator_id": current_user["id"]}
    if status:
        query["status"] = status
    
    offers = await db.shared_offers.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"offers": offers, "count": len(offers)}


@router.get("/offers/{offer_id}", response_model=dict)
async def get_offer_detail(
    offer_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get offer details"""
    offer = await db.shared_offers.find_one({"id": offer_id}, {"_id": 0})
    if not offer:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    
    # Check romantic subscription
    if offer["offer_type"] == "romantic":
        has_subscription = await check_romantic_subscription(current_user["id"])
        if not has_subscription and offer["creator_id"] != current_user["id"]:
            raise HTTPException(status_code=402, detail="Abonnement romantique requis")
    
    return {"offer": offer}


@router.delete("/offers/{offer_id}")
async def cancel_offer(
    offer_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Cancel an offer"""
    offer = await db.shared_offers.find_one({"id": offer_id})
    if not offer:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    
    if offer["creator_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Vous ne pouvez annuler que vos propres offres")
    
    await db.shared_offers.update_one(
        {"id": offer_id},
        {"$set": {"status": "cancelled", "updated_at": datetime.now(timezone.utc)}}
    )
    
    # Notify participants
    for p in offer.get("participants", []):
        if p["user_id"] != current_user["id"]:
            await ws_manager.send_personal_message({
                "type": "offer_cancelled",
                "offer_id": offer_id,
                "message": f"L'offre '{offer['title']}' a été annulée"
            }, p["user_id"])
    
    return {"message": "Offre annulée"}


# ============ INVITATIONS ENDPOINTS ============

@router.post("/invitations", response_model=dict)
async def send_invitation(
    invitation_data: InvitationCreate,
    current_user: dict = Depends(get_current_user)
):
    """Send an invitation to join an offer"""
    user_id = current_user["id"]
    
    # Get offer
    offer = await db.shared_offers.find_one({"id": invitation_data.offer_id})
    if not offer:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    
    if offer["status"] != "open":
        raise HTTPException(status_code=400, detail="Cette offre n'est plus disponible")
    
    if offer["creator_id"] != user_id:
        raise HTTPException(status_code=403, detail="Seul le créateur peut envoyer des invitations")
    
    # Check if already invited
    existing = await db.invitations.find_one({
        "offer_id": invitation_data.offer_id,
        "invitee_id": invitation_data.invitee_id,
        "status": {"$in": ["pending", "accepted"]}
    })
    if existing:
        raise HTTPException(status_code=400, detail="Cette personne a déjà été invitée")
    
    # Get user info
    inviter_info = await get_user_basic_info(user_id)
    invitee_info = await get_user_basic_info(invitation_data.invitee_id)
    
    invitation_id = str(uuid.uuid4())
    invitation = {
        "id": invitation_id,
        "offer_id": invitation_data.offer_id,
        "offer_title": offer["title"],
        "offer_type": offer["offer_type"],
        "inviter_id": user_id,
        "inviter_name": inviter_info["name"],
        "inviter_image": inviter_info["image"],
        "invitee_id": invitation_data.invitee_id,
        "invitee_name": invitee_info["name"],
        "message": invitation_data.message,
        "status": "pending",
        "payment_status": "pending" if offer["offer_type"] == "romantic" else "not_required",
        "acceptance_fee": INVITATION_ACCEPTANCE_FEE,
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.invitations.insert_one(invitation)
    
    # Send real-time notification
    await ws_manager.send_personal_message({
        "type": "new_invitation",
        "invitation": {
            "id": invitation_id,
            "offer_title": offer["title"],
            "inviter_name": inviter_info["name"],
            "offer_type": offer["offer_type"],
            "message": invitation_data.message
        }
    }, invitation_data.invitee_id)
    
    # Award gamification points
    await award_gamification_points(user_id, "rdv_invitation_sent")
    
    return {"message": "Invitation envoyée", "invitation_id": invitation_id}


@router.get("/invitations/received", response_model=dict)
async def get_received_invitations(
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Get invitations received by current user"""
    query = {"invitee_id": current_user["id"]}
    if status:
        query["status"] = status
    
    invitations = await db.invitations.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"invitations": invitations, "count": len(invitations)}


@router.get("/invitations/sent", response_model=dict)
async def get_sent_invitations(
    current_user: dict = Depends(get_current_user)
):
    """Get invitations sent by current user"""
    invitations = await db.invitations.find(
        {"inviter_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return {"invitations": invitations, "count": len(invitations)}


@router.post("/invitations/{invitation_id}/accept", response_model=dict)
async def accept_invitation(
    invitation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Accept an invitation - Creates Stripe checkout for 2 CHF fee"""
    invitation = await db.invitations.find_one({"id": invitation_id})
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation non trouvée")
    
    if invitation["invitee_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Cette invitation ne vous est pas destinée")
    
    if invitation["status"] != "pending":
        raise HTTPException(status_code=400, detail="Cette invitation n'est plus en attente")
    
    # Create Stripe checkout session for 2 CHF
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'chf',
                    'product_data': {
                        'name': f'Acceptation invitation - {invitation.get("offer_title", "Rdv Titelli")}',
                        'description': 'Frais d\'acceptation d\'invitation Rdv chez Titelli'
                    },
                    'unit_amount': int(INVITATION_ACCEPTANCE_FEE * 100),  # 200 centimes = 2 CHF
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'{FRONTEND_URL}/rdv?invitation_accepted={invitation_id}',
            cancel_url=f'{FRONTEND_URL}/rdv?invitation_cancelled={invitation_id}',
            metadata={
                'type': 'rdv_invitation_acceptance',
                'invitation_id': invitation_id,
                'user_id': current_user["id"]
            }
        )
        
        # Store checkout session ID
        await db.invitations.update_one(
            {"id": invitation_id},
            {"$set": {"checkout_session_id": checkout_session.id}}
        )
        
        return {
            "requires_payment": True,
            "checkout_url": checkout_session.url,
            "amount": INVITATION_ACCEPTANCE_FEE,
            "currency": "CHF"
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=500, detail="Erreur de paiement")


@router.post("/invitations/{invitation_id}/confirm-payment")
async def confirm_invitation_payment(
    invitation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Confirm invitation payment and complete acceptance"""
    invitation = await db.invitations.find_one({"id": invitation_id})
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation non trouvée")
    
    if invitation["invitee_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Cette invitation ne vous est pas destinée")
    
    # Verify Stripe payment
    checkout_session_id = invitation.get("checkout_session_id")
    if checkout_session_id:
        try:
            session = stripe.checkout.Session.retrieve(checkout_session_id)
            if session.payment_status != "paid":
                raise HTTPException(status_code=402, detail="Paiement non confirmé")
        except stripe.error.StripeError:
            raise HTTPException(status_code=402, detail="Impossible de vérifier le paiement")
    
    # Update invitation
    await db.invitations.update_one(
        {"id": invitation_id},
        {"$set": {"status": "accepted", "payment_status": "paid", "accepted_at": datetime.now(timezone.utc)}}
    )
    
    # Get offer and update
    offer = await db.shared_offers.find_one({"id": invitation["offer_id"]})
    chat_room_id = None
    
    if offer:
        user_info = await get_user_basic_info(current_user["id"])
        
        # Add participant
        await db.shared_offers.update_one(
            {"id": offer["id"]},
            {
                "$push": {"participants": {
                    "user_id": current_user["id"],
                    "name": user_info["name"],
                    "image": user_info["image"],
                    "role": "invitee"
                }},
                "$set": {"status": "confirmed", "updated_at": datetime.now(timezone.utc)}
            }
        )
        
        # Create chat room
        participant_ids = [offer["creator_id"], current_user["id"]]
        chat_room_id = await create_chat_room(offer["id"], participant_ids)
        
        await db.shared_offers.update_one(
            {"id": offer["id"]},
            {"$set": {"chat_room_id": chat_room_id}}
        )
        
        # Notify creator
        await ws_manager.send_personal_message({
            "type": "invitation_accepted",
            "offer_id": offer["id"],
            "offer_title": offer["title"],
            "participant_name": user_info["name"],
            "chat_room_id": chat_room_id
        }, offer["creator_id"])
    
    # Award gamification points to both users
    await award_gamification_points(current_user["id"], "rdv_invitation_accepted")
    await award_gamification_points(offer["creator_id"], "rdv_invitation_accepted")
    
    return {
        "message": "Invitation acceptée ! Vous pouvez maintenant discuter",
        "chat_room_id": chat_room_id
    }


@router.post("/invitations/{invitation_id}/decline")
async def decline_invitation(
    invitation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Decline an invitation"""
    invitation = await db.invitations.find_one({"id": invitation_id})
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation non trouvée")
    
    if invitation["invitee_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Cette invitation ne vous est pas destinée")
    
    await db.invitations.update_one(
        {"id": invitation_id},
        {"$set": {"status": "declined", "declined_at": datetime.now(timezone.utc)}}
    )
    
    # Notify inviter
    await ws_manager.send_personal_message({
        "type": "invitation_declined",
        "offer_id": invitation["offer_id"],
        "invitee_name": invitation["invitee_name"]
    }, invitation["inviter_id"])
    
    return {"message": "Invitation déclinée"}


# ============ AVAILABLE USERS ENDPOINTS ============

@router.post("/availability", response_model=dict)
async def register_availability(
    availability_data: UserAvailabilityCreate,
    current_user: dict = Depends(get_current_user)
):
    """Register as available for activities"""
    user_id = current_user["id"]
    
    # Check romantic subscription if registering for romantic
    if availability_data.availability_type in ["romantic", "both"]:
        has_subscription = await check_romantic_subscription(user_id)
        if not has_subscription:
            raise HTTPException(
                status_code=402,
                detail="Abonnement romantique requis pour les rencontres romantiques"
            )
    
    user_info = await get_user_basic_info(user_id)
    
    availability = {
        "user_id": user_id,
        "user_name": user_info["name"],
        "user_image": user_info["image"],
        "availability_type": availability_data.availability_type,
        "interests": availability_data.interests,
        "bio": availability_data.bio,
        "preferred_categories": availability_data.preferred_categories,
        "available_days": availability_data.available_days,
        "age_range_min": availability_data.age_range_min,
        "age_range_max": availability_data.age_range_max,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    # Upsert
    await db.user_availability.update_one(
        {"user_id": user_id},
        {"$set": availability},
        upsert=True
    )
    
    return {"message": "Disponibilité enregistrée", "availability": availability}


@router.get("/available-users", response_model=dict)
async def get_available_users(
    availability_type: str = Query(..., pattern="^(friendly|romantic)$"),
    category: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    """Get list of available users"""
    user_id = current_user["id"]
    
    # Check romantic subscription
    if availability_type == "romantic":
        has_subscription = await check_romantic_subscription(user_id)
        if not has_subscription:
            raise HTTPException(
                status_code=402,
                detail="Abonnement romantique requis (200 CHF/mois)"
            )
    
    query = {
        "is_active": True,
        "user_id": {"$ne": user_id},
        "$or": [
            {"availability_type": availability_type},
            {"availability_type": "both"}
        ]
    }
    
    if category:
        query["preferred_categories"] = category
    
    users = await db.user_availability.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    total = await db.user_availability.count_documents(query)
    
    return {
        "users": users,
        "total": total,
        "availability_type": availability_type
    }


@router.delete("/availability")
async def remove_availability(current_user: dict = Depends(get_current_user)):
    """Remove user availability"""
    await db.user_availability.update_one(
        {"user_id": current_user["id"]},
        {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc)}}
    )
    return {"message": "Disponibilité désactivée"}


# ============ ROMANTIC SUBSCRIPTION ENDPOINTS ============

@router.post("/subscriptions/romantic", response_model=dict)
async def subscribe_romantic(
    current_user: dict = Depends(get_current_user)
):
    """Subscribe to romantic mode (200 CHF/month) - Creates Stripe checkout"""
    user_id = current_user["id"]
    
    # Check existing subscription
    existing = await db.romantic_subscriptions.find_one({
        "user_id": user_id,
        "status": "active",
        "expires_at": {"$gt": datetime.now(timezone.utc)}
    })
    
    if existing:
        existing.pop('_id', None)
        return {
            "message": "Vous avez déjà un abonnement actif",
            "expires_at": existing["expires_at"].isoformat() if isinstance(existing["expires_at"], datetime) else existing["expires_at"],
            "status": "active",
            "has_subscription": True
        }
    
    # Create Stripe checkout session
    try:
        subscription_id = str(uuid.uuid4())
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'chf',
                    'product_data': {
                        'name': 'Abonnement Romantique Titelli',
                        'description': 'Accès aux fonctionnalités romantiques pendant 30 jours'
                    },
                    'unit_amount': int(ROMANTIC_SUBSCRIPTION_PRICE * 100),  # 20000 centimes = 200 CHF
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'{FRONTEND_URL}/rdv?subscription_success={subscription_id}',
            cancel_url=f'{FRONTEND_URL}/rdv?subscription_cancelled=true',
            metadata={
                'type': 'rdv_romantic_subscription',
                'subscription_id': subscription_id,
                'user_id': user_id
            }
        )
        
        # Store pending subscription
        subscription = {
            "id": subscription_id,
            "user_id": user_id,
            "plan": "romantic_monthly",
            "price": ROMANTIC_SUBSCRIPTION_PRICE,
            "currency": "CHF",
            "status": "pending",
            "payment_status": "pending",
            "checkout_session_id": checkout_session.id,
            "created_at": datetime.now(timezone.utc)
        }
        
        await db.romantic_subscriptions.insert_one(subscription)
        
        return {
            "message": "Redirection vers le paiement",
            "subscription_id": subscription_id,
            "checkout_url": checkout_session.url,
            "price": ROMANTIC_SUBSCRIPTION_PRICE,
            "currency": "CHF"
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=500, detail="Erreur de paiement")


@router.post("/subscriptions/romantic/{subscription_id}/confirm")
async def confirm_romantic_subscription(
    subscription_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Confirm romantic subscription after Stripe payment"""
    subscription = await db.romantic_subscriptions.find_one({"id": subscription_id})
    if not subscription:
        raise HTTPException(status_code=404, detail="Abonnement non trouvé")
    
    if subscription["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Cet abonnement ne vous appartient pas")
    
    # Verify Stripe payment
    checkout_session_id = subscription.get("checkout_session_id")
    if checkout_session_id:
        try:
            session = stripe.checkout.Session.retrieve(checkout_session_id)
            if session.payment_status != "paid":
                raise HTTPException(status_code=402, detail="Paiement non confirmé")
        except stripe.error.StripeError:
            raise HTTPException(status_code=402, detail="Impossible de vérifier le paiement")
    
    # Activate subscription
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    
    await db.romantic_subscriptions.update_one(
        {"id": subscription_id},
        {
            "$set": {
                "status": "active",
                "payment_status": "paid",
                "started_at": datetime.now(timezone.utc),
                "expires_at": expires_at
            }
        }
    )
    
    # Send confirmation email
    if EMAIL_SERVICE_AVAILABLE:
        user_name = current_user.get("name") or current_user.get("email", "").split("@")[0]
        user_email = current_user.get("email")
        if user_email:
            asyncio.create_task(send_payment_confirmation(
                user_email=user_email,
                user_name=user_name,
                service_name="Abonnement Romantique - RDV chez Titelli",
                amount=ROMANTIC_SUBSCRIPTION_PRICE,
                currency="CHF",
                subscription_type="Mensuel",
                next_billing_date=expires_at.strftime("%d/%m/%Y")
            ))
    
    return {
        "message": "Abonnement romantique activé !",
        "expires_at": expires_at.isoformat(),
        "has_subscription": True
    }


@router.get("/subscriptions/romantic/status", response_model=dict)
async def get_romantic_subscription_status(current_user: dict = Depends(get_current_user)):
    """Get current romantic subscription status"""
    subscription = await db.romantic_subscriptions.find_one(
        {"user_id": current_user["id"], "status": "active"},
        {"_id": 0}
    )
    
    if subscription and subscription["expires_at"] > datetime.now(timezone.utc):
        return {
            "has_subscription": True,
            "subscription": subscription
        }
    
    return {
        "has_subscription": False,
        "price": ROMANTIC_SUBSCRIPTION_PRICE,
        "currency": "CHF"
    }


# ============ CHAT ENDPOINTS ============

@router.get("/chat/rooms", response_model=dict)
async def get_chat_rooms(current_user: dict = Depends(get_current_user)):
    """Get all chat rooms for current user"""
    rooms = await db.chat_rooms.find(
        {"participants": current_user["id"]},
        {"_id": 0}
    ).sort("last_message_at", -1).to_list(50)
    
    # Enrich with offer info and last message
    enriched_rooms = []
    for room in rooms:
        offer = await db.shared_offers.find_one({"id": room["offer_id"]}, {"_id": 0, "title": 1, "offer_type": 1})
        last_message = await db.chat_messages.find_one(
            {"room_id": room["id"]},
            {"_id": 0}
        )
        
        # Get other participant info
        other_participant_id = [p for p in room["participants"] if p != current_user["id"]][0] if len(room["participants"]) > 1 else None
        other_participant = await get_user_basic_info(other_participant_id) if other_participant_id else None
        
        enriched_rooms.append({
            **room,
            "offer": offer,
            "last_message": last_message,
            "other_participant": other_participant
        })
    
    return {"rooms": enriched_rooms, "count": len(enriched_rooms)}


@router.get("/chat/rooms/{room_id}/messages", response_model=dict)
async def get_chat_messages(
    room_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get messages from a chat room"""
    # Verify access
    room = await db.chat_rooms.find_one({"id": room_id})
    if not room:
        raise HTTPException(status_code=404, detail="Salon non trouvé")
    
    if current_user["id"] not in room["participants"]:
        raise HTTPException(status_code=403, detail="Vous n'avez pas accès à ce salon")
    
    messages = await db.chat_messages.find(
        {"room_id": room_id},
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    # Reverse to get chronological order
    messages.reverse()
    
    return {"messages": messages, "room_id": room_id}


@router.post("/chat/rooms/{room_id}/messages", response_model=dict)
async def send_chat_message(
    room_id: str,
    message_data: ChatMessageCreate,
    current_user: dict = Depends(get_current_user)
):
    """Send a message to a chat room"""
    # Verify access
    room = await db.chat_rooms.find_one({"id": room_id})
    if not room:
        raise HTTPException(status_code=404, detail="Salon non trouvé")
    
    if current_user["id"] not in room["participants"]:
        raise HTTPException(status_code=403, detail="Vous n'avez pas accès à ce salon")
    
    user_info = await get_user_basic_info(current_user["id"])
    
    message_id = str(uuid.uuid4())
    message = {
        "id": message_id,
        "room_id": room_id,
        "sender_id": current_user["id"],
        "sender_name": user_info["name"],
        "sender_image": user_info["image"],
        "content": message_data.content,
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.chat_messages.insert_one(message)
    
    # Remove _id before returning
    message.pop('_id', None)
    
    # Update room last message time
    await db.chat_rooms.update_one(
        {"id": room_id},
        {"$set": {"last_message_at": datetime.now(timezone.utc)}}
    )
    
    # Send via WebSocket to room
    await chat_manager.send_to_room(room_id, {
        "type": "new_message",
        "message": {
            "id": message_id,
            "sender_id": current_user["id"],
            "sender_name": user_info["name"],
            "sender_image": user_info["image"],
            "content": message_data.content,
            "created_at": message["created_at"].isoformat()
        }
    }, exclude_user=current_user["id"])
    
    # Also notify via main WebSocket for offline users
    for participant_id in room["participants"]:
        if participant_id != current_user["id"]:
            await ws_manager.send_personal_message({
                "type": "chat_message",
                "room_id": room_id,
                "sender_name": user_info["name"],
                "preview": message_data.content[:50] + "..." if len(message_data.content) > 50 else message_data.content
            }, participant_id)
    
    # Convert datetime for JSON serialization
    message["created_at"] = message["created_at"].isoformat()
    
    return {"message": message, "sent": True}


# ============ WEBSOCKET CHAT ENDPOINT ============

@router.websocket("/chat/ws/{room_id}")
async def websocket_chat(websocket: WebSocket, room_id: str, token: str = Query(...)):
    """WebSocket endpoint for real-time chat"""
    # Authenticate
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            await websocket.close(code=4001)
            return
    except jwt.InvalidTokenError:
        await websocket.close(code=4001)
        return
    
    # Verify room access
    room = await db.chat_rooms.find_one({"id": room_id})
    if not room or user_id not in room["participants"]:
        await websocket.close(code=4003)
        return
    
    # Connect
    await chat_manager.connect(websocket, room_id, user_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "message":
                user_info = await get_user_basic_info(user_id)
                message_id = str(uuid.uuid4())
                message = {
                    "id": message_id,
                    "room_id": room_id,
                    "sender_id": user_id,
                    "sender_name": user_info["name"],
                    "sender_image": user_info["image"],
                    "content": data.get("content", ""),
                    "created_at": datetime.now(timezone.utc)
                }
                
                await db.chat_messages.insert_one(message)
                
                # Broadcast to room
                await chat_manager.send_to_room(room_id, {
                    "type": "new_message",
                    "message": {
                        **message,
                        "created_at": message["created_at"].isoformat()
                    }
                })
                
            elif data.get("type") == "typing":
                await chat_manager.send_to_room(room_id, {
                    "type": "typing",
                    "user_id": user_id
                }, exclude_user=user_id)
                
    except WebSocketDisconnect:
        await chat_manager.disconnect(room_id, user_id)


# ============ CATEGORIES ENDPOINT ============

@router.get("/categories", response_model=dict)
async def get_rdv_categories():
    """Get available categories for shared offers"""
    categories = [
        {"id": "restaurant", "name": "Restaurant", "icon": "utensils", "description": "Brunch, déjeuner, dîner..."},
        {"id": "sport", "name": "Sport", "icon": "dumbbell", "description": "Tennis, foot, fitness..."},
        {"id": "wellness", "name": "Bien-être", "icon": "spa", "description": "Spa, massage, yoga..."},
        {"id": "culture", "name": "Culture", "icon": "theater-masks", "description": "Musée, théâtre, cinéma..."},
        {"id": "nature", "name": "Nature", "icon": "tree", "description": "Randonnée, parc, lac..."},
        {"id": "party", "name": "Soirée", "icon": "glass-cheers", "description": "Bar, club, concert..."},
        {"id": "creative", "name": "Créatif", "icon": "palette", "description": "Atelier, cours, DIY..."},
        {"id": "other", "name": "Autre", "icon": "ellipsis-h", "description": "Autre activité..."}
    ]
    return {"categories": categories}


# ============ STATS ENDPOINT ============

@router.get("/stats", response_model=dict)
async def get_rdv_stats(current_user: dict = Depends(get_current_user)):
    """Get user's RDV statistics"""
    user_id = current_user["id"]
    
    # Count offers created
    offers_created = await db.shared_offers.count_documents({"creator_id": user_id})
    
    # Count confirmed offers
    offers_confirmed = await db.shared_offers.count_documents({
        "$or": [
            {"creator_id": user_id},
            {"participants.user_id": user_id}
        ],
        "status": "confirmed"
    })
    
    # Count invitations received
    invitations_received = await db.invitations.count_documents({"invitee_id": user_id})
    invitations_accepted = await db.invitations.count_documents({"invitee_id": user_id, "status": "accepted"})
    
    # Check subscription
    has_romantic = await check_romantic_subscription(user_id)
    
    return {
        "offers_created": offers_created,
        "offers_confirmed": offers_confirmed,
        "invitations_received": invitations_received,
        "invitations_accepted": invitations_accepted,
        "has_romantic_subscription": has_romantic
    }
