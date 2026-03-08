#!/usr/bin/env python3
"""
SCRAPER V8 - Sites connus + Recherche améliorée
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
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')

os.makedirs(UPLOADS_DIR, exist_ok=True)

# Known brand websites
KNOWN_WEBSITES = {
    'migros': 'https://www.migros.ch',
    'coop': 'https://www.coop.ch',
    'denner': 'https://www.denner.ch',
    'manor': 'https://www.manor.ch',
    'h&m': 'https://www.hm.com/ch_fr',
    'zara': 'https://www.zara.com/ch',
    'mango': 'https://www.mango.com',
    'nike': 'https://www.nike.com/ch',
    'adidas': 'https://www.adidas.ch',
    'decathlon': 'https://www.decathlon.ch',
    'ikea': 'https://www.ikea.com/ch/fr',
    'mcdonalds': 'https://www.mcdonalds.ch',
    'starbucks': 'https://www.starbucks.ch',
    'subway': 'https://www.subway.ch',
    'burger king': 'https://www.burgerking.ch',
    'swatch': 'https://www.swatch.com',
    'rolex': 'https://www.rolex.com',
    'omega': 'https://www.omegawatches.com',
    'tissot': 'https://www.tissotwatches.com',
    'tag heuer': 'https://www.tagheuer.com',
    'apple': 'https://www.apple.com/chfr',
    'samsung': 'https://www.samsung.com/ch',
    'swisscom': 'https://www.swisscom.ch',
    'sunrise': 'https://www.sunrise.ch',
    'salt': 'https://www.salt.ch',
    'ubs': 'https://www.ubs.com/ch/fr',
    'credit suisse': 'https://www.credit-suisse.com',
    'raiffeisen': 'https://www.raiffeisen.ch',
    'post': 'https://www.post.ch',
    'sbb': 'https://www.sbb.ch',
    'cff': 'https://www.sbb.ch/fr',
    'ochsner sport': 'https://www.ochsnersport.ch',
    'intersport': 'https://www.intersport.ch',
    'sportxx': 'https://www.sportxx.ch',
    'media markt': 'https://www.mediamarkt.ch',
    'fust': 'https://www.fust.ch',
    'interdiscount': 'https://www.interdiscount.ch',
    'fnac': 'https://www.fnac.ch',
    'digitec': 'https://www.digitec.ch',
    'galaxus': 'https://www.galaxus.ch',
    'la poste': 'https://www.post.ch/fr',
    'pharmacie': 'https://www.sunstore.ch',
    'bodyminute': 'https://www.bodyminute.com',
    'yves rocher': 'https://www.yves-rocher.ch',
    'the body shop': 'https://www.thebodyshop.com',
    'sephora': 'https://www.sephora.ch',
    'marionnaud': 'https://www.marionnaud.ch',
    'douglas': 'https://www.douglas.ch',
    'lush': 'https://www.lush.com/ch/fr',
    'kiko': 'https://www.kikocosmetics.com',
    'bershka': 'https://www.bershka.com',
    'pull&bear': 'https://www.pullandbear.com',
    'massimo dutti': 'https://www.massimodutti.com',
    'uniqlo': 'https://www.uniqlo.com',
    'primark': 'https://www.primark.com',
    'c&a': 'https://www.c-and-a.com',
    'esprit': 'https://www.esprit.ch',
    'only': 'https://www.only.com',
    'vero moda': 'https://www.veromoda.com',
    'jack & jones': 'https://www.jackjones.com',
    'guess': 'https://www.guess.eu',
    'tommy hilfiger': 'https://ch.tommy.com',
    'calvin klein': 'https://www.calvinklein.ch',
    'lacoste': 'https://www.lacoste.com',
    'hugo boss': 'https://www.hugoboss.com',
    'louis vuitton': 'https://www.louisvuitton.com',
    'gucci': 'https://www.gucci.com',
    'prada': 'https://www.prada.com',
    'chanel': 'https://www.chanel.com',
    'dior': 'https://www.dior.com',
    'hermès': 'https://www.hermes.com',
    'cartier': 'https://www.cartier.com',
    'tiffany': 'https://www.tiffany.com',
    'pandora': 'https://www.pandora.net',
    'swarovski': 'https://www.swarovski.com',
    'fielmann': 'https://www.fielmann.ch',
    'visilab': 'https://www.visilab.ch',
    'mcoptique': 'https://www.mcoptique.ch',
    'pearle': 'https://www.pearle.ch',
    'amplifon': 'https://www.amplifon.com/ch',
    'pharmacieplus': 'https://www.pharmacieplus.ch',
    'amavita': 'https://www.amavita.ch',
    'benu': 'https://www.benu.ch',
    'coop vitality': 'https://www.coopvitality.ch',
}

print("=" * 70)
print("   SCRAPER V8 - SITES CONNUS + SCRAPING")
print("=" * 70)


def parse_price(text):
    if not text: return 0
    text = re.sub(r'(CHF|Fr\.|€|\$)', '', text, flags=re.I)
    text = text.replace("'", "").replace(" ", "").replace(".-", "")
    match = re.search(r'(\d+\.?\d*)', text.replace(',', '.'))
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


def find_known_website(name):
    """Find website from known brands"""
    name_lower = name.lower().strip()
    for brand, url in KNOWN_WEBSITES.items():
        if brand in name_lower or name_lower in brand:
            return url
    return None


async def scrape_website(page, website, eid):
    """Scrape real data from website"""
    result = {'cover': None, 'logo': None, 'description': None, 'photos': [], 'products': []}
    
    if not website:
        return result
    
    try:
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
                if src and 'logo' not in src.lower():
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
        for sel in ['.product', '[class*="product"]', '.item', '.card']:
            try:
                items = await page.query_selector_all(sel)
                for item in items[:10]:
                    prod = {}
                    for ns in ['h2', 'h3', '.title', '.name']:
                        try:
                            ne = await item.query_selector(ns)
                            if ne:
                                nt = await ne.text_content()
                                if nt and 3 < len(nt.strip()) < 80:
                                    prod['name'] = nt.strip()
                                    break
                        except:
                            continue
                    for ps in ['.price', '[class*="price"]']:
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
    }).limit(1000)
    
    enterprises = await cursor.to_list(1000)
    print(f'\nFound {len(enterprises)} enterprises to enrich\n')
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        stats = {'total': 0, 'covers': 0, 'logos': 0, 'products': 0}
        
        for i, ent in enumerate(enterprises):
            eid = ent.get('id')
            name = ent.get('business_name') or ent.get('name', '')
            existing_website = ent.get('website')
            
            if not name:
                continue
            
            stats['total'] += 1
            print(f'[{i+1}/{len(enterprises)}] {name[:40]}')
            
            # Use existing website or find known one
            website = existing_website
            if not website or not website.startswith('http'):
                website = find_known_website(name)
            
            if website:
                data = await scrape_website(page, website, eid)
                
                if data['cover']:
                    update = {
                        'website': website,
                        'cover_image': data['cover'],
                        'enriched_at': datetime.now(timezone.utc).isoformat(),
                        'enrichment_source': 'website_v8'
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
                            await db.services_products.insert_one({
                                'id': str(uuid.uuid4()),
                                'enterprise_id': eid,
                                'name': prod['name'],
                                'type': 'product',
                                'price': prod['price'],
                                'is_available': True,
                                'source': 'scraping_v8'
                            })
                            stats['products'] += 1
                    
                    print(f'    ✓ Cover{", Logo" if data["logo"] else ""}{", " + str(len(data["products"])) + " prods" if data["products"] else ""}')
                else:
                    print(f'    ✗ Failed')
            else:
                print(f'    ✗ No website')
            
            await asyncio.sleep(1)
        
        await browser.close()
    
    client.close()
    
    print(f'\n{"=" * 70}')
    print(f'   TERMINÉ! Covers: {stats["covers"]} | Logos: {stats["logos"]} | Products: {stats["products"]}')
    print(f'{"=" * 70}')


if __name__ == '__main__':
    asyncio.run(main())
