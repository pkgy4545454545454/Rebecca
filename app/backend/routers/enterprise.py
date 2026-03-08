"""
Enterprise Router - Gestion des entreprises Titelli
Routes pour les profils entreprise, services, produits, avis
"""
from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import logging
import uuid

from .shared import db, get_current_user

router = APIRouter(prefix="/api", tags=["Entreprises"])
logger = logging.getLogger(__name__)


# ============ PYDANTIC MODELS ============

class EnterpriseProfile(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    business_name: str
    name: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = "Lausanne"
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    logo: Optional[str] = None
    cover_image: Optional[str] = None
    opening_hours: Optional[dict] = None
    is_certified: bool = False
    is_labeled: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class EnterpriseCreate(BaseModel):
    business_name: str
    name: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: str = "Lausanne"
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None


class ServiceProductCreate(BaseModel):
    enterprise_id: str
    name: str
    type: str  # "service" or "product"
    description: Optional[str] = None
    price: float
    duration: Optional[int] = None  # minutes for services
    category: Optional[str] = None
    images: Optional[List[str]] = []


class ReviewCreate(BaseModel):
    enterprise_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


# ============ ENTERPRISE ROUTES ============

@router.post("/enterprises")
async def create_enterprise(data: EnterpriseCreate, current_user: dict = Depends(get_current_user)):
    """Create a new enterprise profile"""
    print(f"DEBUG: user_type = {current_user.get('user_type')}, allowed = ['enterprise', 'entreprise', 'admin']")
    if current_user.get("user_type") not in ["enterprise", "entreprise", "admin"]:
        raise HTTPException(status_code=403, detail="Seules les entreprises peuvent créer un profil")
    
    enterprise_id = str(uuid.uuid4())
    enterprise = {
        "id": enterprise_id,
        "user_id": current_user["id"],
        **data.model_dump(),
        "is_certified": False,
        "is_labeled": False,
        "activation_status": "pending",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db.enterprises.insert_one(enterprise)
    enterprise.pop('_id', None)
    
    # Update user with enterprise_id
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"enterprise_id": enterprise_id}}
    )
    
    return enterprise


@router.get("/enterprises")
async def list_enterprises(
    category: Optional[str] = None,
    city: Optional[str] = None,
    search: Optional[str] = None,
    certified_only: bool = False,
    skip: int = 0,
    limit: int = 20
):
    """List enterprises with filters"""
    query = {"activation_status": "active"}
    
    if category:
        query["category"] = category
    if city:
        query["city"] = {"$regex": city, "$options": "i"}
    if certified_only:
        query["is_certified"] = True
    if search:
        query["$or"] = [
            {"business_name": {"$regex": search, "$options": "i"}},
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    enterprises = await db.enterprises.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    total = await db.enterprises.count_documents(query)
    
    return {"enterprises": enterprises, "total": total, "skip": skip, "limit": limit}


@router.get("/enterprises/available")
async def get_available_enterprises(
    search: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """Get available enterprises for registration"""
    query = {
        "$or": [
            {"activation_status": {"$exists": False}},
            {"activation_status": "inactive"},
            {"status": "disponible"}
        ]
    }
    
    if search:
        query["$and"] = [
            {"$or": [
                {"business_name": {"$regex": search, "$options": "i"}},
                {"name": {"$regex": search, "$options": "i"}}
            ]}
        ]
    
    if category:
        query["category"] = category
    
    enterprises = await db.enterprises.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    total = await db.enterprises.count_documents(query)
    
    return {"enterprises": enterprises, "total": total}


@router.get("/enterprises/all-public")
async def get_all_enterprises_public(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None
):
    """Get all public enterprises"""
    query = {}
    if category:
        query["category"] = category
    
    enterprises = await db.enterprises.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    total = await db.enterprises.count_documents(query)
    
    return {"enterprises": enterprises, "total": total}


@router.get("/enterprises/{enterprise_id}")
async def get_enterprise(enterprise_id: str):
    """Get enterprise by ID"""
    enterprise = await db.enterprises.find_one({"id": enterprise_id}, {"_id": 0})
    if not enterprise:
        raise HTTPException(status_code=404, detail="Entreprise non trouvée")
    return enterprise


@router.put("/enterprises/{enterprise_id}")
async def update_enterprise(enterprise_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    """Update enterprise profile"""
    enterprise = await db.enterprises.find_one({"id": enterprise_id})
    if not enterprise:
        raise HTTPException(status_code=404, detail="Entreprise non trouvée")
    
    if enterprise.get("user_id") != current_user["id"] and current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Non autorisé")
    
    data["updated_at"] = datetime.now(timezone.utc)
    await db.enterprises.update_one({"id": enterprise_id}, {"$set": data})
    
    updated = await db.enterprises.find_one({"id": enterprise_id}, {"_id": 0})
    return updated


# ============ SERVICES/PRODUCTS ROUTES ============

@router.post("/services-products")
async def create_service_product(data: ServiceProductCreate, current_user: dict = Depends(get_current_user)):
    """Create a service or product"""
    item_id = str(uuid.uuid4())
    item = {
        "id": item_id,
        **data.model_dump(),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db.services_products.insert_one(item)
    item.pop('_id', None)
    
    return item


@router.get("/services-products")
async def list_services_products(
    enterprise_id: Optional[str] = None,
    type: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """List services and products"""
    query = {}
    if enterprise_id:
        query["enterprise_id"] = enterprise_id
    if type:
        query["type"] = type
    if category:
        query["category"] = category
    
    items = await db.services_products.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    total = await db.services_products.count_documents(query)
    
    return {"items": items, "total": total}


@router.get("/services-products/{item_id}")
async def get_service_product(item_id: str):
    """Get service/product by ID"""
    item = await db.services_products.find_one({"id": item_id}, {"_id": 0})
    if not item:
        raise HTTPException(status_code=404, detail="Service/produit non trouvé")
    return item


@router.put("/services-products/{item_id}")
async def update_service_product(item_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    """Update service/product"""
    item = await db.services_products.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Service/produit non trouvé")
    
    data["updated_at"] = datetime.now(timezone.utc)
    await db.services_products.update_one({"id": item_id}, {"$set": data})
    
    updated = await db.services_products.find_one({"id": item_id}, {"_id": 0})
    return updated


@router.delete("/services-products/{item_id}")
async def delete_service_product(item_id: str, current_user: dict = Depends(get_current_user)):
    """Delete service/product"""
    item = await db.services_products.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Service/produit non trouvé")
    
    await db.services_products.delete_one({"id": item_id})
    return {"message": "Supprimé avec succès"}


# ============ REVIEWS ROUTES ============

@router.post("/reviews")
async def create_review(data: ReviewCreate, current_user: dict = Depends(get_current_user)):
    """Create a review for an enterprise"""
    # Check enterprise exists
    enterprise = await db.enterprises.find_one({"id": data.enterprise_id})
    if not enterprise:
        raise HTTPException(status_code=404, detail="Entreprise non trouvée")
    
    review_id = str(uuid.uuid4())
    review = {
        "id": review_id,
        "user_id": current_user["id"],
        "user_name": current_user.get("name", current_user.get("email", "").split("@")[0]),
        **data.model_dump(),
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.reviews.insert_one(review)
    review.pop('_id', None)
    
    # Update enterprise average rating
    reviews = await db.reviews.find({"enterprise_id": data.enterprise_id}).to_list(1000)
    if reviews:
        avg_rating = sum(r["rating"] for r in reviews) / len(reviews)
        await db.enterprises.update_one(
            {"id": data.enterprise_id},
            {"$set": {"average_rating": round(avg_rating, 1), "review_count": len(reviews)}}
        )
    
    return review


@router.get("/reviews/{enterprise_id}")
async def get_reviews(enterprise_id: str, limit: int = 50, skip: int = 0):
    """Get reviews for an enterprise"""
    reviews = await db.reviews.find(
        {"enterprise_id": enterprise_id},
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    return {"reviews": reviews, "count": len(reviews)}


# ============ CATEGORIES ROUTES ============

@router.get("/categories/products")
async def get_product_categories():
    """Get product categories"""
    return {"categories": [
        "Mode & Vêtements", "Bijouterie & Montres", "Beauté & Cosmétiques",
        "Alimentation & Vins", "High-Tech", "Maison & Décoration",
        "Sports & Loisirs", "Art & Culture", "Autre"
    ]}


@router.get("/categories/services")
async def get_service_categories():
    """Get service categories"""
    return {"categories": [
        "Coiffure & Beauté", "Bien-être & Spa", "Restaurant & Gastronomie",
        "Fitness & Sport", "Santé", "Éducation & Formation",
        "Services aux entreprises", "Événementiel", "Autre"
    ]}
