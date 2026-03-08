import asyncio
import os
import httpx
import re
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from urllib.parse import urljoin

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'secondevie')
UPLOADS_DIR = "/app/backend/uploads/enterprises"
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://image-fix-demo.preview.emergentagent.com')

os.makedirs(UPLOADS_DIR, exist_ok=True)

# Category to image mapping
CATEGORY_IMAGES = {
    'restaurant': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800',
    'restauration': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800',
    'cafe': 'https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=800',
    'coiffure': 'https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800',
    'salon': 'https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800',
    'beaute': 'https://images.unsplash.com/photo-1560750588-73207b1ef5b8?w=800',
    'spa': 'https://images.unsplash.com/photo-1544161515-4ab6ce6db874?w=800',
    'fitness': 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800',
    'sport': 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800',
    'cours_sport': 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800',
    'bijouterie': 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800',
    'bijouteries': 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800',
    'horlogerie': 'https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=800',
    'mode': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800',
    'vetement': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800',
    'accessoires': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800',
    'immobilier': 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800',
    'agences immobilieres': 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800',
    'agence': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800',
    'services': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800',
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
    'services financiers': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800',
    'finance': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800',
    'banque': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800',
    'assurance': 'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=800',
    'juridique': 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=800',
    'avocat': 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=800',
    'default': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800'
}

async def fetch_logo(website: str, eid: str) -> str:
    """Try to fetch logo from website"""
    if not website:
        return None
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = await client.get(website, headers=headers)
            html = r.text
            
            # Search for logo
            patterns = [
                r'<link[^>]*rel=["\'](?:apple-touch-icon|icon)["\'][^>]*href=["\']([^"\']+)["\']',
                r'<img[^>]*class=["\'][^"\']*logo[^"\']*["\'][^>]*src=["\']([^"\']+)["\']',
                r'<img[^>]*src=["\']([^"\']+logo[^"\']*)["\']',
            ]
            
            for p in patterns:
                m = re.findall(p, html, re.I)
                if m:
                    logo_url = m[0]
                    if not logo_url.startswith('http'):
                        logo_url = urljoin(website, logo_url)
                    
                    # Download
                    lr = await client.get(logo_url, headers=headers)
                    if lr.status_code == 200 and len(lr.content) > 500:
                        ext = 'png' if '.png' in logo_url.lower() else 'jpg'
                        fname = f"{eid}_logo.{ext}"
                        fpath = os.path.join(UPLOADS_DIR, fname)
                        with open(fpath, 'wb') as f:
                            f.write(lr.content)
                        return f"{BASE_URL}/api/uploads/enterprises/{fname}"
    except:
        pass
    return None

def get_cover_for_category(category: str) -> str:
    """Get cover image URL for category"""
    cat = (category or '').lower()
    for key, url in CATEGORY_IMAGES.items():
        if key in cat:
            return url
    return CATEGORY_IMAGES['default']

async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    cursor = db.enterprises.find({}).limit(1000)
    enterprises = await cursor.to_list(1000)
    
    print(f"Processing {len(enterprises)} enterprises...")
    
    logos = 0
    covers = 0
    
    for i, e in enumerate(enterprises):
        eid = e.get('id')
        updates = {}
        
        # Logo
        if not e.get('logo'):
            logo = await fetch_logo(e.get('website'), eid)
            if logo:
                updates['logo'] = logo
                logos += 1
        
        # Cover
        if not e.get('cover_image'):
            cover = get_cover_for_category(e.get('category'))
            updates['cover_image'] = cover
            covers += 1
        
        if updates:
            await db.enterprises.update_one({"id": eid}, {"$set": updates})
        
        if (i+1) % 50 == 0:
            print(f"Progress: {i+1}/{len(enterprises)} | Logos: {logos} | Covers: {covers}")
    
    print(f"Done! Logos: {logos}, Covers: {covers}")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
