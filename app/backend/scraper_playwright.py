#!/usr/bin/env python3
"""
Advanced scraper for local.ch using Playwright for JavaScript rendering
"""

import asyncio
import re
import json
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
        logging.FileHandler('/app/backend/scraper_v2.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URL = "mongodb+srv://prankgy:Minijetaime1996@cluster0.kwjifsg.mongodb.net/secondevie?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "secondevie"


async def get_existing_keys(db):
    """Get set of existing business keys"""
    existing = set()
    cursor = db.enterprises.find({}, {"name": 1, "business_name": 1, "address": 1})
    async for doc in cursor:
        name = doc.get("name") or doc.get("business_name", "")
        address = doc.get("address", "")
        if name:
            key = f"{name.lower().strip()}|{address.lower().strip()[:50]}"
            existing.add(key)
    logger.info(f"Found {len(existing)} existing businesses")
    return existing


def normalize_key(name, address):
    """Create normalized key for duplicate detection"""
    name_clean = name.lower().strip() if name else ""
    addr_clean = address.lower().strip()[:50] if address else ""
    return f"{name_clean}|{addr_clean}"


async def scrape_with_playwright(category, max_pages=50):
    """Scrape a category using Playwright for JS rendering"""
    from playwright.async_api import async_playwright
    
    businesses = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            locale='fr-FR'
        )
        page = await context.new_page()
        
        for page_num in range(1, max_pages + 1):
            url = f"https://www.local.ch/fr/s/{category}/lausanne?page={page_num}"
            logger.info(f"Scraping: {url}")
            
            try:
                await page.goto(url, wait_until='networkidle', timeout=30000)
                await page.wait_for_timeout(2000)  # Wait for content to load
                
                # Get all business listings
                listings = await page.query_selector_all('a[href*="/fr/d/lausanne/"]')
                
                if not listings:
                    logger.info(f"No listings found on page {page_num}")
                    break
                
                page_businesses = []
                
                for listing in listings:
                    try:
                        href = await listing.get_attribute('href')
                        text = await listing.inner_text()
                        
                        # Parse business info from text
                        lines = [l.strip() for l in text.split('\n') if l.strip()]
                        if not lines:
                            continue
                        
                        business = {
                            'name': lines[0][:100] if lines else '',
                            'city': 'Lausanne',
                            'canton': 'Vaud',
                            'country': 'Suisse',
                            'source': 'local.ch',
                            'activation_status': 'inactive',
                            'status': 'bientot_disponible',
                            'is_verified': False,
                            'is_certified': False,
                            'is_premium': False,
                            'category': category.replace('-', ' ').title(),
                        }
                        
                        # Find address
                        for line in lines[1:]:
                            if re.search(r'\d{4}\s+Lausanne', line, re.IGNORECASE):
                                business['address'] = line
                                break
                        
                        # Find phone
                        phone_match = re.search(r'(\+41[\s]?\d{2}[\s]?\d{3}[\s]?\d{2}[\s]?\d{2}|0\d{2}[\s]?\d{3}[\s]?\d{2}[\s]?\d{2})', text)
                        if phone_match:
                            business['phone'] = phone_match.group(1)
                        
                        # Find rating
                        rating_match = re.search(r'(\d[.,]\d)\s*/\s*5', text)
                        if rating_match:
                            try:
                                business['rating'] = float(rating_match.group(1).replace(',', '.'))
                            except:
                                pass
                        
                        if business.get('name'):
                            page_businesses.append(business)
                            
                    except Exception as e:
                        logger.debug(f"Error parsing listing: {e}")
                        continue
                
                businesses.extend(page_businesses)
                logger.info(f"Page {page_num}: Found {len(page_businesses)} businesses")
                
                if len(page_businesses) < 5:
                    logger.info("Fewer than 5 results, likely last page")
                    break
                    
                await page.wait_for_timeout(1500)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error on page {page_num}: {e}")
                break
        
        await browser.close()
    
    return businesses


async def insert_businesses(db, businesses, existing_keys):
    """Insert new businesses into MongoDB"""
    now = datetime.now(timezone.utc).isoformat()
    new_businesses = []
    
    for biz in businesses:
        key = normalize_key(biz['name'], biz.get('address', ''))
        if key not in existing_keys:
            biz['id'] = f"localch_{abs(hash(biz['name'] + biz.get('address', ''))) % 10000000000}"
            biz['created_at'] = now
            biz['updated_at'] = now
            
            # Generate avatar
            if not biz.get('image'):
                name_encoded = quote(biz['name'][:20])
                biz['image'] = f"https://ui-avatars.com/api/?name={name_encoded}&background=0047AB&color=fff&size=400"
            
            new_businesses.append(biz)
            existing_keys.add(key)
    
    if not new_businesses:
        return 0
    
    try:
        result = await db.enterprises.insert_many(new_businesses, ordered=False)
        return len(result.inserted_ids)
    except Exception as e:
        logger.warning(f"Insert error: {e}")
        inserted = 0
        for biz in new_businesses:
            try:
                await db.enterprises.insert_one(biz)
                inserted += 1
            except:
                pass
        return inserted


async def main():
    """Main function"""
    logger.info("=" * 60)
    logger.info("Starting local.ch scraper v2 (Playwright)")
    logger.info("=" * 60)
    
    # Connect to MongoDB
    mongo_client = AsyncIOMotorClient(MONGO_URL)
    db = mongo_client[DB_NAME]
    
    existing_keys = await get_existing_keys(db)
    initial_count = len(existing_keys)
    
    # Categories to scrape
    categories = [
        "restaurant",
        "cafe",
        "bar",
        "coiffeur",
        "institut-de-beaute",
        "massage",
        "spa",
        "fitness",
        "medecin",
        "dentiste",
        "pharmacie",
        "opticien",
        "physiotherapie",
        "psychologue",
        "avocat",
        "notaire",
        "comptable",
        "banque",
        "assurance",
        "immobilier",
        "hotel",
        "garage",
        "boulangerie",
        "epicerie",
        "supermarche",
        "boucherie",
        "fleuriste",
        "bijouterie",
        "horlogerie",
        "mode",
        "vetements",
        "chaussures",
        "sport",
        "electronique",
        "informatique",
        "meuble",
        "decoration",
        "bricolage",
        "librairie",
        "pizzeria",
        "sushi",
        "italien",
        "chinois",
        "thai",
        "indien",
        "japonais",
        "mexicain",
        "kebab",
        "fast-food",
        "traiteur",
    ]
    
    total_new = 0
    
    for category in categories:
        logger.info(f"\n--- Category: {category} ---")
        
        try:
            businesses = await scrape_with_playwright(category, max_pages=20)
            
            if businesses:
                inserted = await insert_businesses(db, businesses, existing_keys)
                total_new += inserted
                logger.info(f"Category '{category}': Inserted {inserted} new businesses")
            
        except Exception as e:
            logger.error(f"Category '{category}': Failed - {e}")
            continue
    
    # Final stats
    final_count = await db.enterprises.count_documents({})
    lausanne_count = await db.enterprises.count_documents({'city': 'Lausanne'})
    
    logger.info("=" * 60)
    logger.info("SCRAPING COMPLETED")
    logger.info(f"Initial count: {initial_count}")
    logger.info(f"Final count: {final_count}")
    logger.info(f"New businesses added: {total_new}")
    logger.info(f"Lausanne businesses: {lausanne_count}")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
