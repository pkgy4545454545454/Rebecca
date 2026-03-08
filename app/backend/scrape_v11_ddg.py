#!/usr/bin/env python3
"""
SCRAPER V11 - DuckDuckGo Search + Screenshots
Recherche les sites via DuckDuckGo (moins restrictif que Google)
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

# Sites à éviter (réseaux sociaux, annuaires, etc.)
BLOCKED_DOMAINS = [
    'facebook.com', 'instagram.com', 'twitter.com', 'linkedin.com',
    'youtube.com', 'tiktok.com', 'pinterest.com',
    'local.ch', 'search.ch', 'pagesjaunes.ch', 'yelp.com',
    'tripadvisor.com', 'google.com', 'wikipedia.org',
    'kompass.com', 'moneyhouse.ch', 'zefix.ch',
]

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

print("=" * 70)
print("   SCRAPER V11 - DUCKDUCKGO + SCREENSHOTS")
print("=" * 70)


def is_valid_website(url):
    """Vérifie si l'URL est un vrai site d'entreprise"""
    if not url:
        return False
    for blocked in BLOCKED_DOMAINS:
        if blocked in url.lower():
            return False
    return True


async def search_duckduckgo(page, name, city="Lausanne"):
    """Recherche sur DuckDuckGo"""
    website = None
    
    try:
        search_query = f'{name} {city} site officiel'
        search_url = f'https://duckduckgo.com/?q={quote_plus(search_query)}'
        
        await page.goto(search_url, wait_until='domcontentloaded', timeout=15000)
        await page.wait_for_timeout(random.randint(2000, 4000))
        
        # Chercher les résultats
        results = await page.query_selector_all('article[data-testid="result"]')
        
        for result in results[:5]:
            try:
                link = await result.query_selector('a[data-testid="result-extras-url-link"]')
                if not link:
                    link = await result.query_selector('a[href]')
                
                if link:
                    href = await link.get_attribute('href')
                    if href and is_valid_website(href):
                        website = href
                        break
            except:
                continue
        
        # Alternative: chercher directement les liens
        if not website:
            all_links = await page.query_selector_all('a[href^="http"]')
            for link in all_links[:20]:
                try:
                    href = await link.get_attribute('href')
                    if href and is_valid_website(href) and 'duckduckgo' not in href:
                        website = href
                        break
                except:
                    continue
                    
    except PlaywrightTimeout:
        pass
    except Exception as e:
        pass
    
    return website


async def scrape_website(page, website, eid):
    """Screenshot du site"""
    result = {'cover': None, 'logo': None, 'description': None}
    
    if not website:
        return result
    
    try:
        await page.goto(website, wait_until='domcontentloaded', timeout=20000)
        await page.wait_for_timeout(2000)
        
        # Screenshot
        cover_file = f'{eid}_cover.jpg'
        cover_path = f'{UPLOADS_DIR}/{cover_file}'
        await page.screenshot(path=cover_path, quality=80, type='jpeg', full_page=False)
        
        if os.path.exists(cover_path) and os.path.getsize(cover_path) > 5000:
            result['cover'] = f'/api/uploads/enterprises/{cover_file}'
        
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
                
    except:
        pass
    
    return result


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Entreprises sans enrichment
    query = {
        '$or': [
            {'cover_image': None},
            {'cover_image': ''},
            {'cover_image': {'$exists': False}},
            {'enriched_at': {'$exists': False}}
        ]
    }
    
    enterprises = await db.enterprises.find(
        query,
        {'_id': 0, 'id': 1, 'name': 1, 'business_name': 1, 'city': 1}
    ).to_list(5000)
    
    total = len(enterprises)
    print(f'\n[INFO] {total} entreprises à traiter\n')
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=random.choice(USER_AGENTS)
        )
        page = await context.new_page()
        
        stats = {'processed': 0, 'success': 0, 'failed': 0}
        
        for i, ent in enumerate(enterprises):
            eid = ent.get('id')
            name = ent.get('business_name') or ent.get('name', '')
            city = ent.get('city', 'Lausanne')
            
            if not name:
                continue
            
            stats['processed'] += 1
            print(f'[{i+1}/{total}] {name[:40]}', end=' ')
            
            # Recherche DuckDuckGo
            website = await search_duckduckgo(page, name, city)
            
            if website:
                print(f'-> {website[:35]}', end=' ')
                data = await scrape_website(page, website, eid)
                
                if data['cover']:
                    update = {
                        'website': website,
                        'cover_image': data['cover'],
                        'enriched_at': datetime.now(timezone.utc).isoformat(),
                        'enrichment_source': 'duckduckgo_v11'
                    }
                    if data['description']:
                        update['description'] = data['description']
                    
                    await db.enterprises.update_one({'id': eid}, {'$set': update})
                    stats['success'] += 1
                    print('OK')
                else:
                    stats['failed'] += 1
                    print('FAIL')
            else:
                stats['failed'] += 1
                print('-> No result')
            
            # Pause aléatoire pour éviter le blocage
            await asyncio.sleep(random.uniform(3.0, 6.0))
            
            if stats['processed'] % 50 == 0:
                print(f'\n--- {stats["success"]} success / {stats["failed"]} failed ---\n')
        
        await browser.close()
    
    client.close()
    
    print(f'\n{"=" * 70}')
    print(f'   Success: {stats["success"]} / {stats["processed"]}')
    print(f'{"=" * 70}')


if __name__ == '__main__':
    asyncio.run(main())
