#!/usr/bin/env python3
"""
Capture TOUS les screenshots du Dashboard Entreprise Titelli
Une capture par section du menu
"""
import os
import time
from playwright.sync_api import sync_playwright

BASE_URL = 'https://image-fix-demo.preview.emergentagent.com'
SCREENSHOTS_DIR = '/app/backend/uploads/brochure_screenshots_v2'
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYzg5OTNlZDktMGQxNC00YTZjLTk1ODQtYjJiNDc5ZjQzMzg1IiwidXNlcl90eXBlIjoiZW50cmVwcmlzZSIsImV4cCI6MTc3MTI4OTMzOS40MjQ4NTZ9.CuT_YZeJgP4RaxXtWk5sVkMt64CK58JGxRIBuGaet-Q"

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def main():
    print("=" * 70)
    print("   CAPTURE DASHBOARD ENTREPRISE - TOUTES LES SECTIONS")
    print("=" * 70)
    
    captured = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1.5
        )
        page = context.new_page()
        
        # Injecter le token dans localStorage
        page.goto(BASE_URL, wait_until='networkidle', timeout=30000)
        time.sleep(2)
        
        # Simuler la connexion via localStorage
        page.evaluate(f"""
            localStorage.setItem('titelli_token', '{TOKEN}');
            localStorage.setItem('token', '{TOKEN}');
        """)
        
        # Sections du dashboard à capturer
        dashboard_sections = [
            # Principal
            ('overview', 'dashboard_accueil', 'Dashboard - Accueil'),
            ('profile', 'dashboard_profil', 'Dashboard - Profil entreprise'),
            ('media', 'dashboard_media', 'Dashboard - Galerie média'),
            ('feed', 'dashboard_fil_actu', 'Dashboard - Mon fil d\'actualité'),
            ('business_feed', 'dashboard_feed_entreprises', 'Dashboard - Feed entreprises'),
            
            # Commercial
            ('services', 'dashboard_services', 'Dashboard - Services & Produits'),
            ('orders', 'dashboard_commandes', 'Dashboard - Mes commandes'),
            ('deliveries', 'dashboard_livraisons', 'Dashboard - Mes livraisons'),
            ('activities', 'dashboard_activites', 'Dashboard - Mes activités'),
            ('stock', 'dashboard_stocks', 'Dashboard - Gestion des stocks'),
            ('permanent', 'dashboard_commandes_permanentes', 'Dashboard - Commandes permanentes'),
            
            # Marketing
            ('offers', 'dashboard_offres', 'Dashboard - Offres & Promotions'),
            ('advertising', 'dashboard_publicites', 'Dashboard - Mes publicités'),
            ('commercial_gesture', 'dashboard_geste_commercial', 'Dashboard - Geste commercial'),
            ('tendances', 'dashboard_tendances', 'Dashboard - Tendances actuelles'),
            ('guests', 'dashboard_guests', 'Dashboard - Guests du moment'),
            
            # IA & Marketing
            ('ia_clients', 'dashboard_ia_ciblage', 'Dashboard - IA Ciblage clients'),
            ('influencers', 'dashboard_influenceurs', 'Dashboard - Influenceurs'),
            ('invitations', 'dashboard_invitations', 'Dashboard - Invitations clients'),
            ('commandes-titelli', 'dashboard_commandes_titelli', 'Dashboard - Commandes Titelli'),
            
            # RH
            ('team', 'dashboard_personnel', 'Dashboard - Mon personnel'),
            ('jobs', 'dashboard_emplois', 'Dashboard - Emplois & Stages'),
            ('applications', 'dashboard_postulations', 'Dashboard - Postulations'),
            ('trainings', 'dashboard_formations', 'Dashboard - Formations'),
            
            # Finances
            ('finances', 'dashboard_finances', 'Dashboard - Mes finances'),
            ('cards', 'dashboard_cartes', 'Dashboard - Mes cartes'),
            ('investments', 'dashboard_investissements', 'Dashboard - Mes investissements'),
            ('donations', 'dashboard_donations', 'Dashboard - Donations'),
            
            # Actualités
            ('business_news', 'dashboard_business_news', 'Dashboard - Business News'),
            ('development', 'dashboard_formations_metier', 'Dashboard - Formations métier'),
            
            # Communication
            ('messages', 'dashboard_messagerie', 'Dashboard - Messagerie'),
            ('contacts', 'dashboard_contacts', 'Dashboard - Contacts'),
            
            # Documents & Paramètres
            ('subscriptions', 'dashboard_abonnements', 'Dashboard - Abonnements'),
            ('documents', 'dashboard_documents', 'Dashboard - Documents'),
            ('realestate', 'dashboard_immobilier', 'Dashboard - Immobilier'),
            ('settings', 'dashboard_parametres', 'Dashboard - Paramètres'),
            
            # Aide
            ('support', 'dashboard_support', 'Dashboard - Service client'),
            ('partners', 'dashboard_partenaires', 'Dashboard - Partenaires'),
            ('about', 'dashboard_apropos', 'Dashboard - À propos'),
        ]
        
        for tab_id, screenshot_name, description in dashboard_sections:
            print(f"\n📸 {description}...")
            
            try:
                # Accéder à la section du dashboard
                url = f"{BASE_URL}/dashboard/entreprise?tab={tab_id}"
                page.goto(url, wait_until='networkidle', timeout=30000)
                time.sleep(2)
                
                # Vérifier si on est bien sur la page
                screenshot_path = f'{SCREENSHOTS_DIR}/{screenshot_name}.png'
                page.screenshot(path=screenshot_path, full_page=False)
                captured.append((screenshot_path, screenshot_name, description))
                print(f"   ✅ {screenshot_path}")
                
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
        
        browser.close()
    
    print("\n" + "=" * 70)
    print(f"   {len(captured)} SCREENSHOTS DASHBOARD CAPTURÉS")
    print("=" * 70)
    
    # Ajouter à la liste
    with open(f'{SCREENSHOTS_DIR}/liste_screenshots.txt', 'a') as f:
        for path, name, desc in captured:
            f.write(f"{name}|{desc}|{path}\n")
    
    return captured


if __name__ == "__main__":
    main()
