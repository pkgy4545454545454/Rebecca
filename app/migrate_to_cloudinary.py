#!/usr/bin/env python3
"""
Script de migration des images vers Cloudinary
Migre toutes les images locales vers Cloudinary et met à jour les URLs en base de données
"""

import cloudinary
import cloudinary.uploader
from pymongo import MongoClient
import os
import requests
from pathlib import Path
import time

# Configuration Cloudinary
cloudinary.config(
    cloud_name="drsdfxvqp",
    api_key="454545949432688",
    api_secret="qBt8PnOkH8PA0Dk76TPU6eIkzBM",
    secure=True
)

# Configuration MongoDB
MONGO_URL = "mongodb+srv://prankgy:Minijetaime1996@cluster0.kwjifsg.mongodb.net/secondevie?retryWrites=true&w=majority&appName=Cluster0"
EMERGENT_BASE_URL = "https://image-fix-demo.preview.emergentagent.com"
LOCAL_UPLOADS_DIR = "/app/backend/uploads"

def upload_to_cloudinary(image_url, folder="titelli"):
    """Upload une image vers Cloudinary et retourne l'URL"""
    try:
        # Si c'est une URL Emergent, télécharger d'abord
        if image_url.startswith("https://"):
            result = cloudinary.uploader.upload(
                image_url,
                folder=folder,
                resource_type="auto",
                timeout=60
            )
        # Si c'est un chemin local
        elif os.path.exists(image_url):
            result = cloudinary.uploader.upload(
                image_url,
                folder=folder,
                resource_type="auto",
                timeout=60
            )
        else:
            return None
            
        return result.get("secure_url")
    except Exception as e:
        print(f"  ⚠ Erreur upload: {str(e)[:50]}")
        return None

def migrate_enterprises():
    """Migre les logos et images des entreprises"""
    client = MongoClient(MONGO_URL)
    db = client["secondevie"]
    
    print("\n" + "="*60)
    print("MIGRATION DES IMAGES VERS CLOUDINARY")
    print("="*60)
    
    # 1. Migrer les logos
    print("\n📦 Migration des logos entreprises...")
    logo_success = 0
    logo_failed = 0
    
    enterprises_with_logo = list(db.enterprises.find({
        "logo": {"$exists": True, "$ne": "", "$ne": None}
    }))
    
    total = len(enterprises_with_logo)
    print(f"   {total} logos à migrer")
    
    for i, enterprise in enumerate(enterprises_with_logo):
        logo_url = enterprise.get("logo", "")
        name = enterprise.get("business_name", enterprise.get("name", "?"))[:30]
        
        # Skip si déjà sur Cloudinary
        if "cloudinary.com" in logo_url:
            continue
            
        # Upload vers Cloudinary
        new_url = upload_to_cloudinary(logo_url, folder="titelli/logos")
        
        if new_url:
            db.enterprises.update_one(
                {"_id": enterprise["_id"]},
                {"$set": {"logo": new_url}}
            )
            logo_success += 1
            if (i + 1) % 20 == 0:
                print(f"   ✓ {i+1}/{total} logos migrés...")
        else:
            logo_failed += 1
        
        # Pause pour éviter le rate limiting
        if (i + 1) % 50 == 0:
            time.sleep(1)
    
    print(f"   ✓ Logos: {logo_success} migrés, {logo_failed} échecs")
    
    # 2. Migrer les cover images
    print("\n📦 Migration des cover images...")
    cover_success = 0
    cover_failed = 0
    
    enterprises_with_cover = list(db.enterprises.find({
        "cover_image": {"$exists": True, "$ne": "", "$ne": None, "$not": {"$regex": "cloudinary.com"}}
    }).limit(500))  # Limiter pour éviter timeout
    
    total = len(enterprises_with_cover)
    print(f"   {total} cover images à migrer")
    
    for i, enterprise in enumerate(enterprises_with_cover):
        cover_url = enterprise.get("cover_image", "")
        
        if "cloudinary.com" in cover_url:
            continue
            
        new_url = upload_to_cloudinary(cover_url, folder="titelli/covers")
        
        if new_url:
            db.enterprises.update_one(
                {"_id": enterprise["_id"]},
                {"$set": {"cover_image": new_url}}
            )
            cover_success += 1
            if (i + 1) % 20 == 0:
                print(f"   ✓ {i+1}/{total} covers migrés...")
        else:
            cover_failed += 1
            
        if (i + 1) % 50 == 0:
            time.sleep(1)
    
    print(f"   ✓ Covers: {cover_success} migrés, {cover_failed} échecs")
    
    client.close()
    
    print("\n" + "="*60)
    print("MIGRATION TERMINÉE!")
    print("="*60)
    print(f"Logos: {logo_success} migrés")
    print(f"Covers: {cover_success} migrés")
    
    return logo_success, cover_success

if __name__ == "__main__":
    migrate_enterprises()
