"""
Titelli - Demandes Spécialistes & Lifestyle Pass
- AI-powered specialist search
- Urgent/specific requests for specialists
- Lifestyle passes (Healthy, Better You, MVP)
- Titelli Pro++ for B2B
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import logging
import uuid
import os
import stripe

from .shared import db, get_current_user

router = APIRouter(prefix="/api/specialists", tags=["Demandes Spécialistes"])
logger = logging.getLogger(__name__)

# Stripe config
stripe.api_key = os.environ.get('STRIPE_API_KEY')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://titelli.ch')


# ============ PYDANTIC MODELS ============

class SpecialistRequestCreate(BaseModel):
    """Create a specialist request"""
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    category: str
    urgency: str = Field(default="normal", pattern="^(urgent|normal|flexible)$")
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    location: Optional[str] = None
    deadline: Optional[datetime] = None


class SpecialistResponseCreate(BaseModel):
    """Specialist response to a request"""
    request_id: str
    message: str = Field(..., min_length=10, max_length=2000)
    proposed_price: Optional[float] = None
    estimated_time: Optional[str] = None


class LifestylePassSubscription(BaseModel):
    """Subscribe to a lifestyle pass"""
    pass_type: str = Field(..., pattern="^(healthy|better_you|mvp)$")


class TitelliProSubscription(BaseModel):
    """Subscribe to Titelli Pro++"""
    business_type: str
    delivery_frequency: Optional[str] = "weekly"


# ============ PASS PRICING ============
LIFESTYLE_PASSES = {
    "healthy": {
        "name": "Healthy Lifestyle Pass",
        "description": "Accès aux prestataires certifiés bien-être et santé",
        "price": 99.00,
        "features": ["Spa & wellness", "Nutrition", "Fitness", "Bien-être mental"]
    },
    "better_you": {
        "name": "Better You Pass", 
        "description": "Développement personnel et bien-être global",
        "price": 149.00,
        "features": ["Coaching", "Développement personnel", "Thérapies alternatives", "Méditation"]
    },
    "mvp": {
        "name": "Special MVP Pass",
        "description": "Accès VIP aux lieux et services exclusifs",
        "price": 299.00,
        "features": ["Accès VIP", "Lieux exclusifs", "Conciergerie", "Événements privés"]
    }
}

TITELLI_PRO_PRICE = 199.00  # CHF/month


# ============ SPECIALIST REQUESTS ============

@router.post("/requests", response_model=dict)
async def create_specialist_request(
    request_data: SpecialistRequestCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a specialist request - visible to all relevant specialists"""
    request_id = str(uuid.uuid4())
    
    request = {
        "id": request_id,
        "user_id": current_user["id"],
        "user_name": f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}".strip() or "Client",
        "title": request_data.title,
        "description": request_data.description,
        "category": request_data.category,
        "urgency": request_data.urgency,
        "budget_min": request_data.budget_min,
        "budget_max": request_data.budget_max,
        "location": request_data.location,
        "deadline": request_data.deadline,
        "status": "open",
        "responses_count": 0,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db.specialist_requests.insert_one(request)
    request.pop('_id', None)
    
    return {"message": "Demande créée avec succès", "request_id": request_id, "request": request}


@router.get("/requests", response_model=dict)
async def get_specialist_requests(
    category: Optional[str] = None,
    urgency: Optional[str] = None,
    status: str = Query("open"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get specialist requests - for specialists to browse and respond"""
    query = {"status": status}
    
    if category:
        query["category"] = category
    if urgency:
        query["urgency"] = urgency
    
    requests = await db.specialist_requests.find(query, {"_id": 0}).sort([
        ("urgency", 1),  # urgent first
        ("created_at", -1)
    ]).skip(skip).limit(limit).to_list(limit)
    
    total = await db.specialist_requests.count_documents(query)
    
    return {
        "requests": requests,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/requests/my", response_model=dict)
async def get_my_requests(
    current_user: dict = Depends(get_current_user)
):
    """Get current user's specialist requests"""
    requests = await db.specialist_requests.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    
    return {"requests": requests, "count": len(requests)}


@router.get("/requests/{request_id}", response_model=dict)
async def get_request_detail(
    request_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specialist request details with responses"""
    request = await db.specialist_requests.find_one({"id": request_id}, {"_id": 0})
    if not request:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    
    # Get responses
    responses = await db.specialist_responses.find(
        {"request_id": request_id},
        {"_id": 0}
    ).to_list(50)
    
    return {"request": request, "responses": responses}


@router.post("/requests/{request_id}/respond", response_model=dict)
async def respond_to_request(
    request_id: str,
    response_data: SpecialistResponseCreate,
    current_user: dict = Depends(get_current_user)
):
    """Specialist responds to a request"""
    # Verify user is enterprise/specialist
    if current_user.get("user_type") not in ["enterprise", "entreprise", "admin"]:
        raise HTTPException(status_code=403, detail="Seuls les prestataires peuvent répondre")
    
    request = await db.specialist_requests.find_one({"id": request_id})
    if not request:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    
    if request["status"] != "open":
        raise HTTPException(status_code=400, detail="Cette demande n'est plus ouverte")
    
    # Check if already responded
    existing = await db.specialist_responses.find_one({
        "request_id": request_id,
        "specialist_id": current_user["id"]
    })
    if existing:
        raise HTTPException(status_code=400, detail="Vous avez déjà répondu à cette demande")
    
    response_id = str(uuid.uuid4())
    response = {
        "id": response_id,
        "request_id": request_id,
        "specialist_id": current_user["id"],
        "specialist_name": f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}".strip(),
        "enterprise_id": current_user.get("enterprise_id"),
        "message": response_data.message,
        "proposed_price": response_data.proposed_price,
        "estimated_time": response_data.estimated_time,
        "status": "pending",
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.specialist_responses.insert_one(response)
    response.pop('_id', None)
    
    # Update response count
    await db.specialist_requests.update_one(
        {"id": request_id},
        {"$inc": {"responses_count": 1}}
    )
    
    return {"message": "Réponse envoyée", "response": response}


@router.post("/requests/{request_id}/accept-response/{response_id}")
async def accept_specialist_response(
    request_id: str,
    response_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Accept a specialist's response"""
    request = await db.specialist_requests.find_one({"id": request_id})
    if not request:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    
    if request["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Seul le demandeur peut accepter une réponse")
    
    response = await db.specialist_responses.find_one({"id": response_id})
    if not response:
        raise HTTPException(status_code=404, detail="Réponse non trouvée")
    
    # Update response status
    await db.specialist_responses.update_one(
        {"id": response_id},
        {"$set": {"status": "accepted"}}
    )
    
    # Update request status
    await db.specialist_requests.update_one(
        {"id": request_id},
        {"$set": {"status": "matched", "matched_specialist_id": response["specialist_id"]}}
    )
    
    # Decline other responses
    await db.specialist_responses.update_many(
        {"request_id": request_id, "id": {"$ne": response_id}},
        {"$set": {"status": "declined"}}
    )
    
    return {"message": "Réponse acceptée ! Vous pouvez maintenant contacter le spécialiste"}


# ============ AI SEARCH (Placeholder for future AI integration) ============

@router.post("/search/ai", response_model=dict)
async def ai_specialist_search(
    query: str = Query(..., min_length=10),
    current_user: dict = Depends(get_current_user)
):
    """AI-powered specialist search"""
    # For now, do a text search on specialists/enterprises
    # In production, this would use embeddings and AI
    
    # Search in enterprises
    enterprises = await db.enterprises.find(
        {
            "$or": [
                {"business_name": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"services": {"$regex": query, "$options": "i"}},
                {"specialties": {"$regex": query, "$options": "i"}}
            ],
            "status": "approved"
        },
        {"_id": 0, "id": 1, "business_name": 1, "name": 1, "description": 1, "category": 1, "location": 1, "rating": 1}
    ).limit(20).to_list(20)
    
    return {
        "query": query,
        "results": enterprises,
        "count": len(enterprises),
        "ai_suggestion": f"Voici les spécialistes correspondant à votre recherche: '{query}'. Vous pouvez également créer une demande spécifique."
    }


# ============ LIFESTYLE PASSES ============

@router.get("/passes", response_model=dict)
async def get_lifestyle_passes():
    """Get available lifestyle passes"""
    return {"passes": LIFESTYLE_PASSES}


@router.post("/passes/subscribe", response_model=dict)
async def subscribe_lifestyle_pass(
    subscription_data: LifestylePassSubscription,
    current_user: dict = Depends(get_current_user)
):
    """Subscribe to a lifestyle pass"""
    pass_type = subscription_data.pass_type
    
    if pass_type not in LIFESTYLE_PASSES:
        raise HTTPException(status_code=400, detail="Type de pass invalide")
    
    pass_info = LIFESTYLE_PASSES[pass_type]
    
    # Check existing subscription
    existing = await db.lifestyle_subscriptions.find_one({
        "user_id": current_user["id"],
        "pass_type": pass_type,
        "status": "active",
        "expires_at": {"$gt": datetime.now(timezone.utc)}
    })
    
    if existing:
        existing.pop('_id', None)
        return {
            "message": "Vous avez déjà ce pass actif",
            "subscription": existing,
            "has_subscription": True
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
                        'name': pass_info["name"],
                        'description': pass_info["description"]
                    },
                    'unit_amount': int(pass_info["price"] * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'{FRONTEND_URL}/specialists?pass_success={subscription_id}',
            cancel_url=f'{FRONTEND_URL}/specialists?pass_cancelled=true',
            metadata={
                'type': 'lifestyle_pass',
                'pass_type': pass_type,
                'subscription_id': subscription_id,
                'user_id': current_user["id"]
            }
        )
        
        # Store pending subscription
        subscription = {
            "id": subscription_id,
            "user_id": current_user["id"],
            "pass_type": pass_type,
            "pass_name": pass_info["name"],
            "price": pass_info["price"],
            "currency": "CHF",
            "status": "pending",
            "checkout_session_id": checkout_session.id,
            "created_at": datetime.now(timezone.utc)
        }
        
        await db.lifestyle_subscriptions.insert_one(subscription)
        
        return {
            "message": "Redirection vers le paiement",
            "checkout_url": checkout_session.url,
            "pass": pass_info
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=500, detail="Erreur de paiement")


@router.post("/passes/{subscription_id}/confirm")
async def confirm_pass_subscription(
    subscription_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Confirm lifestyle pass after payment"""
    subscription = await db.lifestyle_subscriptions.find_one({"id": subscription_id})
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
    
    await db.lifestyle_subscriptions.update_one(
        {"id": subscription_id},
        {
            "$set": {
                "status": "active",
                "started_at": datetime.now(timezone.utc),
                "expires_at": expires_at
            }
        }
    )
    
    return {
        "message": f"Pass {subscription['pass_name']} activé !",
        "expires_at": expires_at.isoformat()
    }


@router.get("/passes/my", response_model=dict)
async def get_my_passes(current_user: dict = Depends(get_current_user)):
    """Get user's active lifestyle passes"""
    passes = await db.lifestyle_subscriptions.find(
        {
            "user_id": current_user["id"],
            "status": "active",
            "expires_at": {"$gt": datetime.now(timezone.utc)}
        },
        {"_id": 0}
    ).to_list(10)
    
    return {"passes": passes, "count": len(passes)}


# ============ TITELLI PRO++ ============

@router.post("/pro/subscribe", response_model=dict)
async def subscribe_titelli_pro(
    subscription_data: TitelliProSubscription,
    current_user: dict = Depends(get_current_user)
):
    """Subscribe to Titelli Pro++ for B2B services"""
    if current_user.get("user_type") not in ["enterprise", "entreprise"]:
        raise HTTPException(status_code=403, detail="Titelli Pro++ est réservé aux entreprises")
    
    # Check existing subscription
    existing = await db.pro_subscriptions.find_one({
        "user_id": current_user["id"],
        "status": "active",
        "expires_at": {"$gt": datetime.now(timezone.utc)}
    })
    
    if existing:
        existing.pop('_id', None)
        return {
            "message": "Vous avez déjà Titelli Pro++ actif",
            "subscription": existing,
            "has_subscription": True
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
                        'description': 'Livraisons B2B, Lifestyle Pass integration, Stock liquidation'
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
                'user_id': current_user["id"]
            }
        )
        
        # Store pending subscription
        subscription = {
            "id": subscription_id,
            "user_id": current_user["id"],
            "enterprise_id": current_user.get("enterprise_id"),
            "business_type": subscription_data.business_type,
            "delivery_frequency": subscription_data.delivery_frequency,
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


@router.get("/pro/features", response_model=dict)
async def get_pro_features():
    """Get Titelli Pro++ features"""
    return {
        "name": "Titelli Pro++",
        "price": TITELLI_PRO_PRICE,
        "currency": "CHF",
        "features": [
            {
                "name": "Livraisons B2B régulières",
                "description": "Livrez vos produits/services aux entreprises clientes de façon récurrente"
            },
            {
                "name": "Intégration Lifestyle Pass",
                "description": "Proposez vos services dans les Lifestyle Passes"
            },
            {
                "name": "Liquidation de stock",
                "description": "Vendez rapidement votre stock excédentaire à prix réduit"
            },
            {
                "name": "Clients entreprises",
                "description": "Accédez au réseau d'entreprises partenaires"
            },
            {
                "name": "Analytics avancés",
                "description": "Suivez vos performances B2B en détail"
            }
        ]
    }


# ============ CATEGORIES ============

@router.get("/categories", response_model=dict)
async def get_specialist_categories():
    """Get specialist categories"""
    categories = [
        {"id": "beaute", "name": "Beauté & Soins", "icon": "sparkles"},
        {"id": "sante", "name": "Santé & Bien-être", "icon": "heart"},
        {"id": "artisanat", "name": "Artisanat", "icon": "hammer"},
        {"id": "restauration", "name": "Restauration", "icon": "utensils"},
        {"id": "mode", "name": "Mode & Style", "icon": "shirt"},
        {"id": "tech", "name": "Tech & Digital", "icon": "laptop"},
        {"id": "education", "name": "Éducation & Formation", "icon": "graduation-cap"},
        {"id": "evenements", "name": "Événements", "icon": "calendar"},
        {"id": "immobilier", "name": "Immobilier", "icon": "home"},
        {"id": "autre", "name": "Autre", "icon": "ellipsis"}
    ]
    return {"categories": categories}
