#!/usr/bin/env python3
"""
Script d'enrichissement V2 - Images via Google Images
"""

import asyncio
import os
import logging
import uuid
from datetime import datetime, timezone
from urllib.parse import quote_plus, urljoin
from motor.motor_asyncio import AsyncIOMotorClient
from playwright.async_api import async_playwright
import httpx

MONGO_URL = os.environ.get('MONGO_URL')
UPLOADS_DIR = "/app/backend/uploads/enterprises"
BASE_URL = "https://image-fix-demo.preview.emergentagent.com"
MAX_ENTERPRISES = 200
MAX_IMAGES = 8

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)
os.makedirs(UPLOADS_DIR, exist_ok=True)


async def download_image(url: str, filepath: str) -> bool:
    """Telecharge une image"""
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200 and len(resp.content) > 10000:  # Min 10KB
                with open(filepath, 'wb') as f:
                    f.write(resp.content)
                return True
    except:
        pass
    return False


async def get_images_from_google(page, query: str, enterprise_id: str, max_images: int = 5) -> list:
    """Recupere des images depuis Google Images"""
    images = []
    try:
        search_url = f"https://www.google.com/search?q={quote_plus(query)}&tbm=isch"
        await page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(2000)
        
        # Trouver les miniatures
        thumbnails = await page.query_selector_all('img.rg_i, img[data-src]')
        
        idx = 0
        for thumb in thumbnails[:20]:
            if idx >= max_images:
                break
            try:
                # Cliquer sur la miniature pour obtenir l'image HD
                await thumb.click()
                await page.wait_for_timeout(1500)
                
                # Trouver l'image HD
                hd_img = await page.query_selector('img[jsname="kn3ccd"]')
                if hd_img:
                    src = await hd_img.get_attribute('src')
                    if src and src.startswith('http') and 'gstatic' not in src:
                        filename = f"{enterprise_id}_photo_{idx}.jpg"
                        filepath = f"{UPLOADS_DIR}/{filename}"
                        
                        if await download_image(src, filepath):
                            images.append(f"{BASE_URL}/api/uploads/enterprises/{filename}")
                            idx += 1
                            logger.info(f"      Image {idx} telechargee")
            except:
                continue
                
    except Exception as e:
        logger.debug(f"Erreur Google Images: {e}")
    
    return images


async def capture_screenshot_as_cover(page, query: str, enterprise_id: str) -> str:
    """Capture un screenshot de la recherche comme cover"""
    try:
        search_url = f"https://www.google.com/search?q={quote_plus(query)}"
        await page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(2000)
        
        filename = f"{enterprise_id}_cover.jpg"
        filepath = f"{UPLOADS_DIR}/{filename}"
        await page.screenshot(path=filepath, quality=85)
        return f"{BASE_URL}/api/uploads/enterprises/{filename}"
    except:
        return None


async def generate_logo_from_initials(name: str, enterprise_id: str) -> str:
    """Genere un logo avec les initiales via UI Avatars"""
    try:
        initials = ''.join([w[0] for w in name.split()[:2]]).upper()
        colors = ['F59E0B', '10B981', '3B82F6', 'EF4444', '8B5CF6', 'EC4899']
        color = colors[hash(name) % len(colors)]
        
        url = f"https://ui-avatars.com/api/?name={quote_plus(initials)}&background={color}&color=fff&size=400&bold=true"
        
        filename = f"{enterprise_id}_logo.png"
        filepath = f"{UPLOADS_DIR}/{filename}"
        
        if await download_image(url, filepath):
            return f"{BASE_URL}/api/uploads/enterprises/{filename}"
    except:
        pass
    return None


def generate_description(name: str, category: str, subcategory: str, city: str) -> str:
    """Genere une description professionnelle"""
    templates = {
        "Beauté & Bien-être": {
            "Coiffeur": f"Bienvenue chez {name}, votre salon de coiffure a {city}. Notre equipe de professionnels passionnes vous accueille dans un cadre chaleureux pour sublimer votre beaute. Coupes, colorations, soins capillaires - nous prenons soin de vous avec expertise et creativite.",
            "default": f"{name} est votre espace beaute et bien-etre a {city}. Nos experts vous proposent des soins personnalises dans une ambiance relaxante. Venez decouvrir nos services et laissez-vous choyer."
        },
        "Restaurant": {
            "default": f"Decouvrez {name} a {city}, une adresse gourmande ou la passion de la cuisine rencontre la qualite des produits. Notre chef vous propose une carte variee et des plats savoureux prepares avec soin. Reservez votre table pour une experience culinaire memorable."
        },
        "Commerce": {
            "default": f"{name}, votre commerce de proximite a {city}. Nous selectionnons pour vous les meilleurs produits et vous accueillons avec le sourire. Service personnalise et conseils d'experts pour repondre a tous vos besoins."
        },
        "default": f"{name} est une entreprise de confiance situee a {city}. Specialises dans le domaine {subcategory or category}, nous mettons notre expertise a votre service. Contactez-nous pour decouvrir nos prestations de qualite."
    }
    
    cat_templates = templates.get(category, templates["default"])
    if isinstance(cat_templates, dict):
        return cat_templates.get(subcategory, cat_templates.get("default", templates["default"]))
    return cat_templates


async def main():
    logger.info("=" * 60)
    logger.info("  ENRICHISSEMENT V2 - IMAGES GOOGLE")
    logger.info("=" * 60)
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.titelli
    
    # Entreprises sans photos
    query = {
        "$or": [
            {"photos": {"$exists": False}},
            {"photos": []},
            {"photos": None}
        ]
    }
    
    enterprises = await db.enterprises.find(query).limit(MAX_ENTERPRISES).to_list(length=MAX_ENTERPRISES)
    logger.info(f"Entreprises a enrichir: {len(enterprises)}\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        success = 0
        
        for i, ent in enumerate(enterprises):
            ent_id = ent.get('id')
            name = ent.get('name', ent.get('business_name', 'Entreprise'))
            city = ent.get('city', 'Lausanne')
            category = ent.get('category', 'Services')
            subcategory = ent.get('subcategory', '')
            
            logger.info(f"[{i+1}/{len(enterprises)}] {name}")
            
            update_data = {
                "enriched_at": datetime.now(timezone.utc).isoformat(),
                "photos": [],
                "gallery": []
            }
            
            try:
                # 1. Rechercher des images sur Google
                query = f"{name} {city} {subcategory}"
                images = await get_images_from_google(page, query, ent_id, MAX_IMAGES)
                
                if images:
                    update_data["photos"] = images
                    update_data["gallery"] = images
                    update_data["cover_url"] = images[0]
                    update_data["cover_image"] = images[0]
                    logger.info(f"    {len(images)} images recuperees")
                else:
                    # Fallback: screenshot de la recherche
                    cover = await capture_screenshot_as_cover(page, query, ent_id)
                    if cover:
                        update_data["photos"] = [cover]
                        update_data["gallery"] = [cover]
                        update_data["cover_url"] = cover
                        update_data["cover_image"] = cover
                        logger.info(f"    Cover screenshot cree")
                
                # 2. Logo
                logo = await generate_logo_from_initials(name, ent_id)
                if logo:
                    update_data["logo_url"] = logo
                    update_data["logo"] = logo
                
                # 3. Description
                update_data["description"] = generate_description(name, category, subcategory, city)
                
                # Update DB
                await db.enterprises.update_one({"id": ent_id}, {"$set": update_data})
                
                success += 1
                logger.info(f"    => OK\n")
                
                await asyncio.sleep(3)
                
            except Exception as e:
                logger.error(f"    => ERREUR: {e}\n")
        
        await browser.close()
    
    logger.info("=" * 60)
    logger.info(f"  TERMINE: {success}/{len(enterprises)} entreprises enrichies")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
