#!/usr/bin/env python3
"""
SCRAPER V12 - Approche batch avec screenshots Playwright
Scrape les sites des grandes enseignes connues + génère des images représentatives
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
from urllib.parse import urljoin
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'secondevie')
UPLOADS_DIR = '/app/backend/uploads/enterprises'

os.makedirs(UPLOADS_DIR, exist_ok=True)

# Base de données très étendue des sites web suisses
KNOWN_WEBSITES = {
    # SUPERMARCHÉS
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
    
    # MODE - GRANDES MARQUES
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
    'calvin klein': 'https://www.calvinklein.ch/fr',
    'tommy hilfiger': 'https://ch.tommy.com/fr',
    'lacoste': 'https://www.lacoste.com/ch/fr',
    'hugo boss': 'https://www.hugoboss.com/ch/fr',
    'ralph lauren': 'https://www.ralphlauren.ch',
    'guess': 'https://www.guess.eu/fr-ch',
    'levi\'s': 'https://www.levi.com/CH/fr_CH',
    'diesel': 'https://ch.diesel.com/fr',
    'replay': 'https://www.replayjeans.com',
    'pepe jeans': 'https://www.pepejeans.com/ch_fr',
    'scotch & soda': 'https://www.scotch-soda.com/ch/fr',
    'superdry': 'https://www.superdry.ch',
    'gant': 'https://www.gant.ch',
    'timberland': 'https://www.timberland.ch',
    'the north face': 'https://www.thenorthface.ch',
    'columbia': 'https://www.columbiasportswear.ch',
    'patagonia': 'https://www.patagonia.com/ch',
    'fjällräven': 'https://www.fjallraven.com/ch/fr',
    'beldona': 'https://www.beldona.com',
    'triumph': 'https://ch.triumph.com',
    'calida': 'https://www.calida.com',
    'wolford': 'https://www.wolford.com',
    
    # CHAUSSURES
    'foot locker': 'https://www.footlocker.ch',
    'snipes': 'https://www.snipes.ch',
    'vögele shoes': 'https://www.voegele-shoes.ch',
    'dosenbach': 'https://www.dosenbach.ch',
    'ochsner shoes': 'https://www.ochsner-shoes.ch',
    'bata': 'https://www.bata.ch',
    'salamander': 'https://www.salamander.ch',
    'deichmann': 'https://www.deichmann.com/CH/fr/shop',
    'geox': 'https://www.geox.com',
    'ecco': 'https://ch.ecco.com',
    'clarks': 'https://www.clarks.ch',
    'birkenstock': 'https://www.birkenstock.com/ch-fr',
    'dr. martens': 'https://www.drmartens.com/ch/fr',
    
    # SPORT
    'nike': 'https://www.nike.com/ch',
    'adidas': 'https://www.adidas.ch/fr',
    'puma': 'https://eu.puma.com/ch/fr',
    'reebok': 'https://www.reebok.ch',
    'asics': 'https://www.asics.com/ch/fr-ch',
    'new balance': 'https://www.newbalance.ch',
    'under armour': 'https://www.underarmour.ch',
    'decathlon': 'https://www.decathlon.ch',
    'ochsner sport': 'https://www.ochsnersport.ch',
    'intersport': 'https://www.intersport.ch',
    'sportxx': 'https://www.sportxx.ch',
    'athletes world': 'https://www.athletesworld.ch',
    
    # ÉLECTRONIQUE
    'media markt': 'https://www.mediamarkt.ch',
    'fust': 'https://www.fust.ch',
    'interdiscount': 'https://www.interdiscount.ch',
    'fnac': 'https://www.fnac.ch',
    'digitec': 'https://www.digitec.ch',
    'galaxus': 'https://www.galaxus.ch',
    'microspot': 'https://www.microspot.ch',
    'apple': 'https://www.apple.com/chfr',
    'samsung': 'https://www.samsung.com/ch_fr',
    'sony': 'https://www.sony.ch',
    'bose': 'https://www.bose.ch',
    'bang & olufsen': 'https://www.bang-olufsen.com/fr-ch',
    
    # TÉLÉCOMS
    'swisscom': 'https://www.swisscom.ch',
    'sunrise': 'https://www.sunrise.ch',
    'salt': 'https://www.salt.ch',
    'yallo': 'https://www.yallo.ch',
    'wingo': 'https://www.wingo.ch',
    
    # BANQUES
    'ubs': 'https://www.ubs.com/ch/fr',
    'credit suisse': 'https://www.credit-suisse.com/ch/fr',
    'raiffeisen': 'https://www.raiffeisen.ch',
    'bcv': 'https://www.bcv.ch',
    'postfinance': 'https://www.postfinance.ch',
    'julius baer': 'https://www.juliusbaer.com',
    'pictet': 'https://www.group.pictet',
    'lombard odier': 'https://www.lombardodier.com',
    
    # RESTAURATION RAPIDE
    'mcdonald\'s': 'https://www.mcdonalds.ch',
    'burger king': 'https://www.burgerking.ch',
    'starbucks': 'https://www.starbucks.ch/fr',
    'subway': 'https://www.subway.com/fr-ch',
    'pizza hut': 'https://www.pizzahut.ch',
    'domino\'s': 'https://www.dominos.ch',
    'kfc': 'https://www.kfc.ch',
    'five guys': 'https://www.fiveguys.ch',
    'holy cow': 'https://www.holycow.ch',
    
    # BEAUTÉ / COSMÉTIQUES
    'sephora': 'https://www.sephora.ch',
    'marionnaud': 'https://www.marionnaud.ch',
    'douglas': 'https://www.douglas.ch',
    'yves rocher': 'https://www.yves-rocher.ch',
    'the body shop': 'https://www.thebodyshop.com/fr-ch',
    'lush': 'https://www.lush.com/ch/fr',
    'kiko': 'https://www.kikocosmetics.com/fr-ch',
    'mac': 'https://www.maccosmetics.ch',
    'nyx': 'https://www.nyxcosmetics.ch',
    'rituals': 'https://www.rituals.com/fr-ch',
    'l\'occitane': 'https://ch.loccitane.com',
    'clarins': 'https://www.clarins.ch',
    'clinique': 'https://www.clinique.ch',
    'estée lauder': 'https://www.esteelauder.ch',
    'lancôme': 'https://www.lancome.ch',
    'chanel beauté': 'https://www.chanel.com/ch/fr/beaute',
    'dior beauté': 'https://www.dior.com/fr_ch/beaute',
    'bodyminute': 'https://www.bodyminute.com',
    
    # PHARMACIES
    'pharmacieplus': 'https://www.pharmacieplus.ch',
    'amavita': 'https://www.amavita.ch',
    'benu': 'https://www.benu.ch',
    'sunstore': 'https://www.sunstore.ch',
    'coop vitality': 'https://www.coopvitality.ch',
    'medbase': 'https://www.medbase.ch',
    
    # OPTIQUE
    'visilab': 'https://www.visilab.ch',
    'fielmann': 'https://www.fielmann.ch',
    'mcoptique': 'https://www.mcoptique.ch',
    'optic 2000': 'https://www.optic2000.ch',
    'pearle': 'https://www.pearle.ch',
    'grandoptical': 'https://www.grandoptical.ch',
    'apollo': 'https://www.apollo.ch',
    
    # MONTRES / BIJOUX
    'swatch': 'https://www.swatch.com/fr-ch',
    'rolex': 'https://www.rolex.com/fr',
    'omega': 'https://www.omegawatches.com/fr-ch',
    'tissot': 'https://www.tissotwatches.com/fr-ch',
    'tag heuer': 'https://www.tagheuer.com/ch/fr',
    'longines': 'https://www.longines.com/fr-ch',
    'breitling': 'https://www.breitling.com/ch-fr',
    'iwc': 'https://www.iwc.com/ch/fr',
    'jaeger-lecoultre': 'https://www.jaeger-lecoultre.com/ch/fr',
    'audemars piguet': 'https://www.audemarspiguet.com/fr-ch',
    'patek philippe': 'https://www.patek.com/fr',
    'vacheron constantin': 'https://www.vacheron-constantin.com/ch/fr',
    'hublot': 'https://www.hublot.com/fr-ch',
    'zenith': 'https://www.zenith-watches.com/fr_ch',
    'tudor': 'https://www.tudorwatch.com/fr_ch',
    'hamilton': 'https://www.hamiltonwatch.com/fr-ch',
    'rado': 'https://www.rado.com/fr_ch',
    'certina': 'https://www.certina.com/fr_ch',
    'mido': 'https://www.midowatches.com/fr_ch',
    'fossil': 'https://www.fossil.com/ch/fr',
    'bucherer': 'https://www.bucherer.com/ch/fr',
    'christ': 'https://www.christ-uhren-schmuck.ch',
    'pandora': 'https://ch.pandora.net/fr',
    'swarovski': 'https://www.swarovski.com/fr-CH',
    
    # LUXE
    'louis vuitton': 'https://fr.louisvuitton.com/fra-ch',
    'gucci': 'https://www.gucci.com/ch/fr',
    'prada': 'https://www.prada.com/ch/fr',
    'chanel': 'https://www.chanel.com/ch/fr',
    'dior': 'https://www.dior.com/fr_ch',
    'hermès': 'https://www.hermes.com/ch/fr',
    'cartier': 'https://www.cartier.ch/fr-ch',
    'tiffany': 'https://www.tiffany.ch/fr',
    'burberry': 'https://ch.burberry.com/fr',
    'versace': 'https://www.versace.com/ch/fr',
    'fendi': 'https://www.fendi.com/ch-fr',
    'balenciaga': 'https://www.balenciaga.com/ch-fr',
    'bottega veneta': 'https://www.bottegaveneta.com/ch-fr',
    'saint laurent': 'https://www.ysl.com/ch-fr',
    'givenchy': 'https://www.givenchy.com/ch/fr',
    'valentino': 'https://www.valentino.com/fr-ch',
    'moncler': 'https://www.moncler.com/fr-ch',
    'bvlgari': 'https://www.bulgari.com/fr-ch',
    'chopard': 'https://www.chopard.com/fr-ch',
    'piaget': 'https://www.piaget.com/ch-fr',
    'van cleef & arpels': 'https://www.vancleefarpels.com/ch/fr',
    
    # MEUBLES / DÉCO
    'ikea': 'https://www.ikea.com/ch/fr',
    'conforama': 'https://www.conforama.ch',
    'maisons du monde': 'https://www.maisonsdumonde.com/CH/fr',
    'pfister': 'https://www.pfister.ch',
    'interio': 'https://www.interio.ch',
    'livique': 'https://www.livique.ch',
    'micasa': 'https://www.micasa.ch',
    'jysk': 'https://jysk.ch',
    'casa': 'https://www.casashops.com/ch_fr',
    'depot': 'https://www.depot-online.com/ch_fr',
    'zara home': 'https://www.zarahome.com/ch/fr',
    'h&m home': 'https://www2.hm.com/fr_ch/maison',
    
    # BRICOLAGE / JARDIN
    'hornbach': 'https://www.hornbach.ch',
    'jumbo': 'https://www.jumbo.ch',
    'obi': 'https://www.obi.ch',
    'coop brico+loisirs': 'https://www.bricoloisirs.ch',
    'landi': 'https://www.landi.ch',
    'do it + garden': 'https://www.doitgarden.ch',
    'bauhaus': 'https://www.bauhaus.ch',
    
    # AUTOMOBILES
    'amag': 'https://www.amag.ch',
    'emil frey': 'https://www.emilfrey.ch',
    'auto zürich': 'https://www.auto-zuerich.ch',
    'garage du lac': 'https://www.garagedulac.ch',
    
    # SERVICES
    'la poste': 'https://www.post.ch/fr',
    'cff': 'https://www.sbb.ch/fr',
    'sbb': 'https://www.sbb.ch',
    'tl': 'https://www.t-l.ch',
    
    # ASSURANCES
    'axa': 'https://www.axa.ch',
    'swiss life': 'https://www.swisslife.ch',
    'mobilière': 'https://www.mobiliere.ch',
    'la mobilière': 'https://www.mobiliere.ch',
    'vaudoise': 'https://www.vaudoise.ch',
    'generali': 'https://www.generali.ch',
    'zurich': 'https://www.zurich.ch',
    'helvetia': 'https://www.helvetia.com/ch/web/fr',
    'baloise': 'https://www.baloise.ch',
    'allianz': 'https://www.allianz.ch',
    
    # VOYAGE / TOURISME
    'kuoni': 'https://www.kuoni.ch',
    'hotelplan': 'https://www.hotelplan.ch',
    'tui': 'https://www.tui.ch',
    'swiss': 'https://www.swiss.com',
    'easyjet': 'https://www.easyjet.com/fr',
    
    # FITNESS / SPORT
    'fitness park': 'https://www.fitnesspark.ch',
    'update fitness': 'https://www.update-fitness.ch',
    'basefit': 'https://www.basefit.ch',
    'kieser training': 'https://www.kieser-training.ch',
    'holmes place': 'https://www.holmesplace.ch',
    'david lloyd': 'https://www.davidlloyd.ch',
    
    # KIOSQUES / TABAC
    'k kiosk': 'https://www.kkiosk.ch',
    'avec': 'https://www.avec.ch',
    'press & books': 'https://www.pressandbooks.ch',
    'naville': 'https://www.naville.ch',
    
    # LIBRAIRIES / PAPETERIE
    'payot': 'https://www.payot.ch',
    'fnac': 'https://www.fnac.ch',
    'ex libris': 'https://www.exlibris.ch',
    'orell füssli': 'https://www.orellfuessli.ch',
    'office world': 'https://www.officeworld.ch',
    'papeterie': 'https://www.officeworld.ch',
    
    # COIFFEURS FRANCHISES
    'gina laura': 'https://www.gina-laura.ch',
    'tchip coiffure': 'https://www.tchip.ch',
    'coiff&co': 'https://www.coiffandco.com',
    'dessange': 'https://www.dessange.ch',
    'jacques dessange': 'https://www.dessange.ch',
    'franck provost': 'https://www.franckprovost.com',
    'jean louis david': 'https://www.jeanlouisdavid.ch',
    'mod\'s hair': 'https://www.modshair.com',
    'camille albane': 'https://www.camillealbane.com',
    
    # INSTITUTS BEAUTÉ FRANCHISES
    'body minute': 'https://www.bodyminute.com',
    'yves rocher': 'https://www.yves-rocher.ch',
    'beauty success': 'https://www.beautysuccess.fr',
    
    # RESTAURANTS SUISSES
    'holy cow': 'https://www.holycow.ch',
    'vapiano': 'https://ch.vapiano.com',
    'hiltl': 'https://www.hiltl.ch',
    'tibits': 'https://www.tibits.ch',
    'au bon pain': 'https://www.aubonpain.ch',
    'yooji\'s': 'https://www.yoojis.ch',
    'nooch': 'https://www.nooch.ch',
    'au gruyère': 'https://www.au-gruyere.ch',
    'café des banques': 'https://www.banques.ch',
    
    # BOULANGERIES FRANCHISES
    'brezelkönig': 'https://www.brezelkoenig.ch',
    'pouly': 'https://www.pouly.ch',
    'fleur de pains': 'https://www.fleurdepains.ch',
    'paul': 'https://www.paul.fr',
}

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

print("=" * 70)
print("   SCRAPER V12 - BASE DE DONNÉES ÉTENDUE")
print("=" * 70)


def normalize_name(name):
    """Normalise le nom pour la recherche"""
    name_lower = name.lower().strip()
    # Enlever les accents et caractères spéciaux
    name_clean = re.sub(r'[^a-zàâäéèêëïîôùûüç0-9\s&\'-]', '', name_lower)
    return name_clean


def find_known_website(name):
    """Trouve le site web dans notre base de données étendue"""
    name_clean = normalize_name(name)
    
    # Correspondance exacte
    if name_clean in KNOWN_WEBSITES:
        return KNOWN_WEBSITES[name_clean]
    
    # Correspondance partielle
    for brand, url in KNOWN_WEBSITES.items():
        # Le nom contient la marque
        if brand in name_clean:
            return url
        # La marque contient le nom
        if name_clean in brand and len(name_clean) > 3:
            return url
        # Chaque mot du nom
        for word in name_clean.split():
            if len(word) > 4 and word == brand:
                return url
    
    return None


async def scrape_website(page, website, eid):
    """Screenshot du site"""
    result = {'cover': None, 'logo': None, 'description': None}
    
    if not website:
        return result
    
    try:
        await page.goto(website, wait_until='domcontentloaded', timeout=25000)
        await page.wait_for_timeout(2500)
        
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
                
    except PlaywrightTimeout:
        pass
    except Exception as e:
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
        {'_id': 0, 'id': 1, 'name': 1, 'business_name': 1}
    ).to_list(10000)
    
    total = len(enterprises)
    print(f'\n[INFO] {total} entreprises à traiter')
    print(f'[INFO] {len(KNOWN_WEBSITES)} sites connus dans la base\n')
    
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
                        'enrichment_source': 'known_sites_v12'
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
            
            # Pause
            await asyncio.sleep(random.uniform(0.3, 1.0))
            
            if stats['processed'] % 100 == 0:
                print(f'\n--- Success: {stats["success"]} | No match: {stats["no_match"]} | Failed: {stats["failed"]} ---\n')
        
        await browser.close()
    
    client.close()
    
    print(f'\n{"=" * 70}')
    print(f'   TERMINÉ!')
    print(f'   Success: {stats["success"]}')
    print(f'   No match: {stats["no_match"]}')
    print(f'   Failed: {stats["failed"]}')
    print(f'{"=" * 70}')


if __name__ == '__main__':
    asyncio.run(main())
