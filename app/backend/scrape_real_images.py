#!/usr/bin/env python3
"""
SCRAPER IMAGES RÉELLES - Capture d'écran des vrais sites web des entreprises
"""
import asyncio
import os
import logging
import re
from datetime import datetime, timezone
from urllib.parse import urljoin
from motor.motor_asyncio import AsyncIOMotorClient
from playwright.async_api import async_playwright
import httpx
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'secondevie')
UPLOADS_DIR = "/app/backend/uploads/enterprises"
BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://image-fix-demo.preview.emergentagent.com")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)
os.makedirs(UPLOADS_DIR, exist_ok=True)


async def download_image(url: str, filepath: str, min_size: int = 2000) -> bool:
    """Download image from URL"""
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200:
                content_type = resp.headers.get('content-type', '')
                if 'image' in content_type or len(resp.content) > min_size:
                    with open(filepath, 'wb') as f:
                        f.write(resp.content)
                    return True
    except Exception as e:
        logger.debug(f"Download error: {e}")
    return False


async def scrape_website(page, enterprise: dict) -> dict:
    """Visit website and capture real screenshot + logo"""
    eid = enterprise.get('id')
    website = enterprise.get('website')
    name = enterprise.get('business_name') or enterprise.get('name', 'Unknown')
    
    result = {
        "cover_image": None,
        "logo": None,
        "photos": [],
        "description": None
    }
    
    if not website:
        return result
    
    # Ensure website has protocol
    if not website.startswith('http'):
        website = 'https://' + website
    
    try:
        logger.info(f"   Visiting: {website}")
        await page.goto(website, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)
        
        # 1. SCREENSHOT DE LA PAGE (COVER IMAGE)
        cover_file = f"{eid}_cover.jpg"
        cover_path = f"{UPLOADS_DIR}/{cover_file}"
        await page.screenshot(path=cover_path, quality=85, type="jpeg")
        result["cover_image"] = f"{BASE_URL}/api/uploads/enterprises/{cover_file}"
        result["photos"].append(result["cover_image"])
        logger.info(f"   ✓ Cover screenshot saved")
        
        # 2. LOGO - Chercher et extraire
        logo_selectors = [
            'img[alt*="logo" i]',
            'img[src*="logo" i]', 
            'img[class*="logo" i]',
            'header img:first-of-type',
            'nav img:first-of-type',
            '.logo img',
            '#logo img',
            'a[href="/"] img',
        ]
        
        for sel in logo_selectors:
            try:
                logo_el = await page.query_selector(sel)
                if logo_el:
                    box = await logo_el.bounding_box()
                    if box and box['width'] > 30 and box['height'] > 30:
                        # Get logo URL and download
                        logo_src = await logo_el.get_attribute('src')
                        if logo_src:
                            if not logo_src.startswith('http'):
                                logo_src = urljoin(website, logo_src)
                            
                            logo_file = f"{eid}_logo.png"
                            logo_path = f"{UPLOADS_DIR}/{logo_file}"
                            
                            if await download_image(logo_src, logo_path, 500):
                                result["logo"] = f"{BASE_URL}/api/uploads/enterprises/{logo_file}"
                                logger.info(f"   ✓ Logo downloaded from {logo_src[:50]}...")
                                break
                        
                        # Fallback: screenshot the logo element
                        if not result["logo"]:
                            logo_file = f"{eid}_logo.png"
                            logo_path = f"{UPLOADS_DIR}/{logo_file}"
                            await logo_el.screenshot(path=logo_path)
                            if os.path.getsize(logo_path) > 500:
                                result["logo"] = f"{BASE_URL}/api/uploads/enterprises/{logo_file}"
                                logger.info(f"   ✓ Logo captured via screenshot")
                                break
            except Exception as e:
                continue
        
        # 3. DESCRIPTION
        desc_selectors = [
            'meta[name="description"]',
            'meta[property="og:description"]',
        ]
        
        for sel in desc_selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    content = await el.get_attribute('content')
                    if content and len(content.strip()) > 30:
                        result["description"] = content.strip()[:500]
                        break
            except:
                continue
        
        # 4. EXTRA IMAGES from the page
        try:
            all_imgs = await page.query_selector_all('img')
            img_count = 0
            
            for img in all_imgs:
                if img_count >= 5:
                    break
                try:
                    src = await img.get_attribute('src')
                    if not src:
                        continue
                    
                    # Skip icons/logos/small images
                    if any(x in src.lower() for x in ['icon', 'logo', 'pixel', '1x1', 'spacer', 'avatar']):
                        continue
                    
                    box = await img.bounding_box()
                    if box and box['width'] > 150 and box['height'] > 100:
                        if not src.startswith('http'):
                            src = urljoin(website, src)
                        
                        img_file = f"{eid}_img_{img_count}.jpg"
                        img_path = f"{UPLOADS_DIR}/{img_file}"
                        
                        if await download_image(src, img_path, 5000):
                            result["photos"].append(f"{BASE_URL}/api/uploads/enterprises/{img_file}")
                            img_count += 1
                except:
                    continue
        except Exception as e:
            logger.debug(f"Error getting extra images: {e}")
        
        logger.info(f"   ✓ Total: {len(result['photos'])} images")
        
    except Exception as e:
        logger.warning(f"   ✗ Error: {str(e)[:100]}")
    
    return result


async def main():
    logger.info("=" * 60)
    logger.info("   SCRAPER IMAGES RÉELLES")
    logger.info("=" * 60)
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Get enterprises WITH websites that need images
    query = {
        "website": {"$exists": True, "$ne": None, "$ne": ""},
        "$or": [
            {"cover_image": None},
            {"cover_image": ""},
            {"cover_image": {"$regex": "enterprise-media.preview"}},
        ]
    }
    
    enterprises = await db.enterprises.find(query).limit(400).to_list(400)
    logger.info(f"Found {len(enterprises)} enterprises with websites to scrape\n")
    
    if not enterprises:
        logger.info("No enterprises to process!")
        return
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        stats = {"success": 0, "failed": 0, "images": 0, "logos": 0}
        
        for i, ent in enumerate(enterprises):
            name = ent.get('business_name') or ent.get('name', 'Unknown')
            eid = ent.get('id')
            
            logger.info(f"[{i+1}/{len(enterprises)}] {name}")
            
            try:
                data = await scrape_website(page, ent)
                
                # Update database
                update = {
                    "enriched_at": datetime.now(timezone.utc).isoformat(),
                    "enrichment_source": "real_website"
                }
                
                if data["cover_image"]:
                    update["cover_image"] = data["cover_image"]
                    stats["images"] += 1
                
                if data["logo"]:
                    update["logo"] = data["logo"]
                    stats["logos"] += 1
                
                if data["photos"]:
                    update["photos"] = data["photos"]
                    update["gallery"] = data["photos"]
                    stats["images"] += len(data["photos"]) - 1
                
                if data["description"]:
                    update["description"] = data["description"]
                
                await db.enterprises.update_one({"id": eid}, {"$set": update})
                stats["success"] += 1
                
            except Exception as e:
                logger.error(f"   Error: {e}")
                stats["failed"] += 1
            
            # Delay between requests
            await asyncio.sleep(2)
        
        await browser.close()
    
    client.close()
    
    logger.info("\n" + "=" * 60)
    logger.info(f"   DONE!")
    logger.info(f"   Success: {stats['success']}, Failed: {stats['failed']}")
    logger.info(f"   Images: {stats['images']}, Logos: {stats['logos']}")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
