#!/usr/bin/env python3
"""
Comprehensive scraper for local.ch - Lausanne businesses
Version 6: 500+ categories, full coverage
"""

import asyncio
import re
import os
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/backend/scraper_v6.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# MongoDB connection - secondevie
MONGO_URL = "mongodb+srv://prankgy:Minijetaime1996@cluster0.kwjifsg.mongodb.net/secondevie?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "secondevie"


async def get_existing_keys(db):
    """Get set of existing business keys"""
    existing = set()
    cursor = db.enterprises.find({}, {"name": 1, "business_name": 1, "address": 1})
    async for doc in cursor:
        name = doc.get("name") or doc.get("business_name", "")
        address = doc.get("address", "")
        if name:
            key = f"{name.lower().strip()[:50]}|{address.lower().strip()[:30]}"
            existing.add(key)
    logger.info(f"Found {len(existing)} existing businesses")
    return existing


def normalize_key(name, address):
    name_clean = name.lower().strip()[:50] if name else ""
    addr_clean = address.lower().strip()[:30] if address else ""
    return f"{name_clean}|{addr_clean}"


async def scrape_search(page, search_term, location, existing_keys, max_pages=30):
    """Scrape search results for a term in a location"""
    from playwright.async_api import TimeoutError as PlaywrightTimeout
    
    businesses = []
    
    for page_num in range(1, max_pages + 1):
        url = f"https://www.local.ch/fr/s/{quote(search_term)}/{quote(location)}?page={page_num}"
        
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=20000)
            await page.wait_for_timeout(1500)
            
            try:
                await page.wait_for_selector('a[href*="/fr/d/"]', timeout=5000)
            except:
                pass
            
            listings = await page.query_selector_all('a[href*="/fr/d/"]')
            
            if not listings:
                break
            
            page_businesses = []
            seen_on_page = set()
            
            for listing in listings:
                try:
                    href = await listing.get_attribute('href')
                    if not href or '/fr/d/' not in href:
                        continue
                    
                    if href in seen_on_page:
                        continue
                    seen_on_page.add(href)
                    
                    text = await listing.inner_text()
                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    
                    if not lines:
                        continue
                    
                    name = lines[0][:100]
                    
                    if len(name) < 3 or name.lower() in ['voir plus', 'plus', 'suivant', 'précédent']:
                        continue
                    
                    business = {
                        'name': name,
                        'business_name': name,
                        'city': 'Lausanne',
                        'canton': 'Vaud',
                        'country': 'Suisse',
                        'source': 'local.ch',
                        'activation_status': 'inactive',
                        'status': 'bientot_disponible',
                        'is_verified': False,
                        'is_certified': False,
                        'is_premium': False,
                        'category': search_term.replace('-', ' ').title(),
                        'subcategory': search_term,
                        'search_location': location,
                        'rating': 0,
                        'reviews_count': 0,
                    }
                    
                    for line in lines[1:5]:
                        if re.search(r'\d{4}', line):
                            business['address'] = line[:200]
                            postal_match = re.search(r'(\d{4})', line)
                            if postal_match:
                                business['postal_code'] = postal_match.group(1)
                            break
                    
                    for line in lines:
                        phone_match = re.search(r'(\+41[\s.-]?\d{2}[\s.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2}|0\d{2}[\s.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2})', line)
                        if phone_match:
                            business['phone'] = phone_match.group(1).replace(' ', '').replace('.', '').replace('-', '')
                            break
                    
                    key = normalize_key(name, business.get('address', ''))
                    if key not in existing_keys:
                        page_businesses.append(business)
                        existing_keys.add(key)
                        
                except Exception as e:
                    continue
            
            if page_businesses:
                businesses.extend(page_businesses)
            
            if len(page_businesses) < 3:
                break
                
            await page.wait_for_timeout(800)
            
        except PlaywrightTimeout:
            break
        except Exception as e:
            break
    
    return businesses


async def insert_businesses(db, businesses):
    if not businesses:
        return 0
    
    now = datetime.now(timezone.utc).isoformat()
    
    for biz in businesses:
        biz['id'] = f"lch_{abs(hash(biz['name'] + biz.get('address', '') + biz.get('phone', ''))) % 10000000000}"
        biz['created_at'] = now
        biz['updated_at'] = now
        
        if not biz.get('image'):
            name_encoded = quote(biz['name'][:20])
            biz['image'] = f"https://ui-avatars.com/api/?name={name_encoded}&background=0047AB&color=fff&size=400"
    
    try:
        result = await db.enterprises.insert_many(businesses, ordered=False)
        return len(result.inserted_ids)
    except Exception as e:
        inserted = 0
        for biz in businesses:
            try:
                await db.enterprises.insert_one(biz)
                inserted += 1
            except:
                pass
        return inserted


async def main():
    from playwright.async_api import async_playwright
    
    logger.info("=" * 60)
    logger.info("LOCAL.CH SCRAPER V6 - 500+ CATEGORIES")
    logger.info("=" * 60)
    
    mongo_client = AsyncIOMotorClient(MONGO_URL)
    db = mongo_client[DB_NAME]
    
    existing_keys = await get_existing_keys(db)
    initial_count = await db.enterprises.count_documents({})
    logger.info(f"Initial count: {initial_count}")
    
    # 500+ CATEGORIES - Complete list
    search_terms = [
        # ========== RESTAURATION (80 termes) ==========
        "restaurant", "cafe", "bar", "pizzeria", "sushi", "thai", "chinois", "indien",
        "japonais", "mexicain", "italien", "francais", "libanais", "turc", "grec",
        "vietnamien", "coreen", "africain", "bresilien", "espagnol", "portugais",
        "marocain", "tunisien", "algerien", "syrien", "persan", "iranien", "afghan",
        "pakistanais", "indonesien", "malaisien", "philippin", "tibetain", "nepalais",
        "boulangerie", "patisserie", "chocolatier", "chocolaterie", "glacier", "confiseur",
        "epicerie", "supermarche", "alimentation", "primeur", "fruits-legumes",
        "boucherie", "charcuterie", "poissonnerie", "fromagerie", "cremerie",
        "caviste", "oenologie", "vin", "spiritueux", "biere", "bieres-artisanales",
        "traiteur", "catering", "banquet", "reception", "food-truck",
        "kebab", "fast-food", "burger", "sandwich", "salade", "wrap", "poke-bowl",
        "vegetarien", "vegan", "bio", "organic", "sans-gluten", "halal", "casher",
        "tea-room", "salon-the", "brunch", "petit-dejeuner", "gouter",
        "bistrot", "brasserie", "pub", "taverne", "lounge", "rooftop",
        "club", "discotheque", "nightclub", "cocktail-bar", "wine-bar",
        
        # ========== BEAUTE & BIEN-ETRE (60 termes) ==========
        "coiffeur", "coiffeuse", "salon-coiffure", "barbier", "barber-shop",
        "coloriste", "visagiste", "extensions-cheveux", "perruque", "postiche",
        "institut-beaute", "estheticienne", "soins-visage", "soins-corps",
        "manucure", "pedicure", "onglerie", "nail-art", "gel-uv", "vernis",
        "maquillage", "maquilleuse", "make-up", "conseillere-beaute",
        "massage", "masseur", "masseuse", "massage-thai", "massage-shiatsu",
        "reflexologie", "drainage-lymphatique", "massage-sportif",
        "spa", "hammam", "sauna", "jacuzzi", "bain-turc", "thermes",
        "epilation", "epilation-laser", "epilation-definitive", "ipl",
        "bronzage", "solarium", "uv", "autobronzant",
        "tatoueur", "tatouage", "tattoo", "piercing", "body-art",
        "microblading", "micropigmentation", "maquillage-permanent",
        "lifting", "botox", "acide-hyaluronique", "medecine-esthetique",
        "liposuccion", "chirurgie-esthetique", "chirurgie-plastique",
        
        # ========== SPORT & FITNESS (50 termes) ==========
        "fitness", "gym", "salle-sport", "musculation", "bodybuilding",
        "crossfit", "hiit", "cardio", "aerobic", "zumba", "step",
        "yoga", "pilates", "stretching", "meditation", "relaxation",
        "danse", "danse-classique", "danse-moderne", "salsa", "tango", "hip-hop",
        "boxe", "kickboxing", "mma", "arts-martiaux", "judo", "karate", "taekwondo",
        "aikido", "kung-fu", "jiu-jitsu", "krav-maga", "self-defense",
        "natation", "piscine", "aquagym", "plongee", "apnee",
        "tennis", "squash", "badminton", "padel", "ping-pong",
        "golf", "mini-golf", "driving-range", "equitation", "centre-equestre",
        "escalade", "climbing", "bloc", "alpinisme", "randonnee",
        "velo", "cyclisme", "spinning", "vtt", "bmx", "skateboard",
        "roller", "patin-glace", "patinoire", "hockey", "curling",
        
        # ========== SANTE & MEDICAL (100 termes) ==========
        "medecin", "docteur", "generaliste", "medecin-famille",
        "specialiste", "interniste", "urgentiste", "sos-medecin",
        "dentiste", "orthodontiste", "implantologue", "parodontiste", "endodontiste",
        "hygieniste-dentaire", "prothesiste-dentaire", "laboratoire-dentaire",
        "pharmacie", "parapharmacie", "droguerie", "herboristerie",
        "opticien", "lunettes", "lentilles", "optometriste", "orthoptiste",
        "audioprothesiste", "appareil-auditif", "audiologie",
        "physiotherapie", "physio", "kinesitherapie", "kine", "reeducation",
        "osteopathe", "osteopathie", "chiropracteur", "chiropratique",
        "acupuncture", "acupuncteur", "medecine-chinoise", "moxibustion",
        "homeopathie", "homeopathe", "naturopathe", "naturopathie",
        "psychologue", "psychiatre", "psychotherapeute", "psychanalyste",
        "therapeute", "hypnose", "hypnotherapie", "sophrologie",
        "coach", "coaching", "life-coach", "coach-sante",
        "nutritionniste", "dieteticien", "dietetique", "nutrition",
        "pediatre", "pedopsychiatre", "neuropediatre", "pediatrie",
        "gynecologue", "sage-femme", "obstetricien", "maternite",
        "dermatologue", "dermatologie", "venereologie",
        "cardiologue", "cardiologie", "angiologie", "phlebologie",
        "pneumologue", "allergologue", "immunologie",
        "gastro-enterologue", "hepatologie", "proctologie",
        "urologue", "nephrologie", "andrologie",
        "neurologue", "neurologie", "neurochirurgie",
        "orl", "oto-rhino", "audiologie", "phoniatrie",
        "ophtalmologue", "ophtalmologie", "chirurgie-oeil",
        "orthopediste", "traumatologie", "rhumatologie",
        "radiologue", "radiologie", "irm", "scanner", "echographie",
        "oncologue", "cancerologie", "chimiotherapie", "radiotherapie",
        "chirurgien", "chirurgie", "chirurgie-ambulatoire",
        "anesthesiste", "anesthesiologie", "reanimation",
        "clinique", "hopital", "polyclinique", "centre-medical",
        "cabinet-medical", "cabinet-groupe", "maison-sante",
        "laboratoire", "analyses", "prise-sang", "biologie",
        "veterinaire", "clinique-veterinaire", "urgences-veterinaires",
        "infirmier", "infirmiere", "soins-domicile", "aide-soignant",
        "ambulance", "transport-medical", "rapatriement",
        
        # ========== SERVICES PROFESSIONNELS (70 termes) ==========
        "avocat", "avocat-affaires", "avocat-famille", "avocat-penal",
        "avocat-travail", "avocat-immobilier", "avocat-fiscal",
        "notaire", "etude-notariale", "acte-notarie",
        "huissier", "huissier-justice", "recouvrement",
        "comptable", "expert-comptable", "fiduciaire", "revision",
        "audit", "auditeur", "controle", "conseil-fiscal",
        "fiscaliste", "declaration-impots", "optimisation-fiscale",
        "consultant", "conseil-entreprise", "conseil-management",
        "coach-professionnel", "coach-entreprise", "executive-coach",
        "formation", "formateur", "centre-formation", "cours-professionnels",
        "traducteur", "traduction", "interprete", "interpretation",
        "secretariat", "assistante", "services-administratifs",
        "centre-affaires", "domiciliation", "bureau-virtuel",
        "coworking", "espace-coworking", "bureau-partage",
        "architecte", "cabinet-architecture", "architecture-interieur",
        "decorateur", "decoration-interieur", "home-staging",
        "geometre", "geometre-expert", "topographie", "bornage",
        "ingenieur", "bureau-etude", "bureau-ingenieur",
        "ingenieur-civil", "genie-civil", "structure",
        "urbaniste", "urbanisme", "amenagement-territoire",
        "paysagiste", "architecte-paysagiste", "jardin",
        "designer", "design", "industrial-design", "product-design",
        "graphiste", "graphisme", "identite-visuelle", "logo",
        "webdesigner", "web-design", "ux-design", "ui-design",
        "photographe", "studio-photo", "photographie",
        "videaste", "production-video", "montage-video",
        "imprimerie", "impression", "offset", "numerique",
        "serigraphie", "impression-textile", "flocage",
        "publicite", "agence-pub", "creation-publicitaire",
        "marketing", "agence-marketing", "digital-marketing",
        "communication", "agence-communication", "relations-presse",
        "relations-publiques", "rp", "media-relations",
        "evenementiel", "agence-evenement", "organisation-evenement",
        "agence-voyage", "tour-operator", "voyagiste",
        
        # ========== FINANCE & IMMOBILIER (50 termes) ==========
        "banque", "etablissement-bancaire", "private-banking",
        "credit", "pret", "financement", "leasing",
        "hypotheque", "pret-hypothecaire", "courtier-hypothecaire",
        "assurance", "courtier-assurance", "agent-assurance",
        "assurance-vie", "assurance-maladie", "assurance-auto",
        "assurance-habitation", "assurance-entreprise", "rc",
        "gestionnaire-fortune", "wealth-management", "asset-management",
        "family-office", "gestion-patrimoine", "conseil-patrimonial",
        "immobilier", "agence-immobiliere", "agent-immobilier",
        "courtier-immobilier", "transaction-immobiliere",
        "syndic", "gerance", "regie", "administration-immeuble",
        "location", "location-appartement", "location-bureau",
        "vente", "vente-immobiliere", "promotion-immobiliere",
        "estimation", "expertise-immobiliere", "evaluation",
        "investissement", "investissement-immobilier", "rendement",
        "placement", "bourse", "trading", "forex",
        "crypto", "bitcoin", "blockchain", "fintech",
        
        # ========== COMMERCE & RETAIL (80 termes) ==========
        "boutique", "magasin", "commerce", "shop", "store",
        "mode", "vetements", "pret-a-porter", "confection",
        "haute-couture", "couturier", "atelier-couture",
        "homme", "femme", "enfant", "bebe", "maternite",
        "accessoires", "foulard", "ceinture", "chapeau", "gants",
        "chaussures", "chausseur", "bottier", "cordonnerie",
        "maroquinerie", "sacs", "valises", "bagages", "cuir",
        "bijouterie", "bijoutier", "joaillerie", "joaillier",
        "horlogerie", "horloger", "montres", "reparation-montres",
        "parfumerie", "parfums", "cosmetiques", "beaute",
        "lingerie", "sous-vetements", "maillots-bain",
        "sport", "articles-sport", "equipement-sportif",
        "outdoor", "camping", "randonnee", "montagne",
        "velo", "cycles", "velo-electrique", "e-bike",
        "ski", "snowboard", "sports-hiver",
        "peche", "chasse", "armurerie", "armes",
        "golf", "tennis", "raquettes",
        "equitation", "sellerie", "equipement-equestre",
        "plongee", "nautisme", "voile", "bateau",
        "electronique", "high-tech", "gadgets",
        "informatique", "ordinateur", "pc", "mac",
        "telephone", "mobile", "smartphone", "tablette",
        "tv", "television", "home-cinema", "hifi", "audio",
        "electromenager", "gros-electromenager", "petit-electromenager",
        "cuisine", "ustensiles", "robot-cuisine", "cookware",
        "meuble", "mobilier", "ameublement", "furniture",
        "canape", "sofa", "fauteuil", "salon",
        "lit", "literie", "matelas", "sommier",
        "armoire", "dressing", "rangement", "placard",
        "bureau", "mobilier-bureau", "chaise-bureau",
        "decoration", "deco", "objets-deco", "art-table",
        "luminaire", "lampe", "lustre", "eclairage",
        "tapis", "moquette", "parquet", "revetement-sol",
        "rideau", "store", "voilage", "textile-maison",
        "linge-maison", "draps", "couette", "oreiller",
        "vaisselle", "porcelaine", "cristal", "argenterie",
        
        # ========== BRICOLAGE & JARDIN (40 termes) ==========
        "bricolage", "quincaillerie", "outillage", "outils",
        "peinture", "vernis", "lasure", "droguerie",
        "papier-peint", "revetement-mural", "decoration-murale",
        "parquet", "stratifie", "lino", "moquette",
        "carrelage", "faience", "carreaux", "mosaique",
        "sanitaire", "robinetterie", "plomberie", "salle-bain",
        "chauffage", "radiateur", "chaudiere", "poele",
        "climatisation", "ventilation", "aeraulique",
        "electricite", "materiel-electrique", "domotique",
        "jardinage", "jardinerie", "pepiniere", "graines",
        "plantes", "fleurs", "arbres", "arbustes",
        "fleuriste", "composition-florale", "bouquet",
        "gazon", "pelouse", "arrosage", "irrigation",
        "piscine", "spa-jardin", "jacuzzi-exterieur",
        "mobilier-jardin", "barbecue", "plancha",
        "cloture", "portail", "grillage", "brise-vue",
        
        # ========== ANIMAUX (20 termes) ==========
        "animalerie", "animaux", "pet-shop",
        "chien", "chat", "rongeur", "lapin",
        "oiseau", "voliere", "perroquet",
        "poisson", "aquarium", "aquariophilie",
        "reptile", "terrarium", "nac",
        "toilettage", "toiletteur", "grooming",
        "pension-animaux", "garde-animaux", "dog-sitter",
        "dressage", "education-canine", "comportementaliste",
        
        # ========== CULTURE & LOISIRS (40 termes) ==========
        "librairie", "livre", "bouquiniste", "bd",
        "papeterie", "fourniture-bureau", "scolaire",
        "jouet", "jeux", "jeux-societe", "puzzle",
        "modelisme", "maquette", "figurine", "collection",
        "musique", "instrument", "guitare", "piano", "batterie",
        "disque", "cd", "vinyle", "vinyl", "platine",
        "art", "galerie-art", "galerie", "exposition",
        "tableau", "peinture", "sculpture", "oeuvre",
        "cadre", "encadrement", "encadreur",
        "antiquaire", "antiquites", "brocante", "vintage",
        "occasion", "depot-vente", "seconde-main", "friperie",
        "loisirs-creatifs", "mercerie", "couture", "tricot",
        "perles", "bijoux-fantaisie", "creation-bijoux",
        
        # ========== AUTOMOBILE (40 termes) ==========
        "garage", "garagiste", "mecanique-auto", "reparation-auto",
        "carrosserie", "carrossier", "debosselage", "peinture-auto",
        "pneu", "pneus", "pneumatique", "jante",
        "vidange", "revision", "entretien-auto",
        "diagnostic", "controle-technique", "expertise-auto",
        "auto", "voiture", "vehicule", "automobile",
        "concessionnaire", "distributeur-auto", "marque-auto",
        "occasion", "voiture-occasion", "vehicule-occasion",
        "location-voiture", "rent-a-car", "location-vehicule",
        "leasing-auto", "financement-auto",
        "moto", "motocycle", "scooter", "deux-roues",
        "quad", "atv", "motoneige",
        "velo", "cycles", "velo-electrique", "e-bike",
        "trottinette", "trottinette-electrique", "mobilite-douce",
        "parking", "garage-parking", "place-parc",
        "lavage-auto", "car-wash", "detailing", "polissage",
        "station-service", "essence", "diesel", "carburant",
        "remorquage", "depannage-auto", "assistance-routiere",
        "auto-ecole", "permis-conduire", "lecons-conduite",
        "taxi", "vtc", "chauffeur-prive", "limousine",
        
        # ========== CONSTRUCTION & RENOVATION (60 termes) ==========
        "construction", "entreprise-generale", "entrepreneur",
        "maconnerie", "macon", "beton", "beton-arme",
        "charpente", "charpentier", "ossature-bois",
        "couverture", "couvreur", "toiture", "toit",
        "facade", "facadier", "ravalement", "crepi",
        "isolation", "isolant", "thermique", "acoustique",
        "etancheite", "etancheur", "impermeabilisation",
        "demolition", "desamiantage", "deconstruction",
        "terrassement", "terrassier", "excavation",
        "fondation", "gros-oeuvre", "structure",
        "second-oeuvre", "finition", "amenagement",
        "menuiserie", "menuisier", "bois", "porte", "fenetre",
        "ebenisterie", "ebeniste", "meuble-sur-mesure",
        "parqueteur", "parquet", "pose-parquet",
        "plombier", "plomberie", "sanitaire", "chauffage",
        "chauffagiste", "installation-chauffage", "pompe-chaleur",
        "climaticien", "climatisation", "ventilation", "vmc",
        "electricien", "electricite", "installation-electrique",
        "domotique", "maison-connectee", "smart-home",
        "alarme", "securite", "videosurveillance", "camera",
        "peintre", "peintre-batiment", "peinture-interieur",
        "tapissier", "papier-peint", "revetement",
        "platrier", "platrerie", "faux-plafond", "cloison",
        "carreleur", "carrelage", "faience", "mosaique",
        "serrurier", "serrurerie", "cle", "porte-blindee",
        "vitrier", "vitrerie", "verre", "miroir", "miroiterie",
        "store", "storiste", "volet", "volet-roulant",
        "pergola", "veranda", "extension", "agrandissement",
        "cuisiniste", "cuisine-equipee", "agencement-cuisine",
        "salle-bain", "sanitaire", "amenagement-sdb",
        "renovation", "transformation", "rehabilitation",
        "demenagement", "demenageur", "transport-meuble",
        "garde-meuble", "self-stockage", "box-stockage",
        "nettoyage", "entreprise-nettoyage", "menage",
        "nettoyage-fin-chantier", "remise-etat",
        "desinsectisation", "deratisation", "nuisibles",
        "ramonage", "ramoneur", "cheminee",
        "debouchage", "curage", "canalisation",
        
        # ========== HOTELLERIE & TOURISME (30 termes) ==========
        "hotel", "hostellerie", "palace", "boutique-hotel",
        "motel", "auberge", "pension", "garni",
        "chambre-hote", "b-and-b", "bed-breakfast",
        "gite", "gite-rural", "chalet", "appartement-vacances",
        "apparthotel", "residence-tourisme", "apart-hotel",
        "camping", "glamping", "mobil-home",
        "hostel", "auberge-jeunesse", "backpacker",
        "refuge", "cabane", "bivouac",
        "tourisme", "office-tourisme", "information-touristique",
        "guide", "guide-touristique", "accompagnateur",
        "excursion", "visite-guidee", "tour",
        "croisiere", "bateau-promenade", "navigation",
        
        # ========== EDUCATION & FORMATION (30 termes) ==========
        "ecole", "etablissement-scolaire", "institution",
        "ecole-privee", "ecole-internationale", "internat",
        "creche", "garderie", "jardin-enfants", "nursery",
        "parascolaire", "accueil-extrascolaire", "uape",
        "soutien-scolaire", "cours-particuliers", "repetiteur",
        "ecole-langue", "cours-langue", "francais", "allemand", "anglais",
        "musique", "conservatoire", "ecole-musique",
        "danse", "ecole-danse", "academie-danse",
        "theatre", "cours-theatre", "art-dramatique",
        "arts", "ecole-art", "beaux-arts",
        "sport", "ecole-sport", "academie-sport",
        
        # ========== TECHNOLOGIE & INFORMATIQUE (40 termes) ==========
        "informatique", "it", "services-informatiques",
        "depannage-informatique", "assistance-informatique",
        "reparation-ordinateur", "reparation-pc", "reparation-mac",
        "data", "data-center", "hebergement-donnees",
        "cloud", "cloud-computing", "saas", "iaas",
        "developpement", "developpeur", "programmation",
        "web", "site-web", "site-internet", "creation-site",
        "application", "app", "developpement-mobile",
        "logiciel", "software", "progiciel", "erp",
        "hardware", "materiel-informatique", "serveur",
        "reseau", "infrastructure", "cablage",
        "securite-informatique", "cybersecurite", "antivirus",
        "telecoms", "telecommunication", "telephonie",
        "fibre", "internet", "connexion", "wifi",
        "mobile", "operateur", "forfait",
        
        # ========== INDUSTRIE & B2B (30 termes) ==========
        "industrie", "industriel", "manufacture",
        "usine", "production", "fabrication",
        "atelier", "atelier-production", "assembly",
        "mecanique-precision", "usinage", "cnc",
        "soudure", "soudage", "assemblage-metallique",
        "metallurgie", "metal", "acier", "aluminium",
        "fonderie", "moulage", "forge",
        "plastique", "injection-plastique", "thermoformage",
        "composite", "fibre-carbone", "fibre-verre",
        "textile", "confection", "couture-industrielle",
        "packaging", "emballage", "conditionnement",
        "logistique", "entrepot", "warehouse",
        "transport", "transporteur", "fret",
        "livraison", "coursier", "express",
        "import-export", "negoce", "trading",
        "grossiste", "distributeur", "fournisseur",
        
        # ========== SERVICES DIVERS (40 termes) ==========
        "pressing", "nettoyage-sec", "teinturerie",
        "laverie", "lavomatic", "blanchisserie",
        "couture", "retouche", "modification",
        "cordonnerie", "cordonnier", "reparation-chaussures",
        "cle-minute", "reproduction-cle", "double-cle",
        "gravure", "graveur", "personnalisation",
        "tampon", "cachet", "timbre",
        "photocopie", "copie", "impression",
        "scan", "numerisation", "archivage",
        "reliure", "brochure", "finition-print",
        "pompes-funebres", "funerarium", "cremation",
        "fleurs-deuil", "couronne", "gerbe",
        "cimetiere", "concession", "monument",
        "securite", "gardiennage", "surveillance",
        "agent-securite", "vigile", "bodyguard",
        "detective", "detective-prive", "enquete",
        "mediation", "arbitrage", "conciliation",
    ]
    
    # Locations to search
    locations = [
        "lausanne",
        "lausanne-1000", "lausanne-1003", "lausanne-1004", "lausanne-1005",
        "lausanne-1006", "lausanne-1007", "lausanne-1010", "lausanne-1012",
        "lausanne-1018", "lausanne-flon", "lausanne-gare", "lausanne-ouchy",
        "pully", "pully-1009", "prilly", "renens", "renens-1020",
        "ecublens", "chavannes", "epalinges", "le-mont-sur-lausanne",
        "crissier", "bussigny", "morges", "morges-1110",
        "lutry", "cully", "vevey", "montreux", "nyon", "rolle",
    ]
    
    total_new = 0
    categories_done = 0
    total_categories = len(search_terms)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            locale='fr-CH',
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        for search_term in search_terms:
            for location in locations:
                try:
                    businesses = await scrape_search(page, search_term, location, existing_keys, max_pages=25)
                    
                    if businesses:
                        inserted = await insert_businesses(db, businesses)
                        total_new += inserted
                        if inserted > 0:
                            logger.info(f"✓ {search_term}/{location}: +{inserted} (Total: {total_new})")
                    
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"✗ {search_term}/{location}: {str(e)[:50]}")
                    continue
                
                if location == "lausanne" and not businesses:
                    break
            
            categories_done += 1
            
            if categories_done % 25 == 0:
                current = await db.enterprises.count_documents({})
                logger.info(f"\n{'='*60}")
                logger.info(f"📊 PROGRESS: {categories_done}/{total_categories} categories ({100*categories_done//total_categories}%)")
                logger.info(f"Total enterprises: {current} (+{total_new} new)")
                logger.info(f"{'='*60}\n")
        
        await browser.close()
    
    final_count = await db.enterprises.count_documents({})
    
    logger.info("=" * 60)
    logger.info("🏁 SCRAPING V6 COMPLETED")
    logger.info(f"Initial: {initial_count}")
    logger.info(f"Final: {final_count}")
    logger.info(f"New added: {total_new}")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
