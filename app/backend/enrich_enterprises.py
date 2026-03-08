#!/usr/bin/env python3
"""
Script d'enrichissement des profils entreprises
- Visite les sites web des entreprises
- Capture des screenshots
- Extrait les logos et images de couverture
- Met à jour les profils dans MongoDB
"""

import asyncio
import os
import sys
import logging
import uuid
import shutil
from datetime import datetime, timezone
from urllib.parse import urlparse
from motor.motor_asyncio import AsyncIOMotorClient
from playwright.async_api import async_playwright

# Configuration
MONGO_URL = "mongodb+srv://prankgy:Minijetaime1996@cluster0.kwjifsg.mongodb.net/secondevie?retryWrites=true&w=majority&appName=Cluster0"
UPLOADS_DIR = "/app/backend/uploads/enterprises"
BASE_URL = "https://image-fix-demo.preview.emergentagent.com"
MAX_ENTERPRISES = 500  # Enrichir TOUTES les entreprises avec site web valide

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Créer le dossier uploads si nécessaire
os.makedirs(UPLOADS_DIR, exist_ok=True)


async def capture_website_screenshot(page, url: str, enterprise_id: str) -> dict:
    """Capture screenshot d'un site web et extrait les images"""
    result = {
        "cover_image": None,
        "logo": None,
        "screenshots": [],
        "description": None,
        "error": None
    }
    
    try:
        # Naviguer vers le site
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(2000)
        
        # Screenshot de la page principale (sera utilisé comme cover)
        cover_filename = f"{enterprise_id}_cover.jpg"
        cover_path = f"{UPLOADS_DIR}/{cover_filename}"
        await page.screenshot(path=cover_path, quality=80, full_page=False)
        result["cover_image"] = f"{BASE_URL}/api/uploads/enterprises/{cover_filename}"
        result["screenshots"].append(cover_filename)
        
        # Essayer de trouver le logo
        logo_selectors = [
            'img[alt*="logo" i]',
            'img[src*="logo" i]',
            'img[class*="logo" i]',
            'header img:first-child',
            'nav img:first-child',
            '.logo img',
            '#logo img'
        ]
        
        for selector in logo_selectors:
            try:
                logo_elem = await page.query_selector(selector)
                if logo_elem:
                    logo_src = await logo_elem.get_attribute('src')
                    if logo_src and logo_src.startswith('http'):
                        result["logo"] = logo_src
                        break
            except:
                continue
        
        # Si pas de logo trouvé, utiliser une partie du screenshot
        if not result["logo"]:
            result["logo"] = result["cover_image"]
        
        # Essayer d'extraire une description
        desc_selectors = [
            'meta[name="description"]',
            'meta[property="og:description"]',
            '.about p',
            '#about p',
            'main p:first-child'
        ]
        
        for selector in desc_selectors:
            try:
                if selector.startswith('meta'):
                    elem = await page.query_selector(selector)
                    if elem:
                        content = await elem.get_attribute('content')
                        if content and len(content) > 20:
                            result["description"] = content[:500]
                            break
                else:
                    elem = await page.query_selector(selector)
                    if elem:
                        text = await elem.text_content()
                        if text and len(text.strip()) > 20:
                            result["description"] = text.strip()[:500]
                            break
            except:
                continue
                
    except Exception as e:
        result["error"] = str(e)[:200]
        logger.warning(f"Erreur capture {url}: {e}")
    
    return result


async def update_enterprise_profile(db, enterprise_id: str, data: dict):
    """Met à jour le profil entreprise dans MongoDB"""
    update_fields = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if data.get("cover_image"):
        update_fields["cover_image"] = data["cover_image"]
    
    if data.get("logo"):
        update_fields["logo"] = data["logo"]
    
    if data.get("description") and len(data["description"]) > 50:
        update_fields["description"] = data["description"]
    
    if data.get("screenshots"):
        update_fields["photos"] = [f"{BASE_URL}/api/uploads/enterprises/{s}" for s in data["screenshots"]]
    
    await db.enterprises.update_one(
        {"id": enterprise_id},
        {"$set": update_fields}
    )


async def main():
    logger.info("=" * 60)
    logger.info("ENRICHISSEMENT DES PROFILS ENTREPRISES")
    logger.info("=" * 60)
    
    # Connexion MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.secondevie
    
    # Récupérer les entreprises avec site web qui n'ont PAS encore été enrichies
    # (pas de cover_image ou logo_url vide)
    cursor = db.enterprises.find(
        {
            "website": {"$ne": None, "$ne": "", "$regex": "^http"},
            "$or": [
                {"cover_image": {"$exists": False}},
                {"cover_image": None},
                {"cover_image": ""},
                {"logo_url": {"$exists": False}},
                {"logo_url": None},
                {"logo_url": ""}
            ]
        },
        {"_id": 0, "id": 1, "business_name": 1, "name": 1, "website": 1, "category": 1}
    ).limit(MAX_ENTERPRISES)
    
    enterprises = await cursor.to_list(MAX_ENTERPRISES)
    logger.info(f"Entreprises à traiter (non enrichies): {len(enterprises)}")
    
    # Lancer Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        success_count = 0
        error_count = 0
        
        for i, ent in enumerate(enterprises, 1):
            name = ent.get('business_name') or ent.get('name', 'N/A')
            website = ent.get('website', '')
            ent_id = ent.get('id')
            
            logger.info(f"\n[{i}/{len(enterprises)}] {name}")
            logger.info(f"  URL: {website}")
            
            if not website or not ent_id:
                logger.warning("  ⏭️ Pas de site web ou ID")
                continue
            
            # Capturer le site
            data = await capture_website_screenshot(page, website, ent_id)
            
            if data.get("error"):
                logger.warning(f"  ❌ Erreur: {data['error'][:50]}")
                error_count += 1
            else:
                # Mettre à jour le profil
                await update_enterprise_profile(db, ent_id, data)
                logger.info(f"  ✅ Profil mis à jour")
                logger.info(f"     Cover: {data.get('cover_image', 'N/A')[:60]}")
                logger.info(f"     Logo: {data.get('logo', 'N/A')[:60]}")
                success_count += 1
            
            # Pause pour ne pas surcharger
            await asyncio.sleep(1)
        
        await browser.close()
    
    client.close()
    
    # Résumé
    logger.info("\n" + "=" * 60)
    logger.info("RÉSUMÉ")
    logger.info("=" * 60)
    logger.info(f"✅ Succès: {success_count}")
    logger.info(f"❌ Erreurs: {error_count}")
    logger.info(f"📁 Images sauvées dans: {UPLOADS_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
