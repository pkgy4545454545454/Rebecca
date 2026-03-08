"""
Titelli Pro++ & Sports Competitions Router
- B2B deliveries
- Stock liquidation
- Sports matches and competitions
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import asyncio
import logging
import uuid
import os
import stripe

from .shared import db, get_current_user

# Import email service
try:
    from services.email_service import send_payment_confirmation
    EMAIL_SERVICE_AVAILABLE = True
except ImportError:
    EMAIL_SERVICE_AVAILABLE = False

router = APIRouter(prefix="/api/pro", tags=["Titelli Pro++"])
logger = logging.getLogger(__name__)

# Stripe config
stripe.api_key = os.environ.get('STRIPE_API_KEY')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://titelli.ch')

TITELLI_PRO_PRICE = 199.00  # CHF/month

# Gamification helper
async def award_gamification_points(user_id: str, action: str):
    """Award gamification points"""
    try:
        from .gamification import award_points
        await award_points(user_id, action)
    except Exception as e:
        logger.warning(f"Could not award points: {e}")


# ============ PYDANTIC MODELS ============

class DeliveryClientCreate(BaseModel):
    """Create a B2B delivery client"""
    client_name: str = Field(..., min_length=2)
    client_email: Optional[str] = None
    product_name: str = Field(..., min_length=2)
    quantity: int = Field(default=1, ge=1)
    frequency: str = Field(default="weekly", pattern="^(daily|weekly|monthly)$")
    delivery_day: str = Field(default="monday")
    notes: Optional[str] = None


class LiquidationItemCreate(BaseModel):
    """Create a liquidation item"""
    product_name: str = Field(..., min_length=2)
    original_price: float = Field(ge=0)
    liquidation_price: float = Field(..., gt=0)
    quantity: int = Field(default=1, ge=1)
    reason: str = Field(default="overstock", pattern="^(overstock|seasonal|expiring|other)$")
    expiry_date: Optional[datetime] = None


class ProSubscription(BaseModel):
    """Subscribe to Pro++"""
    business_type: str = "general"


# ============ PRO++ SUBSCRIPTION ============

@router.get("/status", response_model=dict)
async def get_pro_status(current_user: dict = Depends(get_current_user)):
    """Get Pro++ subscription status"""
    if current_user.get("user_type") not in ["enterprise", "entreprise"]:
        raise HTTPException(status_code=403, detail="Réservé aux entreprises")
    
    subscription = await db.pro_subscriptions.find_one({
        "user_id": current_user["id"],
        "status": "active",
        "expires_at": {"$gt": datetime.now(timezone.utc)}
    }, {"_id": 0})
    
    if subscription:
        return {
            "has_subscription": True,
            "subscription": subscription,
            "expires_at": subscription.get("expires_at")
        }
    
    return {
        "has_subscription": False,
        "price": TITELLI_PRO_PRICE,
        "currency": "CHF"
    }


@router.post("/subscribe", response_model=dict)
async def subscribe_pro(
    subscription_data: ProSubscription,
    current_user: dict = Depends(get_current_user)
):
    """Subscribe to Titelli Pro++"""
    if current_user.get("user_type") not in ["enterprise", "entreprise"]:
        raise HTTPException(status_code=403, detail="Réservé aux entreprises")
    
    user_id = current_user["id"]
    
    # Check existing
    existing = await db.pro_subscriptions.find_one({
        "user_id": user_id,
        "status": "active",
        "expires_at": {"$gt": datetime.now(timezone.utc)}
    })
    
    if existing:
        existing.pop('_id', None)
        return {
            "message": "Vous avez déjà Titelli Pro++",
            "has_subscription": True,
            "subscription": existing
        }
    
    # Create Stripe checkout
    try:
        subscription_id = str(uuid.uuid4())
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'chf',
                    'product_data': {
                        'name': 'Titelli Pro++',
                        'description': 'Accès complet aux fonctionnalités B2B avancées'
                    },
                    'unit_amount': int(TITELLI_PRO_PRICE * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'{FRONTEND_URL}/enterprise/pro?success={subscription_id}',
            cancel_url=f'{FRONTEND_URL}/enterprise/pro?cancelled=true',
            metadata={
                'type': 'titelli_pro',
                'subscription_id': subscription_id,
                'user_id': user_id
            }
        )
        
        subscription = {
            "id": subscription_id,
            "user_id": user_id,
            "enterprise_id": current_user.get("enterprise_id"),
            "business_type": subscription_data.business_type,
            "price": TITELLI_PRO_PRICE,
            "currency": "CHF",
            "status": "pending",
            "checkout_session_id": checkout_session.id,
            "created_at": datetime.now(timezone.utc)
        }
        
        await db.pro_subscriptions.insert_one(subscription)
        
        return {
            "message": "Redirection vers le paiement",
            "checkout_url": checkout_session.url,
            "price": TITELLI_PRO_PRICE
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=500, detail="Erreur de paiement")


@router.post("/subscribe/{subscription_id}/confirm")
async def confirm_pro_subscription(
    subscription_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Confirm Pro++ subscription after payment"""
    subscription = await db.pro_subscriptions.find_one({"id": subscription_id})
    if not subscription:
        raise HTTPException(status_code=404, detail="Abonnement non trouvé")
    
    if subscription["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Non autorisé")
    
    # Verify Stripe payment
    checkout_session_id = subscription.get("checkout_session_id")
    if checkout_session_id:
        try:
            session = stripe.checkout.Session.retrieve(checkout_session_id)
            if session.payment_status != "paid":
                raise HTTPException(status_code=402, detail="Paiement non confirmé")
        except stripe.error.StripeError:
            raise HTTPException(status_code=402, detail="Impossible de vérifier le paiement")
    
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    
    await db.pro_subscriptions.update_one(
        {"id": subscription_id},
        {
            "$set": {
                "status": "active",
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
                service_name="Titelli Pro++ - Services B2B",
                amount=TITELLI_PRO_PRICE,
                currency="CHF",
                subscription_type="Mensuel",
                next_billing_date=expires_at.strftime("%d/%m/%Y")
            ))
    
    return {
        "message": "Titelli Pro++ activé !",
        "expires_at": expires_at.isoformat()
    }


# ============ B2B DELIVERIES ============

@router.get("/deliveries", response_model=dict)
async def get_deliveries(current_user: dict = Depends(get_current_user)):
    """Get B2B delivery clients"""
    if current_user.get("user_type") not in ["enterprise", "entreprise"]:
        raise HTTPException(status_code=403, detail="Réservé aux entreprises")
    
    deliveries = await db.b2b_deliveries.find(
        {"enterprise_user_id": current_user["id"]},
        {"_id": 0}
    ).to_list(100)
    
    return {"deliveries": deliveries, "count": len(deliveries)}


@router.post("/deliveries", response_model=dict)
async def create_delivery(
    delivery_data: DeliveryClientCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a B2B delivery client"""
    if current_user.get("user_type") not in ["enterprise", "entreprise"]:
        raise HTTPException(status_code=403, detail="Réservé aux entreprises")
    
    # Check Pro++ subscription
    pro_sub = await db.pro_subscriptions.find_one({
        "user_id": current_user["id"],
        "status": "active",
        "expires_at": {"$gt": datetime.now(timezone.utc)}
    })
    
    if not pro_sub:
        raise HTTPException(status_code=402, detail="Abonnement Pro++ requis")
    
    delivery_id = str(uuid.uuid4())
    delivery = {
        "id": delivery_id,
        "enterprise_user_id": current_user["id"],
        "enterprise_id": current_user.get("enterprise_id"),
        "client_name": delivery_data.client_name,
        "client_email": delivery_data.client_email,
        "product_name": delivery_data.product_name,
        "quantity": delivery_data.quantity,
        "frequency": delivery_data.frequency,
        "delivery_day": delivery_data.delivery_day,
        "notes": delivery_data.notes,
        "status": "active",
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.b2b_deliveries.insert_one(delivery)
    delivery.pop('_id', None)
    
    return {"message": "Client B2B ajouté", "delivery": delivery}


@router.delete("/deliveries/{delivery_id}")
async def delete_delivery(
    delivery_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a B2B delivery client"""
    delivery = await db.b2b_deliveries.find_one({"id": delivery_id})
    if not delivery:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    if delivery["enterprise_user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Non autorisé")
    
    await db.b2b_deliveries.delete_one({"id": delivery_id})
    return {"message": "Client supprimé"}


# ============ LIQUIDATION ============

@router.get("/liquidations", response_model=dict)
async def get_liquidations(current_user: dict = Depends(get_current_user)):
    """Get liquidation items"""
    if current_user.get("user_type") not in ["enterprise", "entreprise"]:
        raise HTTPException(status_code=403, detail="Réservé aux entreprises")
    
    items = await db.liquidation_items.find(
        {"enterprise_user_id": current_user["id"]},
        {"_id": 0}
    ).to_list(100)
    
    return {"items": items, "count": len(items)}


@router.get("/liquidations/all", response_model=dict)
async def get_all_liquidations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """Get all liquidation items (public)"""
    items = await db.liquidation_items.find(
        {"status": "active"},
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    total = await db.liquidation_items.count_documents({"status": "active"})
    
    return {"items": items, "total": total}


@router.post("/liquidations", response_model=dict)
async def create_liquidation(
    item_data: LiquidationItemCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a liquidation item"""
    if current_user.get("user_type") not in ["enterprise", "entreprise"]:
        raise HTTPException(status_code=403, detail="Réservé aux entreprises")
    
    # Check Pro++ subscription
    pro_sub = await db.pro_subscriptions.find_one({
        "user_id": current_user["id"],
        "status": "active",
        "expires_at": {"$gt": datetime.now(timezone.utc)}
    })
    
    if not pro_sub:
        raise HTTPException(status_code=402, detail="Abonnement Pro++ requis")
    
    item_id = str(uuid.uuid4())
    item = {
        "id": item_id,
        "enterprise_user_id": current_user["id"],
        "enterprise_id": current_user.get("enterprise_id"),
        "product_name": item_data.product_name,
        "original_price": item_data.original_price,
        "liquidation_price": item_data.liquidation_price,
        "discount_percent": round((1 - item_data.liquidation_price / item_data.original_price) * 100) if item_data.original_price > 0 else 0,
        "quantity": item_data.quantity,
        "reason": item_data.reason,
        "expiry_date": item_data.expiry_date,
        "status": "active",
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.liquidation_items.insert_one(item)
    item.pop('_id', None)
    
    return {"message": "Article en liquidation ajouté", "item": item}


@router.delete("/liquidations/{item_id}")
async def delete_liquidation(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a liquidation item"""
    item = await db.liquidation_items.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    if item["enterprise_user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Non autorisé")
    
    await db.liquidation_items.delete_one({"id": item_id})
    return {"message": "Article supprimé"}


# ============ SPORTS COMPETITIONS ============

sports_router = APIRouter(prefix="/api/sports", tags=["Sports & Competitions"])


class MatchCreate(BaseModel):
    """Create a sports match"""
    sport: str = Field(..., min_length=2)  # football, tennis, basketball, etc.
    title: str = Field(..., min_length=3)
    match_type: str = Field(default="friendly", pattern="^(friendly|competition|tournament)$")
    location: Optional[str] = None
    date_time: Optional[datetime] = None
    max_players: int = Field(default=2, ge=2)
    team_size: int = Field(default=1, ge=1)  # 1 for individual, 5 for football team, etc.
    description: Optional[str] = None
    looking_for: str = Field(default="opponent", pattern="^(opponent|players|team)$")


class TeamCreate(BaseModel):
    """Create a team"""
    name: str = Field(..., min_length=2)
    sport: str
    description: Optional[str] = None


class CompetitionCreate(BaseModel):
    """Create a competition/tournament"""
    name: str = Field(..., min_length=3)
    sport: str
    competition_type: str = Field(default="knockout", pattern="^(knockout|league|group)$")
    max_teams: int = Field(default=8, ge=2)
    registration_deadline: Optional[datetime] = None
    start_date: Optional[datetime] = None
    prize: Optional[str] = None
    entry_fee: float = Field(default=0, ge=0)
    description: Optional[str] = None


@sports_router.get("/categories")
async def get_sports_categories():
    """Get available sports categories"""
    categories = [
        {"id": "football", "name": "Football", "team_size": 11, "icon": "⚽"},
        {"id": "tennis", "name": "Tennis", "team_size": 1, "icon": "🎾"},
        {"id": "basketball", "name": "Basketball", "team_size": 5, "icon": "🏀"},
        {"id": "volleyball", "name": "Volleyball", "team_size": 6, "icon": "🏐"},
        {"id": "badminton", "name": "Badminton", "team_size": 1, "icon": "🏸"},
        {"id": "padel", "name": "Padel", "team_size": 2, "icon": "🎾"},
        {"id": "running", "name": "Course", "team_size": 1, "icon": "🏃"},
        {"id": "swimming", "name": "Natation", "team_size": 1, "icon": "🏊"},
        {"id": "cycling", "name": "Cyclisme", "team_size": 1, "icon": "🚴"},
        {"id": "fitness", "name": "Fitness", "team_size": 1, "icon": "💪"},
        {"id": "other", "name": "Autre", "team_size": 1, "icon": "🏆"}
    ]
    return {"categories": categories}


@sports_router.post("/matches", response_model=dict)
async def create_match(
    match_data: MatchCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a sports match - Find an opponent or players"""
    match_id = str(uuid.uuid4())
    
    user_info = {
        "id": current_user["id"],
        "name": f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}".strip() or "Joueur"
    }
    
    match = {
        "id": match_id,
        "creator_id": current_user["id"],
        "creator_name": user_info["name"],
        "sport": match_data.sport,
        "title": match_data.title,
        "match_type": match_data.match_type,
        "location": match_data.location,
        "date_time": match_data.date_time,
        "max_players": match_data.max_players,
        "team_size": match_data.team_size,
        "description": match_data.description,
        "looking_for": match_data.looking_for,
        "status": "open",
        "participants": [user_info],
        "teams": [],
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.sports_matches.insert_one(match)
    match.pop('_id', None)
    
    return {"message": "Match créé", "match_id": match_id, "match": match}


@sports_router.get("/matches", response_model=dict)
async def get_matches(
    sport: Optional[str] = None,
    looking_for: Optional[str] = None,
    status: str = Query("open"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get available matches"""
    query = {"status": status, "creator_id": {"$ne": current_user["id"]}}
    
    if sport:
        query["sport"] = sport
    if looking_for:
        query["looking_for"] = looking_for
    
    matches = await db.sports_matches.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.sports_matches.count_documents(query)
    
    return {"matches": matches, "total": total}


@sports_router.get("/matches/my", response_model=dict)
async def get_my_matches(current_user: dict = Depends(get_current_user)):
    """Get user's matches"""
    matches = await db.sports_matches.find(
        {"$or": [
            {"creator_id": current_user["id"]},
            {"participants.id": current_user["id"]}
        ]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    
    return {"matches": matches, "count": len(matches)}


@sports_router.post("/matches/{match_id}/join", response_model=dict)
async def join_match(
    match_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Join a match"""
    match = await db.sports_matches.find_one({"id": match_id})
    if not match:
        raise HTTPException(status_code=404, detail="Match non trouvé")
    
    if match["status"] != "open":
        raise HTTPException(status_code=400, detail="Ce match n'est plus ouvert")
    
    # Check if already joined
    if any(p["id"] == current_user["id"] for p in match.get("participants", [])):
        raise HTTPException(status_code=400, detail="Vous participez déjà à ce match")
    
    # Check if full
    if len(match.get("participants", [])) >= match["max_players"]:
        raise HTTPException(status_code=400, detail="Ce match est complet")
    
    user_info = {
        "id": current_user["id"],
        "name": f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}".strip() or "Joueur"
    }
    
    # Add participant
    await db.sports_matches.update_one(
        {"id": match_id},
        {"$push": {"participants": user_info}}
    )
    
    # Check if match is now full
    updated_match = await db.sports_matches.find_one({"id": match_id})
    if len(updated_match.get("participants", [])) >= updated_match["max_players"]:
        await db.sports_matches.update_one(
            {"id": match_id},
            {"$set": {"status": "confirmed"}}
        )
    
    return {"message": "Vous avez rejoint le match !", "match_id": match_id}


@sports_router.post("/teams", response_model=dict)
async def create_team(
    team_data: TeamCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a sports team"""
    team_id = str(uuid.uuid4())
    
    user_info = {
        "id": current_user["id"],
        "name": f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}".strip(),
        "role": "captain"
    }
    
    team = {
        "id": team_id,
        "captain_id": current_user["id"],
        "name": team_data.name,
        "sport": team_data.sport,
        "description": team_data.description,
        "members": [user_info],
        "wins": 0,
        "losses": 0,
        "draws": 0,
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.sports_teams.insert_one(team)
    team.pop('_id', None)
    
    return {"message": "Équipe créée", "team": team}


@sports_router.get("/teams", response_model=dict)
async def get_teams(
    sport: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """Get teams"""
    query = {}
    if sport:
        query["sport"] = sport
    
    teams = await db.sports_teams.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    total = await db.sports_teams.count_documents(query)
    
    return {"teams": teams, "total": total}


@sports_router.get("/teams/my", response_model=dict)
async def get_my_teams(current_user: dict = Depends(get_current_user)):
    """Get teams where current user is a member"""
    teams = await db.sports_teams.find(
        {"members.id": current_user["id"]},
        {"_id": 0}
    ).to_list(100)
    
    return {"teams": teams, "count": len(teams)}


@sports_router.post("/teams/{team_id}/join", response_model=dict)
async def join_team(
    team_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Request to join a team"""
    team = await db.sports_teams.find_one({"id": team_id})
    if not team:
        raise HTTPException(status_code=404, detail="Équipe non trouvée")
    
    if any(m["id"] == current_user["id"] for m in team.get("members", [])):
        raise HTTPException(status_code=400, detail="Vous êtes déjà membre de cette équipe")
    
    user_info = {
        "id": current_user["id"],
        "name": f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}".strip(),
        "role": "member"
    }
    
    await db.sports_teams.update_one(
        {"id": team_id},
        {"$push": {"members": user_info}}
    )
    
    return {"message": "Vous avez rejoint l'équipe !"}


@sports_router.post("/competitions", response_model=dict)
async def create_competition(
    comp_data: CompetitionCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a competition/tournament"""
    comp_id = str(uuid.uuid4())
    
    competition = {
        "id": comp_id,
        "organizer_id": current_user["id"],
        "organizer_name": f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}".strip(),
        "name": comp_data.name,
        "sport": comp_data.sport,
        "competition_type": comp_data.competition_type,
        "max_teams": comp_data.max_teams,
        "registration_deadline": comp_data.registration_deadline,
        "start_date": comp_data.start_date,
        "prize": comp_data.prize,
        "entry_fee": comp_data.entry_fee,
        "description": comp_data.description,
        "status": "registration_open",
        "registered_teams": [],
        "bracket": [],
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.sports_competitions.insert_one(competition)
    competition.pop('_id', None)
    
    return {"message": "Compétition créée", "competition": competition}


@sports_router.get("/competitions", response_model=dict)
async def get_competitions(
    sport: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """Get competitions"""
    query = {}
    if sport:
        query["sport"] = sport
    if status:
        query["status"] = status
    
    competitions = await db.sports_competitions.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.sports_competitions.count_documents(query)
    
    return {"competitions": competitions, "total": total}


@sports_router.post("/competitions/{comp_id}/register", response_model=dict)
async def register_team_for_competition(
    comp_id: str,
    team_id: str = Query(...),
    current_user: dict = Depends(get_current_user)
):
    """Register a team for a competition"""
    competition = await db.sports_competitions.find_one({"id": comp_id})
    if not competition:
        raise HTTPException(status_code=404, detail="Compétition non trouvée")
    
    if competition["status"] != "registration_open":
        raise HTTPException(status_code=400, detail="Les inscriptions sont fermées")
    
    team = await db.sports_teams.find_one({"id": team_id})
    if not team:
        raise HTTPException(status_code=404, detail="Équipe non trouvée")
    
    if team["captain_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Seul le capitaine peut inscrire l'équipe")
    
    if len(competition.get("registered_teams", [])) >= competition["max_teams"]:
        raise HTTPException(status_code=400, detail="Compétition complète")
    
    if any(t["id"] == team_id for t in competition.get("registered_teams", [])):
        raise HTTPException(status_code=400, detail="Équipe déjà inscrite")
    
    team_info = {
        "id": team_id,
        "name": team["name"],
        "captain_id": team["captain_id"]
    }
    
    await db.sports_competitions.update_one(
        {"id": comp_id},
        {"$push": {"registered_teams": team_info}}
    )
    
    return {"message": f"Équipe {team['name']} inscrite à la compétition !"}
