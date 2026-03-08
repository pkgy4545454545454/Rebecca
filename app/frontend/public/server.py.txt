from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, Header
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import bcrypt
import jwt
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Config
JWT_SECRET = os.environ.get('JWT_SECRET', 'titelli_jwt_secret_key_2024')
JWT_ALGORITHM = "HS256"

# Stripe Config
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')

# Create the main app
app = FastAPI(title="Titelli API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============ MODELS ============

# User Models
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    user_type: str = Field(..., description="'client' or 'entreprise'")

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    cashback_balance: float = 0.0
    is_premium: bool = False
    is_verified: bool = False
    is_certified: bool = False
    is_labeled: bool = False
    profile_image: Optional[str] = None
    address: Optional[str] = None
    city: str = "Lausanne"

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str]
    user_type: str
    cashback_balance: float
    is_premium: bool
    is_verified: bool
    is_certified: bool
    is_labeled: bool
    profile_image: Optional[str]
    city: str

# Enterprise Profile Models
class EnterpriseProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    business_name: str
    slogan: Optional[str] = None
    description: str
    category: str
    subcategory: Optional[str] = None
    address: str
    city: str = "Lausanne"
    phone: str
    email: EmailStr
    website: Optional[str] = None
    logo: Optional[str] = None
    cover_image: Optional[str] = None
    photos: List[str] = []
    videos: List[str] = []
    opening_hours: Optional[Dict[str, str]] = None
    is_certified: bool = False
    is_labeled: bool = False
    is_premium: bool = False
    rating: float = 0.0
    review_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EnterpriseCreate(BaseModel):
    business_name: str
    slogan: Optional[str] = None
    description: str
    category: str
    subcategory: Optional[str] = None
    address: str
    phone: str
    email: EmailStr
    website: Optional[str] = None

# Service/Product Models
class ServiceProduct(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    enterprise_id: str
    name: str
    description: str
    price: float
    currency: str = "CHF"
    category: str
    type: str = Field(..., description="'service' or 'product'")
    images: List[str] = []
    is_available: bool = True
    is_premium: bool = False
    is_delivery: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ServiceProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    type: str
    images: List[str] = []
    is_delivery: bool = False

# Review Models
class Review(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    enterprise_id: str
    user_id: str
    user_name: str
    rating: int = Field(..., ge=1, le=5)
    comment: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ReviewCreate(BaseModel):
    enterprise_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: str

# Order Models
class OrderItem(BaseModel):
    service_product_id: str
    name: str
    price: float
    quantity: int

class Order(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    enterprise_id: str
    items: List[OrderItem]
    total: float
    status: str = "pending"
    payment_status: str = "pending"
    stripe_session_id: Optional[str] = None
    delivery_address: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class OrderCreate(BaseModel):
    enterprise_id: str
    items: List[OrderItem]
    delivery_address: Optional[str] = None
    notes: Optional[str] = None

# Subscription Plans
SUBSCRIPTION_PLANS = {
    "annual": {"name": "Abonnement Annuel", "price": 250.0, "duration_months": 12},
    "premium_annual": {"name": "Premium Annuel", "price": 540.0, "duration_months": 12},
    "premium_monthly": {"name": "Premium Mensuel", "price": 45.0, "duration_months": 1},
}

# Advertising Plans
AD_PLANS = {
    "pub_flash_offres": {"name": "Pub Flash - Offres du moment", "min_price": 10.0, "max_price": 1000.0},
    "pub_flash_certifies": {"name": "Pub Flash - Certifiés", "min_price": 20.0, "max_price": 1000.0},
    "pub_flash_labellises": {"name": "Pub Flash - Labellisés", "min_price": 30.0, "max_price": 2000.0},
    "pub_flash_domaine": {"name": "Pub Flash - Son domaine", "min_price": 10.0, "max_price": 1000.0},
    "pub_flash_guests": {"name": "Pub Flash - Guests", "min_price": 10.0, "max_price": 1000.0},
    "pub_flash_tendances": {"name": "Pub Flash - Tendances actuelles", "min_price": 20.0, "max_price": 1000.0},
    "pub_expert_standard": {"name": "Pub Expert Standard", "price": 300.0, "duration": "annual"},
    "pub_expert_premium": {"name": "Pub Expert Premium", "price": 1000.0, "duration": "annual"},
    "pub_referencement": {"name": "Pub Référencement", "min_price": 10.0, "max_price": 1000.0},
}

# Categories
PRODUCT_CATEGORIES = [
    {"id": "courses_alimentaires", "name": "Courses alimentaires", "icon": "shopping-cart"},
    {"id": "vetements_mode", "name": "Vêtements et accessoires de mode", "icon": "shirt"},
    {"id": "enfant", "name": "Tout pour mon enfant", "icon": "baby"},
    {"id": "soins", "name": "Matériel de soins", "icon": "heart"},
    {"id": "maquillage_beaute", "name": "Maquillage et beauté", "icon": "sparkles"},
    {"id": "sport", "name": "Matériel de sport", "icon": "dumbbell"},
    {"id": "loisirs", "name": "Matériel de loisirs", "icon": "gamepad-2"},
    {"id": "voyages", "name": "Nécessaire voyages", "icon": "plane"},
    {"id": "electronique", "name": "Appareils électroniques", "icon": "smartphone"},
    {"id": "bureautique", "name": "Matériel de bureautique", "icon": "printer"},
    {"id": "electromenager", "name": "Appareils électroménager", "icon": "refrigerator"},
    {"id": "ameublement_deco", "name": "Ameublement et décoration d'intérieur", "icon": "sofa"},
    {"id": "artisanal", "name": "Matériel artisanal", "icon": "hammer"},
    {"id": "bricolage_jardinage", "name": "Matériel de bricolage et jardinage", "icon": "wrench"},
    {"id": "immobilier", "name": "Acheter un bien immobilier", "icon": "home"},
    {"id": "automobiles", "name": "Automobiles", "icon": "car"},
    {"id": "securite", "name": "Matériel de sécurité", "icon": "shield"},
    {"id": "animaux", "name": "Matériel animaux", "icon": "paw-print"},
    {"id": "professionnel", "name": "Matériel professionnel", "icon": "briefcase"},
    {"id": "metaux_precieux", "name": "Métaux précieux et matières premières", "icon": "gem"},
    {"id": "haute_joaillerie", "name": "Haute joaillerie", "icon": "crown"},
    {"id": "montres", "name": "Montres", "icon": "watch"},
]

SERVICE_CATEGORIES = [
    {"id": "restauration", "name": "Restauration", "icon": "utensils"},
    {"id": "soins_esthetiques", "name": "Soins esthétiques", "icon": "sparkles"},
    {"id": "coiffure_barber", "name": "Visagiste, coiffeur ou barber", "icon": "scissors"},
    {"id": "cours_sport", "name": "Cours de sport", "icon": "dumbbell"},
    {"id": "activites_loisirs", "name": "Activités, Loisirs et Évènements", "icon": "calendar"},
    {"id": "nettoyage", "name": "Personnel de nettoyage", "icon": "spray-can"},
    {"id": "multiservices", "name": "Agent multiservices", "icon": "wrench"},
    {"id": "petits_travaux", "name": "Spécialiste petits travaux", "icon": "hammer"},
    {"id": "garagiste", "name": "Garagiste", "icon": "car"},
    {"id": "plombier", "name": "Plombier", "icon": "droplet"},
    {"id": "serrurier", "name": "Serrurier", "icon": "key"},
    {"id": "electricien", "name": "Électricien", "icon": "zap"},
    {"id": "formation", "name": "Formation maintenant", "icon": "graduation-cap"},
    {"id": "emploi", "name": "Emploi maintenant", "icon": "briefcase"},
    {"id": "sante", "name": "Professionnel de la santé", "icon": "stethoscope"},
    {"id": "voyages", "name": "Les meilleurs voyages", "icon": "plane"},
    {"id": "agent_immobilier", "name": "Agent immobilier", "icon": "home"},
    {"id": "expert_tech", "name": "Expert en technologie", "icon": "laptop"},
    {"id": "agent_securite", "name": "Agent de sécurité", "icon": "shield"},
    {"id": "expert_fiscal", "name": "Expert fiscal", "icon": "calculator"},
    {"id": "expert_juridique", "name": "Expert juridique", "icon": "scale"},
    {"id": "gestion_admin", "name": "Professionnel en gestion administrative", "icon": "file-text"},
    {"id": "construction", "name": "Professionnel de la construction", "icon": "building"},
    {"id": "autres_maison", "name": "Professionnels autres de maison", "icon": "home"},
    {"id": "veterinaire", "name": "Vétérinaire", "icon": "paw-print"},
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
        "exp": datetime.now(timezone.utc).timestamp() + 86400 * 7  # 7 days
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
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
    
    user = User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        user_type=user_data.user_type
    )
    user_dict = user.model_dump()
    user_dict['password'] = hash_password(user_data.password)
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    
    await db.users.insert_one(user_dict)
    
    token = create_token(user.id, user.user_type)
    return {"token": token, "user": UserResponse(**user_dict)}

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
    
    existing = await db.enterprises.find_one({"user_id": current_user['id']})
    if existing:
        raise HTTPException(status_code=400, detail="Profil entreprise déjà existant")
    
    enterprise = EnterpriseProfile(
        user_id=current_user['id'],
        **data.model_dump()
    )
    enterprise_dict = enterprise.model_dump()
    enterprise_dict['created_at'] = enterprise_dict['created_at'].isoformat()
    
    # Insert and return without _id
    insert_doc = enterprise_dict.copy()
    await db.enterprises.insert_one(insert_doc)
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
    
    # Get services/products
    services = await db.services_products.find({"enterprise_id": enterprise_id}, {"_id": 0}).to_list(100)
    
    # Get reviews
    reviews = await db.reviews.find({"enterprise_id": enterprise_id}, {"_id": 0}).sort("created_at", -1).to_list(50)
    
    return {**enterprise, "services": services, "reviews": reviews}

@api_router.put("/enterprises/{enterprise_id}")
async def update_enterprise(enterprise_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    enterprise = await db.enterprises.find_one({"id": enterprise_id})
    if not enterprise:
        raise HTTPException(status_code=404, detail="Entreprise non trouvée")
    if enterprise['user_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Non autorisé")
    
    data.pop('id', None)
    data.pop('user_id', None)
    data.pop('created_at', None)
    
    await db.enterprises.update_one({"id": enterprise_id}, {"$set": data})
    return {"message": "Profil mis à jour"}

# ============ SERVICES/PRODUCTS ROUTES ============

@api_router.post("/services-products")
async def create_service_product(data: ServiceProductCreate, current_user: dict = Depends(get_current_user)):
    enterprise = await db.enterprises.find_one({"user_id": current_user['id']})
    if not enterprise:
        raise HTTPException(status_code=404, detail="Créez d'abord un profil entreprise")
    
    item = ServiceProduct(
        enterprise_id=enterprise['id'],
        **data.model_dump()
    )
    item_dict = item.model_dump()
    item_dict['created_at'] = item_dict['created_at'].isoformat()
    
    insert_doc = item_dict.copy()
    await db.services_products.insert_one(insert_doc)
    return item_dict

@api_router.get("/services-products")
async def list_services_products(
    type: Optional[str] = None,
    category: Optional[str] = None,
    enterprise_id: Optional[str] = None,
    is_premium: Optional[bool] = None,
    limit: int = 50,
    skip: int = 0
):
    query = {"is_available": True}
    if type:
        query["type"] = type
    if category:
        query["category"] = category
    if enterprise_id:
        query["enterprise_id"] = enterprise_id
    if is_premium is not None:
        query["is_premium"] = is_premium
    
    items = await db.services_products.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    total = await db.services_products.count_documents(query)
    return {"items": items, "total": total}

@api_router.get("/services-products/{item_id}")
async def get_service_product(item_id: str):
    item = await db.services_products.find_one({"id": item_id}, {"_id": 0})
    if not item:
        raise HTTPException(status_code=404, detail="Service/Produit non trouvé")
    return item

@api_router.put("/services-products/{item_id}")
async def update_service_product(item_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    item = await db.services_products.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Service/Produit non trouvé")
    
    enterprise = await db.enterprises.find_one({"id": item['enterprise_id']})
    if enterprise['user_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Non autorisé")
    
    data.pop('id', None)
    data.pop('enterprise_id', None)
    data.pop('created_at', None)
    
    await db.services_products.update_one({"id": item_id}, {"$set": data})
    return {"message": "Mis à jour avec succès"}

@api_router.delete("/services-products/{item_id}")
async def delete_service_product(item_id: str, current_user: dict = Depends(get_current_user)):
    item = await db.services_products.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Service/Produit non trouvé")
    
    enterprise = await db.enterprises.find_one({"id": item['enterprise_id']})
    if enterprise['user_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Non autorisé")
    
    await db.services_products.delete_one({"id": item_id})
    return {"message": "Supprimé avec succès"}

# ============ REVIEWS ROUTES ============

@api_router.post("/reviews")
async def create_review(data: ReviewCreate, current_user: dict = Depends(get_current_user)):
    enterprise = await db.enterprises.find_one({"id": data.enterprise_id})
    if not enterprise:
        raise HTTPException(status_code=404, detail="Entreprise non trouvée")
    
    review = Review(
        enterprise_id=data.enterprise_id,
        user_id=current_user['id'],
        user_name=f"{current_user['first_name']} {current_user['last_name']}",
        rating=data.rating,
        comment=data.comment
    )
    review_dict = review.model_dump()
    review_dict['created_at'] = review_dict['created_at'].isoformat()
    
    insert_doc = review_dict.copy()
    await db.reviews.insert_one(insert_doc)
    
    # Update enterprise rating
    all_reviews = await db.reviews.find({"enterprise_id": data.enterprise_id}).to_list(1000)
    avg_rating = sum(r['rating'] for r in all_reviews) / len(all_reviews)
    await db.enterprises.update_one(
        {"id": data.enterprise_id},
        {"$set": {"rating": round(avg_rating, 1), "review_count": len(all_reviews)}}
    )
    
    return review_dict

@api_router.get("/reviews/{enterprise_id}")
async def get_reviews(enterprise_id: str, limit: int = 50, skip: int = 0):
    reviews = await db.reviews.find(
        {"enterprise_id": enterprise_id}, {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return reviews

# ============ ORDERS ROUTES ============

@api_router.post("/orders")
async def create_order(data: OrderCreate, current_user: dict = Depends(get_current_user)):
    total = sum(item.price * item.quantity for item in data.items)
    
    order = Order(
        user_id=current_user['id'],
        enterprise_id=data.enterprise_id,
        items=[item.model_dump() for item in data.items],
        total=total,
        delivery_address=data.delivery_address,
        notes=data.notes
    )
    order_dict = order.model_dump()
    order_dict['created_at'] = order_dict['created_at'].isoformat()
    
    insert_doc = order_dict.copy()
    await db.orders.insert_one(insert_doc)
    return order_dict

@api_router.get("/orders")
async def get_orders(current_user: dict = Depends(get_current_user)):
    if current_user['user_type'] == 'entreprise':
        enterprise = await db.enterprises.find_one({"user_id": current_user['id']})
        if enterprise:
            orders = await db.orders.find({"enterprise_id": enterprise['id']}, {"_id": 0}).sort("created_at", -1).to_list(100)
        else:
            orders = []
    else:
        orders = await db.orders.find({"user_id": current_user['id']}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return orders

@api_router.put("/orders/{order_id}/status")
async def update_order_status(order_id: str, status: str, current_user: dict = Depends(get_current_user)):
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    await db.orders.update_one({"id": order_id}, {"$set": {"status": status}})
    return {"message": "Statut mis à jour"}

# ============ PAYMENT ROUTES ============

@api_router.post("/payments/checkout")
async def create_checkout(
    request: Request,
    package_type: str,
    amount: Optional[float] = None,
    current_user: dict = Depends(get_current_user)
):
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    # Determine amount based on package
    if package_type in SUBSCRIPTION_PLANS:
        final_amount = SUBSCRIPTION_PLANS[package_type]['price']
        metadata = {"type": "subscription", "plan": package_type, "user_id": current_user['id']}
    elif package_type in AD_PLANS:
        if amount is None:
            raise HTTPException(status_code=400, detail="Montant requis pour ce type de publicité")
        plan = AD_PLANS[package_type]
        if 'price' in plan:
            final_amount = plan['price']
        else:
            if amount < plan['min_price'] or amount > plan['max_price']:
                raise HTTPException(status_code=400, detail=f"Montant doit être entre {plan['min_price']} et {plan['max_price']} CHF")
            final_amount = amount
        metadata = {"type": "advertising", "plan": package_type, "user_id": current_user['id']}
    elif package_type == "order":
        if amount is None:
            raise HTTPException(status_code=400, detail="Montant requis")
        final_amount = amount
        metadata = {"type": "order", "user_id": current_user['id']}
    else:
        raise HTTPException(status_code=400, detail="Type de package invalide")
    
    # Get frontend origin from referer or use base_url
    origin = request.headers.get('origin', host_url.replace('/api', ''))
    success_url = f"{origin}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin}/payment/cancel"
    
    checkout_request = CheckoutSessionRequest(
        amount=float(final_amount),
        currency="chf",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    # Store transaction
    transaction = {
        "id": str(uuid.uuid4()),
        "session_id": session.session_id,
        "user_id": current_user['id'],
        "amount": final_amount,
        "currency": "CHF",
        "type": package_type,
        "metadata": metadata,
        "payment_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.payment_transactions.insert_one(transaction)
    
    return {"url": session.url, "session_id": session.session_id}

@api_router.get("/payments/status/{session_id}")
async def get_payment_status(session_id: str, request: Request):
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    status = await stripe_checkout.get_checkout_status(session_id)
    
    # Update transaction status
    transaction = await db.payment_transactions.find_one({"session_id": session_id})
    if transaction and transaction['payment_status'] != status.payment_status:
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {"payment_status": status.payment_status, "status": status.status}}
        )
        
        # If payment successful, apply benefits
        if status.payment_status == "paid" and transaction['payment_status'] != "paid":
            metadata = transaction.get('metadata', {})
            user_id = metadata.get('user_id')
            
            if metadata.get('type') == 'subscription':
                plan = metadata.get('plan')
                is_premium = 'premium' in plan
                await db.users.update_one(
                    {"id": user_id},
                    {"$set": {"is_premium": is_premium, "is_verified": True}}
                )
    
    return {
        "status": status.status,
        "payment_status": status.payment_status,
        "amount_total": status.amount_total,
        "currency": status.currency
    }

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("Stripe-Signature")
    
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        logger.info(f"Webhook received: {webhook_response.event_type}")
        
        if webhook_response.payment_status == "paid":
            await db.payment_transactions.update_one(
                {"session_id": webhook_response.session_id},
                {"$set": {"payment_status": "paid", "status": "complete"}}
            )
        
        return {"received": True}
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return {"received": True}

# ============ CATEGORIES ROUTES ============

@api_router.get("/categories/products")
async def get_product_categories():
    return PRODUCT_CATEGORIES

@api_router.get("/categories/services")
async def get_service_categories():
    return SERVICE_CATEGORIES

# ============ ADMIN ROUTES ============

@api_router.get("/admin/stats")
async def get_admin_stats(current_user: dict = Depends(get_current_user)):
    # Simple admin check (in production, use proper role system)
    if current_user.get('email') != 'admin@titelli.com':
        raise HTTPException(status_code=403, detail="Admin uniquement")
    
    total_users = await db.users.count_documents({})
    total_enterprises = await db.enterprises.count_documents({})
    total_orders = await db.orders.count_documents({})
    total_reviews = await db.reviews.count_documents({})
    
    recent_users = await db.users.find({}, {"_id": 0, "password": 0}).sort("created_at", -1).limit(10).to_list(10)
    recent_orders = await db.orders.find({}, {"_id": 0}).sort("created_at", -1).limit(10).to_list(10)
    
    return {
        "stats": {
            "total_users": total_users,
            "total_enterprises": total_enterprises,
            "total_orders": total_orders,
            "total_reviews": total_reviews
        },
        "recent_users": recent_users,
        "recent_orders": recent_orders
    }

@api_router.get("/admin/users")
async def get_all_users(current_user: dict = Depends(get_current_user), limit: int = 100, skip: int = 0):
    if current_user.get('email') != 'admin@titelli.com':
        raise HTTPException(status_code=403, detail="Admin uniquement")
    
    users = await db.users.find({}, {"_id": 0, "password": 0}).skip(skip).limit(limit).to_list(limit)
    total = await db.users.count_documents({})
    return {"users": users, "total": total}

@api_router.put("/admin/users/{user_id}/verify")
async def verify_user(user_id: str, is_certified: bool = False, is_labeled: bool = False, current_user: dict = Depends(get_current_user)):
    if current_user.get('email') != 'admin@titelli.com':
        raise HTTPException(status_code=403, detail="Admin uniquement")
    
    update_data = {"is_verified": True}
    if is_certified:
        update_data["is_certified"] = True
    if is_labeled:
        update_data["is_labeled"] = True
    
    await db.users.update_one({"id": user_id}, {"$set": update_data})
    
    # Also update enterprise if exists
    await db.enterprises.update_one(
        {"user_id": user_id},
        {"$set": {"is_certified": is_certified, "is_labeled": is_labeled}}
    )
    
    return {"message": "Utilisateur vérifié"}

# ============ CASHBACK ROUTES ============

@api_router.get("/cashback/balance")
async def get_cashback_balance(current_user: dict = Depends(get_current_user)):
    return {"balance": current_user.get('cashback_balance', 0.0)}

@api_router.post("/cashback/add")
async def add_cashback(user_id: str, amount: float, current_user: dict = Depends(get_current_user)):
    # Only admin or system can add cashback
    if current_user.get('email') != 'admin@titelli.com':
        raise HTTPException(status_code=403, detail="Non autorisé")
    
    await db.users.update_one(
        {"id": user_id},
        {"$inc": {"cashback_balance": amount}}
    )
    return {"message": f"Cashback de {amount} CHF ajouté"}

# ============ FEATURED/TRENDING ROUTES ============

@api_router.get("/featured/tendances")
async def get_tendances():
    enterprises = await db.enterprises.find(
        {"is_labeled": True}, {"_id": 0}
    ).sort("rating", -1).limit(6).to_list(6)
    return enterprises

@api_router.get("/featured/guests")
async def get_guests():
    enterprises = await db.enterprises.find(
        {"is_certified": True}, {"_id": 0}
    ).sort("rating", -1).limit(6).to_list(6)
    return enterprises

@api_router.get("/featured/offres")
async def get_offres():
    items = await db.services_products.find(
        {"is_available": True}, {"_id": 0}
    ).sort("created_at", -1).limit(6).to_list(6)
    return items

@api_router.get("/featured/premium")
async def get_premium():
    enterprises = await db.enterprises.find(
        {"is_premium": True}, {"_id": 0}
    ).sort("rating", -1).limit(6).to_list(6)
    return enterprises

# ============ ROOT ROUTE ============

@api_router.get("/")
async def root():
    return {"message": "Bienvenue sur l'API Titelli", "version": "1.0.0"}

# ============ HEALTH CHECK ============

@api_router.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
