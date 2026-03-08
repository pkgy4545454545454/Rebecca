# ============================================
# TITELLI BACKEND - VERSION SIMPLIFIÉE POUR INSTALLATION LOCALE
# ============================================
from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone
import bcrypt
import jwt

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'titelli')]

# JWT Config
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key')
JWT_ALGORITHM = "HS256"

# Create FastAPI app
app = FastAPI(title="Titelli API", version="1.0.0")
api_router = APIRouter(prefix="/api")

# ============ MODELS ============
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    user_type: str = "client"  # "client" or "entreprise"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class EnterpriseCreate(BaseModel):
    business_name: str
    slogan: Optional[str] = None
    description: str
    category: str
    address: str
    phone: str
    email: EmailStr
    website: Optional[str] = None

class ServiceProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    type: str = "service"  # "service" or "product"

class ReviewCreate(BaseModel):
    enterprise_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: str

# ============ CATEGORIES ============
PRODUCT_CATEGORIES = [
    {"id": "courses_alimentaires", "name": "Courses alimentaires"},
    {"id": "vetements_mode", "name": "Vêtements et accessoires de mode"},
    {"id": "electronique", "name": "Appareils électroniques"},
    {"id": "ameublement_deco", "name": "Ameublement et décoration"},
    {"id": "bricolage_jardinage", "name": "Bricolage et jardinage"},
    {"id": "automobiles", "name": "Automobiles"},
    {"id": "sport", "name": "Matériel de sport"},
    {"id": "beaute", "name": "Maquillage et beauté"},
]

SERVICE_CATEGORIES = [
    {"id": "restauration", "name": "Restauration"},
    {"id": "soins_esthetiques", "name": "Soins esthétiques"},
    {"id": "coiffure_barber", "name": "Coiffeur / Barber"},
    {"id": "plombier", "name": "Plombier"},
    {"id": "electricien", "name": "Électricien"},
    {"id": "nettoyage", "name": "Personnel de nettoyage"},
    {"id": "garagiste", "name": "Garagiste"},
    {"id": "expert_tech", "name": "Expert en technologie"},
    {"id": "sante", "name": "Professionnel de la santé"},
]

# ============ HELPER FUNCTIONS ============
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str, user_type: str) -> str:
    payload = {
        "user_id": user_id,
        "user_type": user_type,
        "exp": datetime.now(timezone.utc).timestamp() + 86400 * 7
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="Token invalide")

async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Non authentifié")
    token = authorization.split(" ")[1]
    payload = decode_token(token)
    user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0, "password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user

# ============ AUTH ROUTES ============
@api_router.post("/auth/register")
async def register(user_data: UserCreate):
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    user_id = str(uuid.uuid4())
    user_dict = {
        "id": user_id,
        "email": user_data.email,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "phone": user_data.phone,
        "user_type": user_data.user_type,
        "password": hash_password(user_data.password),
        "cashback_balance": 0.0,
        "is_premium": False,
        "is_certified": False,
        "is_labeled": False,
        "city": "Lausanne",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_dict.copy())
    
    token = create_token(user_id, user_data.user_type)
    del user_dict['password']
    return {"token": token, "user": user_dict}

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user or not verify_password(credentials.password, user['password']):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    token = create_token(user['id'], user['user_type'])
    user_response = {k: v for k, v in user.items() if k != 'password'}
    return {"token": token, "user": user_response}

@api_router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

# ============ ENTERPRISE ROUTES ============
@api_router.post("/enterprises")
async def create_enterprise(data: EnterpriseCreate, current_user: dict = Depends(get_current_user)):
    if current_user['user_type'] != 'entreprise':
        raise HTTPException(status_code=403, detail="Seules les entreprises peuvent créer un profil")
    
    enterprise_id = str(uuid.uuid4())
    enterprise_dict = {
        "id": enterprise_id,
        "user_id": current_user['id'],
        "business_name": data.business_name,
        "slogan": data.slogan,
        "description": data.description,
        "category": data.category,
        "address": data.address,
        "city": "Lausanne",
        "phone": data.phone,
        "email": data.email,
        "website": data.website,
        "is_certified": False,
        "is_labeled": False,
        "is_premium": False,
        "rating": 0.0,
        "review_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.enterprises.insert_one(enterprise_dict.copy())
    return enterprise_dict

@api_router.get("/enterprises")
async def list_enterprises(
    category: Optional[str] = None,
    is_certified: Optional[bool] = None,
    is_labeled: Optional[bool] = None,
    is_premium: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
):
    query = {}
    if category:
        query["category"] = category
    if is_certified is not None:
        query["is_certified"] = is_certified
    if is_labeled is not None:
        query["is_labeled"] = is_labeled
    if is_premium is not None:
        query["is_premium"] = is_premium
    if search:
        query["$or"] = [
            {"business_name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    enterprises = await db.enterprises.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    total = await db.enterprises.count_documents(query)
    return {"enterprises": enterprises, "total": total}

@api_router.get("/enterprises/{enterprise_id}")
async def get_enterprise(enterprise_id: str):
    enterprise = await db.enterprises.find_one({"id": enterprise_id}, {"_id": 0})
    if not enterprise:
        raise HTTPException(status_code=404, detail="Entreprise non trouvée")
    
    services = await db.services_products.find({"enterprise_id": enterprise_id}, {"_id": 0}).to_list(100)
    reviews = await db.reviews.find({"enterprise_id": enterprise_id}, {"_id": 0}).sort("created_at", -1).to_list(50)
    
    return {**enterprise, "services": services, "reviews": reviews}

# ============ SERVICES/PRODUCTS ROUTES ============
@api_router.post("/services-products")
async def create_service_product(data: ServiceProductCreate, current_user: dict = Depends(get_current_user)):
    enterprise = await db.enterprises.find_one({"user_id": current_user['id']})
    if not enterprise:
        raise HTTPException(status_code=404, detail="Créez d'abord un profil entreprise")
    
    item_id = str(uuid.uuid4())
    item_dict = {
        "id": item_id,
        "enterprise_id": enterprise['id'],
        "name": data.name,
        "description": data.description,
        "price": data.price,
        "currency": "CHF",
        "category": data.category,
        "type": data.type,
        "is_available": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.services_products.insert_one(item_dict.copy())
    return item_dict

@api_router.get("/services-products")
async def list_services_products(
    type: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
):
    query = {"is_available": True}
    if type:
        query["type"] = type
    if category:
        query["category"] = category
    
    items = await db.services_products.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    total = await db.services_products.count_documents(query)
    return {"items": items, "total": total}

# ============ REVIEWS ROUTES ============
@api_router.post("/reviews")
async def create_review(data: ReviewCreate, current_user: dict = Depends(get_current_user)):
    review_id = str(uuid.uuid4())
    review_dict = {
        "id": review_id,
        "enterprise_id": data.enterprise_id,
        "user_id": current_user['id'],
        "user_name": f"{current_user['first_name']} {current_user['last_name']}",
        "rating": data.rating,
        "comment": data.comment,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.reviews.insert_one(review_dict.copy())
    
    # Update enterprise rating
    all_reviews = await db.reviews.find({"enterprise_id": data.enterprise_id}).to_list(1000)
    avg_rating = sum(r['rating'] for r in all_reviews) / len(all_reviews)
    await db.enterprises.update_one(
        {"id": data.enterprise_id},
        {"$set": {"rating": round(avg_rating, 1), "review_count": len(all_reviews)}}
    )
    
    return review_dict

# ============ CATEGORIES ROUTES ============
@api_router.get("/categories/products")
async def get_product_categories():
    return PRODUCT_CATEGORIES

@api_router.get("/categories/services")
async def get_service_categories():
    return SERVICE_CATEGORIES

# ============ FEATURED ROUTES ============
@api_router.get("/featured/tendances")
async def get_tendances():
    return await db.enterprises.find({"is_labeled": True}, {"_id": 0}).sort("rating", -1).limit(6).to_list(6)

@api_router.get("/featured/guests")
async def get_guests():
    return await db.enterprises.find({"is_certified": True}, {"_id": 0}).sort("rating", -1).limit(6).to_list(6)

@api_router.get("/featured/offres")
async def get_offres():
    return await db.services_products.find({"is_available": True}, {"_id": 0}).sort("created_at", -1).limit(6).to_list(6)

@api_router.get("/featured/premium")
async def get_premium():
    return await db.enterprises.find({"is_premium": True}, {"_id": 0}).sort("rating", -1).limit(6).to_list(6)

# ============ CASHBACK ============
@api_router.get("/cashback/balance")
async def get_cashback_balance(current_user: dict = Depends(get_current_user)):
    return {"balance": current_user.get('cashback_balance', 0.0)}

# ============ HEALTH & ROOT ============
@api_router.get("/")
async def root():
    return {"message": "Bienvenue sur l'API Titelli", "version": "1.0.0"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include router and add CORS
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ RUN SERVER ============
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
