#!/usr/bin/env python3
"""
Capture améliorée du Dashboard Admin avec clics sur les onglets
"""
import os
import time
import requests
from playwright.sync_api import sync_playwright

BASE_URL = 'https://image-fix-demo.preview.emergentagent.com'
SCREENSHOTS_DIR = '/app/backend/uploads/brochure_admin_screenshots'

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def get_admin_token():
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@titelli.com", "password": "Admin123456"}
    )
    if response.status_code == 200:
        return response.json().get('token')
    return None

def main():
    print("=" * 70)
    print("   CAPTURE DASHBOARD ADMIN V2 - AVEC CLICS")
    print("=" * 70)
    
    token = get_admin_token()
    if not token:
        print("❌ Impossible de se connecter")
        return []
    
    print(f"✅ Token admin: {token[:30]}...")
    
    captured = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1.5
        )
        page = context.new_page()
        
        # Injecter le token et aller sur l'admin
        page.goto(BASE_URL, wait_until='networkidle', timeout=30000)
        time.sleep(2)
        page.evaluate(f"""
            localStorage.setItem('titelli_token', '{token}');
            localStorage.setItem('token', '{token}');
        """)
        
        # Aller sur la page admin
        page.goto(f"{BASE_URL}/admin", wait_until='networkidle', timeout=30000)
        time.sleep(3)
        
        # Capture vue d'ensemble (déjà affichée)
        print("\n📸 Admin - Vue d'ensemble...")
        page.screenshot(path=f'{SCREENSHOTS_DIR}/admin_overview.png', full_page=False)
        captured.append(f'{SCREENSHOTS_DIR}/admin_overview.png')
        print("   ✅ Capturé")
        
        # Liste des onglets à cliquer
        tabs_to_click = [
            ('Inscriptions en attente', 'admin_inscriptions'),
            ('Pub Média IA', 'admin_pub_media'),
            ('Algorithmes', 'admin_algorithmes'),
            ('Abonnements', 'admin_abonnements'),
            ('Comptabilité', 'admin_comptabilite'),
            ('Retraits', 'admin_retraits'),
            ('Utilisateurs', 'admin_utilisateurs'),
            ('Entreprises', 'admin_entreprises'),
            ('Commandes', 'admin_commandes'),
            ('Paiements', 'admin_paiements'),
            ('Paramètres', 'admin_parametres'),
        ]
        
        for tab_label, screenshot_name in tabs_to_click:
            print(f"\n📸 Admin - {tab_label}...")
            try:
                # Cliquer sur l'onglet dans le menu
                tab_button = page.locator(f"text={tab_label}").first
                if tab_button.count() > 0:
                    tab_button.click()
                    time.sleep(2)
                    
                    screenshot_path = f'{SCREENSHOTS_DIR}/{screenshot_name}.png'
                    page.screenshot(path=screenshot_path, full_page=False)
                    captured.append(screenshot_path)
                    print(f"   ✅ Capturé")
                else:
                    print(f"   ⚠️ Onglet non trouvé")
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
        
        browser.close()
    
    print("\n" + "=" * 70)
    print(f"   {len(captured)} SCREENSHOTS CAPTURÉS")
    print("=" * 70)
    
    return captured


if __name__ == "__main__":
    main()
