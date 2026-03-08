#!/usr/bin/env python3
"""
Titelli Enterprise Scraper - Lausanne Region
Scrapes businesses from local.ch for the Titelli marketplace
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
        logging.FileHandler('/app/backend/scraper_titelli.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Use secondevie MongoDB (same as before)
MONGO_URL = "mongodb+srv://prankgy:Minijetaime1996@cluster0.kwjifsg.mongodb.net/secondevie?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "secondevie"


async def get_existing_keys(db):
    """Get existing business keys to avoid duplicates"""
    existing = set()
    cursor = db.enterprises.find({}, {"name": 1, "business_name": 1, "address": 1})
    async for doc in cursor:
        name = doc.get("name") or doc.get("business_name", "")
        address = doc.get("address", "")
        if name:
            key = f"{name.lower().strip()[:50]}|{address.lower().strip()[:30]}"
            existing.add(key)
    logger.info(f"Found {len(existing)} existing businesses in database")
    return existing


def normalize_key(name, address):
    name_clean = name.lower().strip()[:50] if name else ""
    addr_clean = address.lower().strip()[:30] if address else ""
    return f"{name_clean}|{addr_clean}"


async def scrape_search(page, search_term, location, existing_keys, max_pages=20):
    """Scrape local.ch search results"""
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
                    
                    # Map search term to Titelli category
                    category_mapping = {
                        'restaurant': 'Restauration',
                        'cafe': 'Restauration',
                        'bar': 'Restauration',
                        'boulangerie': 'Alimentation',
                        'patisserie': 'Alimentation',
                        'chocolaterie': 'Alimentation',
                        'coiffeur': 'Beauté & Bien-être',
                        'coiffeuse': 'Beauté & Bien-être',
                        'esthetique': 'Beauté & Bien-être',
                        'spa': 'Beauté & Bien-être',
                        'massage': 'Beauté & Bien-être',
                        'fitness': 'Sport & Loisirs',
                        'sport': 'Sport & Loisirs',
                        'yoga': 'Sport & Loisirs',
                        'medecin': 'Santé',
                        'dentiste': 'Santé',
                        'pharmacie': 'Santé',
                        'avocat': 'Services Professionnels',
                        'notaire': 'Services Professionnels',
                        'comptable': 'Services Professionnels',
                        'architecte': 'Services Professionnels',
                        'plombier': 'Artisanat & Travaux',
                        'electricien': 'Artisanat & Travaux',
                        'menuisier': 'Artisanat & Travaux',
                        'peintre': 'Artisanat & Travaux',
                        'bijouterie': 'Commerce',
                        'horlogerie': 'Commerce',
                        'boutique': 'Commerce',
                        'vetement': 'Mode',
                        'chaussure': 'Mode',
                        'hotel': 'Hébergement',
                        'garage': 'Automobile',
                        'taxi': 'Transport',
                        'fleuriste': 'Commerce',
                        'photographe': 'Services Créatifs',
                    }
                    
                    category = 'Services'
                    for key, cat in category_mapping.items():
                        if key in search_term.lower():
                            category = cat
                            break
                    
                    business = {
                        'name': name,
                        'business_name': name,
                        'city': 'Lausanne',
                        'canton': 'Vaud',
                        'country': 'Suisse',
                        'source': 'local.ch',
                        'activation_status': 'inactive',
                        'status': 'bientot_disponible',
                        'is_verified': False,
                        'is_certified': False,
                        'is_premium': False,
                        'category': category,
                        'subcategory': search_term.replace('-', ' ').title(),
                        'search_location': location,
                        'rating': 0,
                        'reviews_count': 0,
                    }
                    
                    # Extract address and postal code
                    for line in lines[1:5]:
                        if re.search(r'\d{4}', line):
                            business['address'] = line[:200]
                            postal_match = re.search(r'(\d{4})', line)
                            if postal_match:
                                business['postal_code'] = postal_match.group(1)
                            break
                    
                    # Extract phone
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
                logger.info(f"  {search_term}/{location} p{page_num}: +{len(page_businesses)} new")
            
            # Stop if few results
            if len(page_businesses) < 3:
                break
                
            await page.wait_for_timeout(800)
            
        except PlaywrightTimeout:
            logger.warning(f"  {search_term}/{location} p{page_num}: Timeout")
            break
        except Exception as e:
            logger.error(f"  {search_term}/{location} p{page_num}: Error - {str(e)[:50]}")
            break
    
    return businesses


async def insert_businesses(db, businesses):
    """Insert businesses into MongoDB"""
    if not businesses:
        return 0
    
    now = datetime.now(timezone.utc).isoformat()
    
    for biz in businesses:
        # Generate unique ID
        biz['id'] = f"ent_{abs(hash(biz['name'] + biz.get('address', '') + biz.get('phone', ''))) % 10000000000}"
        biz['created_at'] = now
        biz['updated_at'] = now
        
        # Generate avatar image
        if not biz.get('image'):
            name_encoded = quote(biz['name'][:20])
            biz['image'] = f"https://ui-avatars.com/api/?name={name_encoded}&background=0047AB&color=fff&size=400"
    
    try:
        result = await db.enterprises.insert_many(businesses, ordered=False)
        return len(result.inserted_ids)
    except Exception as e:
        # Insert one by one on error
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
    logger.info("🚀 TITELLI ENTERPRISE SCRAPER - LAUSANNE")
    logger.info("=" * 60)
    
    # Connect to MongoDB
    mongo_client = AsyncIOMotorClient(MONGO_URL)
    db = mongo_client[DB_NAME]
    
    existing_keys = await get_existing_keys(db)
    initial_count = await db.enterprises.count_documents({})
    logger.info(f"Initial count: {initial_count} enterprises")
    
    # Categories to scrape - prioritized for Titelli marketplace
    search_terms = [
        # Beauté & Bien-être (prioritaire pour Titelli)
        "coiffeur", "coiffeuse", "salon-coiffure", "barbier",
        "estheticienne", "institut-beaute", "onglerie", "manucure",
        "spa", "massage", "relaxation", "bien-etre",
        "maquillage", "cosmetique",
        
        # Restauration
        "restaurant", "cafe", "bar", "brasserie", "bistrot",
        "pizzeria", "sushi", "thai", "italien", "chinois",
        "boulangerie", "patisserie", "chocolaterie", "confiserie",
        "traiteur", "food-truck",
        
        # Santé
        "medecin", "generaliste", "dentiste", "orthodontiste",
        "kinesitherapeute", "osteopathe", "chiropracteur",
        "pharmacie", "opticien", "orthophoniste",
        "psychologue", "therapeute",
        
        # Artisanat & Travaux
        "plombier", "electricien", "menuisier", "charpentier",
        "peintre-batiment", "carreleur", "maçon",
        "serrurier", "vitrier", "couvreur",
        "chauffagiste", "climatisation",
        
        # Commerce
        "bijouterie", "horlogerie", "joaillerie",
        "fleuriste", "decoration", "cadeau",
        "librairie", "papeterie",
        "epicerie", "fromagerie", "boucherie", "poissonnerie",
        
        # Mode
        "vetement", "boutique-mode", "chaussure",
        "maroquinerie", "accessoire",
        "couture", "retouche", "tailleur",
        
        # Services Professionnels
        "avocat", "notaire", "comptable", "fiduciaire",
        "architecte", "geometre", "ingenieur",
        "consultant", "coach", "formation",
        
        # Sport & Loisirs
        "fitness", "musculation", "yoga", "pilates",
        "danse", "arts-martiaux", "boxe",
        "tennis", "golf", "natation",
        
        # Automobile
        "garage", "carrosserie", "mecanique",
        "pneu", "lavage-auto", "location-voiture",
        
        # Services Créatifs
        "photographe", "videaste", "graphiste",
        "imprimerie", "serigraphie",
        
        # Hébergement
        "hotel", "auberge", "chambre-hote",
        
        # Transport
        "taxi", "vtc", "demenagement", "coursier",
        
        # Nettoyage
        "nettoyage", "menage", "pressing", "laverie",
    ]
    
    locations = [
        "lausanne",
        "lausanne-1000", "lausanne-1003", "lausanne-1004", "lausanne-1005",
        "lausanne-1006", "lausanne-1007", "lausanne-1010", "lausanne-1012",
        "pully", "prilly", "renens", "ecublens", 
        "morges", "crissier", "bussigny",
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
            logger.info(f"\n📌 Catégorie: {search_term}")
            
            for location in locations:
                try:
                    businesses = await scrape_search(page, search_term, location, existing_keys, max_pages=15)
                    
                    if businesses:
                        inserted = await insert_businesses(db, businesses)
                        total_new += inserted
                        if inserted > 0:
                            logger.info(f"  ✓ {location}: +{inserted} (Total: {total_new})")
                    
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"  ✗ {location}: {str(e)[:50]}")
                    continue
                
                # Skip other locations if no results in main Lausanne
                if location == "lausanne" and not businesses:
                    break
            
            categories_done += 1
            
            # Log progress every 5 categories
            if categories_done % 5 == 0:
                current_count = await db.enterprises.count_documents({})
                logger.info(f"\n📊 Progress: {categories_done}/{len(search_terms)} categories, {current_count} total enterprises\n")
        
        await browser.close()
    
    # Final stats
    final_count = await db.enterprises.count_documents({})
    
    logger.info("\n" + "=" * 60)
    logger.info("🏁 SCRAPING TERMINÉ")
    logger.info("=" * 60)
    logger.info(f"Entreprises initiales: {initial_count}")
    logger.info(f"Nouvelles entreprises: {total_new}")
    logger.info(f"Total en base: {final_count}")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
