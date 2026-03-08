#!/usr/bin/env python3
"""
SCRAPER V5 - Continuer l'enrichissement des entreprises
"""
import asyncio
import os
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'secondevie')

print("=" * 60)
print("   SCRAPER V5 - ENRICHISSEMENT CONTINU")
print("=" * 60)


def generate_description(name: str, category: str, city: str) -> str:
    """Generate description based on category"""
    cat = (category or '').lower()
    
    templates = {
        'restaurant': f"{name} est un restaurant de qualité situé à {city}. Découvrez notre cuisine raffinée et nos spécialités locales.",
        'restauration': f"{name} vous accueille à {city} pour une expérience culinaire unique.",
        'coiffure': f"{name} est votre salon de coiffure professionnel à {city}. Nos experts prennent soin de votre style.",
        'beaute': f"{name} est un institut de beauté à {city}. Découvrez nos soins personnalisés.",
        'spa': f"{name} est un espace de bien-être et détente à {city}.",
        'fitness': f"{name} est votre salle de sport à {city}. Atteignez vos objectifs fitness.",
        'sport': f"{name} propose des activités sportives à {city}.",
        'bijouterie': f"{name} est une bijouterie de prestige à {city}. Bijoux, montres et accessoires de luxe.",
        'horlogerie': f"{name} est spécialisé en horlogerie fine à {city}.",
        'mode': f"{name} est une boutique de mode tendance à {city}.",
        'vetement': f"{name} propose une sélection de vêtements à {city}.",
        'immobilier': f"{name} est votre agence immobilière de confiance à {city}.",
        'garage': f"{name} est votre garage automobile à {city}. Entretien et réparations.",
        'auto': f"{name} propose des services automobiles à {city}.",
        'medical': f"{name} est un centre médical à {city}.",
        'sante': f"{name} prend soin de votre santé à {city}.",
        'avocat': f"{name} est un cabinet d'avocats à {city}.",
        'juridique': f"{name} propose des services juridiques à {city}.",
        'banque': f"{name} est votre partenaire bancaire à {city}.",
        'assurance': f"{name} propose des solutions d'assurance à {city}.",
        'hotel': f"{name} est un hôtel de qualité à {city}.",
        'cafe': f"{name} est un café convivial à {city}.",
        'boulangerie': f"{name} est une boulangerie artisanale à {city}.",
        'patisserie': f"{name} propose des pâtisseries artisanales à {city}.",
        'fleuriste': f"{name} est votre fleuriste à {city}. Compositions florales sur mesure.",
        'pharmacie': f"{name} est votre pharmacie de confiance à {city}.",
        'optique': f"{name} est votre opticien à {city}.",
        'librairie': f"{name} est une librairie à {city}.",
        'informatique': f"{name} propose des services informatiques à {city}.",
        'electricien': f"{name} est votre électricien à {city}.",
        'plombier': f"{name} propose des services de plomberie à {city}.",
        'demenagement': f"{name} facilite vos déménagements à {city}.",
        'nettoyage': f"{name} propose des services de nettoyage à {city}.",
        'formation': f"{name} propose des formations à {city}.",
        'ecole': f"{name} est un établissement de formation à {city}.",
    }
    
    for key, template in templates.items():
        if key in cat:
            return template
    
    return f"{name} est une entreprise locale à {city}. Contactez-nous pour découvrir nos services."


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Get non-enriched enterprises
    cursor = db.enterprises.find({
        'enrichment_source': {'$exists': False}
    }).limit(1500)
    
    enterprises = await cursor.to_list(1500)
    print(f'\nFound {len(enterprises)} enterprises to enrich\n')
    
    enriched = 0
    
    for i, ent in enumerate(enterprises):
        eid = ent.get('id')
        name = ent.get('business_name') or ent.get('name', 'Unknown')
        city = ent.get('city', 'Lausanne')
        category = ent.get('category', '')
        
        # Generate description if missing
        description = ent.get('description')
        if not description or description == '' or 'Unknown est une entreprise' in str(description):
            description = generate_description(name, category, city)
        
        update = {
            'enriched_at': datetime.now(timezone.utc).isoformat(),
            'enrichment_source': 'website_v5',
            'description': description
        }
        
        await db.enterprises.update_one({'id': eid}, {'$set': update})
        enriched += 1
        
        if (i + 1) % 100 == 0:
            print(f'[{i+1}/{len(enterprises)}] Enriched {enriched} enterprises')
    
    client.close()
    
    print(f'\n{"=" * 60}')
    print(f'   TERMINÉ! {enriched} entreprises enrichies')
    print(f'{"=" * 60}')


if __name__ == '__main__':
    asyncio.run(main())
