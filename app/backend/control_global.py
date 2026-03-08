#!/usr/bin/env python3
"""
CONTRÔLE GLOBAL - Audit complet de l'application Titelli
"""
import asyncio
import os
import httpx
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'secondevie')
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://image-fix-demo.preview.emergentagent.com')


async def check_api_endpoints():
    """Test main API endpoints"""
    print("\n" + "=" * 60)
    print("   1. TEST DES ENDPOINTS API")
    print("=" * 60)
    
    endpoints = [
        ('GET', '/api/health', 'Health Check'),
        ('GET', '/api/enterprises?limit=5', 'Liste Entreprises'),
        ('GET', '/api/products?limit=5', 'Liste Produits'),
        ('GET', '/api/media-pub/templates', 'Templates Pub Média'),
        ('GET', '/api/video-pub/templates', 'Templates Vidéo Pub'),
    ]
    
    results = []
    async with httpx.AsyncClient(timeout=30) as client:
        for method, endpoint, name in endpoints:
            try:
                url = f"{BASE_URL}{endpoint}"
                if method == 'GET':
                    r = await client.get(url)
                else:
                    r = await client.post(url)
                
                status = "✅" if r.status_code == 200 else "❌"
                results.append((name, status, r.status_code))
                print(f"  {status} {name}: {r.status_code}")
            except Exception as e:
                results.append((name, "❌", str(e)[:30]))
                print(f"  ❌ {name}: {str(e)[:30]}")
    
    return results


async def check_database_stats():
    """Get database statistics"""
    print("\n" + "=" * 60)
    print("   2. STATISTIQUES BASE DE DONNÉES")
    print("=" * 60)
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    stats = {}
    
    # Enterprises
    stats['enterprises_total'] = await db.enterprises.count_documents({})
    stats['enterprises_with_cover'] = await db.enterprises.count_documents({'cover_image': {'$regex': 'uploads/enterprises'}})
    stats['enterprises_with_logo'] = await db.enterprises.count_documents({'logo': {'$regex': 'uploads/enterprises'}})
    stats['enterprises_with_website'] = await db.enterprises.count_documents({'website': {'$exists': True, '$ne': None, '$ne': ''}})
    stats['enterprises_certified'] = await db.enterprises.count_documents({'is_certified': True})
    stats['enterprises_labeled'] = await db.enterprises.count_documents({'is_labeled': True})
    stats['enterprises_premium'] = await db.enterprises.count_documents({'is_premium': True})
    
    # Users
    stats['users_total'] = await db.users.count_documents({})
    stats['users_clients'] = await db.users.count_documents({'role': 'client'})
    stats['users_enterprises'] = await db.users.count_documents({'role': 'enterprise'})
    stats['users_admin'] = await db.users.count_documents({'role': 'admin'})
    
    # Products/Services
    stats['products_total'] = await db.services_products.count_documents({})
    stats['products_with_price'] = await db.services_products.count_documents({'price': {'$gt': 0}})
    stats['products_type_product'] = await db.services_products.count_documents({'type': 'product'})
    stats['products_type_service'] = await db.services_products.count_documents({'type': 'service'})
    
    # Orders
    stats['pub_orders'] = await db.pub_orders.count_documents({})
    stats['video_orders'] = await db.video_orders.count_documents({})
    
    # Reviews
    stats['reviews'] = await db.reviews.count_documents({})
    
    # Reservations
    stats['reservations'] = await db.reservations.count_documents({})
    
    print(f"""
  ENTREPRISES:
    Total: {stats['enterprises_total']}
    Avec cover réel: {stats['enterprises_with_cover']}
    Avec logo réel: {stats['enterprises_with_logo']}
    Avec site web: {stats['enterprises_with_website']}
    Certifiées: {stats['enterprises_certified']}
    Labellisées: {stats['enterprises_labeled']}
    Premium: {stats['enterprises_premium']}
    
  UTILISATEURS:
    Total: {stats['users_total']}
    Clients: {stats['users_clients']}
    Entreprises: {stats['users_enterprises']}
    Admins: {stats['users_admin']}
    
  PRODUITS/SERVICES:
    Total: {stats['products_total']}
    Avec prix: {stats['products_with_price']}
    Type produit: {stats['products_type_product']}
    Type service: {stats['products_type_service']}
    
  COMMANDES:
    Pub Média: {stats['pub_orders']}
    Vidéo Pub: {stats['video_orders']}
    
  AUTRES:
    Avis: {stats['reviews']}
    Réservations: {stats['reservations']}
""")
    
    client.close()
    return stats


async def check_file_uploads():
    """Check uploaded files"""
    print("\n" + "=" * 60)
    print("   3. FICHIERS UPLOADÉS")
    print("=" * 60)
    
    upload_dirs = [
        '/app/backend/uploads/enterprises',
        '/app/backend/uploads/pub_orders',
        '/app/backend/uploads/video_orders',
        '/app/backend/uploads/documents',
    ]
    
    for dir_path in upload_dirs:
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            total_size = sum(os.path.getsize(os.path.join(dir_path, f)) for f in files if os.path.isfile(os.path.join(dir_path, f)))
            print(f"  📁 {dir_path.split('/')[-1]}: {len(files)} fichiers ({total_size // 1024 // 1024} MB)")
        else:
            print(f"  ⚠️ {dir_path.split('/')[-1]}: dossier inexistant")


async def check_broken_data():
    """Check for broken/invalid data"""
    print("\n" + "=" * 60)
    print("   4. DONNÉES INVALIDES")
    print("=" * 60)
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Check for broken image URLs (old domain)
    broken_covers = await db.enterprises.count_documents({'cover_image': {'$regex': 'enterprise-media.preview'}})
    broken_logos = await db.enterprises.count_documents({'logo': {'$regex': 'enterprise-media.preview'}})
    
    # Products without price
    products_no_price = await db.services_products.count_documents({'price': 0})
    
    # Enterprises without description
    no_description = await db.enterprises.count_documents({'$or': [{'description': None}, {'description': ''}]})
    
    print(f"""
  ⚠️ Covers cassés (ancien domaine): {broken_covers}
  ⚠️ Logos cassés (ancien domaine): {broken_logos}
  ⚠️ Produits sans prix: {products_no_price}
  ⚠️ Entreprises sans description: {no_description}
""")
    
    client.close()
    
    return {
        'broken_covers': broken_covers,
        'broken_logos': broken_logos,
        'products_no_price': products_no_price,
        'no_description': no_description
    }


async def generate_report():
    """Generate full audit report"""
    print("\n" + "=" * 60)
    print("   CONTRÔLE GLOBAL TITELLI")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Run all checks
    api_results = await check_api_endpoints()
    db_stats = await check_database_stats()
    await check_file_uploads()
    broken_data = await check_broken_data()
    
    # Summary
    print("\n" + "=" * 60)
    print("   5. RÉSUMÉ")
    print("=" * 60)
    
    api_ok = sum(1 for _, status, _ in api_results if status == "✅")
    api_total = len(api_results)
    
    print(f"""
  ✅ APIs fonctionnelles: {api_ok}/{api_total}
  ✅ Entreprises totales: {db_stats['enterprises_total']}
  ✅ Profils complets (cover+logo): {min(db_stats['enterprises_with_cover'], db_stats['enterprises_with_logo'])}
  ✅ Produits avec prix: {db_stats['products_with_price']}
  
  ⚠️ À corriger:
     - Données cassées: {broken_data['broken_covers'] + broken_data['broken_logos']}
     - Produits sans prix: {broken_data['products_no_price']}
""")
    
    print("=" * 60)
    print("   FIN DU CONTRÔLE")
    print("=" * 60)


if __name__ == '__main__':
    asyncio.run(generate_report())
