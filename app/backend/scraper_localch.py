#!/usr/bin/env python3
"""
Scraper for local.ch - Lausanne businesses
This script scrapes business information from local.ch and adds them to the MongoDB database.
"""

import asyncio
import httpx
import re
import json
import os
import time
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin, quote

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/backend/scraper_localch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URL = "mongodb+srv://prankgy:Minijetaime1996@cluster0.kwjifsg.mongodb.net/secondevie?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "secondevie"

# Headers to mimic a browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

BASE_URL = "https://www.local.ch/fr/s/lausanne"


async def get_existing_businesses(db):
    """Get set of existing business names and addresses to avoid duplicates"""
    existing = set()
    cursor = db.enterprises.find({}, {"name": 1, "business_name": 1, "address": 1})
    async for doc in cursor:
        name = doc.get("name") or doc.get("business_name", "")
        address = doc.get("address", "")
        if name:
            # Create a normalized key for comparison
            key = f"{name.lower().strip()}|{address.lower().strip()[:50]}"
            existing.add(key)
    logger.info(f"Found {len(existing)} existing businesses in database")
    return existing


def normalize_key(name, address):
    """Create normalized key for duplicate detection"""
    name_clean = name.lower().strip() if name else ""
    addr_clean = address.lower().strip()[:50] if address else ""
    return f"{name_clean}|{addr_clean}"


async def scrape_page(client, page_num, existing_keys):
    """Scrape a single page from local.ch"""
    url = f"{BASE_URL}?page={page_num}"
    
    try:
        response = await client.get(url, headers=HEADERS, timeout=30.0)
        
        if response.status_code != 200:
            logger.warning(f"Page {page_num}: HTTP {response.status_code}")
            return [], False
        
        soup = BeautifulSoup(response.text, 'html.parser')
        businesses = []
        
        # Find all business cards - local.ch uses specific structure
        # Looking for business listings in the search results
        listings = soup.find_all('a', href=re.compile(r'/fr/d/lausanne/\d+/'))
        
        if not listings:
            # Try alternative selectors
            listings = soup.select('[data-testid="search-result-item"]')
        
        if not listings:
            # Try finding by the structure we saw in the scraped content
            # Looking for elements with business info
            text_content = soup.get_text()
            if "Aucun résultat" in text_content or "404" in text_content:
                logger.info(f"Page {page_num}: No more results")
                return [], False
        
        # Parse the HTML for business information
        # Based on the structure from local.ch
        for listing in listings:
            try:
                business = parse_business_listing(listing, soup)
                if business and business.get('name'):
                    key = normalize_key(business['name'], business.get('address', ''))
                    if key not in existing_keys:
                        businesses.append(business)
                        existing_keys.add(key)
            except Exception as e:
                logger.debug(f"Error parsing listing: {e}")
                continue
        
        # Check if there are more pages
        has_more = bool(soup.find('a', text=re.compile(r'Suivant|Next|›'))) or \
                   bool(soup.find('a', href=re.compile(f'page={page_num + 1}')))
        
        logger.info(f"Page {page_num}: Found {len(businesses)} new businesses")
        return businesses, has_more
        
    except httpx.TimeoutException:
        logger.warning(f"Page {page_num}: Timeout")
        return [], True  # Retry possible
    except Exception as e:
        logger.error(f"Page {page_num}: Error - {e}")
        return [], True


def parse_business_listing(listing, soup):
    """Parse a single business listing element"""
    business = {}
    
    try:
        # Get the full text and link
        href = listing.get('href', '')
        text = listing.get_text(separator=' ', strip=True)
        
        # Extract name - usually the first bold/strong text or first line
        name_elem = listing.find(['strong', 'b', 'h2', 'h3'])
        if name_elem:
            business['name'] = name_elem.get_text(strip=True)
        else:
            # Take first significant text
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            if lines:
                business['name'] = lines[0][:100]
        
        # Extract address - look for typical Swiss address pattern
        address_match = re.search(r'((?:Rue|Avenue|Chemin|Place|Route|Boulevard|Passage|Allée|Impasse)[^,\n]+,?\s*\d{4}\s+\w+)', text, re.IGNORECASE)
        if address_match:
            business['address'] = address_match.group(1).strip()
        else:
            # Try to find postal code pattern
            postal_match = re.search(r'([^,\n]+,?\s*\d{4}\s+Lausanne)', text, re.IGNORECASE)
            if postal_match:
                business['address'] = postal_match.group(1).strip()
        
        # Extract categories - usually after the name
        categories = []
        category_patterns = [
            r'(Restaurant|Coiffeur|Institut de beauté|Médecin|Avocat|Pharmacie|Boulangerie|Café|Bar|Hotel|Garage|Dentiste|Opticien|Banque|Assurance|Immobilier|Fitness|Spa|Massage|Physiothérapie|Kinésithérapie|Ostéopathie|Psychologue|Psychiatre|Pédiatre|Gynécologue|Cardiologue|Dermatologue|ORL|Ophtalmologue|Orthopédiste|Chirurgien|Fleuriste|Bijouterie|Horlogerie|Mode|Vêtements|Chaussures|Sport|Électronique|Informatique|Téléphonie|Électroménager|Meuble|Décoration|Bricolage|Jardinage|Animalerie|Librairie|Papeterie|Jouet|Supermarché|Épicerie|Boucherie|Poissonnerie|Fromagerie|Traiteur|Pizzeria|Sushi|Thai|Chinois|Japonais|Indien|Mexicain|Italien|Français|Suisse)',
            text
        ]
        for pattern in category_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            categories.extend(matches[:3])  # Max 3 categories
        
        if categories:
            business['category'] = categories[0]
            business['categories'] = list(set(categories))
        else:
            business['category'] = 'Commerce'
        
        # Extract phone if present
        phone_match = re.search(r'(\+41[\s]?\d{2}[\s]?\d{3}[\s]?\d{2}[\s]?\d{2}|0\d{2}[\s]?\d{3}[\s]?\d{2}[\s]?\d{2})', text)
        if phone_match:
            business['phone'] = phone_match.group(1).strip()
        
        # Extract rating if present
        rating_match = re.search(r'(\d[.,]\d)\s*/\s*5', text)
        if rating_match:
            try:
                business['rating'] = float(rating_match.group(1).replace(',', '.'))
            except:
                pass
        
        # Set default values
        business['city'] = 'Lausanne'
        business['canton'] = 'Vaud'
        business['country'] = 'Suisse'
        business['source'] = 'local.ch'
        business['activation_status'] = 'inactive'
        business['status'] = 'bientot_disponible'
        business['is_verified'] = False
        business['is_certified'] = False
        business['is_premium'] = False
        
        return business if business.get('name') else None
        
    except Exception as e:
        logger.debug(f"Parse error: {e}")
        return None


async def scrape_with_api(client, page_num, existing_keys):
    """Alternative approach: Try to find and use local.ch's API"""
    # local.ch might have a JSON API
    api_url = f"https://www.local.ch/fr/s/lausanne?page={page_num}&format=json"
    
    try:
        response = await client.get(api_url, headers=HEADERS, timeout=30.0)
        if response.status_code == 200 and 'application/json' in response.headers.get('content-type', ''):
            data = response.json()
            # Process JSON response
            return process_api_response(data, existing_keys)
    except:
        pass
    
    return [], True


async def insert_businesses(db, businesses):
    """Insert businesses into MongoDB"""
    if not businesses:
        return 0
    
    now = datetime.now(timezone.utc).isoformat()
    
    for biz in businesses:
        biz['id'] = f"localch_{hash(biz['name'] + biz.get('address', '')) % 10000000000}"
        biz['created_at'] = now
        biz['updated_at'] = now
        
        # Generate avatar if no image
        if not biz.get('image'):
            name_encoded = quote(biz['name'][:20])
            biz['image'] = f"https://ui-avatars.com/api/?name={name_encoded}&background=0047AB&color=fff&size=400"
    
    try:
        result = await db.enterprises.insert_many(businesses, ordered=False)
        return len(result.inserted_ids)
    except Exception as e:
        # Handle duplicate key errors gracefully
        logger.warning(f"Insert error (some may be duplicates): {e}")
        # Try one by one
        inserted = 0
        for biz in businesses:
            try:
                await db.enterprises.insert_one(biz)
                inserted += 1
            except:
                pass
        return inserted


async def scrape_category(client, db, category, existing_keys):
    """Scrape businesses for a specific category in Lausanne"""
    businesses = []
    page = 1
    max_pages = 100  # Safety limit per category
    
    category_url = f"https://www.local.ch/fr/s/{quote(category)}/lausanne"
    
    while page <= max_pages:
        try:
            url = f"{category_url}?page={page}"
            response = await client.get(url, headers=HEADERS, timeout=30.0)
            
            if response.status_code != 200:
                break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            page_businesses = []
            
            # Find listings
            listings = soup.find_all('a', href=re.compile(r'/fr/d/'))
            
            for listing in listings:
                business = parse_business_listing(listing, soup)
                if business and business.get('name'):
                    key = normalize_key(business['name'], business.get('address', ''))
                    if key not in existing_keys:
                        business['category'] = category
                        page_businesses.append(business)
                        existing_keys.add(key)
            
            if not page_businesses:
                break
            
            businesses.extend(page_businesses)
            logger.info(f"Category '{category}' page {page}: Found {len(page_businesses)} new businesses")
            
            # Check for next page
            if not soup.find('a', href=re.compile(f'page={page + 1}')):
                break
            
            page += 1
            await asyncio.sleep(1)  # Rate limiting
            
        except Exception as e:
            logger.error(f"Category '{category}' page {page}: Error - {e}")
            break
    
    return businesses


async def main():
    """Main scraping function"""
    logger.info("=" * 60)
    logger.info("Starting local.ch scraper for Lausanne businesses")
    logger.info("=" * 60)
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Get existing businesses
    existing_keys = await get_existing_businesses(db)
    initial_count = len(existing_keys)
    
    # Categories to scrape
    categories = [
        "restaurant",
        "coiffeur",
        "institut-de-beaute",
        "medecin",
        "avocat",
        "pharmacie",
        "boulangerie",
        "cafe",
        "bar",
        "hotel",
        "garage",
        "dentiste",
        "opticien",
        "banque",
        "assurance",
        "immobilier",
        "fitness",
        "spa",
        "massage",
        "physiotherapie",
        "psychologue",
        "fleuriste",
        "bijouterie",
        "horlogerie",
        "mode",
        "vetements",
        "chaussures",
        "sport",
        "electronique",
        "informatique",
        "telephonie",
        "electromenager",
        "meuble",
        "decoration",
        "bricolage",
        "jardinage",
        "librairie",
        "supermarche",
        "epicerie",
        "boucherie",
        "traiteur",
        "pizzeria",
        "sushi",
        "thai",
        "chinois",
        "indien",
        "italien",
        "architecte",
        "notaire",
        "comptable",
        "veterinaire",
        "creche",
        "ecole",
        "auto-ecole",
        "taxi",
        "demenagement",
        "nettoyage",
        "serrurier",
        "plombier",
        "electricien",
        "peintre",
        "menuisier",
        "carreleur",
        "chauffagiste",
        "climatisation",
        "photographe",
        "imprimerie",
        "graphiste",
        "traducteur",
        "agence-voyage",
    ]
    
    total_new = 0
    
    async with httpx.AsyncClient() as http_client:
        for category in categories:
            logger.info(f"\n--- Scraping category: {category} ---")
            
            try:
                businesses = await scrape_category(http_client, db, category, existing_keys)
                
                if businesses:
                    inserted = await insert_businesses(db, businesses)
                    total_new += inserted
                    logger.info(f"Category '{category}': Inserted {inserted} businesses")
                
                # Rate limiting
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Category '{category}': Failed - {e}")
                continue
            
            # Log progress every 10 categories
            if categories.index(category) % 10 == 9:
                current_count = await db.enterprises.count_documents({})
                logger.info(f"\n=== Progress: {current_count} total businesses ({total_new} new) ===\n")
    
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
