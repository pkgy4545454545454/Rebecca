#!/usr/bin/env python3
"""
SCRAPER V13 - Entreprises restantes avec base étendue + recherche Google simple
"""
import asyncio
import os
import re
import uuid
import random
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from urllib.parse import urljoin, quote_plus
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'secondevie')
UPLOADS_DIR = '/app/backend/uploads/enterprises'

os.makedirs(UPLOADS_DIR, exist_ok=True)

# Base de données MASSIVE de sites web
KNOWN_WEBSITES = {
    # Supermarchés
    'migros': 'https://www.migros.ch', 'coop': 'https://www.coop.ch',
    'denner': 'https://www.denner.ch', 'aldi': 'https://www.aldi-suisse.ch',
    'lidl': 'https://www.lidl.ch', 'manor': 'https://www.manor.ch',
    'spar': 'https://www.spar.ch', 'volg': 'https://www.volg.ch',
    
    # Mode
    'h&m': 'https://www2.hm.com/fr_ch', 'zara': 'https://www.zara.com/ch/fr',
    'mango': 'https://shop.mango.com/ch/fr', 'c&a': 'https://www.c-and-a.com/ch/fr',
    'esprit': 'https://www.esprit.ch', 'bershka': 'https://www.bershka.com/ch/fr',
    'pull&bear': 'https://www.pullandbear.com/ch/fr',
    'stradivarius': 'https://www.stradivarius.com/ch/fr',
    'massimo dutti': 'https://www.massimodutti.com/ch/fr',
    'uniqlo': 'https://www.uniqlo.com/ch/fr', 'primark': 'https://www.primark.com/fr-ch',
    'guess': 'https://www.guess.eu/fr-ch', 'tommy hilfiger': 'https://ch.tommy.com/fr',
    'calvin klein': 'https://www.calvinklein.ch/fr', 'lacoste': 'https://www.lacoste.com/ch/fr',
    'hugo boss': 'https://www.hugoboss.com/ch/fr', 'gant': 'https://www.gant.ch',
    'superdry': 'https://www.superdry.ch', 'beldona': 'https://www.beldona.com',
    'calida': 'https://www.calida.com', 'wolford': 'https://www.wolford.com',
    'diesel': 'https://ch.diesel.com/fr', 'replay': 'https://www.replayjeans.com',
    
    # Chaussures
    'foot locker': 'https://www.footlocker.ch', 'snipes': 'https://www.snipes.ch',
    'dosenbach': 'https://www.dosenbach.ch', 'ochsner shoes': 'https://www.ochsner-shoes.ch',
    'bata': 'https://www.bata.ch', 'deichmann': 'https://www.deichmann.com/CH/fr/shop',
    'geox': 'https://www.geox.com', 'ecco': 'https://ch.ecco.com',
    'clarks': 'https://www.clarks.ch', 'birkenstock': 'https://www.birkenstock.com/ch-fr',
    
    # Sport
    'nike': 'https://www.nike.com/ch', 'adidas': 'https://www.adidas.ch/fr',
    'puma': 'https://eu.puma.com/ch/fr', 'asics': 'https://www.asics.com/ch/fr-ch',
    'new balance': 'https://www.newbalance.ch', 'decathlon': 'https://www.decathlon.ch',
    'ochsner sport': 'https://www.ochsnersport.ch', 'intersport': 'https://www.intersport.ch',
    'sportxx': 'https://www.sportxx.ch',
    
    # Électronique
    'media markt': 'https://www.mediamarkt.ch', 'fust': 'https://www.fust.ch',
    'interdiscount': 'https://www.interdiscount.ch', 'fnac': 'https://www.fnac.ch',
    'digitec': 'https://www.digitec.ch', 'galaxus': 'https://www.galaxus.ch',
    'apple': 'https://www.apple.com/chfr', 'samsung': 'https://www.samsung.com/ch_fr',
    
    # Télécoms/Banques
    'swisscom': 'https://www.swisscom.ch', 'sunrise': 'https://www.sunrise.ch',
    'salt': 'https://www.salt.ch', 'ubs': 'https://www.ubs.com/ch/fr',
    'raiffeisen': 'https://www.raiffeisen.ch', 'bcv': 'https://www.bcv.ch',
    'postfinance': 'https://www.postfinance.ch',
    
    # Fast Food
    'mcdonald': 'https://www.mcdonalds.ch', 'burger king': 'https://www.burgerking.ch',
    'starbucks': 'https://www.starbucks.ch/fr', 'subway': 'https://www.subway.com/fr-ch',
    'kfc': 'https://www.kfc.ch', 'holy cow': 'https://www.holycow.ch',
    
    # Beauté
    'sephora': 'https://www.sephora.ch', 'marionnaud': 'https://www.marionnaud.ch',
    'douglas': 'https://www.douglas.ch', 'yves rocher': 'https://www.yves-rocher.ch',
    'the body shop': 'https://www.thebodyshop.com/fr-ch',
    'lush': 'https://www.lush.com/ch/fr', 'kiko': 'https://www.kikocosmetics.com/fr-ch',
    'rituals': 'https://www.rituals.com/fr-ch', "l'occitane": 'https://ch.loccitane.com',
    'clarins': 'https://www.clarins.ch', 'bodyminute': 'https://www.bodyminute.com',
    
    # Pharmacies
    'pharmacieplus': 'https://www.pharmacieplus.ch', 'amavita': 'https://www.amavita.ch',
    'sunstore': 'https://www.sunstore.ch', 'coop vitality': 'https://www.coopvitality.ch',
    
    # Optique
    'visilab': 'https://www.visilab.ch', 'fielmann': 'https://www.fielmann.ch',
    'optic 2000': 'https://www.optic2000.ch', 'mcoptique': 'https://www.mcoptique.ch',
    'grandoptical': 'https://www.grandoptical.ch',
    
    # Montres/Bijoux
    'swatch': 'https://www.swatch.com/fr-ch', 'rolex': 'https://www.rolex.com/fr',
    'omega': 'https://www.omegawatches.com/fr-ch', 'tissot': 'https://www.tissotwatches.com/fr-ch',
    'tag heuer': 'https://www.tagheuer.com/ch/fr', 'longines': 'https://www.longines.com/fr-ch',
    'breitling': 'https://www.breitling.com/ch-fr', 'hublot': 'https://www.hublot.com/fr-ch',
    'tudor': 'https://www.tudorwatch.com/fr_ch', 'bucherer': 'https://www.bucherer.com/ch/fr',
    'christ': 'https://www.christ-uhren-schmuck.ch', 'pandora': 'https://ch.pandora.net/fr',
    'swarovski': 'https://www.swarovski.com/fr-CH',
    
    # Luxe
    'louis vuitton': 'https://fr.louisvuitton.com/fra-ch',
    'gucci': 'https://www.gucci.com/ch/fr', 'prada': 'https://www.prada.com/ch/fr',
    'chanel': 'https://www.chanel.com/ch/fr', 'dior': 'https://www.dior.com/fr_ch',
    'hermès': 'https://www.hermes.com/ch/fr', 'cartier': 'https://www.cartier.ch/fr-ch',
    'burberry': 'https://ch.burberry.com/fr', 'versace': 'https://www.versace.com/ch/fr',
    'fendi': 'https://www.fendi.com/ch-fr', 'balenciaga': 'https://www.balenciaga.com/ch-fr',
    'valentino': 'https://www.valentino.com/fr-ch', 'moncler': 'https://www.moncler.com/fr-ch',
    'bulgari': 'https://www.bulgari.com/fr-ch', 'chopard': 'https://www.chopard.com/fr-ch',
    
    # Meubles
    'ikea': 'https://www.ikea.com/ch/fr', 'conforama': 'https://www.conforama.ch',
    'maisons du monde': 'https://www.maisonsdumonde.com/CH/fr',
    'pfister': 'https://www.pfister.ch', 'interio': 'https://www.interio.ch',
    'livique': 'https://www.livique.ch', 'micasa': 'https://www.micasa.ch',
    'jysk': 'https://jysk.ch',
    
    # Bricolage
    'hornbach': 'https://www.hornbach.ch', 'jumbo': 'https://www.jumbo.ch',
    'obi': 'https://www.obi.ch', 'landi': 'https://www.landi.ch',
    'do it garden': 'https://www.doitgarden.ch', 'bauhaus': 'https://www.bauhaus.ch',
    
    # Transport
    'la poste': 'https://www.post.ch/fr', 'cff': 'https://www.sbb.ch/fr',
    'sbb': 'https://www.sbb.ch', 'tl': 'https://www.t-l.ch',
    
    # Assurances
    'axa': 'https://www.axa.ch', 'mobilière': 'https://www.mobiliere.ch',
    'vaudoise': 'https://www.vaudoise.ch', 'generali': 'https://www.generali.ch',
    'zurich': 'https://www.zurich.ch', 'helvetia': 'https://www.helvetia.com/ch/web/fr',
    'baloise': 'https://www.baloise.ch', 'allianz': 'https://www.allianz.ch',
    
    # Fitness
    'fitness park': 'https://www.fitnesspark.ch', 'basefit': 'https://www.basefit.ch',
    'update fitness': 'https://www.update-fitness.ch',
    
    # Kiosques
    'k kiosk': 'https://www.kkiosk.ch', 'avec': 'https://www.avec.ch',
    'naville': 'https://www.naville.ch',
    
    # Librairies
    'payot': 'https://www.payot.ch', 'ex libris': 'https://www.exlibris.ch',
    'orell füssli': 'https://www.orellfuessli.ch', 'office world': 'https://www.officeworld.ch',
    
    # Coiffure franchises
    'jean louis david': 'https://www.jeanlouisdavid.ch',
    'franck provost': 'https://www.franckprovost.com',
    'dessange': 'https://www.dessange.ch',
    "mod's hair": 'https://www.modshair.com',
    
    # Restaurants suisses
    'vapiano': 'https://ch.vapiano.com', 'tibits': 'https://www.tibits.ch',
    'hiltl': 'https://www.hiltl.ch',
    
    # Autres marques populaires
    'intimissimi': 'https://www.intimissimi.com/ch/fr',
    'calzedonia': 'https://www.calzedonia.com/ch/fr',
    'oysho': 'https://www.oysho.com/ch/fr',
    'promod': 'https://www.promod.ch',
    'etam': 'https://www.etam.com',
    'cache cache': 'https://www.cache-cache.fr',
    'jennifer': 'https://www.jennyfer.com',
    'pimkie': 'https://www.pimkie.ch',
    'kiabi': 'https://www.kiabi.ch',
    'camaieu': 'https://www.camaieu.fr',
    'celio': 'https://www.celio.com',
    'jules': 'https://www.jules.com',
    'devred': 'https://www.devred.com',
    'burton': 'https://www.burton.co.uk',
    'dockers': 'https://www.dockers.com',
    'lee': 'https://www.lee.com',
    'wrangler': 'https://www.wrangler.com',
    'vans': 'https://www.vans.ch',
    'converse': 'https://www.converse.com/ch',
    'skechers': 'https://www.skechers.ch',
    'crocs': 'https://www.crocs.ch',
    'havaianas': 'https://www.havaianas-store.com/ch_fr',
    'king jouet': 'https://www.king-jouet.ch',
    'toys r us': 'https://www.smythstoys.com/ch/fr-ch',
    'orchestra': 'https://ch.shop-orchestra.com',
    'sergent major': 'https://www.sergent-major.com',
    'catimini': 'https://www.catimini.com',
    'bonpoint': 'https://www.bonpoint.com',
    'petit bateau': 'https://www.petit-bateau.ch',
    'jacadi': 'https://www.jacadi.ch',
    'vertbaudet': 'https://www.vertbaudet.ch',
}

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
]

print("=" * 70)
print("   SCRAPER V13 - BASE ÉTENDUE + MATCHING AMÉLIORÉ")
print(f"   {len(KNOWN_WEBSITES)} sites dans la base")
print("=" * 70)


def normalize_name(name):
    """Normalise le nom"""
    name_lower = name.lower().strip()
    # Enlever ponctuation mais garder &
    name_clean = re.sub(r'[^a-zàâäéèêëïîôùûüç0-9\s&\'-]', '', name_lower)
    return name_clean


def find_known_website(name):
    """Trouve le site avec matching strict"""
    name_clean = normalize_name(name)
    words = name_clean.split()
    
    # Correspondance exacte
    if name_clean in KNOWN_WEBSITES:
        return KNOWN_WEBSITES[name_clean]
    
    # Correspondance par marque exacte dans le nom
    for brand, url in KNOWN_WEBSITES.items():
        brand_words = brand.split()
        # La marque entière doit être dans le nom
        if all(bw in words for bw in brand_words):
            return url
        # Le nom entier est la marque
        if name_clean == brand:
            return url
    
    # Correspondance stricte : le premier mot significatif (>4 chars) doit matcher exactement
    for word in words:
        if len(word) > 4 and word in KNOWN_WEBSITES:
            return KNOWN_WEBSITES[word]
    
    return None


async def scrape_website(page, website, eid):
    """Screenshot du site"""
    result = {'cover': None, 'description': None}
    
    try:
        await page.goto(website, wait_until='domcontentloaded', timeout=20000)
        await page.wait_for_timeout(2000)
        
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
    
    # Entreprises SANS cover image valide
    query = {
        '$or': [
            {'cover_image': None},
            {'cover_image': ''},
            {'cover_image': {'$exists': False}}
        ]
    }
    
    enterprises = await db.enterprises.find(
        query,
        {'_id': 0, 'id': 1, 'name': 1, 'business_name': 1}
    ).to_list(10000)
    
    total = len(enterprises)
    print(f'\n[INFO] {total} entreprises sans cover à traiter\n')
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=random.choice(USER_AGENTS)
        )
        page = await context.new_page()
        
        stats = {'processed': 0, 'success': 0, 'no_match': 0, 'failed': 0}
        
        for i, ent in enumerate(enterprises):
            eid = ent.get('id')
            name = ent.get('business_name') or ent.get('name', '')
            
            if not name:
                continue
            
            stats['processed'] += 1
            print(f'[{i+1}/{total}] {name[:40]}', end=' ')
            
            website = find_known_website(name)
            
            if website:
                print(f'-> {website[:35]}', end=' ')
                data = await scrape_website(page, website, eid)
                
                if data['cover']:
                    update = {
                        'website': website,
                        'cover_image': data['cover'],
                        'enriched_at': datetime.now(timezone.utc).isoformat(),
                        'enrichment_source': 'known_v13'
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
                stats['no_match'] += 1
                print('-> No match')
            
            await asyncio.sleep(random.uniform(0.3, 0.8))
            
            if stats['processed'] % 100 == 0:
                print(f'\n--- Success: {stats["success"]} | No match: {stats["no_match"]} ---\n')
        
        await browser.close()
    
    client.close()
    
    print(f'\n{"=" * 70}')
    print(f'   Success: {stats["success"]} | No match: {stats["no_match"]} | Failed: {stats["failed"]}')
    print(f'{"=" * 70}')


if __name__ == '__main__':
    asyncio.run(main())
