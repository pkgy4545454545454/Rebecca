"""
Video Pub Router - Système de commande de vidéos publicitaires IA
- Templates vidéo (15-30 secondes)
- Personnalisation texte/couleurs
- Génération via Sora 2
- Temps estimé: ~1 heure
- Paiement Stripe avant téléchargement
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import os
import logging
import asyncio
import time

from dotenv import load_dotenv
load_dotenv()

# Official OpenAI SDK for Sora 2 video generation
from openai import OpenAI

# Email service
from services.email_service import send_email

# Official Stripe SDK for payments
import stripe

router = APIRouter(prefix="/api/video-pub", tags=["Video Pub"])
logger = logging.getLogger(__name__)

# MongoDB connection (will be set from server.py)
db = None

def set_db(database):
    global db
    db = database

# Configuration
# On deployment (OnRender): Use OPENAI_API_KEY from environment
# On Emergent preview: EMERGENT_LLM_KEY is available but requires emergentintegrations
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")

# Use relative path for uploads to work on both Emergent and OnRender
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOADS_DIR = os.path.join(BACKEND_DIR, "uploads", "video_orders")
BASE_URL = os.getenv("REACT_APP_BACKEND_URL", "https://image-fix-demo.preview.emergentagent.com")

# Créer le dossier si nécessaire (avec gestion d'erreur pour les environnements restreints)
try:
    os.makedirs(UPLOADS_DIR, exist_ok=True)
except PermissionError:
    # Sur certains environnements comme Render, utiliser un dossier temporaire
    import tempfile
    UPLOADS_DIR = os.path.join(tempfile.gettempdir(), "video_orders")
    os.makedirs(UPLOADS_DIR, exist_ok=True)


# ============ VIDEO TEMPLATES ============

VIDEO_TEMPLATES = [
    # Réseaux Sociaux - Instagram/TikTok
    {
        "id": "social_reel_1",
        "name": "Instagram Reel - Produit",
        "category": "Réseaux Sociaux",
        "subcategory": "Instagram Reels",
        "description": "Vidéo verticale dynamique pour présenter un produit",
        "preview_image": "https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0?w=400",
        "duration": 15,
        "size": "1024x1792",
        "price": 199.90,
        "prompt_template": "Professional product showcase video, {product_name}, {style}, dynamic camera movements, luxury feel, {colors} color scheme, modern aesthetic, no text overlays"
    },
    {
        "id": "social_reel_2",
        "name": "TikTok - Tendance",
        "category": "Réseaux Sociaux",
        "subcategory": "TikTok",
        "description": "Vidéo courte style TikTok pour engagement",
        "preview_image": "https://images.unsplash.com/photo-1611162618071-b39a2ec055fb?w=400",
        "duration": 8,
        "size": "1024x1792",
        "price": 149.90,
        "prompt_template": "Trendy TikTok style video, {product_name}, fast cuts, engaging visuals, {style}, vibrant {colors} colors, youth appeal, energetic"
    },
    {
        "id": "social_story",
        "name": "Story Animée",
        "category": "Réseaux Sociaux",
        "subcategory": "Stories",
        "description": "Story Instagram/Facebook avec animations",
        "preview_image": "https://images.unsplash.com/photo-1611162616475-46b635cb6868?w=400",
        "duration": 8,
        "size": "1024x1792",
        "price": 129.90,
        "prompt_template": "Instagram story style video, {product_name}, smooth animations, {style} aesthetic, {colors} palette, clean modern look"
    },
    
    # Publicités Professionnelles
    {
        "id": "ad_hero",
        "name": "Pub Hero - Premium",
        "category": "Publicités",
        "subcategory": "Hero Ads",
        "description": "Vidéo publicitaire premium pour site web",
        "preview_image": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400",
        "duration": 15,
        "size": "1792x1024",
        "price": 249.90,
        "prompt_template": "Premium cinematic advertisement video, {product_name}, professional quality, {style} mood, elegant {colors} color grading, high-end brand feel, smooth camera work"
    },
    {
        "id": "ad_product",
        "name": "Spot Produit 30s",
        "category": "Publicités",
        "subcategory": "Spots TV",
        "description": "Spot publicitaire professionnel format TV",
        "preview_image": "https://images.unsplash.com/photo-1551650975-87deedd944c3?w=400",
        "duration": 12,
        "size": "1792x1024",
        "price": 299.90,
        "prompt_template": "Television commercial style video, {product_name}, broadcast quality, {style}, compelling visuals, {colors} brand colors, professional lighting"
    },
    {
        "id": "ad_teaser",
        "name": "Teaser Lancement",
        "category": "Publicités",
        "subcategory": "Teasers",
        "description": "Teaser mystérieux pour lancement produit",
        "preview_image": "https://images.unsplash.com/photo-1536240478700-b869070f9279?w=400",
        "duration": 8,
        "size": "1280x720",
        "price": 179.90,
        "prompt_template": "Mysterious teaser video, {product_name} reveal, suspenseful {style} mood, dramatic {colors} lighting, building anticipation, cinematic"
    },
    
    # Restauration
    {
        "id": "resto_menu",
        "name": "Menu Vidéo",
        "category": "Restauration",
        "subcategory": "Menus",
        "description": "Présentation vidéo des plats du menu",
        "preview_image": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400",
        "duration": 15,
        "size": "1280x720",
        "price": 199.90,
        "prompt_template": "Food menu showcase video, {product_name}, appetizing close-ups, {style} restaurant ambiance, warm {colors} tones, culinary excellence"
    },
    {
        "id": "resto_ambiance",
        "name": "Ambiance Restaurant",
        "category": "Restauration",
        "subcategory": "Ambiance",
        "description": "Vidéo d'ambiance pour restaurant/bar",
        "preview_image": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400",
        "duration": 12,
        "size": "1792x1024",
        "price": 219.90,
        "prompt_template": "Restaurant ambiance video, {product_name}, cozy atmosphere, {style} interior, {colors} warm lighting, inviting dining experience"
    },
    
    # Services & Entreprises
    {
        "id": "corp_intro",
        "name": "Présentation Entreprise",
        "category": "Corporate",
        "subcategory": "Présentations",
        "description": "Vidéo de présentation d'entreprise",
        "preview_image": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=400",
        "duration": 15,
        "size": "1792x1024",
        "price": 249.90,
        "prompt_template": "Corporate introduction video, {product_name} company, professional {style}, modern office environment, {colors} brand identity, trust and excellence"
    },
    {
        "id": "service_showcase",
        "name": "Vitrine Services",
        "category": "Corporate",
        "subcategory": "Services",
        "description": "Présentation de vos services en vidéo",
        "preview_image": "https://images.unsplash.com/photo-1556761175-b413da4baf72?w=400",
        "duration": 12,
        "size": "1280x720",
        "price": 199.90,
        "prompt_template": "Service showcase video, {product_name}, professional demonstration, {style} approach, {colors} consistent branding, customer focus"
    },
    
    # Événements
    {
        "id": "event_promo",
        "name": "Promo Événement",
        "category": "Événements",
        "subcategory": "Promotions",
        "description": "Vidéo promotionnelle pour événement",
        "preview_image": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=400",
        "duration": 15,
        "size": "1280x720",
        "price": 219.90,
        "prompt_template": "Event promotion video, {product_name}, exciting {style} atmosphere, {colors} event branding, dynamic energy, invitation appeal"
    },
    {
        "id": "event_countdown",
        "name": "Compte à Rebours",
        "category": "Événements",
        "subcategory": "Countdowns",
        "description": "Vidéo compte à rebours avant événement",
        "preview_image": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=400",
        "duration": 8,
        "size": "1024x1024",
        "price": 149.90,
        "prompt_template": "Countdown video, {product_name} event, building excitement, {style} aesthetic, {colors} theme, anticipation and hype"
    },
    
    # Sur Mesure
    {
        "id": "sur_mesure",
        "name": "Création Sur Mesure",
        "category": "Sur Mesure",
        "subcategory": "Custom",
        "description": "Vidéo entièrement personnalisée selon vos besoins",
        "preview_image": "https://images.unsplash.com/photo-1626785774573-4b799315345d?w=400",
        "duration": 15,
        "size": "1280x720",
        "price": 399.90,
        "prompt_template": "{custom_prompt}"
    }
]


# ============ PYDANTIC MODELS ============

class VideoOrderCreate(BaseModel):
    template_id: str
    enterprise_id: str
    product_name: str
    slogan: Optional[str] = ""
    description: Optional[str] = ""
    style: Optional[str] = "moderne et élégant"
    brand_colors: Optional[List[str]] = ["#F59E0B", "#FFFFFF"]
    custom_prompt: Optional[str] = ""  # Pour sur mesure
    additional_notes: Optional[str] = ""


class PaymentRequest(BaseModel):
    order_id: str
    origin_url: str


# ============ ENDPOINTS ============

@router.get("/templates")
async def get_video_templates():
    """Récupérer tous les templates vidéo disponibles"""
    categories = {}
    for t in VIDEO_TEMPLATES:
        cat = t["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(t)
    
    return {
        "templates": VIDEO_TEMPLATES,
        "by_category": categories,
        "categories": list(categories.keys()),
        "total": len(VIDEO_TEMPLATES)
    }


@router.get("/templates/{template_id}")
async def get_video_template(template_id: str):
    """Récupérer un template spécifique"""
    template = next((t for t in VIDEO_TEMPLATES if t["id"] == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template non trouvé")
    return template


@router.post("/orders")
async def create_video_order(order_data: VideoOrderCreate, background_tasks: BackgroundTasks):
    """Créer une commande de vidéo publicitaire"""
    
    # Trouver le template
    template = next((t for t in VIDEO_TEMPLATES if t["id"] == order_data.template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template non trouvé")
    
    order_id = str(uuid.uuid4())[:8]
    
    # Construire le prompt
    if order_data.template_id == "sur_mesure":
        final_prompt = order_data.custom_prompt or f"Professional video for {order_data.product_name}"
    else:
        colors_str = " and ".join(order_data.brand_colors[:2]) if order_data.brand_colors else "gold and white"
        final_prompt = template["prompt_template"].format(
            product_name=order_data.product_name,
            style=order_data.style or "modern and elegant",
            colors=colors_str
        )
    
    # Créer la commande
    order = {
        "id": order_id,
        "template_id": order_data.template_id,
        "template_name": template["name"],
        "enterprise_id": order_data.enterprise_id,
        "product_name": order_data.product_name,
        "slogan": order_data.slogan,
        "description": order_data.description,
        "style": order_data.style,
        "brand_colors": order_data.brand_colors,
        "custom_prompt": order_data.custom_prompt,
        "additional_notes": order_data.additional_notes,
        "final_prompt": final_prompt,
        "duration": template["duration"],
        "size": template["size"],
        "price": template["price"],
        "status": "pending_payment",  # Attente paiement
        "payment_status": "pending",
        "video_url": None,
        "preview_url": None,
        "estimated_time": "~1 heure",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.video_orders.insert_one(order)
    
    logger.info(f"📹 Video order created: {order_id} - {template['name']}")
    
    return {
        "id": order_id,
        "status": "pending_payment",
        "template": template["name"],
        "price": template["price"],
        "estimated_time": "~1 heure",
        "message": "Commande créée. Procédez au paiement pour lancer la génération."
    }


@router.get("/orders/{order_id}")
async def get_video_order(order_id: str):
    """Récupérer le statut d'une commande"""
    order = await db.video_orders.find_one({"id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    return order


@router.get("/orders/enterprise/{enterprise_id}")
async def get_enterprise_video_orders(enterprise_id: str, limit: int = 20):
    """Récupérer toutes les commandes vidéo d'une entreprise"""
    cursor = db.video_orders.find(
        {"enterprise_id": enterprise_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit)
    
    orders = await cursor.to_list(limit)
    return {"orders": orders, "total": len(orders)}


# ============ STRIPE PAYMENT ============

@router.post("/payment/create-session")
async def create_payment_session(payment_request: PaymentRequest):
    """Créer une session Stripe pour payer la vidéo"""
    
    order = await db.video_orders.find_one({"id": payment_request.order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    if order.get("payment_status") == "paid":
        raise HTTPException(status_code=400, detail="Cette commande a déjà été payée")
    
    price = float(order.get("price", 199.90))
    price_cents = int(price * 100)  # Stripe uses cents
    
    # Configure Stripe
    stripe.api_key = STRIPE_API_KEY
    
    origin_url = payment_request.origin_url.rstrip('/')
    success_url = f"{origin_url}/video-pub/success?session_id={{CHECKOUT_SESSION_ID}}&order_id={payment_request.order_id}"
    cancel_url = f"{origin_url}/video-pub?cancelled=true&order_id={payment_request.order_id}"
    
    try:
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "chf",
                    "product_data": {
                        "name": f"Vidéo Pub IA - {order.get('template_name', 'Création')}",
                        "description": f"Vidéo publicitaire: {order.get('product_name', '')}",
                    },
                    "unit_amount": price_cents,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "order_id": payment_request.order_id,
                "enterprise_id": order.get("enterprise_id", ""),
                "template_name": order.get("template_name", ""),
                "type": "video_pub_order"
            }
        )
        
        # Enregistrer la transaction
        await db.payment_transactions.insert_one({
            "id": str(uuid.uuid4()),
            "session_id": session.id,
            "order_id": payment_request.order_id,
            "amount": price,
            "currency": "CHF",
            "type": "video_pub",
            "payment_status": "pending",
            "enterprise_id": order.get("enterprise_id"),
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        await db.video_orders.update_one(
            {"id": payment_request.order_id},
            {"$set": {"stripe_session_id": session.id}}
        )
        
        return {
            "checkout_url": session.url,
            "session_id": session.id
        }
        
    except Exception as e:
        logger.error(f"Stripe session error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur Stripe: {str(e)}")


@router.get("/payment/status/{session_id}")
async def check_payment_status(session_id: str, order_id: str, background_tasks: BackgroundTasks):
    """Vérifier le statut du paiement et lancer la génération si payé"""
    
    stripe.api_key = STRIPE_API_KEY
    
    try:
        # Retrieve session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == "paid":
            # Vérifier si déjà traité
            order = await db.video_orders.find_one({"id": order_id})
            if order and order.get("payment_status") == "paid":
                return {
                    "status": "paid",
                    "message": "Paiement confirmé. Génération en cours.",
                    "order_id": order_id
                }
            
            # Marquer comme payé
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {"payment_status": "paid", "paid_at": datetime.now(timezone.utc).isoformat()}}
            )
            
            await db.video_orders.update_one(
                {"id": order_id},
                {"$set": {
                    "payment_status": "paid",
                    "status": "generating",
                    "paid_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            # Lancer la génération en arrière-plan
            background_tasks.add_task(generate_video_async, order_id)
            
            # Notification
            if order:
                await db.notifications.insert_one({
                    "id": str(uuid.uuid4()),
                    "user_id": order.get("user_id"),
                    "type": "video_order_paid",
                    "title": "Paiement confirmé - Vidéo Pub IA",
                    "message": f"Votre vidéo #{order_id} est en cours de génération. Temps estimé: ~1 heure.",
                    "link": "/dashboard/entreprise?tab=videos-titelli",
                    "is_read": False,
                    "created_at": datetime.now(timezone.utc).isoformat()
                })
            
            logger.info(f"✅ Payment confirmed, starting video generation for {order_id}")
            
            return {
                "status": "paid",
                "message": "Paiement confirmé ! Génération vidéo lancée (~1 heure).",
                "order_id": order_id
            }
        
        return {
            "status": session.payment_status or "unpaid",
            "message": "Paiement en attente",
            "order_id": order_id
        }
        
    except Exception as e:
        logger.error(f"Payment status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ VIDEO GENERATION ============

def wait_for_video_completion(client, video_id: str, poll_interval: int = 10, timeout: int = 900):
    """Poll for video completion status"""
    elapsed = 0
    while elapsed < timeout:
        job = client.videos.retrieve(video_id)
        status = job.status
        progress = getattr(job, 'progress', 0)
        logger.info(f"📹 Video {video_id}: Status={status}, Progress={progress}%")
        
        if status == "completed":
            return job
        if status == "failed":
            error_msg = getattr(job, 'error', {})
            if hasattr(error_msg, 'message'):
                raise RuntimeError(f"Video generation failed: {error_msg.message}")
            raise RuntimeError(f"Video generation failed: {error_msg}")
        
        time.sleep(poll_interval)
        elapsed += poll_interval
    
    raise RuntimeError("Video generation timed out")


async def generate_video_async(order_id: str):
    """Générer la vidéo en arrière-plan après paiement"""
    
    try:
        order = await db.video_orders.find_one({"id": order_id})
        if not order:
            logger.error(f"Order {order_id} not found for video generation")
            return
        
        logger.info(f"🎬 Starting video generation for order {order_id}")
        
        # Mettre à jour le statut
        await db.video_orders.update_one(
            {"id": order_id},
            {"$set": {
                "status": "generating",
                "generation_started_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # Initialize OpenAI client
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = order.get("final_prompt", "Professional business video")
        duration = order.get("duration", 8)
        
        # Map durations to Sora 2 supported values
        if duration <= 5:
            sora_duration = 5
        else:
            sora_duration = 10
        
        logger.info(f"📹 Generating video: {prompt[:50]}... | {sora_duration}s")
        
        # Create video job with Sora 2
        video_job = client.videos.create(
            model="sora-2",
            prompt=prompt
        )
        
        logger.info(f"📹 Video job created: {video_job.id}")
        
        # Poll for completion (run in thread to avoid blocking)
        import asyncio
        loop = asyncio.get_event_loop()
        completed_job = await loop.run_in_executor(
            None, 
            lambda: wait_for_video_completion(client, video_job.id, poll_interval=15, timeout=900)
        )
        
        if completed_job and completed_job.status == "completed":
            # Download the video
            video_url_from_api = None
            if hasattr(completed_job, 'result') and completed_job.result:
                video_url_from_api = completed_job.result.url if hasattr(completed_job.result, 'url') else None
            
            if video_url_from_api:
                # Download and save locally
                import httpx
                async with httpx.AsyncClient() as http_client:
                    video_response = await http_client.get(video_url_from_api)
                    video_bytes = video_response.content
                
                filename = f"video_{order_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
                filepath = os.path.join(UPLOADS_DIR, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(video_bytes)
                
                video_url = f"{BASE_URL}/api/uploads/video_orders/{filename}"
            else:
                # Use the API URL directly if local save fails
                video_url = video_url_from_api or f"{BASE_URL}/api/video-pub/orders/{order_id}/stream"
            
            # Mettre à jour la commande
            await db.video_orders.update_one(
                {"id": order_id},
                {"$set": {
                    "status": "completed",
                    "video_url": video_url,
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            # Notification de succès
            await db.notifications.insert_one({
                "id": str(uuid.uuid4()),
                "user_id": order.get("user_id"),
                "type": "video_order_ready",
                "title": "🎬 Votre vidéo est prête !",
                "message": f"La vidéo #{order_id} est disponible au téléchargement.",
                "link": "/dashboard/entreprise?tab=videos-titelli",
                "is_read": False,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            
            logger.info(f"✅ Video generation completed: {order_id} -> {video_url}")
            
        else:
            raise Exception("Video generation returned no data")
            
    except Exception as e:
        logger.error(f"❌ Video generation failed for {order_id}: {e}")
        
        await db.video_orders.update_one(
            {"id": order_id},
            {"$set": {
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # Notification d'erreur
        await db.notifications.insert_one({
            "id": str(uuid.uuid4()),
            "user_id": order.get("user_id") if order else None,
            "type": "video_order_failed",
            "title": "Erreur génération vidéo",
            "message": f"La vidéo #{order_id} n'a pas pu être générée. Notre équipe a été notifiée.",
            "link": "/dashboard/entreprise?tab=videos-titelli",
            "is_read": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        })


@router.get("/orders/{order_id}/download")
async def download_video(order_id: str):
    """Télécharger la vidéo (seulement si payée et générée)"""
    
    order = await db.video_orders.find_one({"id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    if order.get("payment_status") != "paid":
        raise HTTPException(status_code=403, detail="Paiement requis")
    
    if order.get("status") != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Vidéo en cours de génération. Statut: {order.get('status')}"
        )
    
    video_url = order.get("video_url")
    if not video_url:
        raise HTTPException(status_code=404, detail="Vidéo non disponible")
    
    return {
        "download_url": video_url,
        "order_id": order_id,
        "template": order.get("template_name"),
        "duration": order.get("duration")
    }


# ============ ADMIN ENDPOINTS ============

@router.get("/admin/orders")
async def get_all_video_orders(limit: int = 50, status: str = None):
    """Admin: Récupérer toutes les commandes vidéo"""
    
    query = {}
    if status:
        query["status"] = status
    
    cursor = db.video_orders.find(query, {"_id": 0}).sort("created_at", -1).limit(limit)
    orders = await cursor.to_list(limit)
    
    # Stats
    total = await db.video_orders.count_documents({})
    generating = await db.video_orders.count_documents({"status": "generating"})
    completed = await db.video_orders.count_documents({"status": "completed"})
    failed = await db.video_orders.count_documents({"status": "failed"})
    
    pipeline = [
        {"$match": {"payment_status": "paid"}},
        {"$group": {"_id": None, "total": {"$sum": "$price"}}}
    ]
    revenue_result = await db.video_orders.aggregate(pipeline).to_list(1)
    total_revenue = revenue_result[0]["total"] if revenue_result else 0
    
    return {
        "orders": orders,
        "stats": {
            "total": total,
            "generating": generating,
            "completed": completed,
            "failed": failed,
            "total_revenue": total_revenue
        }
    }
