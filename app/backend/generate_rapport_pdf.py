#!/usr/bin/env python3
"""
Générateur de Rapport PDF Titelli
"""

from fpdf import FPDF
from datetime import datetime
import os

BASE_URL = "https://image-fix-demo.preview.emergentagent.com"
MEDIA_PATH = "/app/backend/uploads/media_titelli"

class TitelliPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
        self.add_font('DejaVu', 'B', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', uni=True)
        
    def header(self):
        self.set_font('DejaVu', 'B', 12)
        self.set_text_color(212, 175, 55)  # Gold
        self.cell(0, 10, 'TITELLI - Rapport Global', border=0, ln=True, align='C')
        self.set_draw_color(212, 175, 55)
        self.line(10, 20, 200, 20)
        self.ln(5)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', '', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}} - Généré le {datetime.now().strftime("%d/%m/%Y %H:%M")}', align='C')
        
    def chapter_title(self, title, emoji=""):
        self.set_font('DejaVu', 'B', 14)
        self.set_text_color(30, 30, 30)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 10, f'{emoji} {title}', border=0, ln=True, fill=True)
        self.ln(3)
        
    def section_title(self, title):
        self.set_font('DejaVu', 'B', 11)
        self.set_text_color(60, 60, 60)
        self.cell(0, 8, title, ln=True)
        self.ln(2)
        
    def body_text(self, text):
        self.set_font('DejaVu', '', 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 6, text)
        self.ln(2)
        
    def add_table(self, headers, data, col_widths=None):
        self.set_font('DejaVu', 'B', 9)
        self.set_fill_color(212, 175, 55)
        self.set_text_color(255, 255, 255)
        
        if col_widths is None:
            col_widths = [190 / len(headers)] * len(headers)
            
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, border=1, align='C', fill=True)
        self.ln()
        
        self.set_font('DejaVu', '', 9)
        self.set_text_color(50, 50, 50)
        fill = False
        for row in data:
            if fill:
                self.set_fill_color(245, 245, 245)
            else:
                self.set_fill_color(255, 255, 255)
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 7, str(cell), border=1, align='C', fill=True)
            self.ln()
            fill = not fill
        self.ln(3)

    def add_link_item(self, title, url, description=""):
        self.set_font('DejaVu', 'B', 10)
        self.set_text_color(30, 30, 30)
        self.cell(0, 6, f"• {title}", ln=True)
        self.set_font('DejaVu', '', 9)
        self.set_text_color(0, 102, 204)
        self.cell(0, 5, url, ln=True, link=url)
        if description:
            self.set_text_color(100, 100, 100)
            self.cell(0, 5, f"  {description}", ln=True)
        self.ln(2)


def generate_report():
    pdf = TitelliPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    
    # === PAGE 1: COUVERTURE ===
    pdf.add_page()
    pdf.ln(30)
    pdf.set_font('DejaVu', 'B', 28)
    pdf.set_text_color(212, 175, 55)
    pdf.cell(0, 15, 'TITELLI', align='C', ln=True)
    pdf.set_font('DejaVu', '', 16)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, 'Plateforme Social Commerce Suisse', align='C', ln=True)
    pdf.ln(10)
    pdf.set_font('DejaVu', 'B', 14)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 10, 'RAPPORT GLOBAL - CAHIER DES CHARGES', align='C', ln=True)
    pdf.cell(0, 10, f'Février 2026', align='C', ln=True)
    pdf.ln(20)
    pdf.set_font('DejaVu', '', 11)
    pdf.cell(0, 8, f'URL: {BASE_URL}', align='C', ln=True)
    
    # === PAGE 2: STATISTIQUES ===
    pdf.add_page()
    pdf.chapter_title('STATISTIQUES BASE DE DONNÉES', '📊')
    
    pdf.section_title('Données Principales')
    pdf.add_table(
        ['Métrique', 'Valeur'],
        [
            ['Total Entreprises', '6,482'],
            ['Total Utilisateurs', '60'],
            ['Notifications actives', '294'],
            ['Offres RDV créées', '4'],
            ['Demandes spécialistes', '1'],
            ['Abonnements lifestyle', '1'],
        ],
        [100, 90]
    )
    
    pdf.section_title('Nouvelles Collections MongoDB')
    pdf.add_table(
        ['Collection', 'Documents', 'Description'],
        [
            ['shared_offers', '4', 'Offres RDV Titelli'],
            ['offer_invitations', '0', 'Invitations RDV'],
            ['chat_rooms', '0', 'Salons de chat'],
            ['chat_messages', '0', 'Messages chat temps réel'],
            ['specialist_requests', '1', 'Demandes spécialistes'],
            ['lifestyle_subscriptions', '1', 'Abonnements passes'],
            ['gamification_points', '0', 'Points utilisateurs'],
            ['sports_matches', '0', 'Matchs sportifs'],
            ['notifications', '294', 'Notifications push'],
        ],
        [60, 30, 100]
    )
    
    # === PAGE 3: FONCTIONNALITÉS RDV ===
    pdf.add_page()
    pdf.chapter_title('RDV CHEZ TITELLI - Social Booking', '💕')
    
    pdf.body_text("""
Fonctionnalité permettant aux utilisateurs de créer des offres pour partager des activités à deux personnes. 
Deux modes disponibles: Amical (gratuit) et Romantique (payant avec abonnement).
    """)
    
    pdf.section_title('Fichiers Source')
    pdf.body_text("• Backend: /app/backend/routers/rdv_titelli.py (1,135 lignes)")
    pdf.body_text("• Frontend: /app/frontend/src/pages/RdvTitelliPage.js")
    pdf.body_text("• Chat: /app/frontend/src/pages/RdvChatPage.js")
    
    pdf.section_title('Tarification')
    pdf.add_table(
        ['Service', 'Prix', 'Type'],
        [
            ['Mode Amical', 'Gratuit', 'Free'],
            ['Abonnement Romantique', '200 CHF/mois', 'Récurrent'],
            ['Acceptation invitation', '2 CHF', 'One-time'],
        ],
        [80, 50, 60]
    )
    
    pdf.section_title('Catégories disponibles')
    pdf.body_text("Restaurant, Sport, Wellness, Culture, Nature, Party, Creative, Autre")
    
    pdf.section_title('API Endpoints')
    pdf.add_table(
        ['Méthode', 'Endpoint', 'Description'],
        [
            ['POST', '/api/rdv/offers', 'Créer une offre'],
            ['GET', '/api/rdv/offers', 'Liste des offres'],
            ['POST', '/api/rdv/invitations/{id}/accept', 'Accepter invitation'],
            ['POST', '/api/rdv/subscriptions/romantic', 'S\'abonner romantique'],
            ['WS', '/ws/rdv/{chat_room_id}', 'Chat temps réel'],
        ],
        [25, 75, 90]
    )
    
    # === PAGE 4: SPÉCIALISTES & PASSES ===
    pdf.add_page()
    pdf.chapter_title('DEMANDES SPÉCIALISTES', '👨‍⚕️')
    
    pdf.body_text("""
Système permettant aux clients de rechercher des spécialistes via IA et de créer des demandes 
spécifiques auxquelles les prestataires peuvent répondre.
    """)
    
    pdf.section_title('Fichiers Source')
    pdf.body_text("• Backend: /app/backend/routers/specialists.py (585 lignes)")
    pdf.body_text("• Frontend: /app/frontend/src/pages/SpecialistsPage.js")
    
    pdf.section_title('API Endpoints')
    pdf.add_table(
        ['Méthode', 'Endpoint', 'Description'],
        [
            ['GET', '/api/specialists/search', 'Recherche IA'],
            ['POST', '/api/specialists/requests', 'Créer demande'],
            ['GET', '/api/specialists/requests/{id}/responses', 'Voir réponses'],
            ['POST', '/api/specialists/requests/{id}/accept/{rid}', 'Accepter réponse'],
        ],
        [25, 85, 80]
    )
    
    pdf.ln(5)
    pdf.chapter_title('LIFESTYLE PASSES', '🎫')
    
    pdf.body_text("Abonnements mensuels donnant accès à des services premium selon le niveau choisi.")
    
    pdf.add_table(
        ['Pass', 'Prix/mois', 'Inclus'],
        [
            ['Healthy Lifestyle', '99 CHF', 'Bien-être, santé'],
            ['Better You', '149 CHF', 'Développement personnel'],
            ['Special MVP', '299 CHF', 'Accès VIP exclusif'],
        ],
        [60, 40, 90]
    )
    
    # === PAGE 5: TITELLI PRO++ ===
    pdf.add_page()
    pdf.chapter_title('TITELLI PRO++ - B2B', '🏢')
    
    pdf.body_text("""
Services B2B pour les entreprises incluant les livraisons récurrentes et la liquidation de stock.
Abonnement mensuel requis pour accéder aux fonctionnalités.
    """)
    
    pdf.section_title('Fichiers Source')
    pdf.body_text("• Backend: /app/backend/routers/titelli_pro.py (720 lignes)")
    pdf.body_text("• Frontend: /app/frontend/src/pages/TitelliProPage.js")
    
    pdf.section_title('Fonctionnalités')
    pdf.body_text("• Livraisons B2B récurrentes (quotidien/hebdomadaire/mensuel)")
    pdf.body_text("• Liquidation de stock (surstock, fin de saison, expiration proche)")
    pdf.body_text("• Analytics B2B")
    
    pdf.section_title('Tarification')
    pdf.add_table(
        ['Service', 'Prix', 'Type'],
        [
            ['Abonnement Pro++', '199 CHF/mois', 'Récurrent'],
        ],
        [80, 50, 60]
    )
    
    pdf.section_title('API Endpoints')
    pdf.add_table(
        ['Méthode', 'Endpoint', 'Description'],
        [
            ['GET', '/api/pro/status', 'Statut abonnement'],
            ['POST', '/api/pro/subscribe', 'S\'abonner Pro++'],
            ['GET', '/api/pro/deliveries', 'Liste clients B2B'],
            ['POST', '/api/pro/liquidations', 'Ajouter liquidation'],
        ],
        [25, 70, 95]
    )
    
    # === PAGE 6: SPORTS ===
    pdf.add_page()
    pdf.chapter_title('SPORTS & COMPÉTITIONS', '⚽')
    
    pdf.body_text("""
Fonctionnalité permettant de créer des matchs sportifs, former des équipes et organiser des compétitions.
11 catégories sportives disponibles.
    """)
    
    pdf.section_title('Fichiers Source')
    pdf.body_text("• Backend: /app/backend/routers/titelli_pro.py (sports_router)")
    pdf.body_text("• Frontend: /app/frontend/src/pages/SportsPage.js")
    
    pdf.section_title('Catégories Sportives')
    pdf.body_text("Football, Tennis, Basketball, Volleyball, Badminton, Padel, Squash, Running, Cycling, Swimming, Fitness")
    
    pdf.section_title('Types de Matchs')
    pdf.body_text("• Cherche adversaire - Match 1v1")
    pdf.body_text("• Cherche joueurs - Besoin de participants")
    pdf.body_text("• Cherche équipe - Rejoindre une équipe existante")
    
    pdf.section_title('API Endpoints')
    pdf.add_table(
        ['Méthode', 'Endpoint', 'Description'],
        [
            ['GET', '/api/sports/categories', 'Liste catégories'],
            ['POST', '/api/sports/matches', 'Créer match'],
            ['GET', '/api/sports/matches/my', 'Mes matchs'],
            ['POST', '/api/sports/matches/{id}/join', 'Rejoindre match'],
            ['POST', '/api/sports/teams', 'Créer équipe'],
            ['POST', '/api/sports/competitions', 'Créer compétition'],
        ],
        [25, 75, 90]
    )
    
    # === PAGE 7: NOTIFICATIONS & GAMIFICATION ===
    pdf.add_page()
    pdf.chapter_title('NOTIFICATIONS PUSH', '🔔')
    
    pdf.body_text("""
Système de notifications temps réel pour informer les utilisateurs des nouvelles activités:
invitations RDV, messages chat, réponses spécialistes, matchs sports.
    """)
    
    pdf.section_title('Fichiers Source')
    pdf.body_text("• Backend: /app/backend/routers/notifications.py (316 lignes)")
    pdf.body_text("• Frontend: /app/frontend/src/components/NotificationsDropdown.js")
    
    pdf.section_title('API Endpoints')
    pdf.add_table(
        ['Méthode', 'Endpoint', 'Description'],
        [
            ['GET', '/api/notifications', 'Liste notifications'],
            ['GET', '/api/notifications/unread-count', 'Compteur non-lus'],
            ['POST', '/api/notifications/{id}/read', 'Marquer comme lu'],
            ['DELETE', '/api/notifications/{id}', 'Supprimer'],
        ],
        [25, 80, 85]
    )
    
    pdf.ln(5)
    pdf.chapter_title('GAMIFICATION', '🎮')
    
    pdf.body_text("Système de points et badges pour récompenser l'activité des utilisateurs.")
    
    pdf.section_title('Points par Action')
    pdf.add_table(
        ['Action', 'Points'],
        [
            ['Créer offre RDV', '+10'],
            ['Envoyer invitation', '+5'],
            ['Accepter invitation', '+15'],
            ['Créer match sport', '+10'],
            ['Rejoindre match', '+5'],
        ],
        [120, 70]
    )
    
    # === PAGE 8: MÉDIAS - IMAGES ===
    pdf.add_page()
    pdf.chapter_title('MÉDIAS MARKETING - IMAGES', '🖼️')
    
    pdf.body_text(f"Dossier: {MEDIA_PATH}/")
    pdf.ln(3)
    
    pdf.section_title('Images Publicitaires Produits')
    images_produits = [
        ['pub_produit_chocolat.png', '1.5 MB', f'{BASE_URL}/uploads/media_titelli/pub_produit_chocolat.png'],
        ['pub_produit_beaute.png', '1.2 MB', f'{BASE_URL}/uploads/media_titelli/pub_produit_beaute.png'],
        ['pub_produit_horlogerie.png', '1.2 MB', f'{BASE_URL}/uploads/media_titelli/pub_produit_horlogerie.png'],
        ['pub_produit_vin.png', '1.2 MB', f'{BASE_URL}/uploads/media_titelli/pub_produit_vin.png'],
    ]
    pdf.add_table(['Fichier', 'Taille', 'URL'], images_produits, [50, 25, 115])
    
    pdf.section_title('Images Publicitaires Services')
    images_services = [
        ['pub_service_beaute.png', '1.4 MB', f'{BASE_URL}/uploads/media_titelli/pub_service_beaute.png'],
        ['pub_service_mode.png', '1.5 MB', f'{BASE_URL}/uploads/media_titelli/pub_service_mode.png'],
        ['pub_service_restaurant.png', '1.4 MB', f'{BASE_URL}/uploads/media_titelli/pub_service_restaurant.png'],
        ['pub_service_wellness.png', '1.5 MB', f'{BASE_URL}/uploads/media_titelli/pub_service_wellness.png'],
    ]
    pdf.add_table(['Fichier', 'Taille', 'URL'], images_services, [50, 25, 115])
    
    pdf.section_title('Screenshots Application')
    screenshots = [
        ['01_homepage.jpg', '42 KB', f'{BASE_URL}/uploads/media_titelli/screenshots/01_homepage.jpg'],
        ['02_produits.jpg', '67 KB', f'{BASE_URL}/uploads/media_titelli/screenshots/02_produits.jpg'],
        ['03_services.jpg', '81 KB', f'{BASE_URL}/uploads/media_titelli/screenshots/03_services.jpg'],
        ['04_entreprises.jpg', '75 KB', f'{BASE_URL}/uploads/media_titelli/screenshots/04_entreprises.jpg'],
    ]
    pdf.add_table(['Fichier', 'Taille', 'URL'], screenshots, [50, 25, 115])
    
    # === PAGE 9: MÉDIAS - VIDÉOS V1 ===
    pdf.add_page()
    pdf.chapter_title('MÉDIAS MARKETING - VIDÉOS V1', '🎬')
    
    pdf.section_title('Vidéos de Présentation')
    videos_pres = [
        ['video_presentation_prestataires_full.mp4', '5.9 MB', 'Présentation complète'],
        ['video_presentation_prestataires_30s.mp4', '5.7 MB', 'Version courte 30s'],
        ['video_presentation_part1.mp4', '2.0 MB', 'Partie 1'],
        ['video_presentation_part2.mp4', '2.5 MB', 'Partie 2'],
        ['video_presentation_part3.mp4', '1.3 MB', 'Partie 3'],
    ]
    pdf.add_table(['Fichier', 'Taille', 'Description'], videos_pres, [80, 30, 80])
    
    pdf.section_title('URLs Vidéos Présentation')
    for v in videos_pres:
        pdf.add_link_item(v[0], f"{BASE_URL}/uploads/media_titelli/{v[0]}", v[2])
    
    pdf.section_title('Vidéos Produits V1')
    videos_prod = [
        ['video_produit_chocolat.mp4', '836 KB', 'Chocolat suisse'],
        ['video_produit_vin.mp4', '874 KB', 'Vin premium'],
        ['video_produit_bijou.mp4', '789 KB', 'Bijouterie'],
        ['video_produit_montre.mp4', '662 KB', 'Horlogerie luxe'],
        ['video_produit_beaute.mp4', '518 KB', 'Soins beauté'],
    ]
    pdf.add_table(['Fichier', 'Taille', 'Description'], videos_prod, [70, 30, 90])
    
    # === PAGE 10: MÉDIAS - VIDÉOS V2 ===
    pdf.add_page()
    pdf.chapter_title('MÉDIAS MARKETING - VIDÉOS V2 (Révisées)', '🎥')
    
    pdf.body_text("Version révisée des vidéos avec style plus moderne et dynamique.")
    pdf.body_text(f"Dossier: {MEDIA_PATH}/v2/")
    pdf.ln(3)
    
    pdf.section_title('Vidéos Produits V2')
    videos_v2 = [
        ['produit_chocolat_suisse_v2.mp4', '580 KB', 'Chocolat suisse - V2', f'{BASE_URL}/uploads/media_titelli/v2/produit_chocolat_suisse_v2.mp4'],
        ['produit_montre_luxe_v2.mp4', '987 KB', 'Montre luxe - V2', f'{BASE_URL}/uploads/media_titelli/v2/produit_montre_luxe_v2.mp4'],
        ['produit_soins_beaute_v2.mp4', '644 KB', 'Soins beauté - V2', f'{BASE_URL}/uploads/media_titelli/v2/produit_soins_beaute_v2.mp4'],
        ['produit_restaurant_gourmet_v2.mp4', '696 KB', 'Restaurant gourmet - V2', f'{BASE_URL}/uploads/media_titelli/v2/produit_restaurant_gourmet_v2.mp4'],
        ['produit_vin_premium_v2.mp4', '1.0 MB', 'Vin premium - V2', f'{BASE_URL}/uploads/media_titelli/v2/produit_vin_premium_v2.mp4'],
    ]
    pdf.add_table(['Fichier', 'Taille', 'Description'], [[v[0], v[1], v[2]] for v in videos_v2], [70, 25, 95])
    
    pdf.section_title('URLs Vidéos V2')
    for v in videos_v2:
        pdf.add_link_item(v[2], v[3])
    
    pdf.section_title('Audio Voiceover')
    pdf.add_link_item(
        'voiceover_french.mp3 (443 KB)',
        f'{BASE_URL}/uploads/media_titelli/v2/voiceover_french.mp3',
        'Voix française pour la vidéo de présentation'
    )
    
    # === PAGE 11: ARCHITECTURE ===
    pdf.add_page()
    pdf.chapter_title('ARCHITECTURE TECHNIQUE', '🏗️')
    
    pdf.section_title('Backend (FastAPI)')
    backend_files = [
        ['server.py', '10,271', 'Fichier principal (REFACTORING REQUIS)'],
        ['routers/rdv_titelli.py', '1,135', 'RDV chez Titelli'],
        ['routers/titelli_pro.py', '720', 'Titelli Pro++ & Sports'],
        ['routers/gamification.py', '591', 'Système gamification'],
        ['routers/specialists.py', '585', 'Demandes spécialistes'],
        ['routers/notifications.py', '316', 'Notifications push'],
        ['routers/client_premium.py', '302', 'Client premium'],
        ['routers/client.py', '278', 'Client standard'],
        ['routers/auth.py', '180', 'Authentification'],
        ['routers/payments.py', '150', 'Paiements'],
        ['routers/websocket.py', '134', 'WebSocket'],
    ]
    pdf.add_table(['Fichier', 'Lignes', 'Description'], backend_files, [60, 25, 105])
    
    pdf.body_text("TOTAL: 14,871 lignes de code backend")
    
    pdf.section_title('Frontend (React)')
    frontend_pages = [
        ['RdvTitelliPage.js', 'Social booking'],
        ['RdvChatPage.js', 'Chat temps réel'],
        ['SpecialistsPage.js', 'Demandes spécialistes'],
        ['TitelliProPage.js', 'B2B services'],
        ['SportsPage.js', 'Sports & compétitions'],
    ]
    pdf.add_table(['Page', 'Description'], frontend_pages, [80, 110])
    
    # === PAGE 12: STRIPE ===
    pdf.add_page()
    pdf.chapter_title('INTÉGRATIONS STRIPE', '💳')
    
    pdf.body_text("Tous les paiements sont gérés via Stripe. Configuration production requise.")
    pdf.ln(3)
    
    pdf.section_title('Paiements Récurrents (Abonnements)')
    stripe_recurring = [
        ['Abonnement Romantique', '200 CHF/mois', 'RDV Titelli'],
        ['Abonnement Pro++', '199 CHF/mois', 'Titelli Pro B2B'],
        ['Healthy Lifestyle Pass', '99 CHF/mois', 'Lifestyle Passes'],
        ['Better You Pass', '149 CHF/mois', 'Lifestyle Passes'],
        ['Special MVP Pass', '299 CHF/mois', 'Lifestyle Passes'],
    ]
    pdf.add_table(['Service', 'Prix', 'Module'], stripe_recurring, [70, 50, 70])
    
    pdf.section_title('Paiements One-Time')
    stripe_onetime = [
        ['Acceptation invitation RDV', '2 CHF', 'RDV Titelli'],
    ]
    pdf.add_table(['Service', 'Prix', 'Module'], stripe_onetime, [70, 50, 70])
    
    # === PAGE 13: IDENTIFIANTS ===
    pdf.add_page()
    pdf.chapter_title('IDENTIFIANTS DE TEST', '🔐')
    
    pdf.section_title('Comptes Utilisateurs')
    credentials = [
        ['Admin', 'admin@titelli.com', 'Admin123!'],
        ['Client', 'test.client@titelli.com', 'Test123!'],
        ['Enterprise', 'test.entreprise@titelli.com', 'Test123!'],
    ]
    pdf.add_table(['Rôle', 'Email', 'Mot de passe'], credentials, [50, 80, 60])
    
    pdf.section_title('URL Application')
    pdf.add_link_item('Application Titelli', BASE_URL, 'URL de prévisualisation')
    
    # === PAGE 14: ROADMAP ===
    pdf.add_page()
    pdf.chapter_title('ROADMAP & TÂCHES RESTANTES', '📋')
    
    pdf.section_title('P0 - Priorité Critique')
    pdf.body_text("• Vérification complète mode production (Stripe live)")
    pdf.body_text("• Tests end-to-end de toutes les nouvelles fonctionnalités")
    
    pdf.section_title('P1 - Priorité Haute')
    pdf.body_text("• Frontend complet Titelli Pro++ (actuellement placeholder)")
    pdf.body_text("• Analytics Comportemental")
    pdf.body_text("• Assemblage vidéo finale 30s avec voiceover français")
    
    pdf.section_title('P2 - Backlog')
    pdf.body_text("• Logique avancée tournois Sports")
    pdf.body_text("• Refactoring server.py (10,271 lignes)")
    pdf.body_text("• Webhooks Stripe temps réel")
    pdf.body_text("• Interface admin médias marketing")
    
    pdf.section_title('Dette Technique')
    pdf.body_text("• server.py monolithique - REFACTORING URGENT")
    pdf.body_text("• Logique Stripe dupliquée - Centralisation nécessaire")
    pdf.body_text("• Frontend pages volumineuses - Décomposition en composants")
    
    # === PAGE 15: RÉSUMÉ ===
    pdf.add_page()
    pdf.chapter_title('RÉSUMÉ EXÉCUTIF', '📊')
    
    summary = [
        ['Entreprises en DB', '6,482'],
        ['Utilisateurs', '60'],
        ['Nouvelles pages Frontend', '5'],
        ['Nouveaux routers Backend', '6'],
        ['Lignes de code ajoutées', '~4,600'],
        ['Collections MongoDB créées', '11'],
        ['Médias marketing', '24+ fichiers'],
        ['Endpoints API ajoutés', '~50'],
        ['Intégrations Stripe', '6 flux'],
    ]
    pdf.add_table(['Métrique', 'Valeur'], summary, [100, 90])
    
    pdf.ln(10)
    pdf.set_font('DejaVu', 'B', 12)
    pdf.set_text_color(212, 175, 55)
    pdf.cell(0, 10, 'Document généré automatiquement', align='C', ln=True)
    pdf.set_font('DejaVu', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, f'Titelli - {datetime.now().strftime("%d/%m/%Y %H:%M")}', align='C', ln=True)
    
    # Save PDF
    output_path = '/app/backend/uploads/RAPPORT_TITELLI_COMPLET.pdf'
    pdf.output(output_path)
    print(f"PDF généré: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_report()
