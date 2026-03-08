#!/usr/bin/env python3
"""
SCRAPER COMPLET V2 - Données réelles des entreprises
- Screenshots réels des sites
- Logos
- Descriptions
- Produits
- Services
- Galerie d'images
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
print("   SCRAPER COMPLET V2 - DONNÉES RÉELLES")
print("=" * 70)

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
    name = enterprise.get('business_name') or enterprise.get('name', 'Unknown')
    
    result = {
        'cover_image': None,
        'logo': None,
        'description': None,
        'photos': [],
        'products': [],
        'services': [],
        'hours': None,
        'social': {}
    }
    
    if not website:
        return result
    
    if not website.startswith('http'):
        website = 'https://' + website
    
    try:
        # Visit the website
        await page.goto(website, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(2000)
        
        # 1. COVER SCREENSHOT
        cover_file = f'{eid}_cover.jpg'
        cover_path = f'{UPLOADS_DIR}/{cover_file}'
        await page.screenshot(path=cover_path, quality=85, type='jpeg')
        result['cover_image'] = f'{BASE_URL}/api/uploads/enterprises/{cover_file}'
        result['photos'].append(result['cover_image'])
        
        # 2. LOGO
        logo_selectors = [
            'img[alt*="logo" i]', 'img[src*="logo" i]', 'img[class*="logo" i]',
            'header img:first-of-type', 'nav img:first-of-type', '.logo img',
            '#logo img', 'a[href="/"] img', '.brand img', '.navbar-brand img'
        ]
        
        for sel in logo_selectors:
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
        
        # 3. DESCRIPTION (meta tags + first paragraphs)
        desc_sources = [
            ('meta[name="description"]', 'content'),
            ('meta[property="og:description"]', 'content'),
            ('meta[name="og:description"]', 'content'),
        ]
        
        for sel, attr in desc_sources:
            try:
                el = await page.query_selector(sel)
                if el:
                    text = await el.get_attribute(attr)
                    if text and len(text.strip()) > 30:
                        result['description'] = text.strip()[:800]
                        break
            except:
                continue
        
        # Fallback: first paragraph
        if not result['description']:
            try:
                paras = await page.query_selector_all('main p, article p, .content p, section p')
                for p in paras[:5]:
                    text = await p.text_content()
                    if text and len(text.strip()) > 50:
                        result['description'] = text.strip()[:800]
                        break
            except:
                pass
        
        # 4. IMAGES (gallery)
        try:
            all_imgs = await page.query_selector_all('img')
            img_count = 0
            seen_srcs = set()
            
            for img in all_imgs:
                if img_count >= 8:
                    break
                try:
                    src = await img.get_attribute('src') or await img.get_attribute('data-src')
                    if not src or src in seen_srcs:
                        continue
                    seen_srcs.add(src)
                    
                    # Skip icons/logos
                    if any(x in src.lower() for x in ['icon', 'logo', 'pixel', '1x1', 'spacer', 'avatar', 'emoji', 'flag']):
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
        
        # 5. PRODUCTS
        product_selectors = [
            '.product', '.produit', '[class*="product"]', '[class*="produit"]',
            '.item', '.card', '.woocommerce-loop-product', '.product-card'
        ]
        
        for sel in product_selectors:
            try:
                items = await page.query_selector_all(sel)
                for item in items[:20]:
                    product = {}
                    
                    # Name
                    for name_sel in ['h2', 'h3', 'h4', '.title', '.name', '[class*="title"]', '[class*="name"]']:
                        try:
                            name_el = await item.query_selector(name_sel)
                            if name_el:
                                name_text = await name_el.text_content()
                                if name_text and 3 < len(name_text.strip()) < 100:
                                    product['name'] = name_text.strip()
                                    break
                        except:
                            continue
                    
                    # Price
                    for price_sel in ['.price', '[class*="price"]', '[class*="prix"]', '.amount']:
                        try:
                            price_el = await item.query_selector(price_sel)
                            if price_el:
                                price_text = await price_el.text_content()
                                # Extract number
                                match = re.search(r'[\d\s.,]+', price_text.replace("'", "").replace(" ", ""))
                                if match:
                                    try:
                                        price_str = match.group().replace(',', '.').replace(' ', '')
                                        product['price'] = float(price_str)
                                        break
                                    except:
                                        pass
                        except:
                            continue
                    
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
                    
                    # Description
                    try:
                        desc_el = await item.query_selector('p, .description, [class*="desc"]')
                        if desc_el:
                            desc_text = await desc_el.text_content()
                            if desc_text and len(desc_text.strip()) > 10:
                                product['description'] = desc_text.strip()[:300]
                    except:
                        pass
                    
                    if product.get('name'):
                        result['products'].append(product)
                
                if result['products']:
                    break
            except:
                continue
        
        # 6. SERVICES
        service_selectors = [
            '.service', '[class*="service"]', '.prestation', '[class*="prestation"]',
            '.offering', '[class*="offering"]'
        ]
        
        for sel in service_selectors:
            try:
                items = await page.query_selector_all(sel)
                for item in items[:15]:
                    service = {}
                    
                    # Name
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
                                match = re.search(r'[\d.,]+', price_text.replace("'", ""))
                                if match:
                                    try:
                                        service['price'] = float(match.group().replace(',', '.'))
                                        break
                                    except:
                                        pass
                        except:
                            continue
                    
                    # Description
                    try:
                        desc_el = await item.query_selector('p, .description')
                        if desc_el:
                            desc_text = await desc_el.text_content()
                            if desc_text:
                                service['description'] = desc_text.strip()[:300]
                    except:
                        pass
                    
                    if service.get('name'):
                        result['services'].append(service)
                
                if result['services']:
                    break
            except:
                continue
        
        # 7. SOCIAL MEDIA LINKS
        social_patterns = {
            'facebook': r'facebook\.com/[^"\s]+',
            'instagram': r'instagram\.com/[^"\s]+',
            'linkedin': r'linkedin\.com/[^"\s]+',
            'twitter': r'twitter\.com/[^"\s]+',
            'youtube': r'youtube\.com/[^"\s]+'
        }
        
        html = await page.content()
        for platform, pattern in social_patterns.items():
            match = re.search(pattern, html)
            if match:
                result['social'][platform] = 'https://' + match.group()
        
        # 8. OPENING HOURS
        try:
            hours_el = await page.query_selector('[class*="hour"], [class*="horaire"], [class*="opening"]')
            if hours_el:
                hours_text = await hours_el.text_content()
                if hours_text and len(hours_text) < 500:
                    result['hours'] = hours_text.strip()
        except:
            pass
            
    except Exception as e:
        print(f'    ✗ Error: {str(e)[:60]}')
    
    return result


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Get enterprises with websites
    cursor = db.enterprises.find({
        'website': {'$exists': True, '$ne': None, '$ne': ''}
    }).limit(500)
    
    enterprises = await cursor.to_list(500)
    print(f'\nFound {len(enterprises)} enterprises with websites\n')
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        stats = {'covers': 0, 'logos': 0, 'products': 0, 'services': 0, 'descriptions': 0}
        
        for i, ent in enumerate(enterprises):
            eid = ent.get('id')
            name = (ent.get('business_name') or ent.get('name', 'Unknown'))[:40]
            
            print(f'[{i+1}/{len(enterprises)}] {name}')
            
            data = await scrape_enterprise(page, ent)
            
            # Build update
            update = {'enriched_at': datetime.now(timezone.utc).isoformat(), 'enrichment_source': 'website_v2'}
            
            if data['cover_image']:
                update['cover_image'] = data['cover_image']
                stats['covers'] += 1
            
            if data['logo']:
                update['logo'] = data['logo']
                stats['logos'] += 1
            
            if data['description']:
                update['description'] = data['description']
                stats['descriptions'] += 1
            
            if data['photos']:
                update['photos'] = data['photos']
                update['gallery'] = data['photos']
            
            if data['social']:
                update['social_links'] = data['social']
            
            if data['hours']:
                update['opening_hours'] = data['hours']
            
            # Update enterprise
            if update:
                await db.enterprises.update_one({'id': eid}, {'$set': update})
            
            # Add products to services_products collection (correct collection)
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
                            'is_premium': False,
                            'created_at': datetime.now(timezone.utc).isoformat(),
                            'source': 'scraping_v2'
                        })
                        stats['products'] += 1
            
            # Add services to services_products collection
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
                            'images': [],
                            'is_available': True,
                            'is_premium': False,
                            'created_at': datetime.now(timezone.utc).isoformat(),
                            'source': 'scraping_v2'
                        })
                        stats['services'] += 1
            
            # Progress
            items = []
            if data['cover_image']:
                items.append('Cover')
            if data['logo']:
                items.append('Logo')
            if data['description']:
                items.append('Desc')
            if data['products']:
                items.append(f'{len(data["products"])} prods')
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
    print(f'   Covers: {stats["covers"]} | Logos: {stats["logos"]} | Descriptions: {stats["descriptions"]}')
    print(f'   Produits: {stats["products"]} | Services: {stats["services"]}')
    print('=' * 70)


if __name__ == '__main__':
    asyncio.run(main())
