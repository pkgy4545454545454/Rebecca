#!/usr/bin/env python3
"""
SCRAPER V9 - Recherche via local.ch + Scraping sites réels
Trouve les sites web des entreprises suisses via local.ch puis scrape les vraies données
"""
import asyncio
import os
import re
import uuid
import random
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
import httpx
from urllib.parse import urljoin, quote_plus
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'secondevie')
UPLOADS_DIR = '/app/backend/uploads/enterprises'
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://image-fix-demo.preview.emergentagent.com')

os.makedirs(UPLOADS_DIR, exist_ok=True)

# User agents pour éviter le blocage
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
]

print("=" * 70)
print("   SCRAPER V9 - LOCAL.CH + VRAIS SITES")
print("=" * 70)


def parse_price(text):
    if not text:
        return 0
    text = re.sub(r'(CHF|Fr\.|€|\$|SFr\.)', '', text, flags=re.I)
    text = text.replace("'", "").replace(" ", "").replace(".-", "").replace("–", "-")
    match = re.search(r'(\d+\.?\d*)', text.replace(',', '.'))
    return float(match.group(1)) if match else 0


async def download_image(url, filepath, min_size=1000):
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            r = await client.get(url, headers={'User-Agent': random.choice(USER_AGENTS)})
            if r.status_code == 200 and len(r.content) > min_size:
                with open(filepath, 'wb') as f:
                    f.write(r.content)
                return True
    except Exception as e:
        pass
    return False


async def search_localch(page, name, city="Lausanne"):
    """Recherche sur local.ch pour trouver le site web"""
    website = None
    
    try:
        search_url = f"https://www.local.ch/fr/q/{quote_plus(name)}?where={quote_plus(city)}"
        await page.goto(search_url, wait_until='domcontentloaded', timeout=20000)
        await page.wait_for_timeout(random.randint(1500, 3000))
        
        # Chercher le premier résultat avec un site web
        results = await page.query_selector_all('article[data-entry-id]')
        
        for result in results[:3]:
            try:
                # Chercher le lien vers le site web
                website_link = await result.query_selector('a[href*="website"]')
                if website_link:
                    href = await website_link.get_attribute('href')
                    if href and 'redirect' in href:
                        # local.ch redirige via leur propre URL, on doit extraire
                        match = re.search(r'url=([^&]+)', href)
                        if match:
                            website = match.group(1)
                            break
                
                # Alternative: chercher l'icône de globe
                globe_link = await result.query_selector('a[data-poi-event="website"]')
                if globe_link:
                    website = await globe_link.get_attribute('href')
                    if website and 'local.ch' not in website:
                        break
                        
            except Exception:
                continue
                
    except PlaywrightTimeout:
        pass
    except Exception as e:
        pass
    
    return website


async def scrape_website(page, website, eid):
    """Scrape les vraies données d'un site web"""
    result = {
        'cover': None,
        'logo': None,
        'description': None,
        'photos': [],
        'products': []
    }
    
    if not website:
        return result
    
    try:
        await page.goto(website, wait_until='domcontentloaded', timeout=25000)
        await page.wait_for_timeout(random.randint(2000, 4000))
        
        # 1. Screenshot de la page
        cover_file = f'{eid}_cover.jpg'
        cover_path = f'{UPLOADS_DIR}/{cover_file}'
        await page.screenshot(path=cover_path, quality=85, type='jpeg', full_page=False)
        
        # Vérifier que l'image fait plus de 10KB
        if os.path.exists(cover_path) and os.path.getsize(cover_path) > 10000:
            result['cover'] = f'/api/uploads/enterprises/{cover_file}'
            result['photos'].append(result['cover'])
        
        # 2. Logo
        logo_selectors = [
            'img[alt*="logo" i]',
            'img[src*="logo" i]',
            'img[class*="logo" i]',
            'header img:first-child',
            '.logo img',
            '#logo img',
            'a[href="/"] img'
        ]
        
        for sel in logo_selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    src = await el.get_attribute('src')
                    if src:
                        if not src.startswith('http'):
                            src = urljoin(website, src)
                        logo_file = f'{eid}_logo.png'
                        logo_path = f'{UPLOADS_DIR}/{logo_file}'
                        if await download_image(src, logo_path, 200):
                            result['logo'] = f'/api/uploads/enterprises/{logo_file}'
                            break
            except Exception:
                continue
        
        # 3. Description depuis meta tags
        desc_selectors = [
            ('meta[name="description"]', 'content'),
            ('meta[property="og:description"]', 'content'),
            ('meta[name="twitter:description"]', 'content'),
        ]
        
        for sel, attr in desc_selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    text = await el.get_attribute(attr)
                    if text and len(text.strip()) > 30:
                        result['description'] = text.strip()[:500]
                        break
            except Exception:
                continue
        
        # 4. Images de la page
        try:
            imgs = await page.query_selector_all('img')
            count = 0
            for img in imgs[:25]:
                if count >= 5:
                    break
                try:
                    src = await img.get_attribute('src')
                    if not src or 'logo' in src.lower() or 'icon' in src.lower():
                        continue
                    box = await img.bounding_box()
                    if box and box['width'] > 150 and box['height'] > 100:
                        if not src.startswith('http'):
                            src = urljoin(website, src)
                        img_file = f'{eid}_img_{count}.jpg'
                        if await download_image(src, f'{UPLOADS_DIR}/{img_file}', 5000):
                            result['photos'].append(f'/api/uploads/enterprises/{img_file}')
                            count += 1
                except Exception:
                    continue
        except Exception:
            pass
        
        # 5. Produits / Services
        product_selectors = [
            '.product',
            '.product-item',
            '[class*="product"]',
            '.service',
            '.item-card',
            '.card-product'
        ]
        
        for sel in product_selectors:
            try:
                items = await page.query_selector_all(sel)
                for item in items[:10]:
                    prod = {}
                    
                    # Nom du produit
                    name_sels = ['h2', 'h3', 'h4', '.title', '.name', '.product-name']
                    for ns in name_sels:
                        try:
                            ne = await item.query_selector(ns)
                            if ne:
                                nt = await ne.text_content()
                                if nt and 3 < len(nt.strip()) < 100:
                                    prod['name'] = nt.strip()
                                    break
                        except Exception:
                            continue
                    
                    # Prix
                    price_sels = ['.price', '[class*="price"]', '.amount', '.cost']
                    for ps in price_sels:
                        try:
                            pe = await item.query_selector(ps)
                            if pe:
                                pt = await pe.text_content()
                                price = parse_price(pt)
                                if price > 0:
                                    prod['price'] = price
                                    break
                        except Exception:
                            continue
                    
                    if prod.get('name') and prod.get('price', 0) > 0:
                        result['products'].append(prod)
                
                if result['products']:
                    break
            except Exception:
                continue
                
    except PlaywrightTimeout:
        pass
    except Exception as e:
        pass
    
    return result


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Entreprises sans image de couverture réelle
    query = {
        '$or': [
            {'cover_image': None},
            {'cover_image': ''},
            {'cover_image': {'$exists': False}},
            {'enriched_at': {'$exists': False}}
        ]
    }
    
    cursor = db.enterprises.find(query, {
        '_id': 0,
        'id': 1,
        'name': 1,
        'business_name': 1,
        'website': 1,
        'city': 1,
        'address': 1
    })
    
    enterprises = await cursor.to_list(5000)
    total_to_process = len(enterprises)
    
    print(f'\n[INFO] {total_to_process} entreprises à enrichir\n')
    
    if total_to_process == 0:
        print("Aucune entreprise à traiter!")
        return
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=random.choice(USER_AGENTS)
        )
        
        page = await context.new_page()
        
        stats = {
            'processed': 0,
            'covers': 0,
            'logos': 0,
            'products': 0,
            'failed': 0
        }
        
        for i, ent in enumerate(enterprises):
            eid = ent.get('id')
            name = ent.get('business_name') or ent.get('name', '')
            existing_website = ent.get('website')
            city = ent.get('city', 'Lausanne')
            
            if not name:
                continue
            
            stats['processed'] += 1
            print(f'[{i+1}/{total_to_process}] {name[:50]}', end=' ... ')
            
            website = existing_website
            
            # Si pas de site web, chercher sur local.ch
            if not website or not website.startswith('http'):
                website = await search_localch(page, name, city)
                if website:
                    print(f'[local.ch: {website[:30]}]', end=' ')
            
            if website:
                data = await scrape_website(page, website, eid)
                
                if data['cover']:
                    update = {
                        'website': website,
                        'cover_image': data['cover'],
                        'enriched_at': datetime.now(timezone.utc).isoformat(),
                        'enrichment_source': 'localch_v9'
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
                    
                    # Ajouter les produits
                    for prod in data['products']:
                        if prod.get('name') and prod.get('price', 0) > 0:
                            await db.services_products.insert_one({
                                'id': str(uuid.uuid4()),
                                'enterprise_id': eid,
                                'name': prod['name'],
                                'description': '',
                                'type': 'product',
                                'price': prod['price'],
                                'currency': 'CHF',
                                'category': 'general',
                                'is_available': True,
                                'images': [],
                                'created_at': datetime.now(timezone.utc).isoformat(),
                                'source': 'scraping_v9'
                            })
                            stats['products'] += 1
                    
                    print(f'OK (cover{", logo" if data["logo"] else ""}{", " + str(len(data["products"])) + " prods" if data["products"] else ""})')
                else:
                    stats['failed'] += 1
                    print('FAIL (no cover)')
            else:
                stats['failed'] += 1
                print('FAIL (no website)')
            
            # Pause aléatoire pour éviter le blocage
            await asyncio.sleep(random.uniform(1.5, 3.0))
            
            # Afficher les stats tous les 50
            if stats['processed'] % 50 == 0:
                print(f'\n--- Stats: {stats["covers"]} covers, {stats["logos"]} logos, {stats["products"]} products, {stats["failed"]} failed ---\n')
        
        await browser.close()
    
    client.close()
    
    print(f'\n{"=" * 70}')
    print(f'   TERMINÉ!')
    print(f'   Traités: {stats["processed"]}')
    print(f'   Covers: {stats["covers"]}')
    print(f'   Logos: {stats["logos"]}')
    print(f'   Products: {stats["products"]}')
    print(f'   Échecs: {stats["failed"]}')
    print(f'{"=" * 70}')


if __name__ == '__main__':
    asyncio.run(main())
