#!/usr/bin/env python3
"""
SCRAPER V10 - Approche hybride:
1. Sites web connus (grandes enseignes suisses)
2. Recherche Google limitée pour les autres
3. Screenshot et scraping des sites trouvés
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

# Base de données complète des sites web connus (enseignes suisses)
KNOWN_WEBSITES = {
    # Supermarchés
    'migros': 'https://www.migros.ch',
    'coop': 'https://www.coop.ch',
    'denner': 'https://www.denner.ch',
    'aldi': 'https://www.aldi-suisse.ch',
    'lidl': 'https://www.lidl.ch',
    'manor': 'https://www.manor.ch',
    'globus': 'https://www.globus.ch',
    'spar': 'https://www.spar.ch',
    'volg': 'https://www.volg.ch',
    'aligro': 'https://www.aligro.ch',
    'prodega': 'https://www.prodega.ch',
    
    # Mode
    'h&m': 'https://www2.hm.com/fr_ch',
    'zara': 'https://www.zara.com/ch/fr',
    'mango': 'https://shop.mango.com/ch/fr',
    'c&a': 'https://www.c-and-a.com/ch/fr',
    'esprit': 'https://www.esprit.ch',
    'only': 'https://www.only.com/ch/fr',
    'vero moda': 'https://www.veromoda.com/ch/fr',
    'jack & jones': 'https://www.jackjones.com/ch/fr',
    'bershka': 'https://www.bershka.com/ch/fr',
    'pull&bear': 'https://www.pullandbear.com/ch/fr',
    'stradivarius': 'https://www.stradivarius.com/ch/fr',
    'massimo dutti': 'https://www.massimodutti.com/ch/fr',
    'uniqlo': 'https://www.uniqlo.com/ch/fr',
    'primark': 'https://www.primark.com/fr-ch',
    
    # Sport
    'nike': 'https://www.nike.com/ch',
    'adidas': 'https://www.adidas.ch/fr',
    'decathlon': 'https://www.decathlon.ch',
    'ochsner sport': 'https://www.ochsnersport.ch',
    'intersport': 'https://www.intersport.ch',
    'sportxx': 'https://www.sportxx.ch',
    
    # Électronique
    'media markt': 'https://www.mediamarkt.ch',
    'fust': 'https://www.fust.ch',
    'interdiscount': 'https://www.interdiscount.ch',
    'fnac': 'https://www.fnac.ch',
    'digitec': 'https://www.digitec.ch',
    'galaxus': 'https://www.galaxus.ch',
    'microspot': 'https://www.microspot.ch',
    'apple': 'https://www.apple.com/chfr',
    'samsung': 'https://www.samsung.com/ch_fr',
    
    # Télécoms
    'swisscom': 'https://www.swisscom.ch',
    'sunrise': 'https://www.sunrise.ch',
    'salt': 'https://www.salt.ch',
    
    # Banques
    'ubs': 'https://www.ubs.com/ch/fr',
    'credit suisse': 'https://www.credit-suisse.com/ch/fr',
    'raiffeisen': 'https://www.raiffeisen.ch',
    'bcv': 'https://www.bcv.ch',
    'postfinance': 'https://www.postfinance.ch',
    
    # Restauration rapide
    'mcdonalds': 'https://www.mcdonalds.ch',
    'burger king': 'https://www.burgerking.ch',
    'starbucks': 'https://www.starbucks.ch/fr',
    'subway': 'https://www.subway.com/fr-ch',
    'pizza hut': 'https://www.pizzahut.ch',
    'dominos': 'https://www.dominos.ch',
    'kfc': 'https://www.kfc.ch',
    
    # Beauté
    'sephora': 'https://www.sephora.ch',
    'marionnaud': 'https://www.marionnaud.ch',
    'douglas': 'https://www.douglas.ch',
    'yves rocher': 'https://www.yves-rocher.ch',
    'the body shop': 'https://www.thebodyshop.com/fr-ch',
    'lush': 'https://www.lush.com/ch/fr',
    'kiko': 'https://www.kikocosmetics.com/fr-ch',
    'mac': 'https://www.maccosmetics.ch',
    'bodyminute': 'https://www.bodyminute.com',
    
    # Pharmacies
    'pharmacieplus': 'https://www.pharmacieplus.ch',
    'amavita': 'https://www.amavita.ch',
    'benu': 'https://www.benu.ch',
    'sunstore': 'https://www.sunstore.ch',
    'coop vitality': 'https://www.coopvitality.ch',
    'medbase': 'https://www.medbase.ch',
    
    # Optique
    'visilab': 'https://www.visilab.ch',
    'fielmann': 'https://www.fielmann.ch',
    'mcoptique': 'https://www.mcoptique.ch',
    'optic 2000': 'https://www.optic2000.ch',
    'pearle': 'https://www.pearle.ch',
    'grandoptical': 'https://www.grandoptical.ch',
    
    # Montres/Bijoux
    'swatch': 'https://www.swatch.com/fr-ch',
    'rolex': 'https://www.rolex.com/fr',
    'omega': 'https://www.omegawatches.com/fr-ch',
    'tissot': 'https://www.tissotwatches.com/fr-ch',
    'tag heuer': 'https://www.tagheuer.com/ch/fr',
    'pandora': 'https://ch.pandora.net/fr',
    'swarovski': 'https://www.swarovski.com/fr-CH',
    'christ': 'https://www.christ-uhren-schmuck.ch',
    
    # Luxe
    'louis vuitton': 'https://fr.louisvuitton.com/fra-ch',
    'gucci': 'https://www.gucci.com/ch/fr',
    'prada': 'https://www.prada.com/ch/fr',
    'chanel': 'https://www.chanel.com/ch/fr',
    'dior': 'https://www.dior.com/fr_ch',
    'hermès': 'https://www.hermes.com/ch/fr',
    'cartier': 'https://www.cartier.ch/fr-ch',
    'tiffany': 'https://www.tiffany.ch/fr',
    'burberry': 'https://ch.burberry.com/fr',
    
    # Meubles/Déco
    'ikea': 'https://www.ikea.com/ch/fr',
    'conforama': 'https://www.conforama.ch',
    'maisons du monde': 'https://www.maisonsdumonde.com/CH/fr',
    'pfister': 'https://www.pfister.ch',
    'interio': 'https://www.interio.ch',
    'livique': 'https://www.livique.ch',
    'micasa': 'https://www.micasa.ch',
    'jysk': 'https://jysk.ch',
    
    # Bricolage
    'hornbach': 'https://www.hornbach.ch',
    'jumbo': 'https://www.jumbo.ch',
    'obi': 'https://www.obi.ch',
    'coop brico+loisirs': 'https://www.bricoloisirs.ch',
    'landi': 'https://www.landi.ch',
    'do it + garden': 'https://www.doitgarden.ch',
    
    # Véhicules
    'garage auto': 'https://www.autoscout24.ch',
    'auto zürich': 'https://www.auto-zuerich.ch',
    'amag': 'https://www.amag.ch',
    'emil frey': 'https://www.emilfrey.ch',
    
    # Services
    'la poste': 'https://www.post.ch/fr',
    'cff': 'https://www.sbb.ch/fr',
    'sbb': 'https://www.sbb.ch',
    'tl': 'https://www.t-l.ch',
    
    # Assurances
    'axa': 'https://www.axa.ch',
    'swiss life': 'https://www.swisslife.ch',
    'mobilière': 'https://www.mobiliere.ch',
    'vaudoise': 'https://www.vaudoise.ch',
    'generali': 'https://www.generali.ch',
    'zurich': 'https://www.zurich.ch',
    'helvetia': 'https://www.helvetia.com/ch/web/fr',
    'baloise': 'https://www.baloise.ch',
    
    # Immobilier
    'homegate': 'https://www.homegate.ch',
    'immoscout24': 'https://www.immoscout24.ch',
    'comparis': 'https://www.comparis.ch',
    
    # Voyage
    'kuoni': 'https://www.kuoni.ch',
    'hotelplan': 'https://www.hotelplan.ch',
    'tui': 'https://www.tui.ch',
    'swiss': 'https://www.swiss.com',
    'easyjet': 'https://www.easyjet.com/fr',
    
    # Restaurants/Cafés
    'starbucks': 'https://www.starbucks.ch',
    'holy cow': 'https://www.holycow.ch',
    
    # Fitness
    'fitness park': 'https://www.fitnesspark.ch',
    'update fitness': 'https://www.update-fitness.ch',
    'basefit': 'https://www.basefit.ch',
    
    # Kiosques
    'k kiosk': 'https://www.kkiosk.ch',
    'avec': 'https://www.avec.ch',
    'press & books': 'https://www.pressandbooks.ch',
    
    # Alimentation spécialisée
    'bio partner': 'https://www.biopartner.ch',
    'reformhaus': 'https://www.reformhaus.ch',
    
    # Office
    'office world': 'https://www.officeworld.ch',
    'orell füssli': 'https://www.orellfuessli.ch',
    'payot': 'https://www.payot.ch',
    'ex libris': 'https://www.exlibris.ch',
}

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
]

print("=" * 70)
print("   SCRAPER V10 - SITES CONNUS + SCREENSHOTS RÉELS")
print("=" * 70)


def find_known_website(name):
    """Trouve le site web dans notre base de données"""
    name_lower = name.lower().strip()
    name_clean = re.sub(r'[^a-zàâäéèêëïîôùûüç\s&]', '', name_lower)
    
    # Correspondance exacte
    for brand, url in KNOWN_WEBSITES.items():
        if brand == name_clean:
            return url
    
    # Correspondance partielle
    for brand, url in KNOWN_WEBSITES.items():
        if brand in name_clean or name_clean in brand:
            return url
        # Vérifier chaque mot
        for word in name_clean.split():
            if len(word) > 3 and word in brand:
                return url
    
    return None


async def download_image(url, filepath, min_size=1000):
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            r = await client.get(url, headers={'User-Agent': random.choice(USER_AGENTS)})
            if r.status_code == 200 and len(r.content) > min_size:
                with open(filepath, 'wb') as f:
                    f.write(r.content)
                return True
    except:
        pass
    return False


async def scrape_website(page, website, eid):
    """Screenshot et scraping du site web"""
    result = {
        'cover': None,
        'logo': None,
        'description': None,
        'photos': []
    }
    
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
            result['photos'].append(result['cover'])
        
        # Logo
        for sel in ['img[alt*="logo" i]', 'img[src*="logo" i]', '.logo img', 'header img']:
            try:
                el = await page.query_selector(sel)
                if el:
                    src = await el.get_attribute('src')
                    if src:
                        if not src.startswith('http'):
                            src = urljoin(website, src)
                        logo_file = f'{eid}_logo.png'
                        if await download_image(src, f'{UPLOADS_DIR}/{logo_file}', 200):
                            result['logo'] = f'/api/uploads/enterprises/{logo_file}'
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
                
    except PlaywrightTimeout:
        pass
    except Exception as e:
        pass
    
    return result


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Toutes les entreprises sans enrichment
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
        {'_id': 0, 'id': 1, 'name': 1, 'business_name': 1, 'website': 1}
    ).to_list(10000)
    
    total = len(enterprises)
    print(f'\n[INFO] {total} entreprises à traiter\n')
    
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
        
        stats = {'processed': 0, 'success': 0, 'failed': 0}
        
        for i, ent in enumerate(enterprises):
            eid = ent.get('id')
            name = ent.get('business_name') or ent.get('name', '')
            
            if not name:
                continue
            
            stats['processed'] += 1
            print(f'[{i+1}/{total}] {name[:45]}', end=' ')
            
            # Chercher le site web
            website = ent.get('website')
            if not website or not website.startswith('http'):
                website = find_known_website(name)
            
            if website:
                print(f'-> {website[:40]}', end=' ')
                data = await scrape_website(page, website, eid)
                
                if data['cover']:
                    update = {
                        'website': website,
                        'cover_image': data['cover'],
                        'enriched_at': datetime.now(timezone.utc).isoformat(),
                        'enrichment_source': 'known_sites_v10'
                    }
                    if data['logo']:
                        update['logo'] = data['logo']
                    if data['description']:
                        update['description'] = data['description']
                    if data['photos']:
                        update['photos'] = data['photos']
                    
                    await db.enterprises.update_one({'id': eid}, {'$set': update})
                    stats['success'] += 1
                    print('OK')
                else:
                    stats['failed'] += 1
                    print('FAIL')
            else:
                stats['failed'] += 1
                print('-> No site found')
            
            # Pause
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Stats intermédiaires
            if stats['processed'] % 100 == 0:
                print(f'\n--- {stats["success"]} success / {stats["failed"]} failed ---\n')
        
        await browser.close()
    
    client.close()
    
    print(f'\n{"=" * 70}')
    print(f'   TERMINÉ!')
    print(f'   Success: {stats["success"]} / {stats["processed"]}')
    print(f'   Failed: {stats["failed"]}')
    print(f'{"=" * 70}')


if __name__ == '__main__':
    asyncio.run(main())
