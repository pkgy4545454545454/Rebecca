"""
Système de Newsletter et Communications
Gestion des abonnements newsletter et envoi de communications
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/api/newsletter", tags=["newsletter"])


class NewsletterSubscribe(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    preferences: Optional[List[str]] = None  # ['promotions', 'news', 'tips']


class NewsletterUnsubscribe(BaseModel):
    email: EmailStr
    reason: Optional[str] = None


@router.post("/subscribe")
async def subscribe_newsletter(data: NewsletterSubscribe):
    """S'abonner à la newsletter"""
    from server import db
    
    # Vérifier si déjà abonné
    existing = db.newsletter_subscribers.find_one({"email": data.email.lower()})
    
    if existing and existing.get("active"):
        return {"success": True, "message": "Vous êtes déjà abonné à notre newsletter"}
    
    subscriber_data = {
        "id": str(uuid.uuid4()),
        "email": data.email.lower(),
        "first_name": data.first_name,
        "preferences": data.preferences or ["promotions", "news", "tips"],
        "active": True,
        "subscribed_at": datetime.now(timezone.utc).isoformat(),
        "source": "website"
    }
    
    if existing:
        db.newsletter_subscribers.update_one(
            {"email": data.email.lower()},
            {"$set": {**subscriber_data, "resubscribed_at": datetime.now(timezone.utc).isoformat()}}
        )
    else:
        db.newsletter_subscribers.insert_one(subscriber_data)
    
    return {
        "success": True,
        "message": "Merci pour votre inscription ! Vous recevrez bientôt nos dernières actualités."
    }


@router.post("/unsubscribe")
async def unsubscribe_newsletter(data: NewsletterUnsubscribe):
    """Se désabonner de la newsletter"""
    from server import db
    
    result = db.newsletter_subscribers.update_one(
        {"email": data.email.lower()},
        {
            "$set": {
                "active": False,
                "unsubscribed_at": datetime.now(timezone.utc).isoformat(),
                "unsubscribe_reason": data.reason
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Email non trouvé dans notre liste")
    
    return {
        "success": True,
        "message": "Vous avez été désabonné de notre newsletter. Vous pouvez vous réabonner à tout moment."
    }


@router.get("/subscribers/count")
async def get_subscribers_count():
    """Nombre d'abonnés (pour stats admin)"""
    from server import db
    
    total = db.newsletter_subscribers.count_documents({})
    active = db.newsletter_subscribers.count_documents({"active": True})
    
    return {
        "total": total,
        "active": active,
        "inactive": total - active
    }


@router.get("/preferences/{email}")
async def get_subscriber_preferences(email: str):
    """Récupère les préférences d'un abonné"""
    from server import db
    
    subscriber = db.newsletter_subscribers.find_one(
        {"email": email.lower()},
        {"_id": 0, "preferences": 1, "active": 1}
    )
    
    if not subscriber:
        raise HTTPException(status_code=404, detail="Abonné non trouvé")
    
    return subscriber


@router.put("/preferences/{email}")
async def update_subscriber_preferences(email: str, preferences: List[str]):
    """Met à jour les préférences d'un abonné"""
    from server import db
    
    valid_preferences = ["promotions", "news", "tips", "weekly_digest"]
    filtered_prefs = [p for p in preferences if p in valid_preferences]
    
    result = db.newsletter_subscribers.update_one(
        {"email": email.lower()},
        {"$set": {"preferences": filtered_prefs}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Abonné non trouvé")
    
    return {"success": True, "preferences": filtered_prefs}
