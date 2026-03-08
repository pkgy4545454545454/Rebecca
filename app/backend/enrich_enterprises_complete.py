#!/usr/bin/env python3
"""
Script d'enrichissement COMPLET des profils entreprises
- Capture screenshots du site web
- Extrait logos et images de couverture
- Recupere TOUTES les images du site
- Detecte et extrait les produits
- Met a jour les profils dans MongoDB
"""

import asyncio
import os
import sys
import logging
import uuid
import shutil
import re
import json
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin
from motor.motor_asyncio import AsyncIOMotorClient
from playwright.async_api import async_playwright
import httpx

# Configuration
MONGO_URL = os.environ.get('MONGO_URL', "mongodb+srv://prankgy:Minijetaime1996@cluster0.kwjifsg.mongodb.net/secondevie?retryWrites=true&w=majority&appName=Cluster0")
UPLOADS_DIR = "/app/backend/uploads/enterprises"
BASE_URL = "https://image-fix-demo.preview.emergentagent.com"
MAX_ENTERPRISES = 100  # Nombre d'entreprises a traiter par batch
MAX_IMAGES_PER_SITE = 20  # Max images a recuperer par site
MAX_PRODUCTS_PER_SITE = 30  # Max produits a detecter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Creer le dossier uploads si necessaire
os.makedirs(UPLOADS_DIR, exist_ok=True)


async def download_image(url: str, enterprise_id: str, index: int) -> str:
    """Telecharge une image et la sauvegarde localement"""
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type:
                    ext = 'jpg'
                    if 'png' in content_type:
                        ext = 'png'
                    elif 'webp' in content_type:
                        ext = 'webp'
                    elif 'gif' in content_type:
                        ext = 'gif'
                    
                    filename = f"{enterprise_id}_img_{index}.{ext}"
                    filepath = f"{UPLOADS_DIR}/{filename}"
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    return f"{BASE_URL}/api/uploads/enterprises/{filename}"
    except Exception as e:
        logger.debug(f"Erreur download image {url}: {e}")
    return None


async def extract_site_data(page, url: str, enterprise_id: str) -> dict:
    """Extrait toutes les donnees d'un site web"""
    result = {
        "cover_url": None,
        "logo_url": None,
        "photos": [],
        "description": None,
        "products": [],
        "videos": [],
        "error": None
    }
    
    try:
        # Naviguer vers le site
        logger.info(f"  Visite de {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(3000)
        
        # 1. SCREENSHOT PRINCIPAL (cover)
        cover_filename = f"{enterprise_id}_cover.jpg"
        cover_path = f"{UPLOADS_DIR}/{cover_filename}"
        await page.screenshot(path=cover_path, quality=85, full_page=False)
        result["cover_url"] = f"{BASE_URL}/api/uploads/enterprises/{cover_filename}"
        result["photos"].append(result["cover_url"])
        logger.info(f"    - Cover capturee")
        
        # 2. EXTRACTION DU LOGO
        logo_selectors = [
            'img[alt*="logo" i]',
            'img[src*="logo" i]',
            'img[class*="logo" i]',
            'a[class*="logo" i] img',
            'header img:first-of-type',
            'nav img:first-of-type',
            '.logo img',
            '#logo img',
            '[class*="brand"] img',
            '[class*="header"] img:first-of-type'
        ]
        
        for selector in logo_selectors:
            try:
                logo_elem = await page.query_selector(selector)
                if logo_elem:
                    logo_src = await logo_elem.get_attribute('src')
                    if logo_src:
                        if not logo_src.startswith('http'):
                            logo_src = urljoin(url, logo_src)
                        # Telecharger le logo
                        logo_filename = f"{enterprise_id}_logo.png"
                        logo_path = f"{UPLOADS_DIR}/{logo_filename}"
                        try:
                            logo_box = await logo_elem.bounding_box()
                            if logo_box and logo_box['width'] > 30:
                                await logo_elem.screenshot(path=logo_path)
                                result["logo_url"] = f"{BASE_URL}/api/uploads/enterprises/{logo_filename}"
                                logger.info(f"    - Logo trouve")
                                break
                        except:
                            result["logo_url"] = logo_src
                            break
            except:
                continue
        
        # Si pas de logo, utiliser le cover
        if not result["logo_url"]:
            result["logo_url"] = result["cover_url"]
        
        # 3. EXTRACTION DE LA DESCRIPTION
        desc_selectors = [
            'meta[name="description"]',
            'meta[property="og:description"]',
            '[class*="about"] p',
            '[class*="description"] p',
            '[id*="about"] p',
            'main p:first-of-type',
            '.intro p',
            '.presentation p',
            'article p:first-of-type'
        ]
        
        for selector in desc_selectors:
            try:
                if selector.startswith('meta'):
                    elem = await page.query_selector(selector)
                    if elem:
                        content = await elem.get_attribute('content')
                        if content and len(content) > 30:
                            result["description"] = content[:800]
                            break
                else:
                    elems = await page.query_selector_all(selector)
                    for elem in elems[:3]:
                        text = await elem.text_content()
                        if text and len(text.strip()) > 50:
                            result["description"] = text.strip()[:800]
                            break
                    if result["description"]:
                        break
            except:
                continue
        
        if result["description"]:
            logger.info(f"    - Description extraite ({len(result['description'])} chars)")
        
        # 4. EXTRACTION DE TOUTES LES IMAGES
        image_urls = set()
        img_elements = await page.query_selector_all('img')
        
        for img in img_elements[:50]:  # Limiter a 50 elements
            try:
                src = await img.get_attribute('src')
                if src:
                    if not src.startswith('http'):
                        src = urljoin(url, src)
                    # Filtrer les petites images et icones
                    if not any(x in src.lower() for x in ['icon', 'favicon', 'pixel', 'tracking', 'spacer', '1x1']):
                        box = await img.bounding_box()
                        if box and box['width'] > 100 and box['height'] > 100:
                            image_urls.add(src)
            except:
                continue
        
        # Telecharger les images
        img_index = 0
        for img_url in list(image_urls)[:MAX_IMAGES_PER_SITE]:
            if img_index >= MAX_IMAGES_PER_SITE:
                break
            downloaded = await download_image(img_url, enterprise_id, img_index)
            if downloaded and downloaded not in result["photos"]:
                result["photos"].append(downloaded)
                img_index += 1
        
        logger.info(f"    - {len(result['photos'])} images recuperees")
        
        # 5. EXTRACTION DES VIDEOS
        video_selectors = [
            'video source',
            'video',
            'iframe[src*="youtube"]',
            'iframe[src*="vimeo"]',
            '[class*="video"] iframe'
        ]
        
        for selector in video_selectors:
            try:
                elems = await page.query_selector_all(selector)
                for elem in elems[:5]:
                    src = await elem.get_attribute('src')
                    if src:
                        if not src.startswith('http'):
                            src = urljoin(url, src)
                        if src not in result["videos"]:
                            result["videos"].append(src)
            except:
                continue
        
        if result["videos"]:
            logger.info(f"    - {len(result['videos'])} videos trouvees")
        
        # 6. DETECTION DES PRODUITS
        product_selectors = [
            '[class*="product"]',
            '[class*="produit"]',
            '[class*="item"]',
            '[class*="card"]',
            '[class*="article"]',
            '.shop-item',
            '.woocommerce-loop-product',
            '[data-product]'
        ]
        
        for selector in product_selectors:
            try:
                products = await page.query_selector_all(selector)
                for prod in products[:MAX_PRODUCTS_PER_SITE]:
                    if len(result["products"]) >= MAX_PRODUCTS_PER_SITE:
                        break
                    
                    product_data = {"id": str(uuid.uuid4())}
                    
                    # Nom du produit
                    name_elem = await prod.query_selector('h2, h3, h4, .title, .name, [class*="title"], [class*="name"]')
                    if name_elem:
                        name = await name_elem.text_content()
                        if name and len(name.strip()) > 2:
                            product_data["name"] = name.strip()[:100]
                    
                    # Prix
                    price_elem = await prod.query_selector('.price, [class*="price"], [class*="prix"], .amount')
                    if price_elem:
                        price_text = await price_elem.text_content()
                        if price_text:
                            # Extraire le prix numerique
                            price_match = re.search(r'[\d.,]+', price_text.replace("'", ""))
                            if price_match:
                                try:
                                    price = float(price_match.group().replace(',', '.'))
                                    product_data["price"] = price
                                except:
                                    pass
                    
                    # Image du produit
                    img_elem = await prod.query_selector('img')
                    if img_elem:
                        img_src = await img_elem.get_attribute('src')
                        if img_src:
                            if not img_src.startswith('http'):
                                img_src = urljoin(url, img_src)
                            product_data["image"] = img_src
                    
                    # Description
                    desc_elem = await prod.query_selector('p, .description, [class*="desc"]')
                    if desc_elem:
                        desc = await desc_elem.text_content()
                        if desc and len(desc.strip()) > 10:
                            product_data["description"] = desc.strip()[:300]
                    
                    # Ajouter seulement si on a un nom
                    if product_data.get("name"):
                        result["products"].append(product_data)
                
                if result["products"]:
                    break  # On a trouve des produits, on arrete
            except:
                continue
        
        if result["products"]:
            logger.info(f"    - {len(result['products'])} produits detectes")
        
        # 7. SCREENSHOT FULL PAGE (optionnel)
        try:
            full_filename = f"{enterprise_id}_full.jpg"
            full_path = f"{UPLOADS_DIR}/{full_filename}"
            await page.screenshot(path=full_path, quality=70, full_page=True)
            result["photos"].append(f"{BASE_URL}/api/uploads/enterprises/{full_filename}")
        except:
            pass
        
    except Exception as e:
        result["error"] = str(e)[:200]
        logger.warning(f"    - ERREUR: {e}")
    
    return result


async def update_enterprise_in_db(db, enterprise: dict, data: dict):
    """Met a jour l'entreprise dans MongoDB avec les nouvelles donnees"""
    enterprise_id = enterprise.get('id')
    update_fields = {
        "enriched_at": datetime.now(timezone.utc).isoformat(),
        "enrichment_source": enterprise.get('website', '')
    }
    
    if data.get("cover_url"):
        update_fields["cover_url"] = data["cover_url"]
        update_fields["cover_image"] = data["cover_url"]
    
    if data.get("logo_url"):
        update_fields["logo_url"] = data["logo_url"]
        update_fields["logo"] = data["logo_url"]
    
    if data.get("description"):
        update_fields["description"] = data["description"]
    
    if data.get("photos"):
        update_fields["photos"] = data["photos"]
        update_fields["gallery"] = data["photos"]
    
    if data.get("videos"):
        update_fields["videos"] = data["videos"]
    
    # Mise a jour entreprise
    await db.enterprises.update_one(
        {"id": enterprise_id},
        {"$set": update_fields}
    )
    
    # Ajouter les produits detectes
    if data.get("products"):
        for product in data["products"]:
            # Verifier si le produit existe deja
            existing = await db.products.find_one({
                "enterprise_id": enterprise_id,
                "name": product.get("name")
            })
            
            if not existing:
                product_doc = {
                    "id": product.get("id", str(uuid.uuid4())),
                    "enterprise_id": enterprise_id,
                    "name": product.get("name", "Produit"),
                    "description": product.get("description", ""),
                    "price": product.get("price", 0),
                    "images": [product.get("image")] if product.get("image") else [],
                    "category": enterprise.get("category", "autre"),
                    "is_active": True,
                    "stock": 100,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "source": "scraping"
                }
                await db.products.insert_one(product_doc)
        
        logger.info(f"    - {len(data['products'])} produits ajoutes a la DB")
    
    return True


async def main():
    logger.info("=" * 70)
    logger.info("   ENRICHISSEMENT COMPLET DES PROFILS ENTREPRISES")
    logger.info("   Photos, Videos, Produits, Descriptions")
    logger.info("=" * 70)
    
    # Connexion MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.titelli
    
    # Trouver les entreprises a enrichir (avec site web, pas encore enrichies)
    query = {
        "$and": [
            {"$or": [
                {"website": {"$exists": True, "$ne": None, "$ne": ""}},
                {"contact.website": {"$exists": True, "$ne": None, "$ne": ""}}
            ]},
            {"$or": [
                {"enriched_at": {"$exists": False}},
                {"photos": {"$exists": False}},
                {"photos": []},
                {"photos": None}
            ]}
        ]
    }
    
    enterprises = await db.enterprises.find(query).limit(MAX_ENTERPRISES).to_list(length=MAX_ENTERPRISES)
    
    logger.info(f"\nEntreprises a enrichir: {len(enterprises)}")
    
    if not enterprises:
        logger.info("Aucune entreprise a enrichir!")
        
        # Chercher toutes les entreprises avec site web
        all_with_website = await db.enterprises.find({
            "$or": [
                {"website": {"$exists": True, "$ne": None, "$ne": ""}},
                {"contact.website": {"$exists": True, "$ne": None, "$ne": ""}}
            ]
        }).limit(MAX_ENTERPRISES).to_list(length=MAX_ENTERPRISES)
        
        logger.info(f"Entreprises avec site web: {len(all_with_website)}")
        enterprises = all_with_website
    
    if not enterprises:
        logger.info("Aucune entreprise avec site web trouve!")
        return
    
    # Lancer Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        success_count = 0
        error_count = 0
        products_added = 0
        
        for i, enterprise in enumerate(enterprises):
            enterprise_id = enterprise.get('id', str(uuid.uuid4()))
            name = enterprise.get('name', enterprise.get('business_name', 'Unknown'))
            website = enterprise.get('website') or enterprise.get('contact', {}).get('website', '')
            
            if not website:
                continue
            
            # Normaliser l'URL
            if not website.startswith('http'):
                website = f"https://{website}"
            
            logger.info(f"\n[{i+1}/{len(enterprises)}] {name}")
            logger.info(f"  URL: {website}")
            
            try:
                # Extraire les donnees du site
                data = await extract_site_data(page, website, enterprise_id)
                
                if data.get("error"):
                    error_count += 1
                    continue
                
                # Mettre a jour la DB
                await update_enterprise_in_db(db, enterprise, data)
                
                success_count += 1
                products_added += len(data.get("products", []))
                
                logger.info(f"  => SUCCESS: {len(data.get('photos', []))} photos, {len(data.get('products', []))} produits")
                
                # Pause pour ne pas surcharger
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"  => ERREUR: {e}")
                error_count += 1
        
        await browser.close()
    
    # Resume
    logger.info("\n" + "=" * 70)
    logger.info("   RESUME ENRICHISSEMENT")
    logger.info("=" * 70)
    logger.info(f"  Entreprises traitees: {success_count + error_count}")
    logger.info(f"  Succes: {success_count}")
    logger.info(f"  Erreurs: {error_count}")
    logger.info(f"  Produits ajoutes: {products_added}")
    logger.info("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
