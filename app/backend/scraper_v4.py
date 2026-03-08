#!/usr/bin/env python3
from dotenv import load_dotenv
load_dotenv()
"""
SCRAPER V4 - RECHERCHE GOOGLE POUR SITES WEB
"""

import asyncio
import os
import logging
import uuid
import re
from datetime import datetime, timezone
from urllib.parse import quote_plus, urljoin
from motor.motor_asyncio import AsyncIOMotorClient
from playwright.async_api import async_playwright
import httpx

MONGO_URL = os.environ.get('MONGO_URL')
UPLOADS_DIR = "/app/backend/uploads/enterprises"
BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://image-fix-demo.preview.emergentagent.com")
MAX_ENTERPRISES = 500
MAX_IMAGES = 20

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)
os.makedirs(UPLOADS_DIR, exist_ok=True)


async def download_image(url: str, filepath: str, min_size: int = 5000) -> bool:
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200 and 'image' in resp.headers.get('content-type', ''):
                if len(resp.content) > min_size:
                    with open(filepath, 'wb') as f:
                        f.write(resp.content)
                    return True
    except:
        pass
    return False


async def find_website_google(page, name: str, city: str) -> str:
    """Trouve le site officiel via Google"""
    try:
        search_query = f"{name} {city} site officiel"
        search_url = f"https://www.google.com/search?q={quote_plus(search_query)}"
        
        await page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(2000)
        
        # Chercher les liens dans les resultats
        links = await page.query_selector_all('a[href^="http"]')
        
        exclude_domains = ['google.', 'facebook.', 'instagram.', 'linkedin.', 'youtube.', 
                          'twitter.', 'local.ch', 'search.ch', 'maps.', 'yelp.', 'tripadvisor.']
        
        for link in links[:20]:
            href = await link.get_attribute('href')
            if href:
                # Filtrer les domaines non pertinents
                if not any(d in href.lower() for d in exclude_domains):
                    # Verifier que c'est bien un site d'entreprise
                    if '.ch' in href or '.com' in href or '.net' in href:
                        return href
                        
    except Exception as e:
        logger.debug(f"Erreur recherche Google: {e}")
    
    return None


async def scrape_all_images(page, url: str, enterprise_id: str) -> dict:
    """Scrape toutes les images et donnees d'un site"""
    result = {"images": [], "products": [], "description": None, "logo": None}
    
    try:
        logger.info(f"      Visite: {url[:50]}...")
        await page.goto(url, wait_until="networkidle", timeout=25000)
        await page.wait_for_timeout(3000)
        
        # Cover screenshot
        cover_file = f"{enterprise_id}_cover.jpg"
        await page.screenshot(path=f"{UPLOADS_DIR}/{cover_file}", quality=85)
        result["images"].append(f"{BASE_URL}/api/uploads/enterprises/{cover_file}")
        
        # Logo
        for sel in ['img[alt*="logo" i]', 'img[src*="logo" i]', 'header img', '.logo img']:
            try:
                logo = await page.query_selector(sel)
                if logo:
                    box = await logo.bounding_box()
                    if box and box['width'] > 40:
                        logo_file = f"{enterprise_id}_logo.png"
                        await logo.screenshot(path=f"{UPLOADS_DIR}/{logo_file}")
                        result["logo"] = f"{BASE_URL}/api/uploads/enterprises/{logo_file}"
                        logger.info(f"      Logo extrait!")
                        break
            except:
                continue
        
        # Description
        for sel in ['meta[name="description"]', 'meta[property="og:description"]', '.about p', 'main p']:
            try:
                elem = await page.query_selector(sel)
                if elem:
                    text = await elem.get_attribute('content') if 'meta' in sel else await elem.text_content()
                    if text and len(text.strip()) > 50:
                        result["description"] = text.strip()[:800]
                        break
            except:
                continue
        
        # Toutes les images
        all_imgs = await page.query_selector_all('img')
        img_idx = 0
        
        for img in all_imgs:
            if img_idx >= MAX_IMAGES:
                break
            try:
                src = await img.get_attribute('src') or await img.get_attribute('data-src')
                if src:
                    if not src.startswith('http'):
                        src = urljoin(url, src)
                    
                    # Filtrer icones
                    if any(x in src.lower() for x in ['icon', 'logo', 'pixel', '1x1', 'spacer']):
                        continue
                    
                    box = await img.bounding_box()
                    if box and box['width'] > 120 and box['height'] > 80:
                        filename = f"{enterprise_id}_img_{img_idx}.jpg"
                        filepath = f"{UPLOADS_DIR}/{filename}"
                        
                        if await download_image(src, filepath, min_size=8000):
                            result["images"].append(f"{BASE_URL}/api/uploads/enterprises/{filename}")
                            img_idx += 1
            except:
                continue
        
        logger.info(f"      {len(result['images'])} images extraites")
        
        # Produits
        for sel in ['[class*="product"]', '[class*="item"]', '.card']:
            try:
                prods = await page.query_selector_all(sel)
                for p in prods[:30]:
                    product = {}
                    
                    # Nom
                    name_el = await p.query_selector('h2, h3, h4, .title, [class*="name"]')
                    if name_el:
                        name = await name_el.text_content()
                        if name and 2 < len(name.strip()) < 100:
                            product["name"] = name.strip()
                    
                    # Prix
                    price_el = await p.query_selector('.price, [class*="price"]')
                    if price_el:
                        price_text = await price_el.text_content()
                        match = re.search(r'[\d.,]+', price_text.replace("'", ""))
                        if match:
                            try:
                                product["price"] = float(match.group().replace(',', '.'))
                            except:
                                pass
                    
                    # Image
                    img_el = await p.query_selector('img')
                    if img_el:
                        product["image"] = await img_el.get_attribute('src')
                    
                    if product.get("name"):
                        result["products"].append(product)
                
                if result["products"]:
                    logger.info(f"      {len(result['products'])} produits detectes!")
                    break
            except:
                continue
        
        # Full page screenshot
        try:
            full_file = f"{enterprise_id}_full.jpg"
            await page.screenshot(path=f"{UPLOADS_DIR}/{full_file}", quality=70, full_page=True)
            result["images"].append(f"{BASE_URL}/api/uploads/enterprises/{full_file}")
        except:
            pass
            
    except Exception as e:
        logger.warning(f"      Erreur: {e}")
    
    return result


async def generate_logo(name: str, ent_id: str) -> str:
    initials = ''.join([w[0] for w in name.split()[:2]]).upper()
    colors = ['F59E0B', '10B981', '3B82F6', 'EF4444', '8B5CF6', 'EC4899']
    color = colors[hash(name) % len(colors)]
    
    url = f"https://ui-avatars.com/api/?name={quote_plus(initials)}&background={color}&color=fff&size=400&bold=true"
    filepath = f"{UPLOADS_DIR}/{ent_id}_logo.png"
    
    if await download_image(url, filepath, 1000):
        return f"{BASE_URL}/api/uploads/enterprises/{ent_id}_logo.png"
    return None


def gen_description(name: str, category: str, city: str) -> str:
    templates = {
        "Beauté & Bien-être": f"Bienvenue chez {name}, votre salon de beaute a {city}. Notre equipe de professionnels vous accueille pour sublimer votre beaute.",
        "Restaurant": f"{name} vous accueille a {city} pour une experience culinaire unique. Decouvrez notre cuisine savoureuse.",
        "Commerce": f"{name}, votre commerce de proximite a {city}. Qualite et service personnalise.",
    }
    return templates.get(category, f"{name} est une entreprise locale a {city}. Contactez-nous!")


async def main():
    logger.info("=" * 60)
    logger.info("   SCRAPER V4 - GOOGLE SEARCH")
    logger.info("=" * 60)
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[os.environ.get("DB_NAME", "secondevie")]
    
    # Entreprises non enrichies V4
    query = {
        "$or": [
            {"enrichment_version": {"$ne": "v4"}},
            {"photos": {"$exists": False}},
            {"photos": []}
        ]
    }
    
    enterprises = await db.enterprises.find(query).limit(MAX_ENTERPRISES).to_list(length=MAX_ENTERPRISES)
    logger.info(f"Entreprises: {len(enterprises)}\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await ctx.new_page()
        
        stats = {"ok": 0, "err": 0, "img": 0, "prod": 0}
        
        for i, ent in enumerate(enterprises):
            ent_id = ent.get('id')
            name = ent.get('name', 'Unknown')
            city = ent.get('city', 'Lausanne')
            category = ent.get('category', 'Services')
            
            logger.info(f"[{i+1}/{len(enterprises)}] {name}")
            
            try:
                # Chercher le site web
                website = await find_website_google(page, name, city)
                
                data = {"images": [], "products": []}
                
                if website:
                    logger.info(f"   Site: {website[:50]}...")
                    data = await scrape_all_images(page, website, ent_id)
                else:
                    # Screenshot Google comme fallback
                    cover_file = f"{ent_id}_cover.jpg"
                    search_url = f"https://www.google.com/search?q={quote_plus(name + ' ' + city)}&tbm=isch"
                    await page.goto(search_url, timeout=10000)
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path=f"{UPLOADS_DIR}/{cover_file}", quality=85)
                    data["images"] = [f"{BASE_URL}/api/uploads/enterprises/{cover_file}"]
                
                # Update DB
                update = {
                    "enriched_at": datetime.now(timezone.utc).isoformat(),
                    "enrichment_version": "v4"
                }
                
                if data["images"]:
                    update["photos"] = data["images"]
                    update["gallery"] = data["images"]
                    update["cover_image"] = data["images"][0]
                
                if data.get("logo"):
                    update["logo_url"] = data["logo"]
                    update["logo"] = data["logo"]
                else:
                    logo = await generate_logo(name, ent_id)
                    if logo:
                        update["logo_url"] = logo
                        update["logo"] = logo
                
                if data.get("description"):
                    update["description"] = data["description"]
                else:
                    update["description"] = gen_description(name, category, city)
                
                if website:
                    update["website"] = website
                
                await db.enterprises.update_one({"id": ent_id}, {"$set": update})
                
                # Ajouter produits
                for prod in data.get("products", []):
                    if prod.get("name"):
                        exists = await db.products.find_one({"enterprise_id": ent_id, "name": prod["name"]})
                        if not exists:
                            await db.products.insert_one({
                                "id": str(uuid.uuid4()),
                                "enterprise_id": ent_id,
                                "name": prod["name"],
                                "price": prod.get("price", 0),
                                "images": [prod.get("image")] if prod.get("image") else [],
                                "is_active": True,
                                "created_at": datetime.now(timezone.utc).isoformat(),
                                "source": "scraping_v4"
                            })
                            stats["prod"] += 1
                
                stats["ok"] += 1
                stats["img"] += len(data.get("images", []))
                logger.info(f"   => OK: {len(data.get('images', []))} images\n")
                
                await asyncio.sleep(3)
                
            except Exception as e:
                logger.error(f"   => ERREUR: {e}\n")
                stats["err"] += 1
        
        await browser.close()
    
    logger.info("=" * 60)
    logger.info(f"   TERMINE: {stats['ok']} OK, {stats['err']} erreurs")
    logger.info(f"   Images: {stats['img']}, Produits: {stats['prod']}")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
