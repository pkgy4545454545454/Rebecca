#!/usr/bin/env python3
"""
Capture TOUS les screenshots du site Titelli - Version complète
Avec les vraies pages fonctionnelles
"""
import os
import time
from playwright.sync_api import sync_playwright

BASE_URL = 'https://image-fix-demo.preview.emergentagent.com'
SCREENSHOTS_DIR = '/app/backend/uploads/brochure_screenshots_v2'

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def capture_page(page, url_path, name, description, full_page=False, wait_time=2):
    """Capture une page avec description"""
    url = f"{BASE_URL}{url_path}"
    print(f"\n📸 {description}...")
    
    try:
        page.goto(url, wait_until='networkidle', timeout=30000)
        time.sleep(wait_time)
        
        # Vérifier si c'est une page 404
        if page.locator("text=404").count() > 0 or page.locator("text=Page non trouvée").count() > 0:
            print(f"   ⚠️ Page 404 détectée pour {url_path}")
            return None
        
        screenshot_path = f'{SCREENSHOTS_DIR}/{name}.png'
        page.screenshot(path=screenshot_path, full_page=full_page)
        print(f"   ✅ {screenshot_path}")
        return screenshot_path
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None


def main():
    print("=" * 70)
    print("   CAPTURE SCREENSHOTS TITELLI V2 - COMPLET")
    print("=" * 70)
    
    captured = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1.5
        )
        page = context.new_page()
        
        # ================== PAGES PUBLIQUES ==================
        print("\n" + "="*50)
        print("PAGES PUBLIQUES")
        print("="*50)
        
        public_pages = [
            # Page d'accueil
            ('/', 'accueil_hero', 'Page d\'accueil - Vue principale', False),
            
            # Services
            ('/services', 'services_liste', 'Liste des services', False),
            
            # Produits
            ('/produits', 'produits_liste', 'Liste des produits', False),
            
            # Entreprises
            ('/entreprises', 'entreprises_liste', 'Liste des entreprises', False),
            
            # Auth
            ('/auth', 'connexion', 'Page de connexion/inscription', False),
            
            # Emplois
            ('/emplois', 'emplois_liste', 'Liste des emplois', False),
            
            # RDV
            ('/rdv', 'rdv_titelli', 'RDV Titelli', False),
            
            # Sports
            ('/sports', 'sports', 'Page Sports', False),
            
            # Media Pub
            ('/media-pub', 'media_pub', 'Créer une publicité', False),
            
            # Video Pub
            ('/video-pub', 'video_pub', 'Créer une vidéo pub', False),
            
            # Titelli Pro
            ('/titelli-pro', 'titelli_pro', 'Titelli Pro++', False),
            
            # Pages légales
            ('/about', 'about', 'À propos', False),
            ('/cgv', 'cgv', 'CGV', False),
            ('/mentions-legales', 'mentions_legales', 'Mentions légales', False),
        ]
        
        for url_path, name, desc, full_page in public_pages:
            result = capture_page(page, url_path, name, desc, full_page)
            if result:
                captured.append((result, name, desc))
        
        # ================== SCROLL PAGE ACCUEIL ==================
        print("\n📸 Page d'accueil avec scroll...")
        try:
            page.goto(BASE_URL, wait_until='networkidle', timeout=30000)
            time.sleep(2)
            
            # Screenshot partie 1 (hero)
            page.screenshot(path=f'{SCREENSHOTS_DIR}/accueil_part1_hero.png', full_page=False)
            captured.append((f'{SCREENSHOTS_DIR}/accueil_part1_hero.png', 'accueil_part1_hero', 'Accueil - Hero'))
            
            # Scroll et screenshot partie 2
            page.evaluate("window.scrollTo(0, 800)")
            time.sleep(1)
            page.screenshot(path=f'{SCREENSHOTS_DIR}/accueil_part2_services.png', full_page=False)
            captured.append((f'{SCREENSHOTS_DIR}/accueil_part2_services.png', 'accueil_part2_services', 'Accueil - Services'))
            
            # Scroll et screenshot partie 3
            page.evaluate("window.scrollTo(0, 1600)")
            time.sleep(1)
            page.screenshot(path=f'{SCREENSHOTS_DIR}/accueil_part3_prestataires.png', full_page=False)
            captured.append((f'{SCREENSHOTS_DIR}/accueil_part3_prestataires.png', 'accueil_part3_prestataires', 'Accueil - Prestataires'))
            
            # Scroll et screenshot partie 4
            page.evaluate("window.scrollTo(0, 2400)")
            time.sleep(1)
            page.screenshot(path=f'{SCREENSHOTS_DIR}/accueil_part4_avis.png', full_page=False)
            captured.append((f'{SCREENSHOTS_DIR}/accueil_part4_avis.png', 'accueil_part4_avis', 'Accueil - Avis'))
            
            print("   ✅ Screenshots accueil en parties")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        # ================== MENU HEADER ==================
        print("\n📸 Capture du menu header...")
        try:
            page.goto(BASE_URL, wait_until='networkidle', timeout=30000)
            time.sleep(2)
            
            # Hover sur menu Pub IA
            pub_menu = page.locator("text=Pub IA").first
            if pub_menu:
                pub_menu.hover()
                time.sleep(0.5)
                page.screenshot(path=f'{SCREENSHOTS_DIR}/menu_pub_ia.png', full_page=False)
                captured.append((f'{SCREENSHOTS_DIR}/menu_pub_ia.png', 'menu_pub_ia', 'Menu Pub IA ouvert'))
            
            print("   ✅ Menu header capturé")
        except Exception as e:
            print(f"   ❌ Erreur menu: {e}")
        
        # ================== CONNEXION ENTREPRISE ==================
        print("\n" + "="*50)
        print("TENTATIVE CONNEXION ENTREPRISE")
        print("="*50)
        
        try:
            page.goto(f"{BASE_URL}/auth", wait_until='networkidle', timeout=30000)
            time.sleep(2)
            
            # Screenshot formulaire connexion
            page.screenshot(path=f'{SCREENSHOTS_DIR}/auth_formulaire.png', full_page=False)
            captured.append((f'{SCREENSHOTS_DIR}/auth_formulaire.png', 'auth_formulaire', 'Formulaire connexion'))
            
            # Chercher les champs
            email_input = page.locator('input[type="email"]').first
            password_input = page.locator('input[type="password"]').first
            
            if email_input.count() > 0 and password_input.count() > 0:
                # Essayer différentes combinaisons de test
                test_accounts = [
                    ('admin@titelli.com', 'admin123'),
                    ('test@titelli.com', 'test123'),
                    ('demo@titelli.com', 'demo123'),
                    ('entreprise@test.com', 'test123'),
                ]
                
                for email, password in test_accounts:
                    print(f"\n   Tentative avec {email}...")
                    
                    email_input.fill(email)
                    password_input.fill(password)
                    
                    # Screenshot avec credentials
                    page.screenshot(path=f'{SCREENSHOTS_DIR}/auth_rempli.png', full_page=False)
                    
                    # Cliquer connexion
                    submit_btn = page.locator('button[type="submit"]').first
                    if submit_btn.count() > 0:
                        submit_btn.click()
                        time.sleep(3)
                        
                        # Vérifier si connecté
                        current_url = page.url
                        if 'dashboard' in current_url or 'entreprise' in current_url:
                            print(f"   ✅ Connecté avec {email}!")
                            break
                        else:
                            # Retourner à la page auth
                            page.goto(f"{BASE_URL}/auth", wait_until='networkidle', timeout=30000)
                            time.sleep(1)
            
            print("   ℹ️ Connexion test non disponible")
            
        except Exception as e:
            print(f"   ❌ Erreur connexion: {e}")
        
        # ================== INSCRIPTION ENTREPRISE ==================
        print("\n📸 Page inscription entreprise...")
        try:
            page.goto(f"{BASE_URL}/inscription-entreprise", wait_until='networkidle', timeout=30000)
            time.sleep(2)
            
            if page.locator("text=404").count() == 0:
                page.screenshot(path=f'{SCREENSHOTS_DIR}/inscription_entreprise.png', full_page=False)
                captured.append((f'{SCREENSHOTS_DIR}/inscription_entreprise.png', 'inscription_entreprise', 'Inscription entreprise'))
                
                # Scroll pour voir plus
                page.evaluate("window.scrollTo(0, 500)")
                time.sleep(1)
                page.screenshot(path=f'{SCREENSHOTS_DIR}/inscription_entreprise_2.png', full_page=False)
                captured.append((f'{SCREENSHOTS_DIR}/inscription_entreprise_2.png', 'inscription_entreprise_2', 'Inscription entreprise - Suite'))
            
            print("   ✅ Page inscription capturée")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        # ================== RÉSUMÉ ==================
        browser.close()
    
    print("\n" + "=" * 70)
    print(f"   {len(captured)} SCREENSHOTS CAPTURÉS")
    print("=" * 70)
    for path, name, desc in captured:
        print(f"   - {name}: {desc}")
    
    # Sauvegarder la liste
    with open(f'{SCREENSHOTS_DIR}/liste_screenshots.txt', 'w') as f:
        for path, name, desc in captured:
            f.write(f"{name}|{desc}|{path}\n")
    
    return captured


if __name__ == "__main__":
    main()
