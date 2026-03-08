#!/usr/bin/env python3
"""
Générateur de Cahiers des Charges Titelli - Version simplifiée
"""
from fpdf import FPDF
from datetime import datetime
import os

OUTPUT_DIR = "/app/backend/uploads/documents"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class TitelliPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_margins(15, 15, 15)  # Marges plus petites
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(245, 158, 11)
        self.cell(95, 10, 'TITELLI')
        self.set_text_color(150, 150, 150)
        self.set_font('Helvetica', '', 8)
        self.cell(95, 10, f'Document confidentiel - {datetime.now().strftime("%d/%m/%Y")}', align='R')
        self.ln(15)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def add_title_page(self, title, subtitle):
        self.add_page()
        self.ln(60)
        self.set_font('Helvetica', 'B', 28)
        self.set_text_color(245, 158, 11)
        self.multi_cell(0, 15, title, align='C')
        self.ln(10)
        self.set_font('Helvetica', '', 14)
        self.set_text_color(100, 100, 100)
        self.multi_cell(0, 8, subtitle, align='C')
        self.ln(30)
        self.set_font('Helvetica', '', 12)
        self.cell(0, 10, f'Date: {datetime.now().strftime("%d %B %Y")}', align='C')
        self.ln(8)
        self.cell(0, 10, 'Version: 1.0', align='C')

    def add_chapter(self, num, title):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(245, 158, 11)
        self.ln(5)
        self.cell(0, 10, f'{num}. {title}')
        self.ln(10)

    def add_section(self, title):
        self.set_x(self.l_margin)  # Reset X position
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 8, title)

    def add_text(self, text):
        self.set_x(self.l_margin)  # Reset X position
        self.set_font('Helvetica', '', 10)
        self.set_text_color(80, 80, 80)
        self.multi_cell(0, 6, text)
        self.ln(3)

    def add_bullet(self, text):
        self.set_x(self.l_margin)  # Reset X position
        self.set_font('Helvetica', '', 10)
        self.set_text_color(80, 80, 80)
        self.multi_cell(0, 6, f"   - {text}")

    def add_highlight(self, title, text):
        self.set_fill_color(245, 158, 11)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 8, f'  {title}', fill=True)
        self.ln(8)
        self.set_fill_color(250, 250, 250)
        self.set_text_color(60, 60, 60)
        self.set_font('Helvetica', '', 10)
        self.multi_cell(0, 6, text, fill=True)
        self.ln(5)


def generate_monetisation():
    pdf = TitelliPDF()
    
    # Page titre
    pdf.add_title_page(
        "CAHIER DES CHARGES\nMONETISATION",
        "Strategie et Modele Economique Titelli"
    )
    
    # 1. Facturation
    pdf.add_page()
    pdf.add_chapter(1, "Procede de Facturation")
    
    pdf.add_highlight(
        "VERSEMENT MENSUEL",
        "Titelli vous verse chaque debut du mois les revenus de vos ventes du mois precedent, deduisant 20% (cash-back + frais Titelli)."
    )
    
    pdf.add_text("Les ventes livrees retiennent des frais de livraison supplementaires.")
    
    pdf.add_highlight(
        "PROJECTION DE BENEFICES",
        "Il est attendu d'obtenir une augmentation de 20 a 45% de vos benefices la premiere annee sous reserve de bonne gestion de vos opportunites business Titelli."
    )
    
    # 2. Cash-Back
    pdf.add_page()
    pdf.add_chapter(2, "Systeme Cash-Back Client")
    
    pdf.add_text("Le Systeme de Cash-Back permet aux utilisateurs de beneficier d'un retour sur leur achat s'elevant a 10% du montant total facture par le prestataire.")
    
    pdf.add_section("Fonctionnement:")
    pdf.add_bullet("Accessible au client chaque debut du mois suivant la facturation")
    pdf.add_bullet("Utilisable sur l'ensemble de la plate-forme")
    pdf.add_bullet("Interchangeable avec tout utilisateur de l'application")
    
    # 3. Cash-Back VIP
    pdf.add_page()
    pdf.add_chapter(3, "Cash-Back Entreprise VIP Secret")
    
    pdf.add_text("Votre cash back entreprise pour plus d'initiatives qui rapportent plus pour votre entreprise.")
    
    pdf.add_section("Avantages inclus:")
    avantages = [
        "Avantages fiscaux",
        "Data la plus importante",
        "Pouvoir de gestion sur ton domaine d'activite",
        "Influence de marche",
        "Investisseurs guests",
        "Reseaux professionnels",
        "Patrimoine",
        "Labellisation particuliere"
    ]
    for av in avantages:
        pdf.add_bullet(av)
    
    pdf.ln(5)
    pdf.add_highlight(
        "TITELLI S'OCCUPE DE TOUT",
        "Oser Titelli, c'est Oser une nouvelle vie! A partir de 20% de ta paie jusqu'a 99%."
    )
    
    pdf.add_section("Services Premium VIP:")
    services = [
        "Premium + livraison instantanee",
        "Recrutement personnel instantane",
        "Pub 2M et Immobilier acces VIP",
        "Premium depot 24/24",
        "Fournisseurs Premium + 20% net",
        "Investissements Premium + 20% net",
        "Expert Marketing Premium",
        "Expert gestion des contrats et entreprise",
        "Liquidation stock des 20'000.-",
        "Formations et Soin entreprise"
    ]
    for s in services:
        pdf.add_bullet(s)
    
    # 4. Tarification
    pdf.add_page()
    pdf.add_chapter(4, "Tarification des Services")
    
    pdf.add_section("Inscription et Abonnements")
    pdf.add_bullet("Inscription annuelle: 250 CHF")
    pdf.add_bullet("Service Premium annuel: 540 CHF")
    pdf.add_bullet("Service Premium mensuel: 45 CHF")
    pdf.add_bullet("Commission sur ventes: 10-20%")
    
    pdf.add_section("Services a la Carte - Pub Media")
    pdf.add_bullet("Templates standards: 29.90 - 49.90 CHF")
    pdf.add_bullet("Creation Sur Mesure: 149.90 CHF")
    
    # 5. Avantages
    pdf.add_page()
    pdf.add_chapter(5, "Avantages Prestataires")
    
    avantages_list = [
        ("Gestion du personnel", "Cahiers des charges, ordres instantanes, suivi performances"),
        ("Gestion des stocks", "Inventaire temps reel, alertes, automatisation reassort"),
        ("Espace finance", "Tableau de bord, factures, portefeuille, previsions"),
        ("Feed entreprises", "Actualites du secteur, elargir le reseau"),
        ("Formations", "Formations continues, evolutions techniques"),
        ("Business News", "Actualites marche et concurrence"),
        ("Page pub spontanee", "Teasers, invitations, ciblage clients, influenceurs")
    ]
    
    for titre, desc in avantages_list:
        pdf.add_section(titre)
        pdf.add_text(desc)
    
    # 6. Services Premium
    pdf.add_page()
    pdf.add_chapter(6, "Services Premium")
    
    services_list = [
        ("Exposition sur Titelli", "Presence reguliere et forte, recommandations constantes"),
        ("Specialiste marketing", "Communication, image, site web, campagne reseaux sociaux"),
        ("Referencement preferentiel", "Suggestions experts et algorithmes"),
        ("Offres illimitees", "Gestes commerciaux, fidelisation, liquidation stocks"),
        ("Livraison 24/24", "Service a domicile en tout temps"),
        ("Fiches exigences clients", "Service personnalise hors du commun")
    ]
    
    for titre, desc in services_list:
        pdf.add_section(titre)
        pdf.add_text(desc)
    
    # 7. Labellisation
    pdf.add_page()
    pdf.add_chapter(7, "Labellisation et Certification")
    
    pdf.add_section("Mention Certifie")
    pdf.add_text("Revaloriser un savoir-faire specifique et reconnaitre des produits de haut-standing.")
    
    pdf.add_section("Labellises")
    pdf.add_text("Prestations prestigieuses repondant a des exigences particulieres par des experts attitres.")
    
    pdf.add_section("Optimisation fiscale")
    pdf.add_text("Expert comptable et juridique pour optimisation refletant sur vos benefices.")
    
    # 8. Renouvellement
    pdf.add_page()
    pdf.add_chapter(8, "Conditions de Renouvellement")
    
    pdf.add_text("Renouvellement de la prestation chaque annee sous reserve d'un courrier ecrit dans le mois qui precede le renouvellement.")
    
    pdf.add_text("Si vous ne souhaitez pas souscrire aux services Titelli, et que vous ne souhaitez pas etre expose a titre indicatif, il vous est possible d'adresser un mail au service client concerne.")
    
    # Sauvegarder
    output = f"{OUTPUT_DIR}/CDC_MONETISATION_TITELLI.pdf"
    pdf.output(output)
    print(f"CDC Monetisation: {output}")
    return output


def generate_fonctionnalites():
    pdf = TitelliPDF()
    
    # Page titre
    pdf.add_title_page(
        "CAHIER DES CHARGES\nFONCTIONNALITES",
        "Plateforme Titelli - Specification Complete"
    )
    
    # PARTIE A - CLIENT
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(245, 158, 11)
    pdf.cell(0, 15, "PARTIE A - FONCTIONNALITES CLIENT", align='C')
    pdf.ln(20)
    
    # 1. Cash-Back
    pdf.add_chapter(1, "Systeme Cash-Back Client")
    pdf.add_text("Retour de 10% sur chaque achat, credite mensuellement.")
    pdf.add_section("Fonctionnalites:")
    foncs = ["Accumulation automatique 10%", "Consultation solde temps reel", "Utilisation plateforme entiere", "Transfert entre utilisateurs", "Historique transactions", "Notifications credit"]
    for f in foncs:
        pdf.add_bullet(f)
    
    # 2. Navigation
    pdf.add_page()
    pdf.add_chapter(2, "Navigation et Recherche")
    pdf.add_section("Page d'accueil:")
    foncs = ["Videos promotionnelles", "Offres du moment carousel", "Suggestions personnalisees", "Tendances actuelles", "Guests du moment"]
    for f in foncs:
        pdf.add_bullet(f)
    
    pdf.add_section("Recherche et Filtres:")
    foncs = ["Recherche nom/categorie/localisation", "Filtres: Certifies, Labellises, Premium", "Tri popularite/prix/distance", "Carte interactive", "Favoris et historique"]
    for f in foncs:
        pdf.add_bullet(f)
    
    # 3. Commandes
    pdf.add_page()
    pdf.add_chapter(3, "Commandes et Paiements")
    pdf.add_section("Processus commande:")
    foncs = ["Panier multi-prestataires", "Choix livraison (standard/express/24h)", "Notes et instructions", "Application cash-back", "Codes promo"]
    for f in foncs:
        pdf.add_bullet(f)
    
    pdf.add_section("Paiements:")
    foncs = ["Stripe securise", "CB/Apple Pay/Google Pay", "Paiement cash-back", "Factures automatiques", "Historique transactions"]
    for f in foncs:
        pdf.add_bullet(f)
    
    # 4. Profil
    pdf.add_page()
    pdf.add_chapter(4, "Profil et Preferences")
    foncs = ["Photo de profil", "Coordonnees et adresses", "Preferences alimentaires/sante", "Centres d'interet", "Fiches d'exigences personnelles", "Espace cartes et fidelite"]
    for f in foncs:
        pdf.add_bullet(f)
    
    # 5. Lifestyle Pass
    pdf.add_chapter(5, "Lifestyle Pass")
    pdf.add_text("Acces a un nouveau mode de vie avec les meilleurs prestataires regionaux.")
    pdf.add_section("Healthy Lifestyle Pass:")
    pdf.add_text("Prestataires repondant aux exigences specifiques de sante.")
    
    # PARTIE B - ENTREPRISE
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(245, 158, 11)
    pdf.cell(0, 15, "PARTIE B - FONCTIONNALITES ENTREPRISE", align='C')
    pdf.ln(20)
    
    # 6. Dashboard
    pdf.add_chapter(6, "Dashboard Entreprise")
    pdf.add_section("Vue d'ensemble:")
    foncs = ["Statistiques ventes temps reel", "Graphiques performance", "CA mensuel/annuel", "Nombre clients/commandes", "Taux satisfaction", "Cash-back genere"]
    for f in foncs:
        pdf.add_bullet(f)
    
    # 7. Personnel
    pdf.add_page()
    pdf.add_chapter(7, "Gestion du Personnel")
    foncs = ["Profils employes", "Cahiers des charges", "Ordres instantanes", "Suivi performances", "Planning disponibilites", "Evaluations", "Publication offres emploi", "Gestion candidatures"]
    for f in foncs:
        pdf.add_bullet(f)
    
    # 8. Stocks
    pdf.add_chapter(8, "Gestion des Stocks")
    foncs = ["Inventaire temps reel", "Mouvements stocks", "Alertes rupture", "Suggestions algorithme", "Automatisation reassort", "Rapports detailles", "Commandes fournisseurs", "Budget minimum executif"]
    for f in foncs:
        pdf.add_bullet(f)
    
    # 9. Finances
    pdf.add_page()
    pdf.add_chapter(9, "Finances et Investissements")
    pdf.add_section("Espace Finance:")
    foncs = ["Tableau de bord financier", "Detail factures", "Suivi paiements", "Gestion portefeuille", "Previsions et objectifs"]
    for f in foncs:
        pdf.add_bullet(f)
    
    pdf.add_section("Investissements:")
    foncs = ["Creation offres investissement", "Recherche investisseurs", "Negociation integree", "Suivi participations", "Documents juridiques"]
    for f in foncs:
        pdf.add_bullet(f)
    
    # 10. Marketing
    pdf.add_page()
    pdf.add_chapter(10, "Marketing et Publicite")
    pdf.add_section("Page pub spontanee:")
    foncs = ["Teaser investisseurs", "Invitations personnelles (200 clients)", "Ciblage nouveaux clients", "Collaboration influenceurs", "Analyse performances"]
    for f in foncs:
        pdf.add_bullet(f)
    
    pdf.add_section("Offres et promotions:")
    foncs = ["Publication offres illimitees", "Gestes commerciaux", "Periodes promotionnelles", "Liquidation stocks", "Fidelisation clientele"]
    for f in foncs:
        pdf.add_bullet(f)
    
    # 11. Pub Media IA
    pdf.add_page()
    pdf.add_chapter(11, "Pub Media IA")
    pdf.add_text("Systeme creation publicites professionnelles avec intelligence artificielle.")
    
    pdf.add_section("Fonctionnalites:")
    foncs = ["34 templates dans 7 categories", "Personnalisation temps reel", "Couleurs de marque", "Texte slogan et description", "Filigrane protection (retire apres paiement)", "Generation IA image", "Post-processing texte (qualite parfaite)", "Telechargement HD"]
    for f in foncs:
        pdf.add_bullet(f)
    
    pdf.add_section("Categories templates:")
    cats = ["Reseaux Sociaux (Instagram, Facebook)", "Bannieres Web", "Restauration (Menus)", "Flyers et Affiches", "Email Marketing", "Stories", "Cartes de visite"]
    for c in cats:
        pdf.add_bullet(c)
    
    pdf.add_section("Tarification:")
    pdf.add_bullet("Templates standards: 29.90 - 49.90 CHF")
    pdf.add_bullet("Creation Sur Mesure: 149.90 CHF")
    
    # PARTIE C - ADMIN
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(245, 158, 11)
    pdf.cell(0, 15, "PARTIE C - FONCTIONNALITES ADMIN", align='C')
    pdf.ln(20)
    
    # 12. Dashboard Admin
    pdf.add_chapter(12, "Dashboard Admin")
    foncs = ["Statistiques globales", "Nombre utilisateurs (clients, entreprises, influenceurs)", "Volume transactions", "Revenus et commissions", "Graphiques tendances", "Validation entreprises", "Moderation avis", "Gestion offres", "Labellisation certification"]
    for f in foncs:
        pdf.add_bullet(f)
    
    # 13. Gestion Utilisateurs
    pdf.add_page()
    pdf.add_chapter(13, "Gestion Utilisateurs")
    pdf.add_section("Clients:")
    foncs = ["Liste et recherche", "Profils detailles", "Historique achats", "Gestion cash-back", "Support client"]
    for f in foncs:
        pdf.add_bullet(f)
    
    pdf.add_section("Entreprises:")
    foncs = ["Validation inscriptions", "Suivi performances", "Gestion abonnements", "Certification et labellisation"]
    for f in foncs:
        pdf.add_bullet(f)
    
    # 14. Statistiques
    pdf.add_chapter(14, "Statistiques et Rapports")
    pdf.add_section("Rapports automatiques:")
    foncs = ["Rapport journalier", "Rapport hebdomadaire", "Rapport mensuel", "Rapport annuel", "Export Excel/PDF"]
    for f in foncs:
        pdf.add_bullet(f)
    
    pdf.add_section("Metriques cles:")
    foncs = ["GMV (Gross Merchandise Value)", "Taux de conversion", "Panier moyen", "Retention client", "NPS (Net Promoter Score)", "CAC (Cout Acquisition Client)"]
    for f in foncs:
        pdf.add_bullet(f)
    
    # Sauvegarder
    output = f"{OUTPUT_DIR}/CDC_FONCTIONNALITES_TITELLI.pdf"
    pdf.output(output)
    print(f"CDC Fonctionnalites: {output}")
    return output


if __name__ == "__main__":
    print("Generation des Cahiers des Charges...")
    path1 = generate_monetisation()
    path2 = generate_fonctionnalites()
    print(f"\nFichiers generes:")
    print(f"  {path1}")
    print(f"  {path2}")
