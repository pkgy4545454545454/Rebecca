#!/usr/bin/env python3
"""
Générateur de CDC Complet Titelli - Version Détaillée
Inclut: Architecture, Pages, Fonctions, Algorithmes
"""
from fpdf import FPDF
from datetime import datetime
import os

OUTPUT_DIR = "/app/backend/uploads/documents"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class TitelliDetailedPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_margins(12, 12, 12)
        self.set_auto_page_break(auto=True, margin=12)
    
    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(245, 158, 11)
        self.cell(95, 8, 'TITELLI - CDC COMPLET')
        self.set_text_color(150, 150, 150)
        self.set_font('Helvetica', '', 7)
        self.cell(95, 8, f'{datetime.now().strftime("%d/%m/%Y")}', align='R')
        self.ln(12)
        
    def footer(self):
        self.set_y(-12)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, f'Page {self.page_no()}', align='C')

    def title_page(self, title, subtitle):
        self.add_page()
        self.ln(50)
        self.set_font('Helvetica', 'B', 26)
        self.set_text_color(245, 158, 11)
        self.multi_cell(0, 12, title, align='C')
        self.ln(8)
        self.set_font('Helvetica', '', 12)
        self.set_text_color(100, 100, 100)
        self.multi_cell(0, 7, subtitle, align='C')
        self.ln(25)
        self.set_font('Helvetica', '', 10)
        self.cell(0, 8, f'Date: {datetime.now().strftime("%d %B %Y")}', align='C')
        self.ln(6)
        self.cell(0, 8, 'Version: 2.0 - Detaillee', align='C')

    def chapter(self, num, title):
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(245, 158, 11)
        self.ln(3)
        self.cell(0, 9, f'{num}. {title}')
        self.ln(9)

    def section(self, title, is_new=False):
        self.set_x(self.l_margin)
        if is_new:
            self.set_font('Helvetica', 'BI', 10)  # Bold Italic pour nouveautés
            self.set_text_color(34, 139, 34)  # Vert pour nouveautés
        else:
            self.set_font('Helvetica', 'B', 10)
            self.set_text_color(60, 60, 60)
        self.multi_cell(0, 7, title)

    def text(self, text, is_new=False):
        self.set_x(self.l_margin)
        if is_new:
            self.set_font('Helvetica', 'I', 9)
            self.set_text_color(34, 139, 34)
        else:
            self.set_font('Helvetica', '', 9)
            self.set_text_color(80, 80, 80)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def bullet(self, text, is_new=False):
        self.set_x(self.l_margin)
        if is_new:
            self.set_font('Helvetica', 'I', 9)
            self.set_text_color(34, 139, 34)
            self.multi_cell(0, 5, f"   [NEW] {text}")
        else:
            self.set_font('Helvetica', '', 9)
            self.set_text_color(80, 80, 80)
            self.multi_cell(0, 5, f"   - {text}")

    def code_block(self, code):
        self.set_x(self.l_margin)
        self.set_font('Courier', '', 8)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 4, code, fill=True)
        self.ln(2)

    def highlight(self, title, text, is_new=False):
        if is_new:
            self.set_fill_color(34, 139, 34)
        else:
            self.set_fill_color(245, 158, 11)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 9)
        self.cell(0, 7, f'  {title}', fill=True)
        self.ln(7)
        self.set_fill_color(250, 250, 250)
        self.set_text_color(60, 60, 60)
        self.set_font('Helvetica', '', 9)
        self.multi_cell(0, 5, text, fill=True)
        self.ln(4)


def generate_cdc_complet():
    pdf = TitelliDetailedPDF()
    
    # Page titre
    pdf.title_page(
        "CAHIER DES CHARGES COMPLET\nTITELLI",
        "Architecture, Code, Pages, Fonctions, Algorithmes\nVersion Detaillee avec Nouveautes 05/02/2026"
    )
    
    # ============ TABLE DES MATIERES ============
    pdf.add_page()
    pdf.chapter("", "TABLE DES MATIERES")
    toc = [
        "1. VUE D'ENSEMBLE DU PROJET",
        "2. ARCHITECTURE TECHNIQUE",
        "3. STRUCTURE DU CODE",
        "4. PAGES FRONTEND (22 pages)",
        "5. ROUTES BACKEND API",
        "6. BASE DE DONNEES MONGODB",
        "7. FONCTIONNALITES DETAILLEES",
        "8. ALGORITHMES ET LOGIQUE METIER",
        "9. INTEGRATIONS TIERCES",
        "10. [NOUVEAU] PUB MEDIA IA - 05/02/2026",
        "11. SECURITE ET AUTHENTIFICATION",
        "12. TESTS ET QUALITE"
    ]
    for item in toc:
        if "[NOUVEAU]" in item:
            pdf.bullet(item, is_new=True)
        else:
            pdf.bullet(item)
    
    # ============ 1. VUE D'ENSEMBLE ============
    pdf.add_page()
    pdf.chapter(1, "VUE D'ENSEMBLE DU PROJET")
    
    pdf.section("Description")
    pdf.text("Titelli est une plateforme de social commerce regionale pour la Suisse (region Lausanne). Elle connecte entreprises locales et clients pour services (beaute, restauration, bien-etre) et produits.")
    
    pdf.section("Objectifs Business")
    pdf.bullet("Connecter prestataires regionaux aux clients")
    pdf.bullet("Systeme de Cash-Back 10% pour fidelisation")
    pdf.bullet("Labellisation et certification des prestataires")
    pdf.bullet("Services Premium et a la carte")
    pdf.bullet("Generation de publicites IA", is_new=True)
    
    pdf.section("Metriques Cles")
    pdf.bullet("22 pages frontend React")
    pdf.bullet("50+ endpoints API REST")
    pdf.bullet("15+ collections MongoDB")
    pdf.bullet("34 templates Pub Media", is_new=True)
    
    # ============ 2. ARCHITECTURE ============
    pdf.add_page()
    pdf.chapter(2, "ARCHITECTURE TECHNIQUE")
    
    pdf.section("Stack Technologique")
    pdf.text("Frontend: React 18 + TailwindCSS + Shadcn/UI")
    pdf.text("Backend: FastAPI (Python 3.11) + Motor (async MongoDB)")
    pdf.text("Base de donnees: MongoDB Atlas")
    pdf.text("Paiements: Stripe (checkout + webhooks)")
    pdf.text("IA: OpenAI DALL-E + Pillow post-processing", is_new=True)
    
    pdf.section("Architecture Fichiers")
    pdf.code_block("""/app/
├── frontend/
│   ├── src/
│   │   ├── pages/          # 22 pages React
│   │   ├── components/     # Composants reutilisables
│   │   │   ├── ui/         # Shadcn components
│   │   │   └── dashboard/  # Composants dashboard
│   │   ├── context/        # AuthContext, CartContext
│   │   └── App.js          # Router principal
│   └── package.json
├── backend/
│   ├── server.py           # API principale (~10000 lignes)
│   ├── routers/
│   │   ├── media_pub.py    # [NOUVEAU] Pub Media IA
│   │   ├── cashback.py     # Systeme cashback
│   │   ├── titelli_pro.py  # Services B2B
│   │   └── sports.py       # Competitions
│   ├── uploads/            # Fichiers statiques
│   └── requirements.txt""")
    
    # ============ 3. STRUCTURE CODE ============
    pdf.add_page()
    pdf.chapter(3, "STRUCTURE DU CODE")
    
    pdf.section("Frontend - Composants Principaux")
    pdf.bullet("Header.js - Navigation, recherche, panier, auth")
    pdf.bullet("Footer.js - Liens, reseaux sociaux")
    pdf.bullet("SplashScreen.js - Animation logo au demarrage")
    pdf.bullet("MainLayout.js - Layout avec header/footer")
    
    pdf.section("Backend - Organisation")
    pdf.bullet("server.py - Routes principales (auth, users, orders, etc.)")
    pdf.bullet("routers/ - Modules separes (media_pub, cashback, sports)")
    pdf.bullet("stripe_helper.py - Integration paiements Stripe")
    
    pdf.section("Contextes React")
    pdf.bullet("AuthContext - Gestion authentification JWT")
    pdf.bullet("CartContext - Panier multi-prestataires")
    
    # ============ 4. PAGES FRONTEND ============
    pdf.add_page()
    pdf.chapter(4, "PAGES FRONTEND (22 pages)")
    
    pdf.section("Pages Publiques")
    pages_public = [
        ("HomePage.js", "Page d'accueil avec hero, services, tendances, offres"),
        ("AuthPage.js", "Connexion/Inscription avec validation"),
        ("ServicesPage.js", "Liste services avec filtres et recherche"),
        ("ProductsPage.js", "Liste produits avec categories"),
        ("EnterprisesPage.js", "Annuaire prestataires avec carte"),
        ("EnterprisePage.js", "Profil detaille d'un prestataire"),
        ("AboutPage.js", "[NOUVEAU] Vision, Mission, Avantages Titelli"),
        ("CGVPage.js", "[NOUVEAU] Conditions Generales de Vente"),
        ("MentionsLegalesPage.js", "[NOUVEAU] Mentions legales, RGPD"),
    ]
    for page, desc in pages_public:
        if "[NOUVEAU]" in desc:
            pdf.bullet(f"{page}: {desc}", is_new=True)
        else:
            pdf.bullet(f"{page}: {desc}")
    
    pdf.section("Pages Client")
    pages_client = [
        ("ClientDashboard.js", "Tableau de bord client (commandes, cashback, favoris)"),
        ("ClientProfilePage.js", "Profil et preferences client"),
        ("CartPage.js", "Panier avec calcul cashback"),
        ("OrdersPage.js", "Historique des commandes"),
    ]
    for page, desc in pages_client:
        pdf.bullet(f"{page}: {desc}")
    
    pdf.section("Pages Entreprise")
    pages_enterprise = [
        ("EnterpriseDashboard.js", "Dashboard complet (stats, commandes, stocks, personnel)"),
        ("EnterpriseRegistrationPage.js", "Inscription prestataire multi-etapes"),
        ("MediaPubPage.js", "[NOUVEAU] Creation publicites IA style Canva"),
    ]
    for page, desc in pages_enterprise:
        if "[NOUVEAU]" in desc:
            pdf.bullet(f"{page}: {desc}", is_new=True)
        else:
            pdf.bullet(f"{page}: {desc}")
    
    pdf.section("Pages Admin")
    pdf.bullet("AdminDashboard.js: Gestion complete plateforme")
    
    pdf.section("Pages Specialisees")
    pages_special = [
        ("TitelliProPage.js", "Services B2B premium"),
        ("SportsPage.js", "Competitions et paris sportifs"),
        ("RdvTitelliPage.js", "Rendez-vous avec chat IA"),
        ("SpecialistsPage.js", "Annuaire specialistes"),
        ("JobsPage.js", "Offres d'emploi"),
    ]
    for page, desc in pages_special:
        pdf.bullet(f"{page}: {desc}")
    
    # ============ 5. ROUTES API ============
    pdf.add_page()
    pdf.chapter(5, "ROUTES BACKEND API")
    
    pdf.section("Authentification (/api/auth)")
    pdf.bullet("POST /register - Inscription utilisateur")
    pdf.bullet("POST /login - Connexion avec JWT")
    pdf.bullet("GET /me - Profil utilisateur connecte")
    pdf.bullet("PUT /me - Mise a jour profil")
    
    pdf.section("Utilisateurs (/api/users)")
    pdf.bullet("GET /clients - Liste clients (admin)")
    pdf.bullet("GET /enterprises - Liste entreprises")
    pdf.bullet("GET /influencers - Liste influenceurs")
    
    pdf.section("Services et Produits")
    pdf.bullet("GET /api/services - Liste services avec filtres")
    pdf.bullet("GET /api/products - Liste produits")
    pdf.bullet("GET /api/service-products/{id} - Detail service/produit")
    pdf.bullet("POST /api/service-products - Creer (entreprise)")
    
    pdf.section("Commandes (/api/orders)")
    pdf.bullet("POST /create - Creer commande")
    pdf.bullet("GET /client - Commandes du client")
    pdf.bullet("GET /enterprise - Commandes pour l'entreprise")
    pdf.bullet("PUT /{id}/status - Mettre a jour statut")
    
    pdf.section("[NOUVEAU] Pub Media IA (/api/media-pub)", is_new=True)
    pdf.bullet("GET /templates - Liste des 34 templates", is_new=True)
    pdf.bullet("POST /orders - Creer commande pub avec generation IA", is_new=True)
    pdf.bullet("GET /orders/{id} - Statut commande et image", is_new=True)
    pdf.bullet("GET /orders?enterprise_id=X - Commandes entreprise", is_new=True)
    
    pdf.section("Cash-Back (/api/cashback)")
    pdf.bullet("GET /balance - Solde cashback")
    pdf.bullet("GET /transactions - Historique")
    pdf.bullet("POST /transfer - Transfert entre utilisateurs")
    
    # ============ 6. BASE DE DONNEES ============
    pdf.add_page()
    pdf.chapter(6, "BASE DE DONNEES MONGODB")
    
    pdf.section("Collections Principales")
    collections = [
        ("users", "Tous les utilisateurs (clients, entreprises, admins)"),
        ("enterprises", "Profils detailles des prestataires"),
        ("services", "Catalogue des services"),
        ("products", "Catalogue des produits"),
        ("orders", "Commandes clients"),
        ("cashback_transactions", "Historique cashback"),
        ("notifications", "Notifications utilisateurs"),
        ("pub_orders", "[NOUVEAU] Commandes publicites IA"),
    ]
    for coll, desc in collections:
        if "[NOUVEAU]" in desc:
            pdf.bullet(f"{coll}: {desc}", is_new=True)
        else:
            pdf.bullet(f"{coll}: {desc}")
    
    pdf.section("Schema: users")
    pdf.code_block("""{
  "id": "uuid",
  "email": "string (unique)",
  "password_hash": "bcrypt hash",
  "user_type": "client|entreprise|admin|influencer",
  "first_name": "string",
  "last_name": "string",
  "created_at": "datetime"
}""")
    
    pdf.section("[NOUVEAU] Schema: pub_orders", is_new=True)
    pdf.code_block("""{
  "id": "uuid court (8 chars)",
  "enterprise_id": "ref enterprises",
  "user_id": "ref users",
  "template_id": "string",
  "template_name": "string",
  "slogan": "string",
  "product_name": "string",
  "description": "string",
  "brand_colors": ["#hex", "#hex"],
  "status": "processing|completed|failed",
  "image_url": "url image generee",
  "price": "number",
  "created_at": "datetime",
  "completed_at": "datetime"
}""")
    
    # ============ 7. FONCTIONNALITES ============
    pdf.add_page()
    pdf.chapter(7, "FONCTIONNALITES DETAILLEES")
    
    pdf.section("7.1 Systeme d'Authentification")
    pdf.text("Methode: JWT (JSON Web Tokens) avec expiration 7 jours")
    pdf.text("Stockage: Token dans localStorage, password hash bcrypt")
    pdf.text("Verification: Middleware verify_token sur routes protegees")
    pdf.code_block("""# Verification JWT
async def verify_token(token: str):
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    user = await db.users.find_one({"id": payload["sub"]})
    return user""")
    
    pdf.section("7.2 Systeme Cash-Back")
    pdf.text("Fonctionnement: 10% du montant achat credite au client")
    pdf.text("Disponibilite: Premier jour du mois suivant")
    pdf.text("Utilisation: Deductible sur toute commande plateforme")
    pdf.code_block("""# Calcul cashback
cashback_amount = order_total * 0.10
await db.cashback_transactions.insert_one({
    "user_id": user_id,
    "amount": cashback_amount,
    "type": "credit",
    "available_date": first_day_next_month
})""")
    
    pdf.section("[NOUVEAU] 7.3 Generation Pub Media IA", is_new=True)
    pdf.text("ETAPE 1: Selection template parmi 34 modeles (7 categories)", is_new=True)
    pdf.text("ETAPE 2: Personnalisation (slogan, couleurs, description)", is_new=True)
    pdf.text("ETAPE 3: Generation image IA avec DALL-E (fond sans texte)", is_new=True)
    pdf.text("ETAPE 4: Post-processing Pillow (ajout texte parfait)", is_new=True)
    pdf.text("ETAPE 5: Sauvegarde et notification utilisateur", is_new=True)
    pdf.text("DELAI: Resultat disponible en environ 1h dans section dediee", is_new=True)
    
    pdf.section("7.4 Gestion des Commandes")
    pdf.text("Statuts: pending -> confirmed -> preparing -> ready -> delivered")
    pdf.text("Notifications: Push a chaque changement de statut")
    pdf.text("Historique: Complet avec filtres par date/statut")
    
    # ============ 8. ALGORITHMES ============
    pdf.add_page()
    pdf.chapter(8, "ALGORITHMES ET LOGIQUE METIER")
    
    pdf.section("8.1 Algorithme de Recherche")
    pdf.text("Methode: Recherche full-text MongoDB avec scoring")
    pdf.code_block("""# Recherche avec scoring
pipeline = [
    {"$match": {"$text": {"$search": query}}},
    {"$addFields": {"score": {"$meta": "textScore"}}},
    {"$sort": {"score": -1, "rating": -1}},
    {"$limit": 20}
]
results = await db.services.aggregate(pipeline).to_list()""")
    
    pdf.section("8.2 Algorithme de Suggestions")
    pdf.text("Base: Historique achats + preferences + popularite")
    pdf.code_block("""# Suggestions personnalisees
user_categories = get_user_purchase_categories(user_id)
popular = await db.services.find({
    "category": {"$in": user_categories},
    "rating": {"$gte": 4.0}
}).sort("order_count", -1).limit(10)""")
    
    pdf.section("[NOUVEAU] 8.3 Algorithme Generation Pub IA", is_new=True)
    pdf.text("1. Construction prompt optimise (sans texte)", is_new=True)
    pdf.text("2. Appel DALL-E avec Emergent LLM Key", is_new=True)
    pdf.text("3. Reception image bytes", is_new=True)
    pdf.text("4. Post-processing Pillow:", is_new=True)
    pdf.code_block("""# Post-processing texte parfait
def add_text_overlay(image_bytes, product_name, slogan, description, colors):
    img = Image.open(BytesIO(image_bytes))
    draw = ImageDraw.Draw(img)
    
    # Overlay semi-transparent en bas
    overlay = Image.new('RGBA', (width, overlay_height), (0,0,0,200))
    img.paste(overlay, (0, height - overlay_height), overlay)
    
    # Ajout texte avec police DejaVuSans
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    draw.text((x, y), product_name, font=font, fill=primary_color)
    draw.text((x, y+offset), slogan, font=font, fill=(255,255,255))
    
    return img.tobytes()""")
    
    pdf.section("8.4 Algorithme Calcul Tarifs Livraison")
    pdf.code_block("""# Calcul livraison
if delivery_type == "standard":
    fee = 5.90
elif delivery_type == "express":
    fee = 12.90
elif delivery_type == "24h":
    fee = 24.90
    
# Livraison gratuite des 50 CHF
if order_total >= 50:
    fee = 0""")
    
    # ============ 9. INTEGRATIONS ============
    pdf.add_page()
    pdf.chapter(9, "INTEGRATIONS TIERCES")
    
    pdf.section("9.1 Stripe - Paiements")
    pdf.text("Mode: Checkout Sessions avec webhooks")
    pdf.text("Evenements: checkout.session.completed, payment_intent.succeeded")
    pdf.code_block("""# Creation session Stripe
session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{
        'price_data': {
            'currency': 'chf',
            'product_data': {'name': product_name},
            'unit_amount': int(price * 100)
        },
        'quantity': 1
    }],
    mode='payment',
    success_url=f"{BASE_URL}/payment-success?session_id={{CHECKOUT_SESSION_ID}}",
    cancel_url=f"{BASE_URL}/payment-cancel"
)""")
    
    pdf.section("[NOUVEAU] 9.2 OpenAI DALL-E - Generation Images", is_new=True)
    pdf.text("Modele: gpt-image-1 via emergentintegrations", is_new=True)
    pdf.text("Cle: Emergent LLM Key (universelle)", is_new=True)
    pdf.text("Cout: ~0.04-0.08 USD par image", is_new=True)
    pdf.code_block("""# Generation image DALL-E
from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration

image_gen = OpenAIImageGeneration(api_key=EMERGENT_LLM_KEY)
images = await image_gen.generate_images(
    prompt=prompt,  # Sans texte dans l'image
    model="gpt-image-1",
    number_of_images=1
)""")
    
    pdf.section("9.3 MongoDB Atlas")
    pdf.text("Driver: Motor (async)")
    pdf.text("Connexion: Connection pooling automatique")
    pdf.text("Indexes: text, compound pour recherche optimisee")
    
    # ============ 10. PUB MEDIA IA ============
    pdf.add_page()
    pdf.chapter(10, "[NOUVEAU] PUB MEDIA IA - 05/02/2026")
    
    pdf.highlight("FONCTIONNALITE COMPLETE", 
        "Systeme de creation de publicites professionnelles avec IA. "
        "Interface style editeur graphique avec apercu en direct. "
        "Generation automatique via DALL-E + post-processing texte Pillow.", is_new=True)
    
    pdf.section("Categories de Templates (34 total)", is_new=True)
    categories = [
        "Reseaux Sociaux (Instagram, Facebook) - 8 templates",
        "Bannieres Web (Hero, Sidebar) - 6 templates", 
        "Restauration (Menus) - 8 templates",
        "Flyers & Affiches - 4 templates",
        "Email Marketing - 4 templates",
        "Stories - 2 templates",
        "Cartes de visite - 2 templates"
    ]
    for cat in categories:
        pdf.bullet(cat, is_new=True)
    
    pdf.section("Tarification Pub Media", is_new=True)
    pdf.bullet("Templates standards: 29.90 - 49.90 CHF", is_new=True)
    pdf.bullet("Creation Sur Mesure: 149.90 CHF", is_new=True)
    pdf.bullet("Cout generation IA: ~0.10 CHF (marge 99%+)", is_new=True)
    
    pdf.section("Protection Anti-Screenshot", is_new=True)
    pdf.text("Filigrane 'TITELLI' visible sur apercu jusqu'au paiement", is_new=True)
    pdf.text("Image finale HD sans filigrane apres paiement", is_new=True)
    
    pdf.section("Delai et Livraison", is_new=True)
    pdf.highlight("IMPORTANT",
        "Le resultat de la generation sera disponible en environ 1 HEURE "
        "dans la section 'Commandes Titelli' du dashboard entreprise. "
        "Une notification sera envoyee avec lien direct vers l'image.", is_new=True)
    
    pdf.section("Fichiers Concernes", is_new=True)
    pdf.bullet("Frontend: /app/frontend/src/pages/MediaPubPage.js (~1000 lignes)", is_new=True)
    pdf.bullet("Backend: /app/backend/routers/media_pub.py (~800 lignes)", is_new=True)
    pdf.bullet("Dashboard: CommandesTitelliSection.js (affichage commandes)", is_new=True)
    
    # ============ 11. SECURITE ============
    pdf.add_page()
    pdf.chapter(11, "SECURITE ET AUTHENTIFICATION")
    
    pdf.section("11.1 Authentification JWT")
    pdf.bullet("Algorithme: HS256")
    pdf.bullet("Expiration: 7 jours")
    pdf.bullet("Stockage: localStorage (client)")
    pdf.bullet("Verification: Middleware sur chaque requete protegee")
    
    pdf.section("11.2 Protection des Donnees")
    pdf.bullet("Passwords: Hash bcrypt avec salt")
    pdf.bullet("CORS: Origins specifiques autorisees")
    pdf.bullet("Rate Limiting: Sur endpoints sensibles")
    pdf.bullet("Validation: Pydantic schemas sur toutes les entrees")
    
    pdf.section("11.3 Conformite")
    pdf.bullet("LPD Suisse: Conforme")
    pdf.bullet("RGPD: Droits acces, rectification, suppression")
    pdf.bullet("Cookies: Consentement utilisateur")
    
    # ============ 12. TESTS ============
    pdf.add_page()
    pdf.chapter(12, "TESTS ET QUALITE")
    
    pdf.section("Tests Backend")
    pdf.bullet("Framework: pytest avec async support")
    pdf.bullet("Coverage: Endpoints principaux")
    pdf.bullet("Rapports: /app/test_reports/iteration_*.json")
    
    pdf.section("Tests Frontend")
    pdf.bullet("Methode: Playwright automation")
    pdf.bullet("Screenshots: Verification visuelle")
    pdf.bullet("data-testid: Sur tous les elements interactifs")
    
    pdf.section("[NOUVEAU] Tests Pub Media IA", is_new=True)
    pdf.bullet("17/17 tests backend passes (100%)", is_new=True)
    pdf.bullet("Verification frontend: OK", is_new=True)
    pdf.bullet("Generation image: Testee avec succes", is_new=True)
    
    # Sauvegarder
    output = f"{OUTPUT_DIR}/CDC_COMPLET_TITELLI_DETAILLE.pdf"
    pdf.output(output)
    print(f"CDC Complet: {output}")
    return output


def generate_fonctionnalites_detaillees():
    pdf = TitelliDetailedPDF()
    
    # Page titre
    pdf.title_page(
        "FONCTIONNALITES DETAILLEES\nTITELLI",
        "Methodes, Algorithmes, Implementation\nVersion 05/02/2026"
    )
    
    # ============ SOMMAIRE ============
    pdf.add_page()
    pdf.chapter("", "SOMMAIRE")
    sections = [
        "1. AUTHENTIFICATION ET SECURITE",
        "2. SYSTEME CASH-BACK",
        "3. GESTION DES COMMANDES",
        "4. CATALOGUE SERVICES/PRODUITS",
        "5. RECHERCHE ET FILTRES",
        "6. DASHBOARD CLIENT",
        "7. DASHBOARD ENTREPRISE",
        "8. DASHBOARD ADMIN",
        "9. [NOUVEAU] PUB MEDIA IA",
        "10. [NOUVEAU] VIDEO PUB IA (A VENIR)",
        "11. PAIEMENTS STRIPE",
        "12. NOTIFICATIONS"
    ]
    for s in sections:
        if "[NOUVEAU]" in s:
            pdf.bullet(s, is_new=True)
        else:
            pdf.bullet(s)
    
    # ============ 1. AUTH ============
    pdf.add_page()
    pdf.chapter(1, "AUTHENTIFICATION ET SECURITE")
    
    pdf.section("1.1 Inscription (Register)")
    pdf.text("Endpoint: POST /api/auth/register")
    pdf.text("Methode: Validation email unique, hash password bcrypt, creation JWT")
    pdf.code_block("""# Processus inscription
1. Validation email format (Pydantic EmailStr)
2. Verification email non existant dans DB
3. Hash password avec bcrypt.hashpw()
4. Creation user dans MongoDB
5. Generation JWT token
6. Retour token + user info (sans password)""")
    
    pdf.section("1.2 Connexion (Login)")
    pdf.text("Endpoint: POST /api/auth/login")
    pdf.text("Methode: Verification password, generation JWT")
    pdf.code_block("""# Processus login
1. Recherche user par email
2. Verification password: bcrypt.checkpw(password, hash)
3. Si OK: generation JWT avec payload {sub: user_id, exp: 7d}
4. Retour token + user info""")
    
    pdf.section("1.3 Verification Token")
    pdf.text("Methode: Middleware sur routes protegees")
    pdf.code_block("""async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Token manquant")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = await db.users.find_one({"id": payload["sub"]})
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expire")""")
    
    # ============ 2. CASHBACK ============
    pdf.add_page()
    pdf.chapter(2, "SYSTEME CASH-BACK")
    
    pdf.section("2.1 Principe")
    pdf.text("Le client recoit 10% de chaque achat en cashback, utilisable sur la plateforme.")
    
    pdf.section("2.2 Credit Cashback")
    pdf.text("Declencheur: Commande passee au statut 'delivered'")
    pdf.code_block("""# Credit automatique apres livraison
async def credit_cashback(order_id: str):
    order = await db.orders.find_one({"id": order_id})
    cashback_amount = order["total"] * 0.10
    
    # Calcul date disponibilite (1er du mois suivant)
    today = datetime.now()
    if today.month == 12:
        available = datetime(today.year + 1, 1, 1)
    else:
        available = datetime(today.year, today.month + 1, 1)
    
    await db.cashback_transactions.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": order["client_id"],
        "amount": cashback_amount,
        "type": "credit",
        "source": "order",
        "order_id": order_id,
        "available_date": available,
        "created_at": datetime.now()
    })""")
    
    pdf.section("2.3 Utilisation Cashback")
    pdf.text("Methode: Deduction sur panier si solde disponible suffisant")
    pdf.code_block("""# Utilisation a la commande
available_cashback = await get_available_balance(user_id)
if use_cashback and available_cashback > 0:
    deduction = min(available_cashback, order_total)
    final_total = order_total - deduction
    
    # Enregistrer debit
    await db.cashback_transactions.insert_one({
        "type": "debit",
        "amount": -deduction,
        "order_id": new_order_id
    })""")
    
    pdf.section("2.4 Transfert entre Utilisateurs")
    pdf.text("Endpoint: POST /api/cashback/transfer")
    pdf.text("Methode: Debit expediteur + Credit destinataire atomique")
    
    # ============ 3. COMMANDES ============
    pdf.add_page()
    pdf.chapter(3, "GESTION DES COMMANDES")
    
    pdf.section("3.1 Cycle de Vie")
    pdf.code_block("""STATUTS:
pending     -> Commande creee, en attente paiement
confirmed   -> Paiement recu, transmise au prestataire
preparing   -> En cours de preparation
ready       -> Prete (a retirer ou a livrer)
delivering  -> En cours de livraison
delivered   -> Livree au client
cancelled   -> Annulee""")
    
    pdf.section("3.2 Creation Commande")
    pdf.text("Endpoint: POST /api/orders/create")
    pdf.code_block("""# Processus creation
1. Validation panier (items, quantities, prix)
2. Calcul total avec livraison
3. Application cashback si demande
4. Creation session Stripe si paiement CB
5. Insertion commande status=pending
6. Notification prestataire
7. Retour order_id + payment_url""")
    
    pdf.section("3.3 Mise a Jour Statut")
    pdf.text("Endpoint: PUT /api/orders/{id}/status")
    pdf.text("Droits: Entreprise peut confirmer/preparer/ready, Livreur peut delivering/delivered")
    
    # ============ 4. CATALOGUE ============
    pdf.add_page()
    pdf.chapter(4, "CATALOGUE SERVICES/PRODUITS")
    
    pdf.section("4.1 Structure")
    pdf.code_block("""# Schema service/product
{
    "id": "uuid",
    "enterprise_id": "ref",
    "type": "service|product",
    "name": "string",
    "description": "text",
    "category": "Beaute|Restauration|...",
    "subcategory": "optional",
    "price": "number",
    "duration": "minutes (services)",
    "images": ["url1", "url2"],
    "is_available": "boolean",
    "is_premium": "boolean",
    "is_certified": "boolean",
    "rating": "0-5",
    "order_count": "integer"
}""")
    
    pdf.section("4.2 Gestion Images")
    pdf.text("Methode: Upload base64 vers /uploads/, stockage URL")
    pdf.code_block("""# Upload image
image_data = base64.b64decode(base64_string)
filename = f"{uuid.uuid4()}.png"
filepath = UPLOADS_DIR / filename
with open(filepath, "wb") as f:
    f.write(image_data)
image_url = f"/api/uploads/{filename}"
""")
    
    # ============ 5. RECHERCHE ============
    pdf.add_page()
    pdf.chapter(5, "RECHERCHE ET FILTRES")
    
    pdf.section("5.1 Recherche Full-Text")
    pdf.text("Index MongoDB sur: name, description, category")
    pdf.code_block("""# Creation index
db.services.create_index([
    ("name", "text"),
    ("description", "text"),
    ("category", "text")
])

# Recherche
results = await db.services.find({
    "$text": {"$search": query}
}).sort([("score", {"$meta": "textScore"})]).to_list(20)""")
    
    pdf.section("5.2 Filtres Disponibles")
    pdf.bullet("category: Filtre par categorie")
    pdf.bullet("price_min/price_max: Fourchette de prix")
    pdf.bullet("is_premium: Services premium uniquement")
    pdf.bullet("is_certified: Prestataires certifies")
    pdf.bullet("rating_min: Note minimum")
    pdf.bullet("location: Rayon autour coordonnees")
    
    # ============ 9. PUB MEDIA IA ============
    pdf.add_page()
    pdf.chapter(9, "[NOUVEAU] PUB MEDIA IA")
    
    pdf.highlight("NOUVELLE FONCTIONNALITE 05/02/2026",
        "Creation de publicites professionnelles avec intelligence artificielle. "
        "Interface editeur avec apercu temps reel et filigrane protection.", is_new=True)
    
    pdf.section("9.1 Architecture", is_new=True)
    pdf.code_block("""Frontend: MediaPubPage.js
├── AnimatedHeader      # Header avec pubs defilantes
├── TemplateSelector    # Selection parmi 34 templates
├── LivePreview         # Apercu temps reel avec filigrane
├── ElementEditor       # Edition elements (texte, couleur, position)
├── PaymentStep         # Paiement Stripe
└── ConfirmStep         # Confirmation commande

Backend: media_pub.py
├── GET /templates      # Liste templates
├── POST /orders        # Creation commande + generation IA
├── GET /orders/{id}    # Statut commande
└── generate_pub_image  # Background task generation""")
    
    pdf.section("9.2 Processus Generation", is_new=True)
    pdf.code_block("""async def generate_pub_image(order_id, order_data):
    # 1. Construction prompt (image de fond SANS texte)
    prompt = f'''Create professional marketing background.
    Theme: {template_name}
    Colors: {brand_colors}
    DO NOT include ANY text in the image.
    Leave bottom 25% darker for text overlay.'''
    
    # 2. Generation DALL-E
    image_gen = OpenAIImageGeneration(api_key=EMERGENT_LLM_KEY)
    images = await image_gen.generate_images(prompt, model="gpt-image-1")
    
    # 3. Post-processing Pillow (texte parfait)
    final_image = add_text_overlay(
        images[0],
        product_name=order_data["product_name"],
        slogan=order_data["slogan"],
        description=order_data["description"],
        brand_colors=order_data["brand_colors"]
    )
    
    # 4. Sauvegarde et notification
    save_image(final_image, order_id)
    await create_notification(user_id, "Votre publicite est prete!")""")
    
    pdf.section("9.3 Post-Processing Texte", is_new=True)
    pdf.text("Le texte est ajoute APRES generation IA pour eviter les erreurs.", is_new=True)
    pdf.code_block("""def add_text_overlay(image_bytes, product_name, slogan, desc, colors):
    img = Image.open(BytesIO(image_bytes))
    draw = ImageDraw.Draw(img)
    
    # Overlay gradient en bas (25% hauteur)
    overlay_height = int(img.height * 0.28)
    overlay = create_gradient_overlay(img.width, overlay_height)
    img.paste(overlay, (0, img.height - overlay_height), overlay)
    
    # Police DejaVuSans-Bold
    font_large = ImageFont.truetype("DejaVuSans-Bold.ttf", size=55)
    font_medium = ImageFont.truetype("DejaVuSans-Bold.ttf", size=40)
    font_small = ImageFont.truetype("DejaVuSans-Bold.ttf", size=28)
    
    # Texte avec ombre pour lisibilite
    y = img.height - overlay_height + 50
    draw.text((x+2, y+2), product_name, font=font_large, fill=(0,0,0))  # Ombre
    draw.text((x, y), product_name, font=font_large, fill=primary_color)
    
    return img.tobytes()""")
    
    pdf.section("9.4 Delai de Livraison", is_new=True)
    pdf.highlight("IMPORTANT - DELAI GENERATION",
        "Le resultat sera disponible en environ 1 HEURE dans la section "
        "'Commandes Titelli' du dashboard entreprise. "
        "Lien direct: /dashboard/entreprise?tab=commandes-titelli", is_new=True)
    
    # ============ 10. VIDEO PUB IA ============
    pdf.add_page()
    pdf.chapter(10, "[NOUVEAU] VIDEO PUB IA (A VENIR)")
    
    pdf.highlight("FONCTIONNALITE EN DEVELOPPEMENT",
        "Systeme similaire a Pub Media mais pour creation de videos publicitaires. "
        "Utilisation de Sora 2 pour generation video IA.", is_new=True)
    
    pdf.section("10.1 Concept", is_new=True)
    pdf.bullet("Selection template video parmi catalogue", is_new=True)
    pdf.bullet("Personnalisation: slogan, musique, duree", is_new=True)
    pdf.bullet("Generation IA avec Sora 2", is_new=True)
    pdf.bullet("Post-processing: ajout texte, logo, transitions", is_new=True)
    
    pdf.section("10.2 Delai Livraison Video", is_new=True)
    pdf.highlight("IMPORTANT - DELAI VIDEO",
        "Les videos generees seront disponibles en environ 1 HEURE "
        "dans la section 'Commandes Titelli' du dashboard. "
        "Notification avec lien direct vers le fichier video.", is_new=True)
    
    pdf.section("10.3 Tarification Prevue", is_new=True)
    pdf.bullet("Video 15s: 99.90 CHF", is_new=True)
    pdf.bullet("Video 30s: 149.90 CHF", is_new=True)
    pdf.bullet("Video 60s: 249.90 CHF", is_new=True)
    pdf.bullet("Sur mesure: Devis personnalise", is_new=True)
    
    # ============ 11. STRIPE ============
    pdf.add_page()
    pdf.chapter(11, "PAIEMENTS STRIPE")
    
    pdf.section("11.1 Integration")
    pdf.text("Mode: Checkout Sessions avec redirection")
    pdf.text("Webhooks: Confirmation automatique paiement")
    
    pdf.code_block("""# Creation session checkout
session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{
        'price_data': {
            'currency': 'chf',
            'product_data': {'name': 'Commande Titelli'},
            'unit_amount': int(total * 100)  # Centimes
        },
        'quantity': 1
    }],
    mode='payment',
    success_url=f"{BASE_URL}/payment-success?session_id={{CHECKOUT_SESSION_ID}}",
    cancel_url=f"{BASE_URL}/payment-cancel",
    metadata={'order_id': order_id}
)""")
    
    pdf.section("11.2 Webhook Handler")
    pdf.code_block("""@app.post("/api/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    event = stripe.Webhook.construct_event(payload, sig, WEBHOOK_SECRET)
    
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = session["metadata"]["order_id"]
        await update_order_status(order_id, "confirmed")
        await credit_cashback(order_id)""")
    
    # ============ 12. NOTIFICATIONS ============
    pdf.add_page()
    pdf.chapter(12, "NOTIFICATIONS")
    
    pdf.section("12.1 Types")
    pdf.bullet("order_status: Changement statut commande")
    pdf.bullet("cashback_credit: Credit cashback disponible")
    pdf.bullet("promotion: Offre speciale")
    pdf.bullet("pub_order_ready: Publicite generee prete", is_new=True)
    
    pdf.section("12.2 Creation Notification")
    pdf.code_block("""async def create_notification(user_id, title, message, type, data=None):
    await db.notifications.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": title,
        "message": message,
        "type": type,
        "data": data,
        "is_read": False,
        "created_at": datetime.now(timezone.utc)
    })""")
    
    pdf.section("12.3 Recuperation")
    pdf.code_block("""# GET /api/notifications
notifications = await db.notifications.find({
    "user_id": user_id
}).sort("created_at", -1).limit(50).to_list(50)

unread_count = await db.notifications.count_documents({
    "user_id": user_id,
    "is_read": False
})""")
    
    # Sauvegarder
    output = f"{OUTPUT_DIR}/FONCTIONNALITES_DETAILLEES_TITELLI.pdf"
    pdf.output(output)
    print(f"Fonctionnalites: {output}")
    return output


if __name__ == "__main__":
    print("Generation des documents detailles...")
    path1 = generate_cdc_complet()
    path2 = generate_fonctionnalites_detaillees()
    print(f"\nFichiers generes:")
    print(f"  {path1}")
    print(f"  {path2}")
