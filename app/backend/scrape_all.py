#!/usr/bin/env python3
"""
SCRAPER COMPLET - Screenshots réels des sites web
"""
import asyncio
import os
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

async def scrape_site(page, eid, website):
    """Visit real website and capture screenshot + logo"""
    result = {'cover': None, 'logo': None}
    
    if not website.startswith('http'):
        website = 'https://' + website
    
    try:
        await page.goto(website, wait_until='networkidle', timeout=25000)
        await page.wait_for_timeout(1500)
        
        # Screenshot homepage
        cover_file = f'{eid}_cover.jpg'
        await page.screenshot(path=f'{UPLOADS_DIR}/{cover_file}', quality=85, type='jpeg')
        result['cover'] = f'{BASE_URL}/api/uploads/enterprises/{cover_file}'
        
        # Find and download logo
        for sel in ['img[alt*="logo" i]', 'img[src*="logo" i]', 'header img:first-child', '.logo img', 'nav img']:
            try:
                el = await page.query_selector(sel)
                if el:
                    box = await el.bounding_box()
                    if box and box['width'] > 25 and box['height'] > 25:
                        src = await el.get_attribute('src')
                        if src:
                            if not src.startswith('http'):
                                src = urljoin(website, src)
                            
                            logo_file = f'{eid}_logo.png'
                            async with httpx.AsyncClient(timeout=10) as client:
                                r = await client.get(src, headers={'User-Agent': 'Mozilla/5.0'})
                                if r.status_code == 200 and len(r.content) > 500:
                                    with open(f'{UPLOADS_DIR}/{logo_file}', 'wb') as f:
                                        f.write(r.content)
                                    result['logo'] = f'{BASE_URL}/api/uploads/enterprises/{logo_file}'
                                    break
            except:
                continue
                
    except Exception as e:
        print(f'    Error: {str(e)[:60]}')
    
    return result

async def main():
    print('=' * 60)
    print('   SCRAPER IMAGES RÉELLES - Sites Web')
    print('=' * 60)
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # All enterprises with websites
    cursor = db.enterprises.find({
        'website': {'$regex': '^https?://'}
    }).limit(500)
    
    enterprises = await cursor.to_list(500)
    print(f'Found {len(enterprises)} enterprises with websites\n')
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        success = 0
        logos = 0
        
        for i, e in enumerate(enterprises):
            eid = e.get('id')
            name = e.get('business_name', e.get('name', 'Unknown'))
            website = e.get('website')
            
            print(f'[{i+1}/{len(enterprises)}] {name[:40]}')
            
            data = await scrape_site(page, eid, website)
            
            if data['cover']:
                update = {'cover_image': data['cover']}
                if data['logo']:
                    update['logo'] = data['logo']
                    logos += 1
                    print(f'    ✓ Cover + Logo')
                else:
                    print(f'    ✓ Cover only')
                
                await db.enterprises.update_one({'id': eid}, {'$set': update})
                success += 1
            
            await asyncio.sleep(1.5)
        
        await browser.close()
    
    client.close()
    
    print('\n' + '=' * 60)
    print(f'   DONE: {success} covers, {logos} logos')
    print('=' * 60)

if __name__ == '__main__':
    asyncio.run(main())
