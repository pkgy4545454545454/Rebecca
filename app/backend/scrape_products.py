#!/usr/bin/env python3
"""
SCRAPER PRODUITS V1 - Scrape les produits/services des 599 entreprises enrichies
"""
import asyncio
import os
import re
import uuid
import random
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from urllib.parse import urljoin
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'secondevie')

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
]

# Sites à ignorer (pas de produits)
SKIP_DOMAINS = ['duckduckgo.com', 'google.com', 'start.duckduckgo']

print("=" * 70)
print("   SCRAPER PRODUITS - DONNÉES RÉELLES")
print("=" * 70)


def parse_price(text):
    """Parse le prix en CHF"""
    if not text:
        return 0
    # Enlever les devises
    text = re.sub(r'(CHF|Fr\.|€|\$|SFr\.|sfr)', '', text, flags=re.I)
    text = text.replace("'", "").replace(" ", "").replace(".-", "").replace("–", "-")
    # Trouver le premier nombre
    match = re.search(r'(\d+[\.,]?\d*)', text)
    if match:
        price_str = match.group(1).replace(',', '.')
        try:
            return float(price_str)
        except:
            return 0
    return 0


async def scrape_products(page, website, enterprise_id):
    """Scrape les produits/services d'un site web"""
    products = []
    
    if not website or any(skip in website.lower() for skip in SKIP_DOMAINS):
        return products
    
    try:
        await page.goto(website, wait_until='domcontentloaded', timeout=25000)
        await page.wait_for_timeout(2000)
        
        # Essayer plusieurs sélecteurs de produits
        product_selectors = [
            # E-commerce classique
            '.product', '.product-item', '.product-card',
            '[class*="product"]', '[data-product]',
            # Services
            '.service', '.service-item', '.service-card',
            '[class*="service"]', '[class*="prestation"]',
            # Cards génériques
            '.card', '.item', '.offer', '.tarif',
            # WooCommerce
            '.woocommerce-loop-product__link',
            # Shopify
            '.product-grid-item', '.product-list__item',
            # Autres
            '[class*="price"]', '[class*="tarif"]', '[class*="menu-item"]'
        ]
        
        found_products = []
        
        for selector in product_selectors:
            try:
                items = await page.query_selector_all(selector)
                if items and len(items) > 0:
                    for item in items[:20]:  # Max 20 produits
                        product = await extract_product_info(item, page)
                        if product and product.get('name') and len(product['name']) > 2:
                            # Éviter les doublons
                            if not any(p['name'].lower() == product['name'].lower() for p in found_products):
                                found_products.append(product)
                    
                    if len(found_products) >= 5:
                        break
            except Exception as e:
                continue
        
        # Si pas de produits trouvés, essayer de scraper la page menu/tarifs
        if len(found_products) < 3:
            menu_links = await page.query_selector_all('a[href*="menu"], a[href*="tarif"], a[href*="price"], a[href*="service"], a[href*="produit"], a[href*="shop"]')
            for link in menu_links[:3]:
                try:
                    href = await link.get_attribute('href')
                    if href:
                        if not href.startswith('http'):
                            href = urljoin(website, href)
                        
                        await page.goto(href, wait_until='domcontentloaded', timeout=15000)
                        await page.wait_for_timeout(1500)
                        
                        # Rescraper sur cette page
                        for selector in product_selectors[:5]:
                            items = await page.query_selector_all(selector)
                            for item in items[:15]:
                                product = await extract_product_info(item, page)
                                if product and product.get('name') and len(product['name']) > 2:
                                    if not any(p['name'].lower() == product['name'].lower() for p in found_products):
                                        found_products.append(product)
                            
                            if len(found_products) >= 8:
                                break
                        
                        if len(found_products) >= 5:
                            break
                except:
                    continue
        
        products = found_products[:15]  # Max 15 produits par entreprise
        
    except PlaywrightTimeout:
        pass
    except Exception as e:
        pass
    
    return products


async def extract_product_info(item, page):
    """Extrait les infos d'un élément produit"""
    product = {}
    
    try:
        # Nom du produit
        name_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '.name', '.product-name', '.product-title', 'a']
        for sel in name_selectors:
            try:
                el = await item.query_selector(sel)
                if el:
                    text = await el.text_content()
                    if text:
                        text = text.strip()
                        # Vérifier que c'est un nom valide
                        if 3 < len(text) < 100 and not text.startswith('http'):
                            product['name'] = text
                            break
            except:
                continue
        
        # Prix
        price_selectors = ['.price', '[class*="price"]', '.amount', '.cost', '.tarif', '[class*="tarif"]']
        for sel in price_selectors:
            try:
                el = await item.query_selector(sel)
                if el:
                    text = await el.text_content()
                    price = parse_price(text)
                    if price > 0:
                        product['price'] = price
                        break
            except:
                continue
        
        # Description (optionnel)
        desc_selectors = ['.description', '.desc', 'p', '.excerpt']
        for sel in desc_selectors:
            try:
                el = await item.query_selector(sel)
                if el:
                    text = await el.text_content()
                    if text and len(text.strip()) > 10:
                        product['description'] = text.strip()[:300]
                        break
            except:
                continue
        
        # Image (optionnel)
        try:
            img = await item.query_selector('img')
            if img:
                src = await img.get_attribute('src')
                if src and src.startswith('http'):
                    product['image'] = src
        except:
            pass
            
    except Exception as e:
        pass
    
    return product


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Entreprises enrichies avec cover mais sans produits
    enriched = await db.enterprises.find(
        {'cover_image': {'$regex': '/api/uploads', '$options': 'i'}},
        {'_id': 0, 'id': 1, 'name': 1, 'business_name': 1, 'website': 1, 'category': 1}
    ).to_list(1000)
    
    # Filtrer celles sans produits et avec un vrai site web
    to_process = []
    for ent in enriched:
        eid = ent.get('id')
        website = ent.get('website', '')
        
        # Skip si pas de site web valide
        if not website or any(skip in website.lower() for skip in SKIP_DOMAINS):
            continue
        
        # Vérifier si déjà des produits
        count = await db.services_products.count_documents({'enterprise_id': eid})
        if count == 0:
            to_process.append(ent)
    
    total = len(to_process)
    print(f'\n[INFO] {total} entreprises à scraper pour les produits\n')
    
    if total == 0:
        print("Aucune entreprise à traiter!")
        return
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=random.choice(USER_AGENTS)
        )
        page = await context.new_page()
        
        stats = {'processed': 0, 'with_products': 0, 'total_products': 0}
        
        for i, ent in enumerate(to_process):
            eid = ent.get('id')
            name = ent.get('business_name') or ent.get('name', '')
            website = ent.get('website')
            category = ent.get('category', 'general')
            
            stats['processed'] += 1
            print(f'[{i+1}/{total}] {name[:40]}', end=' ')
            print(f'({website[:30]}...)', end=' ')
            
            products = await scrape_products(page, website, eid)
            
            if products:
                # Sauvegarder les produits
                for prod in products:
                    if prod.get('name'):
                        doc = {
                            'id': str(uuid.uuid4()),
                            'enterprise_id': eid,
                            'name': prod['name'],
                            'description': prod.get('description', ''),
                            'price': prod.get('price', 0),
                            'currency': 'CHF',
                            'type': 'product' if prod.get('price', 0) > 0 else 'service',
                            'category': category,
                            'images': [prod['image']] if prod.get('image') else [],
                            'is_available': True,
                            'created_at': datetime.now(timezone.utc).isoformat(),
                            'source': 'website_scraping'
                        }
                        await db.services_products.insert_one(doc)
                        stats['total_products'] += 1
                
                stats['with_products'] += 1
                print(f'-> {len(products)} produits')
            else:
                print('-> 0 produits')
            
            await asyncio.sleep(random.uniform(1.0, 2.0))
            
            if stats['processed'] % 50 == 0:
                print(f'\n--- {stats["with_products"]} entreprises avec produits, {stats["total_products"]} produits total ---\n')
        
        await browser.close()
    
    client.close()
    
    print(f'\n{"=" * 70}')
    print(f'   TERMINÉ!')
    print(f'   Entreprises traitées: {stats["processed"]}')
    print(f'   Avec produits trouvés: {stats["with_products"]}')
    print(f'   Total produits ajoutés: {stats["total_products"]}')
    print(f'{"=" * 70}')


if __name__ == '__main__':
    asyncio.run(main())
