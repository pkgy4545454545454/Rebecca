#!/usr/bin/env python3
"""
SCRAPER ENTREPRISES V3 - EXTRACTION MAXIMALE
=============================================
1. Recherche le site web de l'entreprise sur local.ch
2. Visite le site web et extrait TOUTES les images
3. Detecte les produits avec prix et descriptions
4. Sauvegarde tout dans MongoDB
"""

import asyncio
import os
import logging
import uuid
import re
import json
from datetime import datetime, timezone
from urllib.parse import quote_plus, urljoin, urlparse
from motor.motor_asyncio import AsyncIOMotorClient
from playwright.async_api import async_playwright
import httpx

# Configuration
MONGO_URL = os.environ.get('MONGO_URL')
UPLOADS_DIR = "/app/backend/uploads/enterprises"
BASE_URL = "https://image-fix-demo.preview.emergentagent.com"
MAX_ENTERPRISES = 100
MAX_IMAGES_PER_SITE = 30  # Maximum d'images par entreprise
MAX_PRODUCTS_PER_SITE = 50  # Maximum de produits

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)
os.makedirs(UPLOADS_DIR, exist_ok=True)


async def download_image(url: str, filepath: str, min_size: int = 5000) -> bool:
    """Telecharge une image si elle fait plus de min_size bytes"""
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            if resp.status_code == 200:
                content_type = resp.headers.get('content-type', '')
                if 'image' in content_type and len(resp.content) > min_size:
                    with open(filepath, 'wb') as f:
                        f.write(resp.content)
                    return True
    except Exception as e:
        pass
    return False


async def find_website_on_localch(page, name: str, city: str) -> dict:
    """Recherche sur local.ch pour trouver le site web et infos"""
    result = {"website": None, "phone": None, "address": None, "images": []}
    
    try:
        search_url = f"https://www.local.ch/fr/q/{quote_plus(name + ' ' + city)}"
        await page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(2000)
        
        # Cliquer sur le premier resultat
        first_link = await page.query_selector('a[href*="/fr/d/"]')
        if first_link:
            await first_link.click()
            await page.wait_for_timeout(3000)
            
            # Extraire le site web
            selectors = [
                'a[href^="http"][rel="noopener"]',
                'a[data-test="website-link"]',
                'a.website-link',
                'a[href*="www."]'
            ]
            for sel in selectors:
                elem = await page.query_selector(sel)
                if elem:
                    href = await elem.get_attribute('href')
                    if href and 'local.ch' not in href and href.startswith('http'):
                        result["website"] = href
                        break
            
            # Extraire telephone
            phone_elem = await page.query_selector('a[href^="tel:"]')
            if phone_elem:
                result["phone"] = await phone_elem.text_content()
            
            # Extraire adresse
            addr_elem = await page.query_selector('[class*="address"], address')
            if addr_elem:
                result["address"] = (await addr_elem.text_content()).strip()
            
            # Extraire images de la page local.ch
            imgs = await page.query_selector_all('img')
            for img in imgs[:10]:
                src = await img.get_attribute('src')
                if src and 'http' in src and 'local.ch' not in src:
                    result["images"].append(src)
                    
    except Exception as e:
        logger.debug(f"Erreur local.ch: {e}")
    
    return result


async def scrape_website_fully(page, url: str, enterprise_id: str) -> dict:
    """Scrape un site web et extrait TOUT: images, produits, infos"""
    result = {
        "images": [],
        "products": [],
        "description": None,
        "logo": None,
        "cover": None,
        "social_links": [],
        "services": []
    }
    
    try:
        logger.info(f"      Visite: {url}")
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)
        
        # ========== 1. SCREENSHOT COVER ==========
        cover_filename = f"{enterprise_id}_cover.jpg"
        cover_path = f"{UPLOADS_DIR}/{cover_filename}"
        await page.screenshot(path=cover_path, quality=85)
        result["cover"] = f"{BASE_URL}/api/uploads/enterprises/{cover_filename}"
        result["images"].append(result["cover"])
        
        # ========== 2. EXTRACTION DU LOGO ==========
        logo_selectors = [
            'img[alt*="logo" i]', 'img[src*="logo" i]', 'img[class*="logo" i]',
            'header img', 'nav img', '.logo img', '#logo img', 
            '[class*="brand"] img', 'a[class*="logo"] img'
        ]
        for sel in logo_selectors:
            try:
                logo = await page.query_selector(sel)
                if logo:
                    box = await logo.bounding_box()
                    if box and box['width'] > 40 and box['height'] > 40:
                        logo_filename = f"{enterprise_id}_logo.png"
                        logo_path = f"{UPLOADS_DIR}/{logo_filename}"
                        await logo.screenshot(path=logo_path)
                        result["logo"] = f"{BASE_URL}/api/uploads/enterprises/{logo_filename}"
                        logger.info(f"      Logo trouve!")
                        break
            except:
                continue
        
        # ========== 3. EXTRACTION DESCRIPTION ==========
        desc_selectors = [
            'meta[name="description"]', 'meta[property="og:description"]',
            '.about p', '#about p', '[class*="description"]', 
            '[class*="presentation"] p', '.intro p', 'main p'
        ]
        for sel in desc_selectors:
            try:
                elem = await page.query_selector(sel)
                if elem:
                    if 'meta' in sel:
                        text = await elem.get_attribute('content')
                    else:
                        text = await elem.text_content()
                    if text and len(text.strip()) > 50:
                        result["description"] = text.strip()[:1000]
                        break
            except:
                continue
        
        # ========== 4. EXTRACTION DE TOUTES LES IMAGES ==========
        all_images = await page.query_selector_all('img')
        image_urls = set()
        
        for img in all_images:
            try:
                src = await img.get_attribute('src')
                data_src = await img.get_attribute('data-src')
                srcset = await img.get_attribute('srcset')
                
                # Collecter toutes les sources d'images
                sources = [src, data_src]
                if srcset:
                    sources.extend([s.split()[0] for s in srcset.split(',')])
                
                for source in sources:
                    if source:
                        if not source.startswith('http'):
                            source = urljoin(url, source)
                        # Filtrer les petites images/icones
                        if not any(x in source.lower() for x in ['icon', 'favicon', 'pixel', '1x1', 'spacer', 'loading', 'spinner']):
                            box = await img.bounding_box()
                            if box and box['width'] > 100 and box['height'] > 80:
                                image_urls.add(source)
            except:
                continue
        
        # Telecharger les images
        img_idx = 0
        for img_url in list(image_urls)[:MAX_IMAGES_PER_SITE]:
            try:
                ext = 'jpg'
                if '.png' in img_url.lower():
                    ext = 'png'
                elif '.webp' in img_url.lower():
                    ext = 'webp'
                
                filename = f"{enterprise_id}_img_{img_idx}.{ext}"
                filepath = f"{UPLOADS_DIR}/{filename}"
                
                if await download_image(img_url, filepath, min_size=8000):
                    local_url = f"{BASE_URL}/api/uploads/enterprises/{filename}"
                    result["images"].append(local_url)
                    img_idx += 1
            except:
                continue
        
        logger.info(f"      {len(result['images'])} images extraites")
        
        # ========== 5. SCREENSHOT FULL PAGE ==========
        try:
            full_filename = f"{enterprise_id}_fullpage.jpg"
            full_path = f"{UPLOADS_DIR}/{full_filename}"
            await page.screenshot(path=full_path, quality=70, full_page=True)
            result["images"].append(f"{BASE_URL}/api/uploads/enterprises/{full_filename}")
        except:
            pass
        
        # ========== 6. DETECTION DES PRODUITS ==========
        product_selectors = [
            '[class*="product"]', '[class*="produit"]', '[class*="article"]',
            '[class*="item"]', '.card', '[class*="shop"]', '[class*="catalog"]',
            '.woocommerce-loop-product', '[data-product]', '[itemtype*="Product"]'
        ]
        
        for sel in product_selectors:
            try:
                products = await page.query_selector_all(sel)
                for prod in products[:MAX_PRODUCTS_PER_SITE]:
                    if len(result["products"]) >= MAX_PRODUCTS_PER_SITE:
                        break
                    
                    product = {"id": str(uuid.uuid4())}
                    
                    # NOM
                    name_sels = ['h1', 'h2', 'h3', 'h4', '.title', '.name', '[class*="title"]', '[class*="name"]']
                    for ns in name_sels:
                        name_el = await prod.query_selector(ns)
                        if name_el:
                            name = await name_el.text_content()
                            if name and 2 < len(name.strip()) < 150:
                                product["name"] = name.strip()
                                break
                    
                    # PRIX
                    price_sels = ['.price', '[class*="price"]', '[class*="prix"]', '.amount', '[class*="cost"]']
                    for ps in price_sels:
                        price_el = await prod.query_selector(ps)
                        if price_el:
                            price_text = await price_el.text_content()
                            # Extraire le nombre
                            match = re.search(r'[\d\'.,]+', price_text.replace(' ', ''))
                            if match:
                                try:
                                    price_str = match.group().replace("'", "").replace(',', '.')
                                    product["price"] = float(price_str)
                                    break
                                except:
                                    pass
                    
                    # IMAGE
                    img_el = await prod.query_selector('img')
                    if img_el:
                        img_src = await img_el.get_attribute('src') or await img_el.get_attribute('data-src')
                        if img_src:
                            if not img_src.startswith('http'):
                                img_src = urljoin(url, img_src)
                            product["image"] = img_src
                    
                    # DESCRIPTION
                    desc_sels = ['p', '.description', '[class*="desc"]', '.excerpt']
                    for ds in desc_sels:
                        desc_el = await prod.query_selector(ds)
                        if desc_el:
                            desc = await desc_el.text_content()
                            if desc and len(desc.strip()) > 10:
                                product["description"] = desc.strip()[:500]
                                break
                    
                    # Ajouter si on a au moins un nom
                    if product.get("name"):
                        result["products"].append(product)
                
                if result["products"]:
                    break
            except:
                continue
        
        if result["products"]:
            logger.info(f"      {len(result['products'])} produits detectes!")
        
        # ========== 7. SERVICES (pour prestataires) ==========
        service_selectors = [
            '[class*="service"]', '[class*="prestation"]', '[class*="tarif"]',
            '[class*="pricing"]', 'table tr', '.menu-item'
        ]
        
        for sel in service_selectors:
            try:
                services = await page.query_selector_all(sel)
                for serv in services[:20]:
                    service = {}
                    
                    # Nom du service
                    title = await serv.query_selector('h3, h4, .title, strong, td:first-child')
                    if title:
                        service["name"] = (await title.text_content()).strip()[:100]
                    
                    # Prix
                    price = await serv.query_selector('.price, [class*="price"], td:last-child')
                    if price:
                        price_text = await price.text_content()
                        match = re.search(r'[\d\'.,]+', price_text)
                        if match:
                            try:
                                service["price"] = float(match.group().replace("'", "").replace(',', '.'))
                            except:
                                pass
                    
                    if service.get("name") and len(service["name"]) > 2:
                        result["services"].append(service)
                
                if result["services"]:
                    break
            except:
                continue
        
        if result["services"]:
            logger.info(f"      {len(result['services'])} services detectes!")
        
        # ========== 8. LIENS SOCIAUX ==========
        social_patterns = ['facebook.com', 'instagram.com', 'twitter.com', 'linkedin.com', 'youtube.com', 'tiktok.com']
        links = await page.query_selector_all('a[href]')
        for link in links[:100]:
            href = await link.get_attribute('href')
            if href:
                for pattern in social_patterns:
                    if pattern in href and href not in result["social_links"]:
                        result["social_links"].append(href)
                        break
        
    except Exception as e:
        logger.warning(f"      Erreur scraping: {e}")
    
    return result


async def generate_logo_initials(name: str, enterprise_id: str) -> str:
    """Genere un logo avec initiales"""
    try:
        initials = ''.join([w[0] for w in name.split()[:2]]).upper()
        colors = ['F59E0B', '10B981', '3B82F6', 'EF4444', '8B5CF6', 'EC4899', '06B6D4', '84CC16']
        color = colors[hash(name) % len(colors)]
        
        url = f"https://ui-avatars.com/api/?name={quote_plus(initials)}&background={color}&color=fff&size=400&bold=true&format=png"
        filename = f"{enterprise_id}_logo.png"
        filepath = f"{UPLOADS_DIR}/{filename}"
        
        if await download_image(url, filepath, min_size=1000):
            return f"{BASE_URL}/api/uploads/enterprises/{filename}"
    except:
        pass
    return None


def generate_description(name: str, category: str, subcategory: str, city: str) -> str:
    """Genere une description professionnelle"""
    templates = {
        "Beauté & Bien-être": f"Bienvenue chez {name}, votre espace beaute et bien-etre a {city}. Notre equipe de professionnels passionnes vous accueille pour prendre soin de vous. Expertise, qualite et attention personnalisee sont au coeur de nos services.",
        "Restaurant": f"Decouvrez {name} a {city}, une adresse gourmande ou la passion culinaire rencontre la qualite des produits. Notre chef vous propose des plats savoureux prepares avec soin. Reservez votre table!",
        "Commerce": f"{name}, votre commerce de confiance a {city}. Nous selectionnons pour vous les meilleurs produits et vous accueillons avec professionnalisme. Venez decouvrir notre selection!",
        "Services": f"{name} vous propose des services professionnels de qualite a {city}. Notre expertise et notre engagement qualite font la difference. Contactez-nous!",
        "Santé": f"{name}, specialiste sante a {city}. Nous mettons notre expertise au service de votre bien-etre. Prenez rendez-vous pour une consultation personnalisee.",
    }
    
    desc = templates.get(category, f"{name} est une entreprise de confiance situee a {city}. Specialises en {subcategory or category}, nous mettons notre expertise a votre service.")
    return desc


async def save_to_database(db, enterprise: dict, scraped_data: dict, localch_data: dict):
    """Sauvegarde toutes les donnees dans MongoDB"""
    ent_id = enterprise.get('id')
    name = enterprise.get('name', enterprise.get('business_name', ''))
    category = enterprise.get('category', 'Services')
    subcategory = enterprise.get('subcategory', '')
    city = enterprise.get('city', 'Lausanne')
    
    update = {
        "enriched_at": datetime.now(timezone.utc).isoformat(),
        "enrichment_version": "v3"
    }
    
    # Images (galerie)
    all_images = scraped_data.get("images", [])
    if all_images:
        update["photos"] = all_images
        update["gallery"] = all_images
        update["cover_url"] = all_images[0]
        update["cover_image"] = all_images[0]
    
    # Logo
    if scraped_data.get("logo"):
        update["logo_url"] = scraped_data["logo"]
        update["logo"] = scraped_data["logo"]
    elif not enterprise.get("logo_url"):
        logo = await generate_logo_initials(name, ent_id)
        if logo:
            update["logo_url"] = logo
            update["logo"] = logo
    
    # Description
    if scraped_data.get("description"):
        update["description"] = scraped_data["description"]
    elif not enterprise.get("description"):
        update["description"] = generate_description(name, category, subcategory, city)
    
    # Site web
    if localch_data.get("website"):
        update["website"] = localch_data["website"]
    
    # Telephone
    if localch_data.get("phone"):
        update["phone"] = localch_data["phone"]
    
    # Adresse
    if localch_data.get("address"):
        update["address_full"] = localch_data["address"]
    
    # Liens sociaux
    if scraped_data.get("social_links"):
        update["social_links"] = scraped_data["social_links"]
    
    # Services
    if scraped_data.get("services"):
        update["services_list"] = scraped_data["services"]
    
    # Update enterprise
    await db.enterprises.update_one({"id": ent_id}, {"$set": update})
    
    # Ajouter les produits
    products_added = 0
    for prod in scraped_data.get("products", []):
        if not prod.get("name"):
            continue
        
        # Verifier si existe deja
        existing = await db.products.find_one({
            "enterprise_id": ent_id,
            "name": prod["name"]
        })
        
        if not existing:
            # Telecharger l'image du produit si disponible
            prod_img = None
            if prod.get("image"):
                try:
                    img_filename = f"{ent_id}_prod_{products_added}.jpg"
                    img_path = f"{UPLOADS_DIR}/{img_filename}"
                    if await download_image(prod["image"], img_path, min_size=3000):
                        prod_img = f"{BASE_URL}/api/uploads/enterprises/{img_filename}"
                except:
                    prod_img = prod.get("image")
            
            product_doc = {
                "id": prod.get("id", str(uuid.uuid4())),
                "enterprise_id": ent_id,
                "name": prod["name"],
                "description": prod.get("description", ""),
                "price": prod.get("price", 0),
                "images": [prod_img] if prod_img else [],
                "category": category,
                "subcategory": subcategory,
                "is_active": True,
                "stock": 100,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "source": "scraping_v3"
            }
            await db.products.insert_one(product_doc)
            products_added += 1
    
    return products_added


async def main():
    logger.info("=" * 70)
    logger.info("   SCRAPER ENTREPRISES V3 - EXTRACTION MAXIMALE")
    logger.info("   Images, Produits, Services, Descriptions")
    logger.info("=" * 70)
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.titelli
    
    # Entreprises a enrichir
    query = {
        "$or": [
            {"enrichment_version": {"$ne": "v3"}},
            {"photos": {"$exists": False}},
            {"photos": []},
            {"photos": None}
        ]
    }
    
    enterprises = await db.enterprises.find(query).limit(MAX_ENTERPRISES).to_list(length=MAX_ENTERPRISES)
    logger.info(f"\nEntreprises a enrichir: {len(enterprises)}\n")
    
    if not enterprises:
        logger.info("Toutes les entreprises sont deja enrichies!")
        return
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        stats = {"success": 0, "errors": 0, "products": 0, "images": 0}
        
        for i, ent in enumerate(enterprises):
            ent_id = ent.get('id')
            name = ent.get('name', ent.get('business_name', 'Unknown'))
            city = ent.get('city', 'Lausanne')
            
            logger.info(f"[{i+1}/{len(enterprises)}] {name} ({city})")
            
            try:
                # 1. Rechercher sur local.ch
                logger.info(f"   -> Recherche local.ch...")
                localch_data = await find_website_on_localch(page, name, city)
                
                scraped_data = {"images": [], "products": [], "services": []}
                
                # 2. Si site web trouve, le scraper
                if localch_data.get("website"):
                    logger.info(f"   -> Site trouve: {localch_data['website'][:50]}...")
                    scraped_data = await scrape_website_fully(page, localch_data["website"], ent_id)
                else:
                    # Sinon, faire un screenshot Google
                    logger.info(f"   -> Pas de site, screenshot Google...")
                    search_url = f"https://www.google.com/search?q={quote_plus(name + ' ' + city)}"
                    await page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
                    await page.wait_for_timeout(2000)
                    
                    cover_filename = f"{ent_id}_cover.jpg"
                    await page.screenshot(path=f"{UPLOADS_DIR}/{cover_filename}", quality=85)
                    scraped_data["images"] = [f"{BASE_URL}/api/uploads/enterprises/{cover_filename}"]
                
                # 3. Sauvegarder en DB
                products_added = await save_to_database(db, ent, scraped_data, localch_data)
                
                stats["success"] += 1
                stats["products"] += products_added
                stats["images"] += len(scraped_data.get("images", []))
                
                img_count = len(scraped_data.get("images", []))
                prod_count = len(scraped_data.get("products", []))
                logger.info(f"   => OK: {img_count} images, {prod_count} produits\n")
                
                await asyncio.sleep(3)  # Pause entre chaque
                
            except Exception as e:
                logger.error(f"   => ERREUR: {e}\n")
                stats["errors"] += 1
        
        await browser.close()
    
    # Resume
    logger.info("=" * 70)
    logger.info("   RESUME FINAL")
    logger.info("=" * 70)
    logger.info(f"   Entreprises traitees: {stats['success'] + stats['errors']}")
    logger.info(f"   Succes: {stats['success']}")
    logger.info(f"   Erreurs: {stats['errors']}")
    logger.info(f"   Total images: {stats['images']}")
    logger.info(f"   Produits ajoutes: {stats['products']}")
    logger.info("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
