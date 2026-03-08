#!/usr/bin/env python3
"""
SCRAPER COMPLET V3 - Avec meilleur parsing des prix suisses
"""
import asyncio
import os
import re
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from playwright.async_api import async_playwright
import httpx
from urllib.parse import urljoin
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'secondevie')
UPLOADS_DIR = '/app/backend/uploads/enterprises'
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://image-fix-demo.preview.emergentagent.com')

os.makedirs(UPLOADS_DIR, exist_ok=True)

print("=" * 70)
print("   SCRAPER COMPLET V3 - PRIX CORRIGÉS")
print("=" * 70)


def parse_swiss_price(text: str) -> float:
    """Parse Swiss price formats: 1'234.56, 1 234,56, CHF 99.-, etc."""
    if not text:
        return 0
    
    # Clean the text
    text = text.strip()
    
    # Remove currency symbols and text
    text = re.sub(r'(CHF|Fr\.|SFr\.?|€|\$)', '', text, flags=re.I)
    
    # Remove ".-" at the end (Swiss format for .00)
    text = re.sub(r'\.-\s*$', '', text)
    
    # Remove spaces and apostrophes (thousand separators)
    text = text.replace("'", "").replace(" ", "").replace("\u00a0", "")
    
    # Handle comma as decimal separator
    if ',' in text and '.' in text:
        # Both present: assume comma is thousand sep, dot is decimal
        text = text.replace(',', '')
    elif ',' in text:
        # Only comma: could be decimal separator
        text = text.replace(',', '.')
    
    # Extract the number
    match = re.search(r'(\d+\.?\d*)', text)
    if match:
        try:
            return float(match.group(1))
        except:
            pass
    
    return 0


async def download_image(url: str, filepath: str, min_size: int = 1000) -> bool:
    """Download image from URL"""
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


async def scrape_enterprise(page, enterprise: dict) -> dict:
    """Scrape toutes les données d'un site d'entreprise"""
    eid = enterprise.get('id')
    website = enterprise.get('website', '')
    
    result = {
        'cover_image': None,
        'logo': None,
        'description': None,
        'photos': [],
        'products': [],
        'services': []
    }
    
    if not website:
        return result
    
    if not website.startswith('http'):
        website = 'https://' + website
    
    try:
        await page.goto(website, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(2000)
        
        # 1. COVER SCREENSHOT
        cover_file = f'{eid}_cover.jpg'
        cover_path = f'{UPLOADS_DIR}/{cover_file}'
        await page.screenshot(path=cover_path, quality=85, type='jpeg')
        result['cover_image'] = f'{BASE_URL}/api/uploads/enterprises/{cover_file}'
        result['photos'].append(result['cover_image'])
        
        # 2. LOGO
        for sel in ['img[alt*="logo" i]', 'img[src*="logo" i]', 'header img:first-of-type', '.logo img', 'nav img']:
            try:
                el = await page.query_selector(sel)
                if el:
                    box = await el.bounding_box()
                    if box and box['width'] > 20 and box['height'] > 20:
                        src = await el.get_attribute('src')
                        if src:
                            if not src.startswith('http'):
                                src = urljoin(website, src)
                            logo_file = f'{eid}_logo.png'
                            if await download_image(src, f'{UPLOADS_DIR}/{logo_file}', 300):
                                result['logo'] = f'{BASE_URL}/api/uploads/enterprises/{logo_file}'
                                break
            except:
                continue
        
        # 3. DESCRIPTION
        for sel, attr in [('meta[name="description"]', 'content'), ('meta[property="og:description"]', 'content')]:
            try:
                el = await page.query_selector(sel)
                if el:
                    text = await el.get_attribute(attr)
                    if text and len(text.strip()) > 30:
                        result['description'] = text.strip()[:800]
                        break
            except:
                continue
        
        # 4. IMAGES
        try:
            all_imgs = await page.query_selector_all('img')
            img_count = 0
            seen = set()
            
            for img in all_imgs:
                if img_count >= 8:
                    break
                try:
                    src = await img.get_attribute('src') or await img.get_attribute('data-src')
                    if not src or src in seen:
                        continue
                    seen.add(src)
                    
                    if any(x in src.lower() for x in ['icon', 'logo', 'pixel', '1x1', 'spacer', 'avatar']):
                        continue
                    
                    box = await img.bounding_box()
                    if box and box['width'] > 150 and box['height'] > 100:
                        if not src.startswith('http'):
                            src = urljoin(website, src)
                        img_file = f'{eid}_img_{img_count}.jpg'
                        if await download_image(src, f'{UPLOADS_DIR}/{img_file}', 5000):
                            result['photos'].append(f'{BASE_URL}/api/uploads/enterprises/{img_file}')
                            img_count += 1
                except:
                    continue
        except:
            pass
        
        # 5. PRODUCTS WITH PRICES
        product_selectors = [
            '.product', '.produit', '[class*="product"]', '[class*="produit"]',
            '.item', '.card', '.woocommerce-loop-product', '.product-card',
            '[data-product]', '.shop-item'
        ]
        
        for sel in product_selectors:
            try:
                items = await page.query_selector_all(sel)
                for item in items[:20]:
                    product = {'name': None, 'price': 0, 'image': None, 'description': None}
                    
                    # Name
                    for name_sel in ['h2', 'h3', 'h4', '.title', '.name', '[class*="title"]', '[class*="name"]', 'a']:
                        try:
                            name_el = await item.query_selector(name_sel)
                            if name_el:
                                name_text = await name_el.text_content()
                                if name_text and 3 < len(name_text.strip()) < 100:
                                    product['name'] = name_text.strip()
                                    break
                        except:
                            continue
                    
                    # Price - improved parsing
                    for price_sel in ['.price', '[class*="price"]', '[class*="prix"]', '.amount', '[class*="cost"]', '[class*="tarif"]', 'span[class*="money"]']:
                        try:
                            price_el = await item.query_selector(price_sel)
                            if price_el:
                                price_text = await price_el.text_content()
                                parsed_price = parse_swiss_price(price_text)
                                if parsed_price > 0:
                                    product['price'] = parsed_price
                                    break
                        except:
                            continue
                    
                    # If no price found in specific element, search in full item text
                    if product['price'] == 0:
                        try:
                            full_text = await item.text_content()
                            # Look for price patterns
                            price_patterns = [
                                r"CHF\s*([\d'., ]+)",
                                r"Fr\.?\s*([\d'., ]+)",
                                r"([\d'., ]+)\s*CHF",
                                r"([\d'., ]+)\s*Fr\.?",
                                r"Prix[:\s]*([\d'., ]+)",
                            ]
                            for pattern in price_patterns:
                                match = re.search(pattern, full_text, re.I)
                                if match:
                                    parsed = parse_swiss_price(match.group(1))
                                    if parsed > 0:
                                        product['price'] = parsed
                                        break
                        except:
                            pass
                    
                    # Image
                    try:
                        img_el = await item.query_selector('img')
                        if img_el:
                            img_src = await img_el.get_attribute('src')
                            if img_src:
                                if not img_src.startswith('http'):
                                    img_src = urljoin(website, img_src)
                                product['image'] = img_src
                    except:
                        pass
                    
                    if product['name']:
                        result['products'].append(product)
                
                if result['products']:
                    break
            except:
                continue
        
        # 6. SERVICES WITH PRICES
        service_selectors = ['.service', '[class*="service"]', '.prestation', '[class*="prestation"]']
        
        for sel in service_selectors:
            try:
                items = await page.query_selector_all(sel)
                for item in items[:15]:
                    service = {'name': None, 'price': 0, 'description': None}
                    
                    for name_sel in ['h2', 'h3', 'h4', '.title', '.name']:
                        try:
                            name_el = await item.query_selector(name_sel)
                            if name_el:
                                name_text = await name_el.text_content()
                                if name_text and 3 < len(name_text.strip()) < 100:
                                    service['name'] = name_text.strip()
                                    break
                        except:
                            continue
                    
                    # Price
                    for price_sel in ['.price', '[class*="price"]', '[class*="prix"]', '[class*="tarif"]']:
                        try:
                            price_el = await item.query_selector(price_sel)
                            if price_el:
                                price_text = await price_el.text_content()
                                parsed_price = parse_swiss_price(price_text)
                                if parsed_price > 0:
                                    service['price'] = parsed_price
                                    break
                        except:
                            continue
                    
                    if service['name']:
                        result['services'].append(service)
                
                if result['services']:
                    break
            except:
                continue
                
    except Exception as e:
        print(f'    ✗ Error: {str(e)[:60]}')
    
    return result


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Get enterprises with websites but NOT YET properly scraped (no real cover)
    cursor = db.enterprises.find({
        'website': {'$exists': True, '$ne': None, '$ne': ''},
        '$or': [
            {'cover_image': None},
            {'cover_image': ''},
            {'cover_image': {'$not': {'$regex': 'uploads/enterprises'}}}
        ]
    }).limit(500)
    
    enterprises = await cursor.to_list(400)
    print(f'\nFound {len(enterprises)} enterprises to scrape\n')
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        stats = {'covers': 0, 'logos': 0, 'products': 0, 'services': 0, 'with_price': 0}
        
        for i, ent in enumerate(enterprises):
            eid = ent.get('id')
            name = (ent.get('business_name') or ent.get('name', 'Unknown'))[:40]
            
            print(f'[{i+1}/{len(enterprises)}] {name}')
            
            data = await scrape_enterprise(page, ent)
            
            update = {'enriched_at': datetime.now(timezone.utc).isoformat(), 'enrichment_source': 'website_v3'}
            
            if data['cover_image']:
                update['cover_image'] = data['cover_image']
                stats['covers'] += 1
            
            if data['logo']:
                update['logo'] = data['logo']
                stats['logos'] += 1
            
            if data['description']:
                update['description'] = data['description']
            
            if data['photos']:
                update['photos'] = data['photos']
                update['gallery'] = data['photos']
            
            await db.enterprises.update_one({'id': eid}, {'$set': update})
            
            # Products
            for prod in data['products']:
                if prod.get('name'):
                    exists = await db.services_products.find_one({'enterprise_id': eid, 'name': prod['name']})
                    if not exists:
                        await db.services_products.insert_one({
                            'id': str(uuid.uuid4()),
                            'enterprise_id': eid,
                            'name': prod['name'],
                            'type': 'product',
                            'category': 'Produit',
                            'description': prod.get('description', ''),
                            'price': prod.get('price', 0),
                            'images': [prod.get('image')] if prod.get('image') else [],
                            'is_available': True,
                            'created_at': datetime.now(timezone.utc).isoformat(),
                            'source': 'scraping_v3'
                        })
                        stats['products'] += 1
                        if prod.get('price', 0) > 0:
                            stats['with_price'] += 1
            
            # Services
            for svc in data['services']:
                if svc.get('name'):
                    exists = await db.services_products.find_one({'enterprise_id': eid, 'name': svc['name']})
                    if not exists:
                        await db.services_products.insert_one({
                            'id': str(uuid.uuid4()),
                            'enterprise_id': eid,
                            'name': svc['name'],
                            'type': 'service',
                            'category': 'Service',
                            'description': svc.get('description', ''),
                            'price': svc.get('price', 0),
                            'duration': 60,
                            'is_available': True,
                            'created_at': datetime.now(timezone.utc).isoformat(),
                            'source': 'scraping_v3'
                        })
                        stats['services'] += 1
                        if svc.get('price', 0) > 0:
                            stats['with_price'] += 1
            
            # Progress
            items = []
            if data['cover_image']:
                items.append('Cover')
            if data['logo']:
                items.append('Logo')
            if data['description']:
                items.append('Desc')
            if data['products']:
                priced = sum(1 for p in data['products'] if p.get('price', 0) > 0)
                items.append(f'{len(data["products"])} prods ({priced} with price)')
            if data['services']:
                items.append(f'{len(data["services"])} svcs')
            if data['photos']:
                items.append(f'{len(data["photos"])} imgs')
            
            if items:
                print(f'    ✓ {", ".join(items)}')
            
            await asyncio.sleep(1.5)
        
        await browser.close()
    
    client.close()
    
    print('\n' + '=' * 70)
    print(f'   TERMINÉ!')
    print(f'   Covers: {stats["covers"]} | Logos: {stats["logos"]}')
    print(f'   Produits: {stats["products"]} | Services: {stats["services"]}')
    print(f'   Avec prix: {stats["with_price"]}')
    print('=' * 70)


if __name__ == '__main__':
    asyncio.run(main())
