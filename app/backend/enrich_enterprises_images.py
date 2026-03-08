import asyncio
import os
import httpx
import re
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from urllib.parse import urljoin, urlparse
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'secondevie')
UPLOADS_DIR = "/app/backend/uploads/enterprises"
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://image-fix-demo.preview.emergentagent.com')

os.makedirs(UPLOADS_DIR, exist_ok=True)

async def fetch_logo_from_website(website_url: str, enterprise_id: str) -> str:
    """Try to find and download logo from website"""
    if not website_url:
        return None
    
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            # Fetch the homepage
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = await client.get(website_url, headers=headers)
            html = response.text
            
            # Look for logo in common patterns
            logo_patterns = [
                r'<link[^>]*rel=["\'](?:apple-touch-icon|icon|shortcut icon)["\'][^>]*href=["\']([^"\']+)["\']',
                r'<img[^>]*class=["\'][^"\']*logo[^"\']*["\'][^>]*src=["\']([^"\']+)["\']',
                r'<img[^>]*src=["\']([^"\']+logo[^"\']*)["\']',
                r'<img[^>]*src=["\']([^"\']+)["\'][^>]*class=["\'][^"\']*logo',
                r'<img[^>]*alt=["\'][^"\']*logo[^"\']*["\'][^>]*src=["\']([^"\']+)["\']',
                r'og:image["\'][^>]*content=["\']([^"\']+)["\']',
            ]
            
            for pattern in logo_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    logo_url = matches[0]
                    # Make absolute URL
                    if not logo_url.startswith('http'):
                        logo_url = urljoin(website_url, logo_url)
                    
                    # Download the logo
                    try:
                        logo_response = await client.get(logo_url, headers=headers)
                        if logo_response.status_code == 200 and len(logo_response.content) > 1000:
                            # Save locally
                            ext = 'png' if '.png' in logo_url.lower() else 'jpg'
                            filename = f"{enterprise_id}_logo.{ext}"
                            filepath = os.path.join(UPLOADS_DIR, filename)
                            with open(filepath, 'wb') as f:
                                f.write(logo_response.content)
                            return f"{BASE_URL}/api/uploads/enterprises/{filename}"
                    except:
                        continue
            
            # Try favicon as fallback
            favicon_url = urljoin(website_url, '/favicon.ico')
            try:
                favicon_response = await client.get(favicon_url, headers=headers)
                if favicon_response.status_code == 200 and len(favicon_response.content) > 100:
                    filename = f"{enterprise_id}_logo.ico"
                    filepath = os.path.join(UPLOADS_DIR, filename)
                    with open(filepath, 'wb') as f:
                        f.write(favicon_response.content)
                    return f"{BASE_URL}/api/uploads/enterprises/{filename}"
            except:
                pass
                
    except Exception as e:
        logger.debug(f"Error fetching logo: {e}")
    
    return None

async def generate_cover_image(enterprise: dict, enterprise_id: str) -> str:
    """Generate a cover image based on category"""
    category = enterprise.get('category', '').lower()
    name = enterprise.get('business_name') or enterprise.get('name', '')
    
    # Map categories to Unsplash images
    category_images = {
        'restaurant': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800',
        'restauration': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800',
        'cafe': 'https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=800',
        'coiffure': 'https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800',
        'salon': 'https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800',
        'beaute': 'https://images.unsplash.com/photo-1560750588-73207b1ef5b8?w=800',
        'spa': 'https://images.unsplash.com/photo-1544161515-4ab6ce6db874?w=800',
        'fitness': 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800',
        'sport': 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800',
        'bijouterie': 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800',
        'horlogerie': 'https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=800',
        'mode': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800',
        'vetement': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800',
        'immobilier': 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800',
        'agence': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800',
        'service': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800',
        'tech': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=800',
        'informatique': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=800',
        'sante': 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=800',
        'medical': 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=800',
        'alimentation': 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=800',
        'boulangerie': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800',
        'hotel': 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800',
        'fleuriste': 'https://images.unsplash.com/photo-1487530811176-3780de880c2d?w=800',
        'garage': 'https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?w=800',
        'auto': 'https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?w=800',
    }
    
    # Find matching category
    for key, url in category_images.items():
        if key in category:
            return url
    
    # Default business image
    return 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800'

async def enrich_enterprise(db, enterprise: dict) -> dict:
    """Enrich a single enterprise with logo and cover"""
    eid = enterprise.get('id')
    website = enterprise.get('website')
    updates = {}
    
    # Try to get logo from website
    if not enterprise.get('logo') and website:
        logo_url = await fetch_logo_from_website(website, eid)
        if logo_url:
            updates['logo'] = logo_url
            logger.info(f"✓ Logo found for {enterprise.get('business_name', eid)[:30]}")
    
    # Set cover image based on category
    if not enterprise.get('cover_image'):
        cover_url = await generate_cover_image(enterprise, eid)
        updates['cover_image'] = cover_url
    
    # Update database
    if updates:
        await db.enterprises.update_one(
            {"id": eid},
            {"$set": updates}
        )
    
    return updates

async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Get enterprises without images
    cursor = db.enterprises.find({
        "$or": [
            {"logo": None},
            {"logo": ""},
            {"cover_image": None},
            {"cover_image": ""}
        ]
    }).limit(500)
    
    enterprises = await cursor.to_list(500)
    logger.info(f"Found {len(enterprises)} enterprises to enrich")
    
    enriched = 0
    logos_found = 0
    
    for i, enterprise in enumerate(enterprises):
        try:
            updates = await enrich_enterprise(db, enterprise)
            if updates:
                enriched += 1
                if 'logo' in updates:
                    logos_found += 1
            
            if (i + 1) % 20 == 0:
                logger.info(f"Progress: {i+1}/{len(enterprises)} - Logos: {logos_found}")
                
        except Exception as e:
            logger.error(f"Error enriching {enterprise.get('id')}: {e}")
        
        # Small delay to avoid overwhelming servers
        await asyncio.sleep(0.3)
    
    logger.info(f"Done! Enriched {enriched} enterprises, found {logos_found} logos")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
