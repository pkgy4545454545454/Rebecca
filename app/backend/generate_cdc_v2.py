#!/usr/bin/env python3
"""
Générateur de Cahiers des Charges Titelli - Version 2.0 Détaillée
Inclut: Code, Algorithmes, Architecture, Pages détaillées
"""
from fpdf import FPDF
from datetime import datetime
import os

OUTPUT_DIR = "/app/backend/uploads/documents"
os.makedirs(OUTPUT_DIR, exist_ok=True)


class TitelliPDFv2(FPDF):
    def __init__(self):
        super().__init__()
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(245, 158, 11)
        self.cell(95, 10, 'TITELLI - CDC v2.0')
        self.set_text_color(150, 150, 150)
        self.set_font('Helvetica', '', 8)
        self.cell(95, 10, f'Confidentiel - {datetime.now().strftime("%d/%m/%Y")}', align='R')
        self.ln(15)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def add_title_page(self, title, subtitle, version="2.0"):
        self.add_page()
        self.ln(50)
        self.set_font('Helvetica', 'B', 32)
        self.set_text_color(245, 158, 11)
        self.multi_cell(0, 15, title, align='C')
        self.ln(10)
        self.set_font('Helvetica', '', 16)
        self.set_text_color(100, 100, 100)
        self.multi_cell(0, 8, subtitle, align='C')
        self.ln(30)
        self.set_font('Helvetica', '', 12)
        self.cell(0, 10, f'Date: {datetime.now().strftime("%d %B %Y")}', align='C')
        self.ln(8)
        self.cell(0, 10, f'Version: {version}', align='C')
        self.ln(8)
        self.set_font('Helvetica', 'I', 10)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, 'Document strictement confidentiel - Titelli SA', align='C')

    def add_chapter(self, num, title):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(245, 158, 11)
        self.ln(5)
        self.cell(0, 12, f'{num}. {title}')
        self.ln(12)
        self.set_draw_color(245, 158, 11)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(8)

    def add_section(self, title, italic=False):
        self.set_x(self.l_margin)
        if italic:
            self.set_font('Helvetica', 'BI', 11)
            self.set_text_color(100, 100, 200)  # Blue italic for new features
        else:
            self.set_font('Helvetica', 'B', 11)
            self.set_text_color(60, 60, 60)
        self.multi_cell(0, 8, title)

    def add_text(self, text, italic=False):
        self.set_x(self.l_margin)
        if italic:
            self.set_font('Helvetica', 'I', 10)
            self.set_text_color(100, 100, 200)
        else:
            self.set_font('Helvetica', '', 10)
            self.set_text_color(80, 80, 80)
        self.multi_cell(0, 6, text)
        self.ln(3)

    def add_bullet(self, text, italic=False):
        self.set_x(self.l_margin)
        if italic:
            self.set_font('Helvetica', 'I', 10)
            self.set_text_color(100, 100, 200)
        else:
            self.set_font('Helvetica', '', 10)
            self.set_text_color(80, 80, 80)
        self.multi_cell(0, 6, f"   - {text}")

    def add_code_block(self, code, title="Code"):
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, title)
        self.ln(6)
        self.set_fill_color(40, 40, 50)
        self.set_text_color(200, 200, 200)
        self.set_font('Courier', '', 8)
        self.multi_cell(0, 5, code, fill=True)
        self.ln(5)
        self.set_text_color(80, 80, 80)

    def add_table_row(self, col1, col2, header=False):
        if header:
            self.set_fill_color(245, 158, 11)
            self.set_text_color(255, 255, 255)
            self.set_font('Helvetica', 'B', 9)
        else:
            self.set_fill_color(250, 250, 250)
            self.set_text_color(60, 60, 60)
            self.set_font('Helvetica', '', 9)
        self.cell(90, 8, col1, border=1, fill=True)
        self.cell(90, 8, col2, border=1, fill=True)
        self.ln()

    def add_highlight(self, title, text):
        self.set_fill_color(245, 158, 11)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 8, f'  {title}', fill=True)
        self.ln(8)
        self.set_fill_color(255, 250, 240)
        self.set_text_color(60, 60, 60)
        self.set_font('Helvetica', '', 10)
        self.multi_cell(0, 6, text, fill=True)
        self.ln(5)

    def add_api_endpoint(self, method, path, description):
        self.set_font('Courier', 'B', 9)
        if method == "GET":
            self.set_text_color(34, 139, 34)
        elif method == "POST":
            self.set_text_color(30, 144, 255)
        elif method == "PUT":
            self.set_text_color(255, 165, 0)
        else:
            self.set_text_color(220, 20, 60)
        self.cell(15, 6, method)
        self.set_text_color(80, 80, 80)
        self.set_font('Courier', '', 9)
        self.cell(80, 6, path)
        self.set_font('Helvetica', '', 9)
        self.cell(0, 6, description)
        self.ln(6)


def generate_monetisation_v2():
    pdf = TitelliPDFv2()
    
    # Page titre
    pdf.add_title_page(
        "CAHIER DES CHARGES\nMONETISATION",
        "Strategie Economique Complete - Titelli SA\nVersion Detaillee avec Algorithmes"
    )
    
    # Table des matieres
    pdf.add_page()
    pdf.add_chapter("", "TABLE DES MATIERES")
    toc = [
        "1. Procede de Facturation et Commission",
        "2. Systeme Cash-Back Client",
        "3. Cash-Back Entreprise VIP Secret",
        "4. Tarification Complete des Services",
        "5. Services Premium et Avantages",
        "6. Labellisation et Certification",
        "7. Algorithmes de Recommandation",
        "8. Projection Financiere",
        "9. Conditions Generales"
    ]
    for item in toc:
        pdf.add_text(item)
    
    # 1. Facturation
    pdf.add_page()
    pdf.add_chapter(1, "Procede de Facturation et Commission")
    
    pdf.add_highlight(
        "MODELE ECONOMIQUE",
        "Titelli fonctionne sur un modele de commission de 20% sur chaque transaction. Ce montant comprend: 10% pour le cash-back client + 10% de frais plateforme."
    )
    
    pdf.add_section("Flux de Facturation:")
    pdf.add_bullet("1. Client effectue un achat aupres d'un prestataire")
    pdf.add_bullet("2. Paiement Stripe securise en temps reel")
    pdf.add_bullet("3. Commission 20% prelevee automatiquement")
    pdf.add_bullet("4. 10% credite en cash-back client (disponible M+1)")
    pdf.add_bullet("5. 10% revenus Titelli")
    pdf.add_bullet("6. Versement prestataire debut du mois suivant")
    
    pdf.add_section("Algorithme de Calcul Commission:", italic=True)
    pdf.add_code_block("""
def calculate_commission(transaction_amount, has_delivery=False):
    base_commission = 0.20  # 20%
    delivery_fee = 0.05 if has_delivery else 0
    
    client_cashback = transaction_amount * 0.10
    titelli_revenue = transaction_amount * 0.10
    delivery_cost = transaction_amount * delivery_fee
    
    net_to_prestataire = transaction_amount - (client_cashback + titelli_revenue + delivery_cost)
    
    return {
        'gross': transaction_amount,
        'cashback': client_cashback,
        'titelli': titelli_revenue,
        'delivery': delivery_cost,
        'net': net_to_prestataire
    }
    """, "Algorithme Python - Commission")
    
    pdf.add_section("Projection de Benefices:")
    pdf.add_text("Augmentation attendue: 20-45% la premiere annee")
    pdf.add_bullet("Visibilite accrue (+500% exposition)")
    pdf.add_bullet("Nouveaux clients via recommendations IA")
    pdf.add_bullet("Fidelisation par cash-back")
    pdf.add_bullet("Marketing automatise")
    
    # 2. Cash-Back
    pdf.add_page()
    pdf.add_chapter(2, "Systeme Cash-Back Client")
    
    pdf.add_text("Le Cash-Back represente 10% de chaque achat, credite automatiquement.")
    
    pdf.add_section("Fonctionnement Technique:", italic=True)
    pdf.add_code_block("""
# Collection MongoDB: cashback_wallets
{
    "user_id": "string",
    "balance": 45.50,
    "pending": 12.30,  # En attente fin de mois
    "total_earned": 157.80,
    "total_spent": 100.00,
    "transactions": [
        {"date": "2026-02-01", "amount": 12.30, "source": "Achat Restaurant X"},
        {"date": "2026-01-15", "amount": -20.00, "usage": "Achat Boutique Y"}
    ]
}
    """, "Schema MongoDB Cash-Back")
    
    pdf.add_section("Regles d'Utilisation:")
    pdf.add_bullet("Disponible le 1er du mois suivant l'achat")
    pdf.add_bullet("Utilisable sur toute la plateforme")
    pdf.add_bullet("Transferable entre utilisateurs Titelli")
    pdf.add_bullet("Pas de date d'expiration")
    pdf.add_bullet("Non convertible en especes")
    
    # 3. VIP Secret
    pdf.add_page()
    pdf.add_chapter(3, "Cash-Back Entreprise VIP Secret")
    
    pdf.add_highlight(
        "PROGRAMME VIP EXCLUSIF",
        "Cash-back entreprise premium avec avantages fiscaux, data privilegiee et services concierge."
    )
    
    pdf.add_section("Avantages VIP:")
    avantages = [
        ("Avantages fiscaux", "Optimisation TVA et charges sociales"),
        ("Data Premium", "Analytics comportementaux clients detailles"),
        ("Influence marche", "Priorite sur les tendances sectorielles"),
        ("Investisseurs guests", "Acces reseau investisseurs Titelli"),
        ("Patrimoine", "Conseils patrimoniaux personnalises"),
        ("Labellisation", "Certification qualite Titelli Premium")
    ]
    for titre, desc in avantages:
        pdf.add_section(titre)
        pdf.add_text(desc)
    
    pdf.add_page()
    pdf.add_section("Services Premium VIP:", italic=True)
    services = [
        "Premium + livraison instantanee 24/24",
        "Recrutement personnel instantane (reseau RH Titelli)",
        "Pub 2M et Immobilier acces VIP",
        "Premium depot securise 24/24",
        "Fournisseurs Premium + 20% net garanti",
        "Investissements Premium + 20% net",
        "Expert Marketing dedie",
        "Expert gestion contrats et entreprise",
        "Liquidation stock prioritaire (jusqu'a 20'000 CHF)",
        "Formations et coaching entreprise"
    ]
    for s in services:
        pdf.add_bullet(s, italic=True)
    
    # 4. Tarification
    pdf.add_page()
    pdf.add_chapter(4, "Tarification Complete des Services")
    
    pdf.add_section("Inscriptions et Abonnements")
    pdf.add_table_row("Service", "Prix", header=True)
    pdf.add_table_row("Inscription Entreprise (annuel)", "250 CHF")
    pdf.add_table_row("Premium Entreprise (annuel)", "540 CHF")
    pdf.add_table_row("Premium Entreprise (mensuel)", "45 CHF/mois")
    pdf.add_table_row("Commission transactions", "10-20%")
    pdf.ln(10)
    
    pdf.add_section("Pub Media IA", italic=True)
    pdf.add_table_row("Template", "Prix", header=True)
    pdf.add_table_row("Instagram Post / Story", "24.90 - 29.90 CHF")
    pdf.add_table_row("Hero Banner Web", "49.90 CHF")
    pdf.add_table_row("Menu Restaurant", "39.90 - 44.90 CHF")
    pdf.add_table_row("Flyer / Affiche", "34.90 - 54.90 CHF")
    pdf.add_table_row("Email Marketing", "19.90 - 49.90 CHF")
    pdf.add_table_row("YouTube Thumbnail", "24.90 CHF")
    pdf.add_table_row("Carte de Visite", "34.90 - 39.90 CHF")
    pdf.add_table_row("Creation Sur Mesure", "149.90 CHF")
    pdf.ln(10)
    
    pdf.add_section("Abonnements Client", italic=True)
    pdf.add_table_row("Pass", "Prix mensuel", header=True)
    pdf.add_table_row("Healthy Lifestyle Pass", "99 CHF/mois")
    pdf.add_table_row("Better You Pass", "149 CHF/mois")
    pdf.add_table_row("Special MVP Pass", "299 CHF/mois")
    pdf.add_table_row("Abonnement Romantique RDV", "200 CHF/mois")
    pdf.add_table_row("Titelli Pro++ (B2B)", "199 CHF/mois")
    
    # 5. Services Premium
    pdf.add_page()
    pdf.add_chapter(5, "Services Premium et Avantages")
    
    services_detail = [
        ("Exposition Titelli", "Presence reguliere et forte sur la plateforme, recommendations constantes par algorithme"),
        ("Specialiste Marketing", "Communication personnalisee, gestion image, site web, campagnes reseaux sociaux"),
        ("Referencement Preferentiel", "Suggestions experts + algorithmes IA de recommendation"),
        ("Offres Illimitees", "Gestes commerciaux, fidelisation, liquidation stocks sans limite"),
        ("Livraison 24/24", "Service livraison a domicile en tout temps"),
        ("Fiches Exigences Clients", "Service personnalise basee sur preferences client")
    ]
    
    for titre, desc in services_detail:
        pdf.add_section(titre)
        pdf.add_text(desc)
        pdf.ln(3)
    
    # 6. Labellisation
    pdf.add_page()
    pdf.add_chapter(6, "Labellisation et Certification")
    
    pdf.add_section("Mention Certifie")
    pdf.add_text("Validation par Titelli d'un savoir-faire specifique. Criteres: qualite produits, service client, hygiene, formations.")
    
    pdf.add_section("Label Premium")
    pdf.add_text("Prestations prestigieuses repondant a des exigences particulieres validees par experts Titelli.")
    
    pdf.add_section("Optimisation Fiscale", italic=True)
    pdf.add_text("Expert comptable et juridique pour optimisation fiscale refletant directement sur vos benefices. Service exclusif VIP.")
    
    # 7. Algorithmes
    pdf.add_page()
    pdf.add_chapter(7, "Algorithmes de Recommandation")
    
    pdf.add_section("Algorithme de Scoring Entreprise:", italic=True)
    pdf.add_code_block("""
def calculate_enterprise_score(enterprise):
    score = 0
    
    # Facteurs positifs
    score += enterprise.avg_rating * 20        # Note moyenne (max 100)
    score += min(enterprise.reviews_count, 50) # Nombre avis (max 50)
    score += enterprise.response_rate * 30     # Taux reponse (max 30)
    score += enterprise.is_premium * 50        # Bonus Premium
    score += enterprise.is_certified * 30      # Bonus Certifie
    
    # Boost temporel
    if enterprise.last_activity < 7_days:
        score *= 1.2
    
    return min(score, 300)  # Score max 300
    """, "Algorithme Python - Scoring")
    
    pdf.add_section("Algorithme de Matching RDV Titelli:", italic=True)
    pdf.add_code_block("""
def match_users_for_rdv(user, offers):
    matches = []
    for offer in offers:
        compatibility = 0
        
        # Proximite geographique
        distance = calculate_distance(user.location, offer.location)
        if distance < 5:
            compatibility += 30
        elif distance < 15:
            compatibility += 20
        
        # Interets communs
        common_interests = set(user.interests) & set(offer.categories)
        compatibility += len(common_interests) * 15
        
        # Age matching (si romantique)
        if offer.type == 'romantic':
            age_diff = abs(user.age - offer.creator_age)
            if age_diff < 5:
                compatibility += 25
        
        matches.append((offer, compatibility))
    
    return sorted(matches, key=lambda x: x[1], reverse=True)
    """, "Algorithme Python - Matching RDV")
    
    # 8. Projection
    pdf.add_page()
    pdf.add_chapter(8, "Projection Financiere")
    
    pdf.add_highlight(
        "OBJECTIFS ANNEE 1",
        "Acquisition de 500 entreprises actives et 10'000 utilisateurs clients genrant un GMV de 2M CHF."
    )
    
    pdf.add_section("Metriques Cles:")
    pdf.add_table_row("Metrique", "Objectif An 1", header=True)
    pdf.add_table_row("Entreprises actives", "500")
    pdf.add_table_row("Clients inscrits", "10'000")
    pdf.add_table_row("GMV (Volume transactions)", "2'000'000 CHF")
    pdf.add_table_row("Revenus Titelli (10%)", "200'000 CHF")
    pdf.add_table_row("Cash-back distribue", "200'000 CHF")
    pdf.add_table_row("Panier moyen", "85 CHF")
    pdf.add_table_row("Taux de retention", "65%")
    
    # 9. Conditions
    pdf.add_page()
    pdf.add_chapter(9, "Conditions Generales")
    
    pdf.add_section("Renouvellement")
    pdf.add_text("Renouvellement automatique chaque annee sauf courrier ecrit 30 jours avant echeance.")
    
    pdf.add_section("Resiliation")
    pdf.add_text("Possible a tout moment par email au service client. Solde cash-back utilisable 90 jours apres resiliation.")
    
    pdf.add_section("Confidentialite")
    pdf.add_text("Toutes les donnees sont traitees conformement au RGPD et a la LPD suisse. Chiffrement AES-256.")
    
    # Sauvegarder
    output = f"{OUTPUT_DIR}/CDC_MONETISATION_TITELLI_V2.pdf"
    pdf.output(output)
    print(f"CDC Monetisation V2: {output}")
    return output


def generate_fonctionnalites_v2():
    pdf = TitelliPDFv2()
    
    # Page titre
    pdf.add_title_page(
        "CAHIER DES CHARGES\nFONCTIONNALITES COMPLETES",
        "Specification Technique Detaillee\nArchitecture, APIs, Algorithmes, Pages"
    )
    
    # Table des matieres
    pdf.add_page()
    pdf.add_chapter("", "TABLE DES MATIERES")
    toc = [
        "PARTIE A - ARCHITECTURE TECHNIQUE",
        "  A1. Stack Technologique",
        "  A2. Structure du Code",
        "  A3. Base de Donnees MongoDB",
        "",
        "PARTIE B - FONCTIONNALITES CLIENT",
        "  B1. Cash-Back et Portefeuille",
        "  B2. Navigation et Recherche",
        "  B3. Commandes et Paiements",
        "  B4. RDV chez Titelli (NOUVEAU)",
        "  B5. Demandes Specialistes (NOUVEAU)",
        "  B6. Sports et Competitions (NOUVEAU)",
        "  B7. Gamification et Parrainage (NOUVEAU)",
        "",
        "PARTIE C - FONCTIONNALITES ENTREPRISE",
        "  C1. Dashboard et Analytics",
        "  C2. Gestion Personnel et Stocks",
        "  C3. Pub Media IA (NOUVEAU)",
        "  C4. Titelli Pro++ B2B (NOUVEAU)",
        "",
        "PARTIE D - FONCTIONNALITES ADMIN",
        "  D1. Dashboard Admin",
        "  D2. Validation et Moderation",
        "",
        "PARTIE E - APIs COMPLETES"
    ]
    for item in toc:
        pdf.add_text(item)
    
    # PARTIE A - ARCHITECTURE
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(245, 158, 11)
    pdf.cell(0, 15, "PARTIE A - ARCHITECTURE TECHNIQUE", align='C')
    pdf.ln(25)
    
    pdf.add_chapter("A1", "Stack Technologique")
    
    pdf.add_section("Frontend")
    pdf.add_bullet("React 18.x avec React Router v6")
    pdf.add_bullet("Tailwind CSS + Shadcn/UI")
    pdf.add_bullet("Lucide Icons")
    pdf.add_bullet("Stripe.js pour paiements")
    
    pdf.add_section("Backend")
    pdf.add_bullet("FastAPI (Python 3.11)")
    pdf.add_bullet("Motor (MongoDB async)")
    pdf.add_bullet("Pydantic pour validation")
    pdf.add_bullet("Pillow pour traitement images")
    pdf.add_bullet("Resend pour emails transactionnels")
    
    pdf.add_section("Infrastructure")
    pdf.add_bullet("MongoDB Atlas (Cloud)")
    pdf.add_bullet("Stripe (paiements LIVE)")
    pdf.add_bullet("OpenAI DALL-E (generation images)")
    pdf.add_bullet("Playwright (scraping enrichissement)")
    
    pdf.add_page()
    pdf.add_chapter("A2", "Structure du Code")
    
    pdf.add_code_block("""
/app/
|-- backend/
|   |-- server.py              # Point d'entree (~10,000 lignes)
|   |-- routers/
|   |   |-- rdv_titelli.py     # RDV social booking (1,135 lignes)
|   |   |-- titelli_pro.py     # B2B services (720 lignes)
|   |   |-- media_pub.py       # Pub Media IA (1,200 lignes)
|   |   |-- gamification.py    # Points et badges (591 lignes)
|   |   |-- specialists.py     # Demandes (585 lignes)
|   |   |-- notifications.py   # Push notifications (316 lignes)
|   |   +-- webhooks.py        # Stripe webhooks
|   |-- services/
|   |   +-- email_service.py   # Templates emails
|   +-- uploads/
|       |-- pub_orders/        # Images generees
|       |-- enterprises/       # Logos scraped
|       +-- documents/         # PDFs generes
|
|-- frontend/
|   +-- src/
|       |-- pages/
|       |   |-- MediaPubPage.js        # Editeur pub IA
|       |   |-- RdvTitelliPage.js      # Social booking
|       |   |-- SpecialistsPage.js     # Specialistes
|       |   |-- SportsPage.js          # Sports
|       |   |-- TitelliProPage.js      # B2B
|       |   +-- EnterpriseDashboard.js # Dashboard
|       +-- components/
|           +-- ui/                    # Shadcn components
|
+-- memory/
    +-- PRD.md                         # Documentation projet
    """, "Structure des fichiers")
    
    pdf.add_page()
    pdf.add_chapter("A3", "Base de Donnees MongoDB")
    
    pdf.add_section("Collections Principales:")
    collections = [
        ("users", "Utilisateurs (clients, entreprises, influenceurs, admins)"),
        ("enterprises", "8,249 entreprises Lausanne pre-chargees"),
        ("products", "Catalogue produits"),
        ("orders", "Commandes e-commerce"),
        ("pub_orders", "Commandes Pub Media IA"),
        ("shared_offers", "Offres RDV Titelli"),
        ("chat_rooms", "Salons de discussion"),
        ("chat_messages", "Messages chat"),
        ("specialist_requests", "Demandes specialistes"),
        ("sports_matches", "Matchs sportifs"),
        ("notifications", "Notifications push"),
        ("gamification_points", "Points et niveaux"),
        ("payment_transactions", "Transactions Stripe"),
        ("cashback_wallets", "Portefeuilles cash-back")
    ]
    for name, desc in collections:
        pdf.add_bullet(f"{name}: {desc}")
    
    # PARTIE B - CLIENT
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(245, 158, 11)
    pdf.cell(0, 15, "PARTIE B - FONCTIONNALITES CLIENT", align='C')
    pdf.ln(25)
    
    pdf.add_chapter("B1", "Cash-Back et Portefeuille")
    pdf.add_text("Systeme de fidelisation avec 10% de retour sur chaque achat.")
    pdf.add_section("Fonctionnalites:")
    pdf.add_bullet("Accumulation automatique 10% par transaction")
    pdf.add_bullet("Consultation solde temps reel")
    pdf.add_bullet("Utilisation sur toute la plateforme")
    pdf.add_bullet("Transfert entre utilisateurs")
    pdf.add_bullet("Historique complet transactions")
    pdf.add_bullet("Notifications de credit")
    
    pdf.add_page()
    pdf.add_chapter("B4", "RDV chez Titelli (NOUVEAU)")
    pdf.add_text("Fonctionnalite sociale permettant de partager des activites a deux (amical ou romantique).", italic=True)
    
    pdf.add_section("Caracteristiques:", italic=True)
    pdf.add_bullet("8 categories: restaurant, sport, wellness, culture, nature, party, creative, autre", italic=True)
    pdf.add_bullet("Types: amical ou romantique", italic=True)
    pdf.add_bullet("Systeme d'invitations avec acceptation payante (2 CHF)", italic=True)
    pdf.add_bullet("Abonnement romantique: 200 CHF/mois (invitations illimitees)", italic=True)
    pdf.add_bullet("Chat temps reel WebSocket entre participants", italic=True)
    
    pdf.add_section("API Endpoints:", italic=True)
    pdf.add_api_endpoint("POST", "/api/rdv/offers", "Creer une offre")
    pdf.add_api_endpoint("GET", "/api/rdv/offers", "Lister les offres")
    pdf.add_api_endpoint("POST", "/api/rdv/invitations/{id}/accept", "Accepter (2 CHF)")
    pdf.add_api_endpoint("POST", "/api/rdv/subscriptions/romantic", "S'abonner (200 CHF/mois)")
    pdf.add_api_endpoint("WS", "/ws/rdv/{room_id}", "Chat temps reel")
    
    pdf.add_page()
    pdf.add_chapter("B5", "Demandes Specialistes (NOUVEAU)")
    pdf.add_text("Recherche et demandes de prestataires specialises via IA.", italic=True)
    
    pdf.add_section("10 Categories:", italic=True)
    cats = ["Plomberie", "Electricite", "Menuiserie", "Peinture", "Jardinage", 
            "Nettoyage", "Demenagement", "Informatique", "Coaching", "Autre"]
    for c in cats:
        pdf.add_bullet(c, italic=True)
    
    pdf.add_section("Fonctionnalites:", italic=True)
    pdf.add_bullet("Recherche IA de specialistes", italic=True)
    pdf.add_bullet("Creation demandes urgentes/specifiques", italic=True)
    pdf.add_bullet("Systeme de reponses prestataires", italic=True)
    pdf.add_bullet("Notation et avis", italic=True)
    
    pdf.add_page()
    pdf.add_chapter("B6", "Sports et Competitions (NOUVEAU)")
    pdf.add_text("Plateforme sportive pour trouver partenaires et organiser competitions.", italic=True)
    
    pdf.add_section("11 Sports:", italic=True)
    sports = ["Football", "Tennis", "Basketball", "Volleyball", "Badminton", 
              "Padel", "Running", "Swimming", "Cycling", "Fitness", "Autre"]
    for s in sports:
        pdf.add_bullet(s, italic=True)
    
    pdf.add_section("Fonctionnalites:", italic=True)
    pdf.add_bullet("Creer matchs (cherche adversaire/joueurs/equipe)", italic=True)
    pdf.add_bullet("Gestion d'equipes", italic=True)
    pdf.add_bullet("Competitions et tournois", italic=True)
    pdf.add_bullet("Classements et statistiques", italic=True)
    
    pdf.add_page()
    pdf.add_chapter("B7", "Gamification et Parrainage (NOUVEAU)")
    pdf.add_text("Systeme de points, niveaux, badges et parrainage.", italic=True)
    
    pdf.add_section("Points par action:", italic=True)
    pdf.add_bullet("+5 points: connexion quotidienne", italic=True)
    pdf.add_bullet("+10 points: premier achat", italic=True)
    pdf.add_bullet("+15 points: laisser un avis", italic=True)
    pdf.add_bullet("+50 points: parrainage reussi", italic=True)
    pdf.add_bullet("+25 points: etre parraine", italic=True)
    
    pdf.add_section("8 Niveaux:", italic=True)
    niveaux = ["Debutant (0)", "Explorateur (100)", "Amateur (300)", "Connaisseur (600)",
               "Expert (1000)", "Master (2000)", "Champion (5000)", "Titan (10000)"]
    for n in niveaux:
        pdf.add_bullet(n, italic=True)
    
    pdf.add_section("Bonus Parrainage:", italic=True)
    pdf.add_bullet("5 parrainages: +100 points bonus", italic=True)
    pdf.add_bullet("10 parrainages: +250 points bonus", italic=True)
    pdf.add_bullet("25 parrainages: +500 points bonus + Badge Influenceur", italic=True)
    
    # PARTIE C - ENTREPRISE
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(245, 158, 11)
    pdf.cell(0, 15, "PARTIE C - FONCTIONNALITES ENTREPRISE", align='C')
    pdf.ln(25)
    
    pdf.add_chapter("C3", "Pub Media IA (NOUVEAU)")
    pdf.add_text("Systeme de creation de publicites professionnelles avec intelligence artificielle.", italic=True)
    
    pdf.add_section("Processus:", italic=True)
    pdf.add_bullet("1. Selection template parmi 34 modeles", italic=True)
    pdf.add_bullet("2. Personnalisation: slogan, couleurs, texte", italic=True)
    pdf.add_bullet("3. Apercu avec filigrane TITELLI", italic=True)
    pdf.add_bullet("4. Paiement Stripe", italic=True)
    pdf.add_bullet("5. Generation IA (DALL-E) + post-processing Pillow", italic=True)
    pdf.add_bullet("6. Telechargement HD sans filigrane", italic=True)
    
    pdf.add_section("Categories Templates:", italic=True)
    cats = ["Reseaux Sociaux (Instagram, Facebook)", "Bannieres Web (Hero, Sidebar)",
            "Restauration (Menus elegant, bistro, moderne)", "Flyers et Affiches",
            "Email Marketing (Headers, Newsletters)", "Video (YouTube Thumbnails)",
            "Print (Cartes de visite, Brochures)"]
    for c in cats:
        pdf.add_bullet(c, italic=True)
    
    pdf.add_section("Algorithme Generation:", italic=True)
    pdf.add_code_block("""
async def generate_pub_image(order_data):
    # 1. Generer image de fond sans texte (DALL-E)
    prompt = build_prompt(order_data)  # Pas de texte dans le prompt!
    background = await dalle.generate(prompt, model="gpt-image-1")
    
    # 2. Post-processing texte avec Pillow
    img = Image.open(BytesIO(background))
    draw = ImageDraw.Draw(img)
    
    # Ajouter overlay semi-transparent en bas
    overlay = create_gradient_overlay(img.size)
    img.paste(overlay, mask=overlay)
    
    # Dessiner texte parfait
    font_large = ImageFont.truetype("DejaVuSans-Bold.ttf", 55)
    draw.text((50, height-200), product_name, font=font_large, fill=primary_color)
    draw.text((50, height-130), slogan, font=font_medium, fill=(255,255,255))
    
    return img
    """, "Algorithme Python - Generation Pub Media")
    
    pdf.add_page()
    pdf.add_chapter("C4", "Titelli Pro++ B2B (NOUVEAU)")
    pdf.add_text("Services B2B pour livraisons recurrentes et liquidation de stocks.", italic=True)
    
    pdf.add_section("Fonctionnalites:", italic=True)
    pdf.add_bullet("Livraisons B2B recurrentes (quotidien/hebdo/mensuel)", italic=True)
    pdf.add_bullet("Liquidation de stock (surstock, fin saison, expiration)", italic=True)
    pdf.add_bullet("Abonnement Pro++: 199 CHF/mois", italic=True)
    pdf.add_bullet("Analytics B2B dedies", italic=True)
    pdf.add_bullet("Restriction: reserve aux comptes entreprise", italic=True)
    
    # PARTIE D - ADMIN
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(245, 158, 11)
    pdf.cell(0, 15, "PARTIE D - FONCTIONNALITES ADMIN", align='C')
    pdf.ln(25)
    
    pdf.add_chapter("D1", "Dashboard Admin")
    pdf.add_section("Statistiques Globales:")
    pdf.add_bullet("Nombre total utilisateurs par type")
    pdf.add_bullet("Volume transactions journalier/mensuel")
    pdf.add_bullet("Revenus et commissions")
    pdf.add_bullet("Graphiques tendances")
    
    pdf.add_section("Gestion:")
    pdf.add_bullet("Validation inscriptions entreprises")
    pdf.add_bullet("Moderation avis et contenus")
    pdf.add_bullet("Gestion offres et promotions")
    pdf.add_bullet("Labellisation et certification")
    
    # PARTIE E - APIs
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(245, 158, 11)
    pdf.cell(0, 15, "PARTIE E - APIs COMPLETES", align='C')
    pdf.ln(25)
    
    pdf.add_chapter("", "Endpoints Principaux")
    
    pdf.add_section("Authentification")
    pdf.add_api_endpoint("POST", "/api/auth/register", "Inscription")
    pdf.add_api_endpoint("POST", "/api/auth/login", "Connexion")
    pdf.add_api_endpoint("GET", "/api/auth/me", "Profil actuel")
    
    pdf.add_section("Entreprises")
    pdf.add_api_endpoint("GET", "/api/enterprises", "Liste entreprises")
    pdf.add_api_endpoint("GET", "/api/enterprises/{id}", "Detail entreprise")
    pdf.add_api_endpoint("POST", "/api/enterprises/register", "Inscription entreprise")
    
    pdf.add_section("Produits et Commandes")
    pdf.add_api_endpoint("GET", "/api/products", "Liste produits")
    pdf.add_api_endpoint("POST", "/api/cart/add", "Ajouter au panier")
    pdf.add_api_endpoint("POST", "/api/orders/checkout", "Passer commande")
    
    pdf.add_section("Pub Media (NOUVEAU)", italic=True)
    pdf.add_api_endpoint("GET", "/api/media-pub/templates", "Liste templates")
    pdf.add_api_endpoint("POST", "/api/media-pub/orders", "Creer commande")
    pdf.add_api_endpoint("POST", "/api/media-pub/payment/create-session", "Session Stripe")
    pdf.add_api_endpoint("GET", "/api/media-pub/payment/status/{session}", "Statut paiement")
    
    pdf.add_section("RDV Titelli (NOUVEAU)", italic=True)
    pdf.add_api_endpoint("GET", "/api/rdv/offers", "Liste offres")
    pdf.add_api_endpoint("POST", "/api/rdv/offers", "Creer offre")
    pdf.add_api_endpoint("POST", "/api/rdv/invitations/{id}/accept", "Accepter invitation")
    
    pdf.add_section("Gamification (NOUVEAU)", italic=True)
    pdf.add_api_endpoint("GET", "/api/gamification/my-stats", "Mes points")
    pdf.add_api_endpoint("GET", "/api/gamification/referral/my-code", "Code parrainage")
    pdf.add_api_endpoint("POST", "/api/gamification/referral/apply", "Appliquer code")
    
    # Sauvegarder
    output = f"{OUTPUT_DIR}/CDC_FONCTIONNALITES_TITELLI_V2.pdf"
    pdf.output(output)
    print(f"CDC Fonctionnalites V2: {output}")
    return output


if __name__ == "__main__":
    print("=" * 60)
    print("GENERATION DES CAHIERS DES CHARGES V2.0 DETAILLES")
    print("=" * 60)
    
    path1 = generate_monetisation_v2()
    path2 = generate_fonctionnalites_v2()
    
    print(f"\n{'=' * 60}")
    print("FICHIERS GENERES:")
    print(f"  {path1}")
    print(f"  {path2}")
    print(f"{'=' * 60}")
