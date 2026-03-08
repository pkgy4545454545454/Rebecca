#!/usr/bin/env python3
"""
Script OPTIMISÉ de copie de base de données MongoDB
Copie toutes les collections de 'secondevie' vers 'rebecca'
Utilise des insertions en bulk pour plus de rapidité
"""

from pymongo import MongoClient, UpdateOne
from datetime import datetime
import sys

# Connexion MongoDB Atlas
MONGO_URL = "mongodb+srv://prankgy:Minijetaime1996@cluster0.kwjifsg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

SOURCE_DB = "secondevie"
TARGET_DB = "rebecca"
BATCH_SIZE = 500  # Nombre de documents par lot

def copy_database():
    print("=" * 60)
    print("🔄 COPIE OPTIMISÉE DE BASE DE DONNÉES MONGODB")
    print("=" * 60)
    print(f"📤 Source: {SOURCE_DB}")
    print(f"📥 Destination: {TARGET_DB}")
    print(f"🕐 Début: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        client = MongoClient(MONGO_URL)
        client.admin.command('ping')
        print("✅ Connexion réussie!")
        
        source_db = client[SOURCE_DB]
        target_db = client[TARGET_DB]
        
        collections = source_db.list_collection_names()
        print(f"\n📋 {len(collections)} collections à copier\n")
        
        total_copied = 0
        
        for collection_name in collections:
            source_col = source_db[collection_name]
            target_col = target_db[collection_name]
            
            count = source_col.count_documents({})
            print(f"📁 {collection_name} ({count} docs)...", end=" ", flush=True)
            
            if count == 0:
                print("⚪ vide")
                continue
            
            # Récupérer tous les documents
            docs = list(source_col.find({}))
            
            # Préparer les opérations bulk
            operations = []
            for doc in docs:
                if 'id' in doc:
                    operations.append(
                        UpdateOne({'id': doc['id']}, {'$set': doc}, upsert=True)
                    )
                elif '_id' in doc:
                    operations.append(
                        UpdateOne({'_id': doc['_id']}, {'$set': doc}, upsert=True)
                    )
            
            # Exécuter en bulk par lots
            if operations:
                for i in range(0, len(operations), BATCH_SIZE):
                    batch = operations[i:i + BATCH_SIZE]
                    target_col.bulk_write(batch, ordered=False)
                
                total_copied += len(docs)
                print(f"✅ {len(docs)}")
            else:
                print("⚠️ pas d'id")
        
        print("\n" + "=" * 60)
        print("✅ COPIE TERMINÉE!")
        print("=" * 60)
        print(f"📊 Total: {total_copied} documents copiés")
        print(f"🕐 Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Vérification rapide
        print(f"\n🔍 Vérification de '{TARGET_DB}':")
        for col in ['users', 'enterprises', 'services_products', 'orders']:
            if col in target_db.list_collection_names():
                c = target_db[col].count_documents({})
                print(f"   • {col}: {c} documents")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🛡️  SCRIPT DE SAUVEGARDE OPTIMISÉ\n")
    success = copy_database()
    
    if success:
        print("\n💡 Backup terminé dans la BDD 'rebecca'")
    
    sys.exit(0 if success else 1)
