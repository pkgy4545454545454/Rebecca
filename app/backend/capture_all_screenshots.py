#!/usr/bin/env python3
"""
Capture tous les screenshots du site Titelli pour la brochure
"""
import os
import time
from playwright.sync_api import sync_playwright

BASE_URL = 'https://image-fix-demo.preview.emergentagent.com'
SCREENSHOTS_DIR = '/app/backend/uploads/brochure_screenshots'

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def capture_page(page, url_path, name, description, scroll=False, full_page=True):
    """Capture une page avec description"""
    url = f"{BASE_URL}{url_path}"
    print(f"\n📸 {description}...")
    
    try:
        page.goto(url, wait_until='networkidle', timeout=30000)
        time.sleep(2)
        
        if scroll:
            # Scroll pour charger tout le contenu
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(1)
        
        screenshot_path = f'{SCREENSHOTS_DIR}/{name}.png'
        page.screenshot(path=screenshot_path, full_page=full_page)
        print(f"   ✅ {screenshot_path}")
        return screenshot_path
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None


def main():
    print("=" * 70)
    print("   CAPTURE SCREENSHOTS TITELLI - BROCHURE")
    print("=" * 70)
    
    captured = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1.5
        )
        page = context.new_page()
        
        # Liste des pages à capturer
        pages_to_capture = [
            # Page d'accueil
            ('/', 'home_hero', 'Page d\'accueil - Hero', False, False),
            ('/', 'home_full', 'Page d\'accueil complète', True, True),
            
            # Prestataires
            ('/prestataires', 'prestataires_list', 'Liste des prestataires', True, True),
            
            # Boutiques
            ('/boutiques', 'boutiques_list', 'Liste des boutiques', True, True),
            
            # Connexion
            ('/auth/login', 'login_page', 'Page de connexion', False, False),
            
            # Inscription
            ('/auth/register', 'register_page', 'Page d\'inscription', False, False),
            
            # Abonnements
            ('/abonnements', 'abonnements', 'Page abonnements', True, True),
            
            # Contact
            ('/contact', 'contact', 'Page contact', False, True),
        ]
        
        for url_path, name, desc, scroll, full_page in pages_to_capture:
            result = capture_page(page, url_path, name, desc, scroll, full_page)
            if result:
                captured.append((result, name, desc))
        
        # Essayer de se connecter pour capturer le dashboard
        print("\n🔐 Tentative de connexion pour capturer le dashboard...")
        try:
            page.goto(f"{BASE_URL}/auth/login", wait_until='networkidle', timeout=30000)
            time.sleep(2)
            
            # Chercher les champs de connexion
            email_input = page.locator('input[type="email"], input[name="email"]').first
            password_input = page.locator('input[type="password"]').first
            
            if email_input and password_input:
                email_input.fill('demo@titelli.com')
                password_input.fill('demo123')
                
                submit_btn = page.locator('button[type="submit"]').first
                if submit_btn:
                    submit_btn.click()
                    time.sleep(3)
                    
                    # Capturer les pages après connexion
                    dashboard_pages = [
                        ('/dashboard', 'dashboard', 'Dashboard principal'),
                        ('/dashboard/profile', 'profile', 'Profil utilisateur'),
                        ('/dashboard/documents', 'documents', 'Documents'),
                        ('/dashboard/abonnement', 'mon_abonnement', 'Mon abonnement'),
                        ('/dashboard/produits', 'produits', 'Mes produits'),
                        ('/dashboard/services', 'services', 'Mes services'),
                        ('/dashboard/horaires', 'horaires', 'Horaires'),
                        ('/dashboard/statistiques', 'statistiques', 'Statistiques'),
                    ]
                    
                    for url_path, name, desc in dashboard_pages:
                        result = capture_page(page, url_path, name, desc, True, True)
                        if result:
                            captured.append((result, name, desc))
        except Exception as e:
            print(f"   ❌ Erreur connexion: {e}")
        
        browser.close()
    
    print("\n" + "=" * 70)
    print(f"   {len(captured)} SCREENSHOTS CAPTURÉS")
    print("=" * 70)
    for path, name, desc in captured:
        print(f"   - {name}: {desc}")
    
    return captured


if __name__ == "__main__":
    main()
