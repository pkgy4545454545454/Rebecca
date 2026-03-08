#!/usr/bin/env python3
"""
Capture TOUS les screenshots du Dashboard Client Titelli
Pour la brochure client
"""
import os
import time
from playwright.sync_api import sync_playwright

BASE_URL = 'https://image-fix-demo.preview.emergentagent.com'
SCREENSHOTS_DIR = '/app/backend/uploads/brochure_client_screenshots'
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjEyYzFhZWItODk4NS00M2I3LThmYmMtODdlZjEzZjgzMWIzIiwidXNlcl90eXBlIjoiY2xpZW50IiwiZXhwIjoxNzcxMjkwNzExLjg0ODUwMn0.B82f5Fq-IuTQgOd4Fx5jF_vN_45Z7MFoc7guMh7cMQw"

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def main():
    print("=" * 70)
    print("   CAPTURE DASHBOARD CLIENT - TOUTES LES SECTIONS")
    print("=" * 70)
    
    captured = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1.5
        )
        page = context.new_page()
        
        # Injecter le token
        page.goto(BASE_URL, wait_until='networkidle', timeout=30000)
        time.sleep(2)
        page.evaluate(f"""
            localStorage.setItem('titelli_token', '{TOKEN}');
            localStorage.setItem('token', '{TOKEN}');
        """)
        
        # ================== PAGES PUBLIQUES CÔTÉ CLIENT ==================
        print("\n" + "="*50)
        print("PAGES PUBLIQUES")
        print("="*50)
        
        public_pages = [
            ('/', 'accueil', 'Page d\'accueil'),
            ('/services', 'services', 'Liste des services'),
            ('/produits', 'produits', 'Liste des produits'),
            ('/entreprises', 'entreprises', 'Liste des entreprises'),
            ('/auth', 'connexion', 'Connexion/Inscription'),
            ('/rdv', 'rdv', 'RDV Titelli'),
            ('/cart', 'panier_page', 'Page panier'),
        ]
        
        for url_path, name, desc in public_pages:
            print(f"\n📸 {desc}...")
            try:
                page.goto(f"{BASE_URL}{url_path}", wait_until='networkidle', timeout=30000)
                time.sleep(2)
                screenshot_path = f'{SCREENSHOTS_DIR}/{name}.png'
                page.screenshot(path=screenshot_path, full_page=False)
                captured.append((screenshot_path, name, desc))
                print(f"   ✅ {screenshot_path}")
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
        
        # ================== DASHBOARD CLIENT ==================
        print("\n" + "="*50)
        print("DASHBOARD CLIENT - TOUTES SECTIONS")
        print("="*50)
        
        client_sections = [
            # Principal
            ('overview', 'client_accueil', 'Dashboard Client - Accueil'),
            ('profile', 'client_profil', 'Dashboard Client - Mon Profil'),
            ('mode_vie', 'client_mode_vie', 'Dashboard Client - Mon mode de vie'),
            ('feed', 'client_fil_actu', 'Dashboard Client - Mon fil d\'actualité'),
            ('my_feed', 'client_mon_feed', 'Dashboard Client - Mon feed'),
            
            # Avantages
            ('cashback', 'client_cashback', 'Dashboard Client - Mon Cash-back'),
            ('parrainage', 'client_parrainage', 'Dashboard Client - Parrainage'),
            ('premium', 'client_premium', 'Dashboard Client - Mon Premium'),
            ('invitations', 'client_invitations', 'Dashboard Client - Mes invitations'),
            ('offres', 'client_offres', 'Dashboard Client - Mes offres du moment'),
            ('guests', 'client_guests', 'Dashboard Client - Mes guests'),
            ('tendances', 'client_tendances', 'Dashboard Client - Mes tendances'),
            
            # Investissements & Emplois
            ('investments', 'client_investissements', 'Dashboard Client - Mes investissements'),
            ('formations', 'client_formations', 'Dashboard Client - Mes formations'),
            
            # Gestion
            ('agenda', 'client_agenda', 'Dashboard Client - Mon agenda'),
            ('cartes', 'client_cartes', 'Dashboard Client - Mes cartes'),
            ('finances', 'client_finances', 'Dashboard Client - Mes finances'),
            ('donations', 'client_donations', 'Dashboard Client - Mes donations'),
            ('documents', 'client_documents', 'Dashboard Client - Mes documents'),
            
            # Communication
            ('messages', 'client_messages', 'Dashboard Client - Messagerie'),
            ('contacts', 'client_contacts', 'Dashboard Client - Contacts & Amis'),
            ('demandes', 'client_demandes', 'Dashboard Client - Demandes en cours'),
            
            # Recommandations
            ('suggestions', 'client_suggestions', 'Dashboard Client - Suggestions'),
            ('prestataires', 'client_prestataires', 'Dashboard Client - Mes prestataires'),
            ('wishlist', 'client_wishlist', 'Dashboard Client - Ma liste de souhaits'),
            
            # Commandes
            ('orders', 'client_commandes', 'Dashboard Client - Mes commandes'),
            ('panier', 'client_panier', 'Dashboard Client - Mon panier'),
            
            # Aide
            ('support', 'client_support', 'Dashboard Client - Service client'),
            ('settings', 'client_parametres', 'Dashboard Client - Paramètres'),
        ]
        
        for tab_id, screenshot_name, description in client_sections:
            print(f"\n📸 {description}...")
            try:
                url = f"{BASE_URL}/dashboard/client?tab={tab_id}"
                page.goto(url, wait_until='networkidle', timeout=30000)
                time.sleep(2)
                
                screenshot_path = f'{SCREENSHOTS_DIR}/{screenshot_name}.png'
                page.screenshot(path=screenshot_path, full_page=False)
                captured.append((screenshot_path, screenshot_name, description))
                print(f"   ✅ {screenshot_path}")
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
        
        browser.close()
    
    print("\n" + "=" * 70)
    print(f"   {len(captured)} SCREENSHOTS CLIENT CAPTURÉS")
    print("=" * 70)
    
    return captured


if __name__ == "__main__":
    main()
