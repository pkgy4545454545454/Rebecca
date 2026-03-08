#!/usr/bin/env python3
"""
Comprehensive scraper for local.ch - Lausanne businesses
Version 5: Continue from construction categories
"""

import asyncio
import re
import os
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/backend/scraper_v5.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

MONGO_URL = "mongodb+srv://prankgy:Minijetaime1996@cluster0.kwjifsg.mongodb.net/secondevie?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "secondevie"


async def get_existing_keys(db):
    existing = set()
    cursor = db.enterprises.find({}, {"name": 1, "business_name": 1, "address": 1})
    async for doc in cursor:
        name = doc.get("name") or doc.get("business_name", "")
        address = doc.get("address", "")
        if name:
            key = f"{name.lower().strip()[:50]}|{address.lower().strip()[:30]}"
            existing.add(key)
    logger.info(f"Found {len(existing)} existing businesses")
    return existing


def normalize_key(name, address):
    name_clean = name.lower().strip()[:50] if name else ""
    addr_clean = address.lower().strip()[:30] if address else ""
    return f"{name_clean}|{addr_clean}"


async def scrape_search(page, search_term, location, existing_keys, max_pages=30):
    from playwright.async_api import TimeoutError as PlaywrightTimeout
    
    businesses = []
    
    for page_num in range(1, max_pages + 1):
        url = f"https://www.local.ch/fr/s/{quote(search_term)}/{quote(location)}?page={page_num}"
        
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=20000)
            await page.wait_for_timeout(1500)
            
            try:
                await page.wait_for_selector('a[href*="/fr/d/"]', timeout=5000)
            except:
                pass
            
            listings = await page.query_selector_all('a[href*="/fr/d/"]')
            
            if not listings:
                break
            
            page_businesses = []
            seen_on_page = set()
            
            for listing in listings:
                try:
                    href = await listing.get_attribute('href')
                    if not href or '/fr/d/' not in href:
                        continue
                    
                    if href in seen_on_page:
                        continue
                    seen_on_page.add(href)
                    
                    text = await listing.inner_text()
                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    
                    if not lines:
                        continue
                    
                    name = lines[0][:100]
                    
                    if len(name) < 3 or name.lower() in ['voir plus', 'plus', 'suivant', 'précédent']:
                        continue
                    
                    business = {
                        'name': name,
                        'city': 'Lausanne',
                        'canton': 'Vaud',
                        'country': 'Suisse',
                        'source': 'local.ch',
                        'activation_status': 'inactive',
                        'status': 'bientot_disponible',
                        'is_verified': False,
                        'is_certified': False,
                        'is_premium': False,
                        'category': search_term.replace('-', ' ').title(),
                        'search_location': location,
                    }
                    
                    for line in lines[1:5]:
                        if re.search(r'\d{4}', line):
                            business['address'] = line[:200]
                            postal_match = re.search(r'(\d{4})', line)
                            if postal_match:
                                business['postal_code'] = postal_match.group(1)
                            break
                    
                    for line in lines:
                        phone_match = re.search(r'(\+41[\s.-]?\d{2}[\s.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2}|0\d{2}[\s.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2})', line)
                        if phone_match:
                            business['phone'] = phone_match.group(1).replace(' ', '').replace('.', '').replace('-', '')
                            break
                    
                    key = normalize_key(name, business.get('address', ''))
                    if key not in existing_keys:
                        page_businesses.append(business)
                        existing_keys.add(key)
                        
                except Exception as e:
                    continue
            
            if page_businesses:
                businesses.extend(page_businesses)
                logger.info(f"{search_term}/{location} p{page_num}: +{len(page_businesses)} new")
            
            if len(page_businesses) < 3:
                break
                
            await page.wait_for_timeout(800)
            
        except PlaywrightTimeout:
            logger.warning(f"{search_term}/{location} p{page_num}: Timeout")
            break
        except Exception as e:
            logger.error(f"{search_term}/{location} p{page_num}: Error - {str(e)[:50]}")
            break
    
    return businesses


async def insert_businesses(db, businesses):
    if not businesses:
        return 0
    
    now = datetime.now(timezone.utc).isoformat()
    
    for biz in businesses:
        biz['id'] = f"lch_{abs(hash(biz['name'] + biz.get('address', '') + biz.get('phone', ''))) % 10000000000}"
        biz['created_at'] = now
        biz['updated_at'] = now
        
        if not biz.get('image'):
            name_encoded = quote(biz['name'][:20])
            biz['image'] = f"https://ui-avatars.com/api/?name={name_encoded}&background=0047AB&color=fff&size=400"
    
    try:
        result = await db.enterprises.insert_many(businesses, ordered=False)
        return len(result.inserted_ids)
    except Exception as e:
        inserted = 0
        for biz in businesses:
            try:
                await db.enterprises.insert_one(biz)
                inserted += 1
            except:
                pass
        return inserted


async def main():
    from playwright.async_api import async_playwright
    
    logger.info("=" * 60)
    logger.info("LOCAL.CH SCRAPER V5 - CONTINUING")
    logger.info("=" * 60)
    
    mongo_client = AsyncIOMotorClient(MONGO_URL)
    db = mongo_client[DB_NAME]
    
    existing_keys = await get_existing_keys(db)
    initial_count = await db.enterprises.count_documents({})
    
    # Continue from where V4 left off + additional categories
    search_terms = [
        # Construction continued
        "menuiserie", "ebenisterie", "parqueteur", "poseur", "installateur",
        "plombier", "plomberie", "chauffagiste", "climaticien", "ventilation",
        "electricien", "electricite", "domotique", "alarme", "videosurveillance",
        "tapissier", "platrerie", "plafonnier",
        "carreleur", "faience", "mosaique", "sol", "revetement",
        "serrurier", "serrurerie", "cle", "coffre-fort", "blindage", "vitrier",
        "verrier", "miroiterie", "store", "volet", "pergola", "veranda",
        "cuisiniste", "cuisine-equipee", "salle-bain", "amenagement", "renovation",
        "demenagement", "garde-meuble", "stockage", "nettoyage", "menage", "entretien",
        "desinsectisation", "desinfection", "ramonage", "debouchage", "assainissement",
        
        # Hotels & Tourism
        "motel", "auberge", "pension", "chambre-hote", "gite", "apparthotel",
        "residence", "apart-hotel", "hostel", "refuge", "chalet",
        "tourisme", "guide", "excursion", "visite", "croisiere",
        
        # Education
        "college", "lycee", "universite", "cours", "soutien",
        "garderie", "jardin-enfants", "parascolaire", "camp", "colonie",
        "ecole-langue", "theatre",
        "musee", "exposition", "cinema", "spectacle", "concert", "festival",
        "bibliotheque", "mediatheque", "ludotheque", "centre-culturel", "association",
        
        # Technology
        "depannage-informatique", "reparation-ordinateur", "data",
        "developpement", "web", "application", "logiciel", "software", "hardware",
        "reseau", "securite-informatique", "cloud", "hebergement", "serveur",
        "telecoms", "telephonie", "fibre", "internet", "operateur",
        
        # Industry
        "industrie", "usine", "manufacture", "production", "fabrication", "atelier",
        "mecanique-precision", "usinage", "soudure", "metallurgie", "fonderie",
        "plastique", "caoutchouc", "composite", "textile", "confection", "broderie",
        "edition", "packaging", "emballage", "conditionnement",
        "logistique", "transport", "livraison", "coursier", "messagerie", "fret",
        "import-export", "negoce", "grossiste", "distributeur", "representant",
        
        # Misc Services
        "pressing", "teinturerie", "laverie", "blanchisserie", "couture", "retouche",
        "cordonnerie", "reparation", "cle-minute", "gravure", "tampon", "cachet",
        "photocopie", "scan", "reliure", "plastification",
        "pompes-funebres", "funeraire", "crematorium",
        "garde", "securite", "surveillance", "gardiennage", "agent-securite",
        "detective", "enqueteur", "recouvrement", "mediation",
        
        # Generic business types
        "agence", "bureau", "cabinet", "centre", "espace", "institut",
        "maison", "service", "societe", "entreprise", "compagnie",
        "boutique", "magasin", "shop", "store", "commerce",
        "studio", "salle", "local", "atelier", "showroom",
        
        # More specific
        "avocat", "notaire", "comptable", "fiduciaire", "audit",
        "architecte", "ingenieur", "geometre", "urbaniste",
        "consultant", "conseil", "expert", "formation", "coaching",
        "marketing", "communication", "publicite", "evenementiel",
        "photographe", "videaste", "graphiste", "designer",
        "traducteur", "interprete", "secretariat",
    ]
    
    locations = [
        "lausanne", "lausanne-1000", "lausanne-1003", "lausanne-1004", "lausanne-1005",
        "lausanne-1006", "lausanne-1007", "lausanne-1010", "lausanne-1012",
        "lausanne-1018", "lausanne-flon", "lausanne-gare", "lausanne-ouchy",
        "pully", "prilly", "renens", "ecublens", "chavannes", "epalinges",
        "le-mont-sur-lausanne", "crissier", "bussigny", "morges",
    ]
    
    total_new = 0
    categories_done = 0
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            locale='fr-CH',
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        for search_term in search_terms:
            for location in locations:
                try:
                    businesses = await scrape_search(page, search_term, location, existing_keys, max_pages=25)
                    
                    if businesses:
                        inserted = await insert_businesses(db, businesses)
                        total_new += inserted
                        if inserted > 0:
                            logger.info(f"✓ {search_term}/{location}: +{inserted} (Total new: {total_new})")
                    
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"✗ {search_term}/{location}: {str(e)[:50]}")
                    continue
                
                if location == "lausanne" and not businesses:
                    break
            
            categories_done += 1
            
            if categories_done % 20 == 0:
                current = await db.enterprises.count_documents({})
                logger.info(f"\n{'='*60}")
                logger.info(f"PROGRESS: {categories_done}/{len(search_terms)} categories")
                logger.info(f"Total enterprises: {current} (+{total_new} new)")
                logger.info(f"{'='*60}\n")
        
        await browser.close()
    
    final_count = await db.enterprises.count_documents({})
    lausanne_count = await db.enterprises.count_documents({'city': 'Lausanne'})
    localch_count = await db.enterprises.count_documents({'source': 'local.ch'})
    
    logger.info("=" * 60)
    logger.info("SCRAPING V5 COMPLETED")
    logger.info(f"Initial: {initial_count}")
    logger.info(f"Final: {final_count}")
    logger.info(f"New added: {total_new}")
    logger.info(f"Total from local.ch: {localch_count}")
    logger.info(f"Lausanne: {lausanne_count}")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
