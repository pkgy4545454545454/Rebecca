#!/usr/bin/env python3
"""
SCRAPER V7 - Recherche Google améliorée + Scraping réel
"""
import asyncio
import os
import re
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from playwright.async_api import async_playwright
import httpx
from urllib.parse import urljoin, quote_plus
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'secondevie')
UPLOADS_DIR = '/app/backend/uploads/enterprises'
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')

os.makedirs(UPLOADS_DIR, exist_ok=True)

print("=" * 70)
print("   SCRAPER V7 - RECHERCHE GOOGLE + SCRAPING RÉEL")
print("=" * 70)


def parse_price(text):
    if not text: return 0
    text = re.sub(r'(CHF|Fr\.|€|\$)', '', text, flags=re.I)
    text = text.replace("'", "").replace(" ", "").replace(".-", "")
    if ',' in text and '.' in text:
        text = text.replace(',', '')
    elif ',' in text:
        text = text.replace(',', '.')
    match = re.search(r'(\d+\.?\d*)', text)
    return float(match.group(1)) if match else 0


async def download_image(url, filepath, min_size=1000):
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            r = await client.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code == 200 and len(r.content) > min_size:
                with open(filepath, 'wb') as f:
                    f.write(r.content)
                return True
    except:
        pass
    return False


async def search_website(page, name, city="Lausanne"):
    """Search for enterprise website via DuckDuckGo (less blocking than Google)"""
    exclude = ['google.', 'youtube.', 'facebook.', 'instagram.', 'linkedin.', 'twitter.', 
               'local.ch', 'search.ch', 'wikipedia', 'yelp.', 'tripadvisor.', 'pages']
    
    try:
        # Try DuckDuckGo first (less blocking)
        query = f"{name} {city} site officiel"
        await page.goto(f"https://duckduckgo.com/?q={quote_plus(query)}", wait_until='networkidle', timeout=15000)
        await page.wait_for_timeout(2000)
        
        # Get results
        links = await page.query_selector_all('a[href^="http"]')
        for link in links[:15]:
            href = await link.get_attribute('href')
            if href and not any(x in href.lower() for x in exclude):
                # Verify it looks like a company website
                if '.ch' in href or '.com' in href or '.fr' in href:
                    return href
    except:
        pass
    
    return None


async def scrape_website(page, website, eid):
    """Scrape real data from website"""
    result = {'cover': None, 'logo': None, 'description': None, 'photos': [], 'products': []}
    
    if not website or not website.startswith('http'):
        return result
    
    try:
        await page.goto(website, wait_until='networkidle', timeout=20000)
        await page.wait_for_timeout(1500)
        
        # Screenshot
        cover_file = f'{eid}_cover.jpg'
        await page.screenshot(path=f'{UPLOADS_DIR}/{cover_file}', quality=85, type='jpeg')
        result['cover'] = f'{BASE_URL}/api/uploads/enterprises/{cover_file}'
        result['photos'].append(result['cover'])
        
        # Logo
        for sel in ['img[alt*="logo" i]', 'img[src*="logo" i]', 'header img', '.logo img', 'nav img']:
            try:
                el = await page.query_selector(sel)
                if el:
                    box = await el.bounding_box()
                    if box and box['width'] > 20:
                        src = await el.get_attribute('src')
                        if src:
                            if not src.startswith('http'):
                                src = urljoin(website, src)
                            logo_file = f'{eid}_logo.png'
                            if await download_image(src, f'{UPLOADS_DIR}/{logo_file}', 200):
                                result['logo'] = f'{BASE_URL}/api/uploads/enterprises/{logo_file}'
                                break
            except:
                continue
        
        # Description
        for sel, attr in [('meta[name="description"]', 'content'), ('meta[property="og:description"]', 'content')]:
            try:
                el = await page.query_selector(sel)
                if el:
                    text = await el.get_attribute(attr)
                    if text and len(text) > 20:
                        result['description'] = text.strip()[:500]
                        break
            except:
                continue
        
        # Images
        try:
            imgs = await page.query_selector_all('img')
            count = 0
            for img in imgs[:20]:
                if count >= 5: break
                src = await img.get_attribute('src')
                if src and 'logo' not in src.lower() and 'icon' not in src.lower():
                    box = await img.bounding_box()
                    if box and box['width'] > 150:
                        if not src.startswith('http'):
                            src = urljoin(website, src)
                        img_file = f'{eid}_img_{count}.jpg'
                        if await download_image(src, f'{UPLOADS_DIR}/{img_file}', 2000):
                            result['photos'].append(f'{BASE_URL}/api/uploads/enterprises/{img_file}')
                            count += 1
        except:
            pass
        
        # Products
        for sel in ['.product', '[class*="product"]', '.item', '.card', '[class*="article"]']:
            try:
                items = await page.query_selector_all(sel)
                for item in items[:10]:
                    prod = {}
                    for ns in ['h2', 'h3', 'h4', '.title', '.name']:
                        try:
                            ne = await item.query_selector(ns)
                            if ne:
                                nt = await ne.text_content()
                                if nt and 3 < len(nt.strip()) < 80:
                                    prod['name'] = nt.strip()
                                    break
                        except:
                            continue
                    for ps in ['.price', '[class*="price"]', '[class*="prix"]']:
                        try:
                            pe = await item.query_selector(ps)
                            if pe:
                                pt = await pe.text_content()
                                price = parse_price(pt)
                                if price > 0:
                                    prod['price'] = price
                                    break
                        except:
                            continue
                    if prod.get('name') and prod.get('price', 0) > 0:
                        result['products'].append(prod)
                if result['products']:
                    break
            except:
                continue
                
    except:
        pass
    
    return result


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Enterprises without real cover
    cursor = db.enterprises.find({
        '$or': [
            {'cover_image': None},
            {'cover_image': ''},
            {'cover_image': {'$not': {'$regex': 'uploads/enterprises'}}}
        ]
    }).limit(500)
    
    enterprises = await cursor.to_list(500)
    print(f'\nFound {len(enterprises)} enterprises to enrich\n')
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        stats = {'total': 0, 'found': 0, 'covers': 0, 'logos': 0, 'products': 0}
        
        for i, ent in enumerate(enterprises):
            eid = ent.get('id')
            name = ent.get('business_name') or ent.get('name', '')
            city = ent.get('city', 'Lausanne')
            existing_website = ent.get('website')
            
            if not name or len(name) < 3:
                continue
            
            stats['total'] += 1
            print(f'[{i+1}/{len(enterprises)}] {name[:40]}')
            
            # Use existing website or search for one
            website = existing_website
            if not website or not website.startswith('http'):
                website = await search_website(page, name, city)
            
            if website:
                stats['found'] += 1
                data = await scrape_website(page, website, eid)
                
                if data['cover']:
                    update = {
                        'website': website,
                        'cover_image': data['cover'],
                        'enriched_at': datetime.now(timezone.utc).isoformat(),
                        'enrichment_source': 'website_v7'
                    }
                    if data['logo']:
                        update['logo'] = data['logo']
                        stats['logos'] += 1
                    if data['description']:
                        update['description'] = data['description']
                    if data['photos']:
                        update['photos'] = data['photos']
                    
                    await db.enterprises.update_one({'id': eid}, {'$set': update})
                    stats['covers'] += 1
                    
                    for prod in data['products']:
                        if prod.get('name') and prod.get('price', 0) > 0:
                            exists = await db.services_products.find_one({'enterprise_id': eid, 'name': prod['name']})
                            if not exists:
                                await db.services_products.insert_one({
                                    'id': str(uuid.uuid4()),
                                    'enterprise_id': eid,
                                    'name': prod['name'],
                                    'type': 'product',
                                    'price': prod['price'],
                                    'is_available': True,
                                    'source': 'scraping_v7'
                                })
                                stats['products'] += 1
                    
                    items = []
                    if data['cover']: items.append('Cover')
                    if data['logo']: items.append('Logo')
                    if data['description']: items.append('Desc')
                    if data['products']: items.append(f"{len(data['products'])} prods")
                    print(f'    ✓ {", ".join(items)}')
                else:
                    print(f'    ✗ Scrape failed')
            else:
                print(f'    ✗ No website')
            
            await asyncio.sleep(1.5)
        
        await browser.close()
    
    client.close()
    
    print(f'\n{"=" * 70}')
    print(f'   TERMINÉ!')
    print(f'   Total: {stats["total"]} | Found: {stats["found"]}')
    print(f'   Covers: {stats["covers"]} | Logos: {stats["logos"]} | Products: {stats["products"]}')
    print(f'{"=" * 70}')


if __name__ == '__main__':
    asyncio.run(main())
