#!/usr/bin/env python3
"""
Script d'enrichissement COMPLET des profils entreprises
1. Recherche le site web sur local.ch/Google
2. Capture screenshots et images
3. Extrait logo, description, photos
4. Detecte et ajoute les produits
"""

import asyncio
import os
import sys
import logging
import uuid
import re
import json
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin, quote_plus
from motor.motor_asyncio import AsyncIOMotorClient
from playwright.async_api import async_playwright
import httpx

# Configuration
MONGO_URL = os.environ.get('MONGO_URL')
UPLOADS_DIR = "/app/backend/uploads/enterprises"
BASE_URL = "https://image-fix-demo.preview.emergentagent.com"
MAX_ENTERPRISES = 50  # Par batch
MAX_IMAGES = 15

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
os.makedirs(UPLOADS_DIR, exist_ok=True)


async def search_enterprise_info(page, enterprise_name: str, city: str) -> dict:
    """Recherche les infos d'une entreprise sur local.ch"""
    result = {
        "website": None,
        "phone": None,
        "address": None,
        "description": None,
        "images": [],
        "found": False
    }
    
    try:
        # Recherche sur local.ch
        search_query = quote_plus(f"{enterprise_name} {city}")
        search_url = f"https://www.local.ch/fr/q/{search_query}"
        
        logger.info(f"    Recherche sur local.ch...")
        await page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(2000)
        
        # Cliquer sur le premier resultat
        first_result = await page.query_selector('a[href*="/fr/d/"]')
        if first_result:
            await first_result.click()
            await page.wait_for_timeout(3000)
            
            # Extraire le site web
            website_elem = await page.query_selector('a[href*="http"][class*="website"], a[data-test="website-link"]')
            if website_elem:
                result["website"] = await website_elem.get_attribute('href')
            
            # Extraire le telephone
            phone_elem = await page.query_selector('a[href^="tel:"]')
            if phone_elem:
                result["phone"] = await phone_elem.text_content()
            
            # Extraire l'adresse
            address_elem = await page.query_selector('[class*="address"], [data-test="address"]')
            if address_elem:
                result["address"] = await address_elem.text_content()
            
            # Extraire la description
            desc_elem = await page.query_selector('[class*="description"], [class*="about"]')
            if desc_elem:
                result["description"] = (await desc_elem.text_content())[:500]
            
            # Extraire les images
            img_elems = await page.query_selector_all('img[src*="local.ch"], img[class*="gallery"]')
            for img in img_elems[:5]:
                src = await img.get_attribute('src')
                if src and 'http' in src:
                    result["images"].append(src)
            
            result["found"] = True
            
    except Exception as e:
        logger.debug(f"    Erreur recherche: {e}")
    
    return result


async def download_and_save_image(url: str, enterprise_id: str, index: int) -> str:
    """Telecharge une image et retourne l'URL locale"""
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url)
            if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
                ext = 'jpg'
                if 'png' in response.headers.get('content-type', ''):
                    ext = 'png'
                
                filename = f"{enterprise_id}_img_{index}.{ext}"
                filepath = f"{UPLOADS_DIR}/{filename}"
                
                # Verifier la taille (min 5KB)
                if len(response.content) > 5000:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    return f"{BASE_URL}/api/uploads/enterprises/{filename}"
    except:
        pass
    return None


async def capture_website_data(page, url: str, enterprise_id: str) -> dict:
    """Capture les donnees d'un site web"""
    result = {
        "logo_url": None,
        "cover_url": None,
        "photos": [],
        "description": None,
        "products": []
    }
    
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(3000)
        
        # Screenshot cover
        cover_filename = f"{enterprise_id}_cover.jpg"
        cover_path = f"{UPLOADS_DIR}/{cover_filename}"
        await page.screenshot(path=cover_path, quality=85)
        result["cover_url"] = f"{BASE_URL}/api/uploads/enterprises/{cover_filename}"
        result["photos"].append(result["cover_url"])
        
        # Chercher le logo
        logo_selectors = ['img[alt*="logo" i]', 'img[src*="logo" i]', 'header img', '.logo img']
        for sel in logo_selectors:
            try:
                logo = await page.query_selector(sel)
                if logo:
                    box = await logo.bounding_box()
                    if box and box['width'] > 30:
                        logo_filename = f"{enterprise_id}_logo.png"
                        await logo.screenshot(path=f"{UPLOADS_DIR}/{logo_filename}")
                        result["logo_url"] = f"{BASE_URL}/api/uploads/enterprises/{logo_filename}"
                        break
            except:
                continue
        
        if not result["logo_url"]:
            result["logo_url"] = result["cover_url"]
        
        # Description
        desc_selectors = ['meta[name="description"]', 'meta[property="og:description"]', '.about p', 'main p']
        for sel in desc_selectors:
            try:
                elem = await page.query_selector(sel)
                if elem:
                    if sel.startswith('meta'):
                        content = await elem.get_attribute('content')
                    else:
                        content = await elem.text_content()
                    if content and len(content) > 30:
                        result["description"] = content[:600]
                        break
            except:
                continue
        
        # Images
        images = await page.query_selector_all('img')
        img_index = 1
        for img in images[:30]:
            try:
                src = await img.get_attribute('src')
                if src and not any(x in src.lower() for x in ['icon', 'logo', 'pixel', '1x1']):
                    if not src.startswith('http'):
                        src = urljoin(url, src)
                    box = await img.bounding_box()
                    if box and box['width'] > 150 and box['height'] > 100:
                        saved = await download_and_save_image(src, enterprise_id, img_index)
                        if saved:
                            result["photos"].append(saved)
                            img_index += 1
                            if img_index > MAX_IMAGES:
                                break
            except:
                continue
        
        # Produits
        product_selectors = ['[class*="product"]', '[class*="item"]', '.card', '[class*="article"]']
        for sel in product_selectors:
            try:
                products = await page.query_selector_all(sel)
                for prod in products[:20]:
                    product_data = {}
                    
                    # Nom
                    name_elem = await prod.query_selector('h2, h3, h4, .title, [class*="name"]')
                    if name_elem:
                        name = await name_elem.text_content()
                        if name and len(name.strip()) > 2 and len(name.strip()) < 100:
                            product_data["name"] = name.strip()
                    
                    # Prix
                    price_elem = await prod.query_selector('.price, [class*="price"], [class*="prix"]')
                    if price_elem:
                        price_text = await price_elem.text_content()
                        match = re.search(r'[\d.,]+', price_text.replace("'", "").replace(" ", ""))
                        if match:
                            try:
                                product_data["price"] = float(match.group().replace(',', '.'))
                            except:
                                pass
                    
                    # Image
                    img_elem = await prod.query_selector('img')
                    if img_elem:
                        src = await img_elem.get_attribute('src')
                        if src:
                            if not src.startswith('http'):
                                src = urljoin(url, src)
                            product_data["image"] = src
                    
                    if product_data.get("name"):
                        result["products"].append(product_data)
                
                if result["products"]:
                    break
            except:
                continue
        
    except Exception as e:
        logger.debug(f"    Erreur capture: {e}")
    
    return result


async def generate_description_from_name(name: str, category: str, city: str) -> str:
    """Genere une description basique si aucune n'est trouvee"""
    templates = {
        "Beauté & Bien-être": f"{name} est un etablissement de beaute et bien-etre situe a {city}. Nous offrons des services professionnels pour prendre soin de vous.",
        "Restaurant": f"{name} vous accueille a {city} pour une experience culinaire unique. Decouvrez notre cuisine et notre ambiance chaleureuse.",
        "Commerce": f"{name}, votre commerce de proximite a {city}. Nous proposons une large gamme de produits pour repondre a vos besoins.",
        "Services": f"{name} propose des services professionnels de qualite a {city}. Contactez-nous pour plus d'informations.",
    }
    return templates.get(category, f"{name} est une entreprise locale situee a {city}. Bienvenue!")


async def main():
    logger.info("=" * 70)
    logger.info("   ENRICHISSEMENT COMPLET DES ENTREPRISES")
    logger.info("   Recherche web + Images + Produits")
    logger.info("=" * 70)
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.titelli
    
    # Entreprises a enrichir (sans photos ou logo generique)
    query = {
        "$or": [
            {"photos": {"$exists": False}},
            {"photos": []},
            {"photos": None},
            {"logo_url": {"$exists": False}},
            {"logo_url": None},
            {"logo_url": {"$regex": "ui-avatars.com"}}
        ]
    }
    
    enterprises = await db.enterprises.find(query).limit(MAX_ENTERPRISES).to_list(length=MAX_ENTERPRISES)
    logger.info(f"\nEntreprises a enrichir: {len(enterprises)}")
    
    if not enterprises:
        logger.info("Toutes les entreprises sont deja enrichies!")
        return
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        success = 0
        errors = 0
        products_added = 0
        
        for i, ent in enumerate(enterprises):
            ent_id = ent.get('id')
            name = ent.get('name', ent.get('business_name', 'Unknown'))
            city = ent.get('city', 'Lausanne')
            category = ent.get('category', 'Services')
            
            logger.info(f"\n[{i+1}/{len(enterprises)}] {name} ({city})")
            
            update_data = {
                "enriched_at": datetime.now(timezone.utc).isoformat()
            }
            
            try:
                # 1. Rechercher sur local.ch
                search_result = await search_enterprise_info(page, name, city)
                
                if search_result["found"]:
                    logger.info(f"    Trouve sur local.ch!")
                    
                    if search_result["website"]:
                        update_data["website"] = search_result["website"]
                        logger.info(f"    Site web: {search_result['website'][:50]}")
                        
                        # 2. Capturer le site web
                        website_data = await capture_website_data(page, search_result["website"], ent_id)
                        
                        if website_data["logo_url"]:
                            update_data["logo_url"] = website_data["logo_url"]
                            update_data["logo"] = website_data["logo_url"]
                        
                        if website_data["cover_url"]:
                            update_data["cover_url"] = website_data["cover_url"]
                            update_data["cover_image"] = website_data["cover_url"]
                        
                        if website_data["photos"]:
                            update_data["photos"] = website_data["photos"]
                            update_data["gallery"] = website_data["photos"]
                        
                        if website_data["description"]:
                            update_data["description"] = website_data["description"]
                        
                        # Ajouter les produits
                        for prod in website_data.get("products", []):
                            existing = await db.products.find_one({
                                "enterprise_id": ent_id,
                                "name": prod["name"]
                            })
                            if not existing and prod.get("name"):
                                await db.products.insert_one({
                                    "id": str(uuid.uuid4()),
                                    "enterprise_id": ent_id,
                                    "name": prod["name"],
                                    "price": prod.get("price", 0),
                                    "images": [prod["image"]] if prod.get("image") else [],
                                    "category": category,
                                    "is_active": True,
                                    "created_at": datetime.now(timezone.utc).isoformat(),
                                    "source": "scraping"
                                })
                                products_added += 1
                    
                    if search_result["phone"]:
                        update_data["phone"] = search_result["phone"]
                    
                    if search_result["address"]:
                        update_data["address"] = search_result["address"]
                    
                    if search_result["images"]:
                        imgs = update_data.get("photos", [])
                        for img_url in search_result["images"]:
                            saved = await download_and_save_image(img_url, ent_id, len(imgs))
                            if saved:
                                imgs.append(saved)
                        update_data["photos"] = imgs
                        update_data["gallery"] = imgs
                
                # Si pas de description, en generer une
                if not update_data.get("description"):
                    update_data["description"] = await generate_description_from_name(name, category, city)
                
                # Si pas de logo, creer un screenshot du nom sur Google
                if not update_data.get("logo_url"):
                    try:
                        search_url = f"https://www.google.com/search?q={quote_plus(name + ' ' + city)}&tbm=isch"
                        await page.goto(search_url, wait_until="domcontentloaded", timeout=10000)
                        await page.wait_for_timeout(2000)
                        
                        # Premier resultat image
                        first_img = await page.query_selector('img[class*="rg_i"]')
                        if first_img:
                            logo_filename = f"{ent_id}_logo.png"
                            await first_img.screenshot(path=f"{UPLOADS_DIR}/{logo_filename}")
                            update_data["logo_url"] = f"{BASE_URL}/api/uploads/enterprises/{logo_filename}"
                            update_data["logo"] = update_data["logo_url"]
                    except:
                        pass
                
                # Mettre a jour la DB
                await db.enterprises.update_one(
                    {"id": ent_id},
                    {"$set": update_data}
                )
                
                photos_count = len(update_data.get("photos", []))
                logger.info(f"    => OK: {photos_count} photos, description: {'Oui' if update_data.get('description') else 'Non'}")
                success += 1
                
                await asyncio.sleep(3)  # Pause entre chaque
                
            except Exception as e:
                logger.error(f"    => ERREUR: {e}")
                errors += 1
        
        await browser.close()
    
    logger.info("\n" + "=" * 70)
    logger.info("   RESUME")
    logger.info("=" * 70)
    logger.info(f"  Succes: {success}/{len(enterprises)}")
    logger.info(f"  Erreurs: {errors}")
    logger.info(f"  Produits ajoutes: {products_added}")
    logger.info("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
