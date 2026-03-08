#!/usr/bin/env python3
"""
Script de copie de base de données MongoDB
Copie toutes les collections de 'secondevie' vers 'rebecca'
Ne modifie RIEN sur le site - script indépendant
"""

from pymongo import MongoClient
from datetime import datetime
import sys

# Connexion MongoDB Atlas (même cluster, différentes BDD)
MONGO_URL = "mongodb+srv://prankgy:Minijetaime1996@cluster0.kwjifsg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

SOURCE_DB = "secondevie"
TARGET_DB = "rebecca"

def copy_database():
    print("=" * 60)
    print("🔄 COPIE DE BASE DE DONNÉES MONGODB")
    print("=" * 60)
    print(f"📤 Source: {SOURCE_DB}")
    print(f"📥 Destination: {TARGET_DB}")
    print(f"🕐 Début: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print("")
    
    try:
        # Connexion au cluster
        print("🔌 Connexion au cluster MongoDB Atlas...")
        client = MongoClient(MONGO_URL)
        
        # Test de connexion
        client.admin.command('ping')
        print("✅ Connexion réussie!")
        print("")
        
        # Bases de données
        source_db = client[SOURCE_DB]
        target_db = client[TARGET_DB]
        
        # Lister toutes les collections de la source
        collections = source_db.list_collection_names()
        print(f"📋 Collections trouvées dans '{SOURCE_DB}': {len(collections)}")
        for col in collections:
            count = source_db[col].count_documents({})
            print(f"   • {col}: {count} documents")
        print("")
        
        # Confirmation
        print("⚠️  ATTENTION: Cette opération va copier toutes les données.")
        print(f"   Les données existantes dans '{TARGET_DB}' seront CONSERVÉES.")
        print("   Les nouvelles données seront AJOUTÉES (pas de suppression).")
        print("")
        
        total_copied = 0
        
        # Copier chaque collection
        for collection_name in collections:
            print(f"📁 Copie de '{collection_name}'...")
            
            source_collection = source_db[collection_name]
            target_collection = target_db[collection_name]
            
            # Récupérer tous les documents
            documents = list(source_collection.find({}))
            
            if documents:
                # Supprimer les _id pour éviter les doublons si on relance le script
                # On va plutôt faire un upsert basé sur 'id' si présent
                
                copied_count = 0
                for doc in documents:
                    # Si le document a un champ 'id', on fait un upsert
                    if 'id' in doc:
                        target_collection.update_one(
                            {'id': doc['id']},
                            {'$set': doc},
                            upsert=True
                        )
                    else:
                        # Sinon on insère directement (peut créer des doublons si relancé)
                        try:
                            target_collection.insert_one(doc)
                        except Exception as e:
                            # Document déjà existant (même _id)
                            pass
                    copied_count += 1
                
                total_copied += copied_count
                print(f"   ✅ {copied_count} documents copiés/mis à jour")
            else:
                print(f"   ⚪ Collection vide, rien à copier")
        
        print("")
        print("=" * 60)
        print("✅ COPIE TERMINÉE AVEC SUCCÈS!")
        print("=" * 60)
        print(f"📊 Total: {total_copied} documents copiés")
        print(f"🕐 Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("")
        
        # Vérification
        print("🔍 VÉRIFICATION DE LA COPIE:")
        print("-" * 40)
        target_collections = target_db.list_collection_names()
        for col in target_collections:
            count = target_db[col].count_documents({})
            print(f"   • {col}: {count} documents")
        
        print("")
        print(f"✅ Base de données '{TARGET_DB}' prête!")
        print(f"   Vous pouvez maintenant utiliser cette BDD comme backup.")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        return False


if __name__ == "__main__":
    print("")
    print("🛡️  SCRIPT DE SAUVEGARDE - NE MODIFIE PAS LE SITE")
    print("")
    
    success = copy_database()
    
    if success:
        print("")
        print("=" * 60)
        print("💡 POUR UTILISER CETTE COPIE PLUS TARD:")
        print("   Changez DB_NAME='rebecca' dans backend/.env")
        print("=" * 60)
    
    sys.exit(0 if success else 1)
