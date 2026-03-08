"""
Media Pub Router - Système de commande de publicités
- Affichage des templates (style Canva)
- Commande de pub avec personnalisation
- Génération IA des images
- Post-processing avec Pillow pour texte parfait
- Suivi des commandes
- Paiement Stripe et confirmation email
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import os
import base64
import logging
import asyncio
from io import BytesIO

from dotenv import load_dotenv
load_dotenv()

# Pillow pour le post-processing du texte
from PIL import Image, ImageDraw, ImageFont

# Email service for confirmations
from services.email_service import send_pub_media_confirmation

router = APIRouter(prefix="/api/media-pub", tags=["Media Pub"])
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

# Use relative path for uploads to work on both Emergent and OnRender
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOADS_DIR = os.path.join(BACKEND_DIR, "uploads", "pub_orders")
BASE_URL = os.getenv("REACT_APP_BACKEND_URL", "https://image-fix-demo.preview.emergentagent.com")

# Créer le dossier si nécessaire (avec gestion d'erreur pour les environnements restreints)
try:
    os.makedirs(UPLOADS_DIR, exist_ok=True)
except PermissionError:
    # Sur certains environnements comme Render, utiliser un dossier temporaire
    import tempfile
    UPLOADS_DIR = os.path.join(tempfile.gettempdir(), "pub_orders")
    os.makedirs(UPLOADS_DIR, exist_ok=True)


# ============ POST-PROCESSING TEXTE ============
# Fonction pour ajouter du texte parfait sur les images générées

def add_text_overlay(image_bytes: bytes, product_name: str, slogan: str, description: str, brand_colors: list) -> bytes:
    """
    Ajoute du texte propre et lisible sur l'image générée par l'IA.
    Le texte est ajouté en post-processing pour éviter les erreurs de DALL-E.
    """
    try:
        # Ouvrir l'image
        img = Image.open(BytesIO(image_bytes))
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Couleurs
        primary_color = brand_colors[0] if brand_colors else "#FFFFFF"
        # secondary_color available for future use
        _ = brand_colors[1] if len(brand_colors) > 1 else "#FFFFFF"
        
        # Convertir hex en RGB
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        primary_rgb = hex_to_rgb(primary_color)
        
        # Charger les polices (utiliser des polices système) - Tailles réduites
        try:
            # Essayer différentes polices
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            ]
            font_large = None
            font_medium = None
            font_small = None
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    # Tailles optimisées pour éviter troncature
                    font_large = ImageFont.truetype(font_path, int(height * 0.055))
                    font_medium = ImageFont.truetype(font_path, int(height * 0.04))
                    font_small = ImageFont.truetype(font_path, int(height * 0.028))
                    break
            
            if not font_large:
                # Fallback to default
                font_large = ImageFont.load_default()
                font_medium = font_large
                font_small = font_large
                
        except Exception as e:
            logger.warning(f"Font loading error: {e}, using default")
            font_large = ImageFont.load_default()
            font_medium = font_large
            font_small = font_large
        
        # Fonction pour tronquer le texte si trop long
        def truncate_text(text, font, max_width):
            """Tronque le texte avec ... si trop long"""
            if not text:
                return text
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            if text_width <= max_width:
                return text
            # Tronquer progressivement
            while text_width > max_width and len(text) > 3:
                text = text[:-4] + "..."
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
            return text
        
        # Créer un fond semi-transparent pour le texte en bas
        overlay_height = int(height * 0.28)  # Un peu plus haut pour plus d'espace
        overlay = Image.new('RGBA', (width, overlay_height), (0, 0, 0, 200))  # Plus opaque
        
        # Ajouter un dégradé sur l'overlay
        for y in range(overlay_height):
            alpha = int(200 * (y / overlay_height))  # Dégradé de transparent à opaque
            for x in range(width):
                overlay.putpixel((x, y), (0, 0, 0, alpha))
        
        # Coller l'overlay en bas de l'image
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        img.paste(overlay, (0, height - overlay_height), overlay)
        
        # Nouveau draw après le paste
        draw = ImageDraw.Draw(img)
        
        # Position de départ pour le texte - avec plus de padding
        text_y = height - overlay_height + int(overlay_height * 0.20)
        padding = int(width * 0.03)  # Padding très réduit
        max_text_width = width - (padding * 2)  # Largeur max pour le texte
        
        # Dessiner le nom du produit (grand)
        if product_name:
            truncated_name = truncate_text(product_name, font_large, max_text_width)
            # Ombre
            draw.text((padding + 2, text_y + 2), truncated_name, font=font_large, fill=(0, 0, 0, 255))
            # Texte principal
            draw.text((padding, text_y), truncated_name, font=font_large, fill=primary_rgb)
            text_y += int(height * 0.065)
        
        # Dessiner le slogan (moyen)
        if slogan:
            truncated_slogan = truncate_text(slogan, font_medium, max_text_width)
            # Ombre
            draw.text((padding + 1, text_y + 1), truncated_slogan, font=font_medium, fill=(0, 0, 0, 255))
            # Texte principal - blanc pour contraste
            draw.text((padding, text_y), truncated_slogan, font=font_medium, fill=(255, 255, 255))
            text_y += int(height * 0.05)
        
        # Dessiner la description (petit)
        if description:
            truncated_desc = truncate_text(description, font_small, max_text_width)
            # Ombre
            draw.text((padding + 1, text_y + 1), truncated_desc, font=font_small, fill=(0, 0, 0, 255))
            # Texte principal
            draw.text((padding, text_y), truncated_desc, font=font_small, fill=(200, 200, 200))
        
        # Convertir en bytes
        output = BytesIO()
        # Convertir en RGB pour sauvegarder en PNG sans alpha
        if img.mode == 'RGBA':
            # Créer un fond blanc
            background = Image.new('RGB', img.size, (0, 0, 0))
            background.paste(img, mask=img.split()[3])
            img = background
        img.save(output, format='PNG', quality=95)
        output.seek(0)
        
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Error in text overlay: {e}")
        # Retourner l'image originale en cas d'erreur
        return image_bytes


# ============ TEMPLATES CATALOGUE ============
# Templates style Canva avec plusieurs modèles par catégorie

TEMPLATES = [
    # =============== RÉSEAUX SOCIAUX - Instagram/Facebook ===============
    {
        "id": "social_promo_1",
        "name": "Promo Flash Moderne",
        "category": "Réseaux Sociaux",
        "subcategory": "Instagram Post",
        "format": "1080x1080",
        "description": "Design épuré avec grande zone texte centrale. Idéal pour promotions.",
        "preview_url": "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=500&h=500&fit=crop",
        "price": 29.90,
        "popular": True,
        "text_position": "center",
        "text_style": "bold_overlay"
    },
    {
        "id": "social_promo_2",
        "name": "Vente Flash Néon",
        "category": "Réseaux Sociaux",
        "subcategory": "Instagram Post",
        "format": "1080x1080",
        "description": "Style néon vibrant avec effets lumineux. Attire l'attention.",
        "preview_url": "https://images.unsplash.com/photo-1557682250-33bd709cbe85?w=500&h=500&fit=crop",
        "price": 29.90,
        "popular": False,
        "text_position": "center",
        "text_style": "neon"
    },
    {
        "id": "social_promo_3",
        "name": "Minimaliste Chic",
        "category": "Réseaux Sociaux",
        "subcategory": "Instagram Post",
        "format": "1080x1080",
        "description": "Design minimaliste élégant. Parfait pour marques luxe.",
        "preview_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=500&h=500&fit=crop",
        "price": 29.90,
        "popular": True,
        "text_position": "bottom",
        "text_style": "minimal"
    },
    {
        "id": "social_promo_4",
        "name": "Gradient Tendance",
        "category": "Réseaux Sociaux",
        "subcategory": "Instagram Post",
        "format": "1080x1080",
        "description": "Dégradés colorés modernes. Style tech et startup.",
        "preview_url": "https://images.unsplash.com/photo-1579546929518-9e396f3cc809?w=500&h=500&fit=crop",
        "price": 29.90,
        "popular": False,
        "text_position": "center",
        "text_style": "gradient"
    },
    {
        "id": "social_story_1",
        "name": "Story Élégante",
        "category": "Réseaux Sociaux",
        "subcategory": "Instagram Story",
        "format": "1080x1920",
        "description": "Format story vertical. Style épuré professionnel.",
        "preview_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=300&h=533&fit=crop",
        "price": 24.90,
        "popular": True,
        "text_position": "center",
        "text_style": "story"
    },
    {
        "id": "social_story_2",
        "name": "Story Dynamique",
        "category": "Réseaux Sociaux",
        "subcategory": "Instagram Story",
        "format": "1080x1920",
        "description": "Design énergique avec formes géométriques.",
        "preview_url": "https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?w=300&h=533&fit=crop",
        "price": 24.90,
        "popular": False,
        "text_position": "top",
        "text_style": "dynamic"
    },
    {
        "id": "social_carousel_1",
        "name": "Carousel Produit",
        "category": "Réseaux Sociaux",
        "subcategory": "Carousel",
        "format": "1080x1080",
        "description": "Multi-images pour présenter plusieurs produits.",
        "preview_url": "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=500&h=500&fit=crop",
        "price": 39.90,
        "popular": False,
        "text_position": "bottom",
        "text_style": "carousel"
    },
    
    # =============== BANNIÈRES WEB ===============
    {
        "id": "banner_hero_1",
        "name": "Hero Banner Corporate",
        "category": "Bannières Web",
        "subcategory": "Hero Banner",
        "format": "1920x600",
        "description": "Grande bannière pour page d'accueil. Style corporate.",
        "preview_url": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=600&h=188&fit=crop",
        "price": 49.90,
        "popular": True,
        "text_position": "left",
        "text_style": "hero"
    },
    {
        "id": "banner_hero_2",
        "name": "Hero Créatif",
        "category": "Bannières Web",
        "subcategory": "Hero Banner",
        "format": "1920x600",
        "description": "Design créatif avec illustrations. Style moderne.",
        "preview_url": "https://images.unsplash.com/photo-1551434678-e076c223a692?w=600&h=188&fit=crop",
        "price": 49.90,
        "popular": False,
        "text_position": "center",
        "text_style": "creative"
    },
    {
        "id": "banner_hero_3",
        "name": "Hero Minimaliste",
        "category": "Bannières Web",
        "subcategory": "Hero Banner",
        "format": "1920x600",
        "description": "Style épuré avec beaucoup d'espace blanc.",
        "preview_url": "https://images.unsplash.com/photo-1497215728101-856f4ea42174?w=600&h=188&fit=crop",
        "price": 49.90,
        "popular": True,
        "text_position": "left",
        "text_style": "minimal"
    },
    {
        "id": "banner_sidebar_1",
        "name": "Sidebar Vertical",
        "category": "Bannières Web",
        "subcategory": "Sidebar",
        "format": "300x600",
        "description": "Format vertical pour barres latérales.",
        "preview_url": "https://images.unsplash.com/photo-1553484771-371a605b060b?w=200&h=400&fit=crop",
        "price": 34.90,
        "popular": False,
        "text_position": "center",
        "text_style": "vertical"
    },
    {
        "id": "banner_leaderboard_1",
        "name": "Leaderboard Classic",
        "category": "Bannières Web",
        "subcategory": "Leaderboard",
        "format": "728x90",
        "description": "Banner horizontal classique pour publicité.",
        "preview_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=728&h=90&fit=crop",
        "price": 29.90,
        "popular": False,
        "text_position": "center",
        "text_style": "banner"
    },
    
    # =============== MENUS RESTAURANT ===============
    {
        "id": "menu_elegant_1",
        "name": "Menu Gastronomique",
        "category": "Restauration",
        "subcategory": "Menu Restaurant",
        "format": "A4",
        "description": "Menu élégant pour restaurant gastronomique. Police raffinée.",
        "preview_url": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400&h=566&fit=crop",
        "price": 44.90,
        "popular": True,
        "text_position": "center",
        "text_style": "elegant"
    },
    {
        "id": "menu_bistro_1",
        "name": "Menu Bistro Ardoise",
        "category": "Restauration",
        "subcategory": "Menu Restaurant",
        "format": "A4",
        "description": "Style ardoise de bistro français. Chaleureux et authentique.",
        "preview_url": "https://images.unsplash.com/photo-1466978913421-dad2ebd01d17?w=400&h=566&fit=crop",
        "price": 39.90,
        "popular": True,
        "text_position": "center",
        "text_style": "chalkboard"
    },
    {
        "id": "menu_modern_1",
        "name": "Menu Moderne Épuré",
        "category": "Restauration",
        "subcategory": "Menu Restaurant",
        "format": "A4",
        "description": "Design contemporain minimaliste. Idéal pour brunch et café.",
        "preview_url": "https://images.unsplash.com/photo-1567521464027-f127ff144326?w=400&h=566&fit=crop",
        "price": 39.90,
        "popular": False,
        "text_position": "left",
        "text_style": "modern"
    },
    {
        "id": "menu_italian_1",
        "name": "Menu Italien Trattoria",
        "category": "Restauration",
        "subcategory": "Menu Restaurant",
        "format": "A4",
        "description": "Style italien traditionnel. Parfait pour pizzeria et trattoria.",
        "preview_url": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400&h=566&fit=crop",
        "price": 39.90,
        "popular": False,
        "text_position": "center",
        "text_style": "italian"
    },
    {
        "id": "menu_sushi_1",
        "name": "Menu Sushi Japonais",
        "category": "Restauration",
        "subcategory": "Menu Restaurant",
        "format": "A4",
        "description": "Design japonais épuré. Idéal pour restaurant sushi.",
        "preview_url": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=400&h=566&fit=crop",
        "price": 44.90,
        "popular": False,
        "text_position": "right",
        "text_style": "japanese"
    },
    {
        "id": "menu_cafe_1",
        "name": "Carte Café & Desserts",
        "category": "Restauration",
        "subcategory": "Menu Café",
        "format": "A5",
        "description": "Menu spécial boissons et desserts. Style cosy.",
        "preview_url": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400&h=566&fit=crop",
        "price": 34.90,
        "popular": True,
        "text_position": "center",
        "text_style": "cafe"
    },
    
    # =============== FLYERS & AFFICHES ===============
    {
        "id": "flyer_event_1",
        "name": "Flyer Événement Moderne",
        "category": "Flyers & Affiches",
        "subcategory": "Événement",
        "format": "A5",
        "description": "Flyer dynamique pour événements et soirées.",
        "preview_url": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=400&h=566&fit=crop",
        "price": 34.90,
        "popular": True,
        "text_position": "center",
        "text_style": "event"
    },
    {
        "id": "flyer_promo_1",
        "name": "Flyer Promotion Vente",
        "category": "Flyers & Affiches",
        "subcategory": "Promotion",
        "format": "A5",
        "description": "Design accrocheur pour ventes et soldes.",
        "preview_url": "https://images.unsplash.com/photo-1607083206869-4c7672e72a8a?w=400&h=566&fit=crop",
        "price": 34.90,
        "popular": True,
        "text_position": "center",
        "text_style": "sale"
    },
    {
        "id": "flyer_opening_1",
        "name": "Flyer Ouverture",
        "category": "Flyers & Affiches",
        "subcategory": "Ouverture",
        "format": "A5",
        "description": "Annonce d'ouverture de magasin ou restaurant.",
        "preview_url": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=566&fit=crop",
        "price": 34.90,
        "popular": False,
        "text_position": "bottom",
        "text_style": "opening"
    },
    {
        "id": "poster_vitrine_1",
        "name": "Affiche Vitrine A3",
        "category": "Flyers & Affiches",
        "subcategory": "Affiche",
        "format": "A3",
        "description": "Grande affiche pour vitrine. Haute résolution.",
        "preview_url": "https://images.unsplash.com/photo-1556742393-d75f468bfcb0?w=400&h=566&fit=crop",
        "price": 54.90,
        "popular": False,
        "text_position": "center",
        "text_style": "poster"
    },
    {
        "id": "poster_concert_1",
        "name": "Affiche Concert/Spectacle",
        "category": "Flyers & Affiches",
        "subcategory": "Spectacle",
        "format": "A3",
        "description": "Design artistique pour événements culturels.",
        "preview_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=400&h=566&fit=crop",
        "price": 54.90,
        "popular": False,
        "text_position": "bottom",
        "text_style": "concert"
    },
    
    # =============== EMAIL MARKETING ===============
    {
        "id": "email_header_1",
        "name": "Header Email Corporate",
        "category": "Email Marketing",
        "subcategory": "Header",
        "format": "600x200",
        "description": "En-tête email professionnel. Compatible tous clients.",
        "preview_url": "https://images.unsplash.com/photo-1563986768494-4dee2763ff3f?w=600&h=200&fit=crop",
        "price": 19.90,
        "popular": False,
        "text_position": "center",
        "text_style": "email"
    },
    {
        "id": "email_header_2",
        "name": "Header Newsletter Créatif",
        "category": "Email Marketing",
        "subcategory": "Header",
        "format": "600x200",
        "description": "Style créatif et coloré pour newsletters.",
        "preview_url": "https://images.unsplash.com/photo-1516321497487-e288fb19713f?w=600&h=200&fit=crop",
        "price": 19.90,
        "popular": False,
        "text_position": "left",
        "text_style": "creative"
    },
    {
        "id": "newsletter_promo_1",
        "name": "Newsletter Promo",
        "category": "Email Marketing",
        "subcategory": "Newsletter",
        "format": "600x900",
        "description": "Template newsletter pour promotions.",
        "preview_url": "https://images.unsplash.com/photo-1557426272-fc759fdf7a8d?w=400&h=600&fit=crop",
        "price": 49.90,
        "popular": True,
        "text_position": "top",
        "text_style": "newsletter"
    },
    {
        "id": "newsletter_product_1",
        "name": "Newsletter Produit",
        "category": "Email Marketing",
        "subcategory": "Newsletter",
        "format": "600x900",
        "description": "Présentation de nouveaux produits par email.",
        "preview_url": "https://images.unsplash.com/photo-1586880244406-556ebe35f282?w=400&h=600&fit=crop",
        "price": 49.90,
        "popular": False,
        "text_position": "center",
        "text_style": "product"
    },
    
    # =============== VIDÉO ===============
    {
        "id": "youtube_thumb_1",
        "name": "Miniature YouTube Gaming",
        "category": "Vidéo",
        "subcategory": "YouTube",
        "format": "1280x720",
        "description": "Miniature accrocheuse style gaming/tech.",
        "preview_url": "https://images.unsplash.com/photo-1611162616475-46b635cb6868?w=400&h=225&fit=crop",
        "price": 24.90,
        "popular": True,
        "text_position": "center",
        "text_style": "youtube"
    },
    {
        "id": "youtube_thumb_2",
        "name": "Miniature YouTube Business",
        "category": "Vidéo",
        "subcategory": "YouTube",
        "format": "1280x720",
        "description": "Style professionnel pour vidéos business.",
        "preview_url": "https://images.unsplash.com/photo-1553484771-047a44eee27b?w=400&h=225&fit=crop",
        "price": 24.90,
        "popular": False,
        "text_position": "left",
        "text_style": "business"
    },
    {
        "id": "youtube_thumb_3",
        "name": "Miniature Tutoriel",
        "category": "Vidéo",
        "subcategory": "YouTube",
        "format": "1280x720",
        "description": "Design clair pour vidéos tutoriels.",
        "preview_url": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&h=225&fit=crop",
        "price": 24.90,
        "popular": False,
        "text_position": "bottom",
        "text_style": "tutorial"
    },
    
    # =============== PRINT ===============
    {
        "id": "business_card_modern",
        "name": "Carte de Visite Moderne",
        "category": "Print",
        "subcategory": "Carte de Visite",
        "format": "85x55mm",
        "description": "Design moderne et professionnel.",
        "preview_url": "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=400&h=235&fit=crop",
        "price": 34.90,
        "popular": True,
        "text_position": "left",
        "text_style": "card"
    },
    {
        "id": "business_card_minimal",
        "name": "Carte de Visite Minimaliste",
        "category": "Print",
        "subcategory": "Carte de Visite",
        "format": "85x55mm",
        "description": "Style épuré et élégant.",
        "preview_url": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=400&h=235&fit=crop",
        "price": 34.90,
        "popular": False,
        "text_position": "center",
        "text_style": "minimal"
    },
    {
        "id": "business_card_creative",
        "name": "Carte de Visite Créative",
        "category": "Print",
        "subcategory": "Carte de Visite",
        "format": "85x55mm",
        "description": "Design original et mémorable.",
        "preview_url": "https://images.unsplash.com/photo-1572044162444-ad60f128bdea?w=400&h=235&fit=crop",
        "price": 39.90,
        "popular": False,
        "text_position": "center",
        "text_style": "creative"
    },
    {
        "id": "brochure_corporate",
        "name": "Brochure Corporate",
        "category": "Print",
        "subcategory": "Brochure",
        "format": "A4 Tri-fold",
        "description": "Brochure 3 volets professionnelle.",
        "preview_url": "https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=400&h=283&fit=crop",
        "price": 69.90,
        "popular": False,
        "text_position": "left",
        "text_style": "brochure"
    },
]


# ============ MODELS ============

class PubOrderCreate(BaseModel):
    template_id: str
    enterprise_id: str
    slogan: str
    product_name: str
    description: Optional[str] = None
    brand_colors: Optional[List[str]] = None  # Ex: ["#FF5733", "#333333"]
    additional_notes: Optional[str] = None


class PubOrderResponse(BaseModel):
    id: str
    status: str
    message: str
    estimated_time: str


# ============ HELPER FUNCTIONS ============

async def get_current_user(authorization: str = None):
    """Simple auth check - à remplacer par vraie auth"""
    # Import ici pour éviter circular imports
    from server import get_current_user as server_get_current_user
    return await server_get_current_user()


async def generate_pub_image(order_id: str, order_data: dict):
    """Génère l'image publicitaire avec IA en arrière-plan + post-processing texte"""
    try:
        from openai import OpenAI
        import base64
        
        logger.info(f"🎨 Génération image pour commande {order_id}")
        
        template = next((t for t in TEMPLATES if t["id"] == order_data["template_id"]), None)
        if not template:
            # Template sur mesure
            template = {
                "id": "sur_mesure",
                "name": "Création Sur Mesure",
                "category": "Personnalisé",
                "format": "1080x1080"
            }
        
        # Construire le prompt pour l'IA - SANS TEXTE (le texte sera ajouté en post-processing)
        colors_str = ", ".join(order_data.get("brand_colors", ["#0066CC", "#FFFFFF"])) if order_data.get("brand_colors") else "blue and white professional colors"
        
        # Prompt optimisé pour image de fond SANS TEXTE
        prompt = f"""Create a professional marketing advertisement background image.

STYLE: {template['name']} - {template['category']}
FORMAT: Square {template['format']}

VISUAL THEME BASED ON:
- Business type: {order_data['product_name']}
- Mood/Style: {order_data.get('description', 'Professional and modern')}

CRITICAL DESIGN REQUIREMENTS:
- DO NOT include ANY text, words, letters or typography in the image
- DO NOT add any watermarks or logos
- DO NOT include any prices, dates, or numbers
- Leave the bottom 25% of the image clean/darker for text overlay
- Use these brand colors as accents: {colors_str}
- Modern, professional, clean aesthetic
- High quality photographic or illustrated style
- DO NOT crop any faces if people are shown
- Professional marketing aesthetic suitable for {template['category']}

The image should be a beautiful visual background that will have text overlaid on it later.
Focus on stunning visuals, NOT text.

STYLE: Premium advertising quality, Swiss/European professional standards, elegant and sophisticated."""

        # Générer l'image avec le SDK OpenAI officiel
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        
        # Récupérer l'image (base64 ou URL)
        image_data = response.data[0]
        
        if hasattr(image_data, 'b64_json') and image_data.b64_json:
            image_bytes = base64.b64decode(image_data.b64_json)
        elif hasattr(image_data, 'url') and image_data.url:
            import httpx
            async with httpx.AsyncClient() as http_client:
                img_response = await http_client.get(image_data.url)
                image_bytes = img_response.content
        else:
            raise ValueError("Aucune image retournée par l'API")
        
        if image_bytes:
            # POST-PROCESSING: Ajouter le texte parfait avec Pillow
            logger.info("📝 Post-processing: ajout du texte sur l'image")
            
            final_image = add_text_overlay(
                image_bytes=image_bytes,
                product_name=order_data.get('product_name', ''),
                slogan=order_data.get('slogan', ''),
                description=order_data.get('description', ''),
                brand_colors=order_data.get('brand_colors', ['#FFFFFF', '#FFFFFF'])
            )
            
            # Sauvegarder l'image finale
            filename = f"pub_{order_id}.png"
            filepath = f"{UPLOADS_DIR}/{filename}"
            
            with open(filepath, "wb") as f:
                f.write(final_image)
            
            image_url = f"{BASE_URL}/api/uploads/pub_orders/{filename}"
            
            # Mettre à jour la commande
            await db.pub_orders.update_one(
                {"id": order_id},
                {"$set": {
                    "status": "completed",
                    "image_url": image_url,
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            logger.info(f"✅ Image générée: {image_url}")
            
            # Créer notification pour l'entreprise
            await db.notifications.insert_one({
                "id": str(uuid.uuid4()),
                "user_id": order_data.get("user_id"),
                "type": "pub_order_ready",
                "title": "Votre publicité est prête !",
                "message": f"Votre commande '{template['name']}' est disponible dans vos commandes Titelli.",
                "link": "/dashboard/entreprise?tab=commandes-titelli",
                "is_read": False,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            
        else:
            raise ValueError("Aucune image générée")
            
    except Exception as e:
        logger.error(f"❌ Erreur génération: {e}")
        await db.pub_orders.update_one(
            {"id": order_id},
            {"$set": {
                "status": "failed",
                "error": str(e)[:500],
                "completed_at": datetime.now(timezone.utc).isoformat()
            }}
        )


# ============ ROUTES ============

@router.get("/templates")
async def get_templates(category: Optional[str] = None):
    """Liste tous les templates disponibles"""
    templates = TEMPLATES
    
    if category:
        templates = [t for t in templates if t["category"].lower() == category.lower()]
    
    # Grouper par catégorie
    categories = {}
    for t in TEMPLATES:
        cat = t["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(t)
    
    return {
        "templates": templates,
        "categories": list(categories.keys()),
        "by_category": categories,
        "total": len(templates)
    }


@router.get("/templates/{template_id}")
async def get_template_detail(template_id: str):
    """Détail d'un template"""
    template = next((t for t in TEMPLATES if t["id"] == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template non trouvé")
    return template


@router.post("/orders", response_model=PubOrderResponse)
async def create_pub_order(
    order: PubOrderCreate,
    background_tasks: BackgroundTasks
):
    """Créer une commande de publicité"""
    
    # Vérifier le template (sauf pour sur mesure)
    if order.template_id == 'sur_mesure':
        template = {
            "id": "sur_mesure",
            "name": "Création Sur Mesure",
            "category": "Sur Mesure",
            "price": 149.90
        }
    else:
        template = next((t for t in TEMPLATES if t["id"] == order.template_id), None)
        if not template:
            raise HTTPException(status_code=404, detail="Template non trouvé")
    
    # Vérifier l'entreprise (permettre demo pour tests)
    if order.enterprise_id == "demo-enterprise":
        enterprise = {
            "id": "demo-enterprise",
            "business_name": "Entreprise Démo",
            "user_id": "demo-user"
        }
    else:
        enterprise = await db.enterprises.find_one({"id": order.enterprise_id})
        if not enterprise:
            raise HTTPException(status_code=404, detail="Entreprise non trouvée")
    
    # Créer la commande
    order_id = str(uuid.uuid4())[:8]
    order_data = {
        "id": order_id,
        "template_id": order.template_id,
        "template_name": template["name"],
        "template_category": template["category"],
        "enterprise_id": order.enterprise_id,
        "enterprise_name": enterprise.get("business_name") or enterprise.get("name"),
        "user_id": enterprise.get("user_id"),
        "slogan": order.slogan,
        "product_name": order.product_name,
        "description": order.description,
        "brand_colors": order.brand_colors or ["#0066CC", "#FFFFFF"],
        "additional_notes": order.additional_notes,
        "price": template["price"],
        "currency": "CHF",
        "status": "processing",
        "image_url": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "error": None
    }
    
    await db.pub_orders.insert_one(order_data)
    
    # Lancer la génération en arrière-plan
    background_tasks.add_task(generate_pub_image, order_id, order_data)
    
    return PubOrderResponse(
        id=order_id,
        status="processing",
        message="Votre publicité est en cours de création",
        estimated_time="2-5 minutes"
    )


@router.get("/orders/{order_id}")
async def get_order_detail(order_id: str):
    """Détail d'une commande"""
    order = await db.pub_orders.find_one({"id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    return order


@router.get("/admin/orders")
async def admin_get_all_orders(
    status: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
):
    """Admin: Liste toutes les commandes pub"""
    query = {}
    if status:
        query["status"] = status
    
    orders = await db.pub_orders.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.pub_orders.count_documents(query)
    
    # Stats
    stats = {
        "total": total,
        "processing": await db.pub_orders.count_documents({"status": "processing"}),
        "completed": await db.pub_orders.count_documents({"status": "completed"}),
        "failed": await db.pub_orders.count_documents({"status": "failed"})
    }
    
    # Revenus
    completed_orders = await db.pub_orders.find({"status": "completed"}, {"price": 1}).to_list(1000)
    stats["total_revenue"] = sum(o.get("price", 0) for o in completed_orders)
    
    return {
        "orders": orders,
        "stats": stats,
        "pagination": {"limit": limit, "skip": skip, "total": total}
    }


@router.get("/orders/enterprise/{enterprise_id}")
async def get_enterprise_orders(enterprise_id: str, limit: int = 50):
    """Récupérer toutes les commandes pub d'une entreprise"""
    cursor = db.pub_orders.find(
        {"enterprise_id": enterprise_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit)
    
    orders = await cursor.to_list(limit)
    return {"orders": orders, "total": len(orders)}


@router.delete("/orders/{order_id}")
async def cancel_order(order_id: str):
    """Annuler une commande (si pas encore traitée)"""
    order = await db.pub_orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    if order.get("status") == "completed":
        raise HTTPException(status_code=400, detail="Commande déjà terminée, impossible d'annuler")
    
    await db.pub_orders.update_one(
        {"id": order_id},
        {"$set": {"status": "cancelled", "completed_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Commande annulée"}


# ============ STRIPE PAYMENT INTEGRATION ============

import stripe
from fastapi import Request

STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")


class PaymentRequest(BaseModel):
    """Request for creating payment session"""
    order_id: str
    origin_url: str  # Frontend origin for redirect URLs


class PaymentStatusRequest(BaseModel):
    """Request for checking payment status"""
    session_id: str
    order_id: str


@router.post("/payment/create-session")
async def create_payment_session(payment_request: PaymentRequest, request: Request):
    """Create Stripe checkout session for a pub order"""
    
    # Get the order
    order = await db.pub_orders.find_one({"id": payment_request.order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    if order.get("payment_status") == "paid":
        raise HTTPException(status_code=400, detail="Cette commande a déjà été payée")
    
    # Get price from server-side (NEVER trust frontend amount)
    price = float(order.get("price", 29.90))
    price_cents = int(price * 100)  # Stripe uses cents
    
    # Configure Stripe
    stripe.api_key = STRIPE_API_KEY
    
    # Build URLs from frontend origin
    origin_url = payment_request.origin_url.rstrip('/')
    success_url = f"{origin_url}/media-pub/success?session_id={{CHECKOUT_SESSION_ID}}&order_id={payment_request.order_id}"
    cancel_url = f"{origin_url}/media-pub?cancelled=true&order_id={payment_request.order_id}"
    
    try:
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "chf",
                    "product_data": {
                        "name": f"Pub Média - {order.get('template_name', 'Création')}",
                        "description": f"Image publicitaire: {order.get('product_name', '')}",
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
                "type": "pub_media_order"
            }
        )
        
        # Create payment transaction record
        await db.payment_transactions.insert_one({
            "id": str(uuid.uuid4()),
            "session_id": session.id,
            "order_id": payment_request.order_id,
            "amount": price,
            "currency": "CHF",
            "type": "pub_media",
            "payment_status": "pending",
            "enterprise_id": order.get("enterprise_id"),
            "user_id": order.get("user_id"),
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Update order with session_id
        await db.pub_orders.update_one(
            {"id": payment_request.order_id},
            {"$set": {
                "stripe_session_id": session.id,
                "payment_status": "pending"
            }}
        )
        
        return {
            "checkout_url": session.url,
            "session_id": session.id
        }
        
    except Exception as e:
        logger.error(f"Stripe session creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur création session Stripe: {str(e)}")


@router.get("/payment/status/{session_id}")
async def check_payment_status(session_id: str, order_id: str):
    """Check payment status and update order if paid"""
    
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    
    stripe.api_key = STRIPE_API_KEY
    
    try:
        # Retrieve session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Find the transaction
        transaction = await db.payment_transactions.find_one({"session_id": session_id})
        
        if session.payment_status == "paid":
            # Check if already processed (prevent double processing)
            if transaction and transaction.get("payment_status") == "paid":
                return {
                    "status": "paid",
                    "message": "Paiement déjà traité",
                    "order_id": order_id
                }
            
            # Update transaction
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {
                    "payment_status": "paid",
                    "paid_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            # Update order payment status
            await db.pub_orders.update_one(
                {"id": order_id},
                {"$set": {
                    "payment_status": "paid",
                    "paid_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            # Create success notification
            order = await db.pub_orders.find_one({"id": order_id})
            if order:
                await db.notifications.insert_one({
                    "id": str(uuid.uuid4()),
                    "user_id": order.get("user_id"),
                    "type": "payment_success",
                    "title": "Paiement confirmé !",
                    "message": f"Votre commande Pub Média #{order_id} a été payée. L'image HD sans filigrane est disponible.",
                    "link": "/dashboard/entreprise?tab=commandes-titelli",
                    "is_read": False,
                    "created_at": datetime.now(timezone.utc).isoformat()
                })
                
                # Send confirmation email
                try:
                    user_id = order.get("user_id")
                    if user_id:
                        user = await db.users.find_one({"id": user_id})
                        if user and user.get("email"):
                            await send_pub_media_confirmation(
                                user_email=user.get("email"),
                                user_name=user.get("name", user.get("email", "Client")),
                                order_id=order_id,
                                template_name=order.get("template_name", "Création Sur Mesure"),
                                amount=float(order.get("price", 0)),
                                slogan=order.get("slogan", ""),
                                product_name=order.get("product_name", "")
                            )
                            logger.info(f"📧 Email confirmation sent for order {order_id}")
                except Exception as email_error:
                    logger.warning(f"Email send failed for order {order_id}: {email_error}")
            
            logger.info(f"✅ Payment confirmed for order {order_id}")
            
            return {
                "status": "paid",
                "message": "Paiement confirmé ! Image HD disponible.",
                "order_id": order_id
            }
            
        elif session.status == "expired":
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {"payment_status": "expired"}}
            )
            return {
                "status": "expired",
                "message": "Session de paiement expirée",
                "order_id": order_id
            }
        else:
            return {
                "status": session.payment_status,
                "message": "Paiement en attente",
                "order_id": order_id
            }
            
    except Exception as e:
        logger.error(f"Payment status check error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur vérification: {str(e)}")


@router.post("/webhook/stripe")
async def handle_stripe_webhook(request: Request):
    """Handle Stripe webhook events for payment confirmation"""
    
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    stripe.api_key = STRIPE_API_KEY
    
    try:
        # If webhook secret is configured, verify signature
        if webhook_secret:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        else:
            # Without webhook secret, parse the event directly (less secure)
            import json
            event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
        
        # Handle checkout.session.completed event
        if event.type == "checkout.session.completed":
            session = event.data.object
            order_id = session.metadata.get("order_id")
            
            if order_id and session.payment_status == "paid":
                # Update transaction
                await db.payment_transactions.update_one(
                    {"session_id": session.id},
                    {"$set": {
                        "payment_status": "paid",
                        "paid_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                
                # Update order
                await db.pub_orders.update_one(
                    {"id": order_id},
                    {"$set": {
                        "payment_status": "paid",
                        "paid_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                
                logger.info(f"✅ Webhook: Payment confirmed for order {order_id}")
        
        return {"status": "received"}
        
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Webhook signature verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/orders/{order_id}/download")
async def download_order_image(order_id: str):
    """Download the final image (only if paid)"""
    
    order = await db.pub_orders.find_one({"id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    if order.get("payment_status") != "paid":
        raise HTTPException(
            status_code=403, 
            detail="Paiement requis pour télécharger l'image HD sans filigrane"
        )
    
    if order.get("status") != "completed":
        raise HTTPException(
            status_code=400, 
            detail="L'image n'est pas encore prête"
        )
    
    image_url = order.get("image_url")
    if not image_url:
        raise HTTPException(status_code=404, detail="Image non disponible")
    
    return {
        "download_url": image_url,
        "order_id": order_id,
        "message": "Image HD sans filigrane"
    }
