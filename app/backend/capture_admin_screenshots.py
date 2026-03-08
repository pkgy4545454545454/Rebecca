#!/usr/bin/env python3
"""
Capture TOUS les screenshots du Dashboard Admin/Manager Titelli
Pour les cahiers de charges manager
"""
import os
import time
import requests
from playwright.sync_api import sync_playwright

BASE_URL = 'https://image-fix-demo.preview.emergentagent.com'
SCREENSHOTS_DIR = '/app/backend/uploads/brochure_admin_screenshots'

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def get_admin_token():
    """Récupère le token admin"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@titelli.com", "password": "Admin123456"}
    )
    if response.status_code == 200:
        return response.json().get('token')
    return None

def main():
    print("=" * 70)
    print("   CAPTURE DASHBOARD ADMIN - TOUTES LES SECTIONS")
    print("=" * 70)
    
    # Récupérer le token admin
    token = get_admin_token()
    if not token:
        print("❌ Impossible de se connecter en tant qu'admin")
        return []
    
    print(f"✅ Token admin récupéré: {token[:30]}...")
    
    captured = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1.5
        )
        page = context.new_page()
        
        # Aller sur le site et injecter le token
        page.goto(BASE_URL, wait_until='networkidle', timeout=30000)
        time.sleep(2)
        
        page.evaluate(f"""
            localStorage.setItem('titelli_token', '{token}');
            localStorage.setItem('token', '{token}');
        """)
        
        # Sections du dashboard admin
        admin_sections = [
            ('overview', 'admin_overview', 'Admin - Vue d\'ensemble'),
            ('registrations', 'admin_inscriptions', 'Admin - Inscriptions en attente'),
            ('pub-media', 'admin_pub_media', 'Admin - Pub Média IA'),
            ('algorithms', 'admin_algorithmes', 'Admin - Algorithmes'),
            ('subscriptions', 'admin_abonnements', 'Admin - Abonnements'),
            ('accounting', 'admin_comptabilite', 'Admin - Comptabilité'),
            ('withdrawals', 'admin_retraits', 'Admin - Retraits'),
            ('users', 'admin_utilisateurs', 'Admin - Utilisateurs'),
            ('enterprises', 'admin_entreprises', 'Admin - Entreprises'),
            ('orders', 'admin_commandes', 'Admin - Commandes'),
            ('payments', 'admin_paiements', 'Admin - Paiements'),
            ('settings', 'admin_parametres', 'Admin - Paramètres'),
        ]
        
        for tab_id, screenshot_name, description in admin_sections:
            print(f"\n📸 {description}...")
            try:
                url = f"{BASE_URL}/admin?tab={tab_id}"
                page.goto(url, wait_until='networkidle', timeout=30000)
                time.sleep(3)
                
                # Vérifier si on est bien connecté
                screenshot_path = f'{SCREENSHOTS_DIR}/{screenshot_name}.png'
                page.screenshot(path=screenshot_path, full_page=False)
                captured.append((screenshot_path, screenshot_name, description))
                print(f"   ✅ {screenshot_path}")
                
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
        
        browser.close()
    
    print("\n" + "=" * 70)
    print(f"   {len(captured)} SCREENSHOTS ADMIN CAPTURÉS")
    print("=" * 70)
    
    return captured


if __name__ == "__main__":
    main()
