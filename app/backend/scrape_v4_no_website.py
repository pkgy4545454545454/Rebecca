#!/usr/bin/env python3
"""
SCRAPER V4 - Entreprises SANS site web
Recherche sur Google/local.ch pour trouver des infos
"""
import asyncio
import os
import re
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from playwright.async_api import async_playwright
import httpx
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'secondevie')
UPLOADS_DIR = '/app/backend/uploads/enterprises'
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://image-fix-demo.preview.emergentagent.com')

os.makedirs(UPLOADS_DIR, exist_ok=True)

print("=" * 70)
print("   SCRAPER V4 - ENTREPRISES SANS SITE WEB")
print("   Recherche Google/local.ch")
print("=" * 70)


async def search_on_localch(page, name: str, city: str = "Lausanne") -> dict:
    """Search enterprise on local.ch and get info"""
    result = {'website': None, 'phone': None, 'address': None, 'description': None}
    
    try:
        search_url = f"https://www.local.ch/fr/q/{quote_plus(name)}?where={quote_plus(city)}"
        await page.goto(search_url, wait_until='networkidle', timeout=20000)
        await page.wait_for_timeout(2000)
        
        # Click first result
        first_result = await page.query_selector('a[data-testid="search-result-entry"]')
        if first_result:
            await first_result.click()
            await page.wait_for_timeout(2000)
            
            # Get website
            website_el = await page.query_selector('a[data-testid="website-link"]')
            if website_el:
                result['website'] = await website_el.get_attribute('href')
            
            # Get phone
            phone_el = await page.query_selector('a[href^="tel:"]')
            if phone_el:
                result['phone'] = await phone_el.text_content()
            
            # Get address
            address_el = await page.query_selector('[data-testid="address"]')
            if address_el:
                result['address'] = await address_el.text_content()
                
    except Exception as e:
        print(f'    local.ch error: {str(e)[:50]}')
    
    return result


async def generate_description_from_category(name: str, category: str, city: str) -> str:
    """Generate a basic description based on category"""
    descriptions = {
        'restaurant': f"{name} est un restaurant situé à {city}. Venez découvrir notre cuisine et nos spécialités.",
        'restauration': f"{name} est un établissement de restauration à {city}.",
        'coiffure': f"{name} est un salon de coiffure professionnel à {city}. Nos experts prennent soin de vos cheveux.",
        'beaute': f"{name} est un institut de beauté à {city}. Découvrez nos soins et prestations.",
        'spa': f"{name} est un spa et centre de bien-être à {city}.",
        'fitness': f"{name} est une salle de sport et fitness à {city}.",
        'bijouterie': f"{name} est une bijouterie à {city}. Découvrez notre sélection de bijoux et montres.",
        'mode': f"{name} est une boutique de mode à {city}.",
        'immobilier': f"{name} est une agence immobilière à {city}.",
        'default': f"{name} est une entreprise locale située à {city}. Contactez-nous pour plus d'informations."
    }
    
    cat_lower = (category or '').lower()
    for key, desc in descriptions.items():
        if key in cat_lower:
            return desc
    return descriptions['default']


async def download_image(url: str, filepath: str) -> bool:
    """Download image"""
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            r = await client.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code == 200 and len(r.content) > 1000:
                with open(filepath, 'wb') as f:
                    f.write(r.content)
                return True
    except:
        pass
    return False


async def scrape_website(page, website: str, eid: str) -> dict:
    """Scrape a found website"""
    result = {'cover': None, 'logo': None, 'description': None, 'photos': []}
    
    if not website:
        return result
    
    try:
        if not website.startswith('http'):
            website = 'https://' + website
            
        await page.goto(website, wait_until='networkidle', timeout=25000)
        await page.wait_for_timeout(2000)
        
        # Screenshot
        cover_file = f'{eid}_cover.jpg'
        await page.screenshot(path=f'{UPLOADS_DIR}/{cover_file}', quality=85, type='jpeg')
        result['cover'] = f'{BASE_URL}/api/uploads/enterprises/{cover_file}'
        result['photos'].append(result['cover'])
        
        # Logo
        for sel in ['img[alt*="logo" i]', 'img[src*="logo" i]', 'header img', '.logo img']:
            try:
                el = await page.query_selector(sel)
                if el:
                    src = await el.get_attribute('src')
                    if src:
                        if not src.startswith('http'):
                            from urllib.parse import urljoin
                            src = urljoin(website, src)
                        logo_file = f'{eid}_logo.png'
                        if await download_image(src, f'{UPLOADS_DIR}/{logo_file}'):
                            result['logo'] = f'{BASE_URL}/api/uploads/enterprises/{logo_file}'
                            break
            except:
                continue
        
        # Description
        for sel in [('meta[name="description"]', 'content'), ('meta[property="og:description"]', 'content')]:
            try:
                el = await page.query_selector(sel[0])
                if el:
                    text = await el.get_attribute(sel[1])
                    if text and len(text) > 30:
                        result['description'] = text.strip()[:500]
                        break
            except:
                continue
                
    except Exception as e:
        print(f'    Website error: {str(e)[:50]}')
    
    return result


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Get enterprises WITHOUT websites that haven't been enriched
    cursor = db.enterprises.find({
        '$or': [
            {'website': None},
            {'website': ''},
            {'website': {'$exists': False}}
        ],
        'enrichment_source': {'$ne': 'website_v4'}
    }).limit(700)
    
    enterprises = await cursor.to_list(700)
    print(f'\nFound {len(enterprises)} enterprises without websites\n')
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        stats = {'enriched': 0, 'websites_found': 0, 'covers': 0}
        
        for i, ent in enumerate(enterprises):
            eid = ent.get('id')
            name = (ent.get('business_name') or ent.get('name', 'Unknown'))
            city = ent.get('city', 'Lausanne')
            category = ent.get('category', '')
            
            print(f'[{i+1}/{len(enterprises)}] {name[:40]}')
            
            update = {'enriched_at': datetime.now(timezone.utc).isoformat(), 'enrichment_source': 'website_v4'}
            
            # Search on local.ch
            localch_data = await search_on_localch(page, name, city)
            
            if localch_data.get('website'):
                update['website'] = localch_data['website']
                stats['websites_found'] += 1
                
                # Scrape the found website
                site_data = await scrape_website(page, localch_data['website'], eid)
                
                if site_data['cover']:
                    update['cover_image'] = site_data['cover']
                    stats['covers'] += 1
                if site_data['logo']:
                    update['logo'] = site_data['logo']
                if site_data['description']:
                    update['description'] = site_data['description']
                if site_data['photos']:
                    update['photos'] = site_data['photos']
                    
                print(f'    ✓ Found website: {localch_data["website"][:50]}')
            else:
                # Generate description from category
                if not ent.get('description') or ent.get('description') == '':
                    update['description'] = await generate_description_from_category(name, category, city)
                print(f'    - No website found, generated description')
            
            if localch_data.get('phone'):
                update['phone'] = localch_data['phone']
            if localch_data.get('address'):
                update['address'] = localch_data['address']
            
            await db.enterprises.update_one({'id': eid}, {'$set': update})
            stats['enriched'] += 1
            
            await asyncio.sleep(2)
        
        await browser.close()
    
    client.close()
    
    print('\n' + '=' * 70)
    print(f'   TERMINÉ!')
    print(f'   Enriched: {stats["enriched"]}')
    print(f'   Websites found: {stats["websites_found"]}')
    print(f'   Covers: {stats["covers"]}')
    print('=' * 70)


if __name__ == '__main__':
    asyncio.run(main())
