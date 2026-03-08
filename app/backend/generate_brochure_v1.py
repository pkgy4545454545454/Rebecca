#!/usr/bin/env python3
"""
Génération de la Brochure Titelli - Version Professionnelle
Avec screenshots réels, schémas explicatifs et tutoriels
"""
import os
import io
from datetime import datetime
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, 
    Table, TableStyle, PageBreak, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

SCREENSHOTS_DIR = '/app/backend/uploads/brochure_screenshots'
OUTPUT_DIR = '/app/backend/uploads'

# Couleurs Titelli
TITELLI_BLUE = colors.Color(0, 71/255, 171/255)  # #0047AB
TITELLI_DARK = colors.Color(5/255, 5/255, 5/255)  # #050505
TITELLI_GOLD = colors.Color(255/255, 193/255, 7/255)  # #FFC107

def create_styles():
    """Crée les styles personnalisés pour la brochure"""
    styles = getSampleStyleSheet()
    
    # Titre principal
    styles.add(ParagraphStyle(
        name='TitelliTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=TITELLI_BLUE,
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    # Sous-titre
    styles.add(ParagraphStyle(
        name='TitelliSubtitle',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.darkgray,
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    ))
    
    # Titre de section
    styles.add(ParagraphStyle(
        name='SectionTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=TITELLI_BLUE,
        spaceBefore=20,
        spaceAfter=15,
        fontName='Helvetica-Bold',
        borderWidth=2,
        borderColor=TITELLI_BLUE,
        borderPadding=10
    ))
    
    # Sous-section
    styles.add(ParagraphStyle(
        name='SubSection',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.black,
        spaceBefore=15,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    ))
    
    # Texte normal
    styles.add(ParagraphStyle(
        name='TitelliBody',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        fontName='Helvetica',
        leading=14
    ))
    
    # Liste à puces
    styles.add(ParagraphStyle(
        name='BulletPoint',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        leftIndent=20,
        spaceAfter=5,
        fontName='Helvetica'
    ))
    
    # Note importante
    styles.add(ParagraphStyle(
        name='Note',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.gray,
        leftIndent=15,
        rightIndent=15,
        spaceAfter=10,
        fontName='Helvetica-Oblique',
        borderWidth=1,
        borderColor=colors.lightgrey,
        borderPadding=8,
        backColor=colors.Color(0.95, 0.95, 0.95)
    ))
    
    # Avantage/Feature
    styles.add(ParagraphStyle(
        name='Feature',
        parent=styles['Normal'],
        fontSize=12,
        textColor=TITELLI_BLUE,
        spaceBefore=8,
        spaceAfter=5,
        fontName='Helvetica-Bold'
    ))
    
    return styles


def add_screenshot(story, image_path, caption, width=16*cm, styles=None, max_height=18*cm):
    """Ajoute une image avec légende"""
    if os.path.exists(image_path):
        try:
            # Ouvrir et redimensionner l'image
            img = Image.open(image_path)
            aspect = img.height / img.width
            height = width * aspect
            
            # Limiter la hauteur maximale
            if height > max_height:
                height = max_height
                width = height / aspect
            
            img_flowable = RLImage(image_path, width=width, height=height)
            
            # Ajouter l'image
            story.append(img_flowable)
            story.append(Spacer(1, 5))
            
            # Ajouter la légende
            if styles:
                caption_style = ParagraphStyle(
                    name='Caption',
                    parent=styles['Normal'],
                    fontSize=9,
                    textColor=colors.gray,
                    alignment=TA_CENTER,
                    fontName='Helvetica-Oblique'
                )
                story.append(Paragraph(f"<i>{caption}</i>", caption_style))
            story.append(Spacer(1, 15))
            return True
        except Exception as e:
            print(f"Erreur image {image_path}: {e}")
    return False


def create_cover_page(story, styles):
    """Crée la page de couverture"""
    story.append(Spacer(1, 3*cm))
    
    # Logo/Titre principal
    story.append(Paragraph("TITELLI", styles['TitelliTitle']))
    story.append(Spacer(1, 1*cm))
    
    # Sous-titre
    story.append(Paragraph("BROCHURE DE PRÉSENTATION", styles['TitelliSubtitle']))
    story.append(Paragraph("Guide Complet pour les Prestataires", styles['TitelliSubtitle']))
    
    story.append(Spacer(1, 2*cm))
    
    # Image d'accueil si disponible
    home_img = f'{SCREENSHOTS_DIR}/home_hero.png'
    if os.path.exists(home_img):
        add_screenshot(story, home_img, "", width=14*cm, styles=styles)
    
    story.append(Spacer(1, 2*cm))
    
    # Date
    story.append(Paragraph(f"Version {datetime.now().strftime('%B %Y')}", styles['TitelliSubtitle']))
    story.append(Paragraph("La plateforme suisse de mise en relation", styles['TitelliBody']))
    
    story.append(PageBreak())


def create_table_of_contents(story, styles):
    """Crée la table des matières"""
    story.append(Paragraph("TABLE DES MATIÈRES", styles['SectionTitle']))
    story.append(Spacer(1, 1*cm))
    
    toc_items = [
        ("1. Présentation de Titelli", "Qu'est-ce que Titelli ?"),
        ("2. Avantages pour les Prestataires", "Pourquoi rejoindre Titelli ?"),
        ("3. Guide d'Inscription", "Comment créer votre compte"),
        ("4. Le Dashboard Entreprise", "Votre espace de gestion"),
        ("5. Services & Produits", "Gérer vos offres"),
        ("6. Système de Monétisation", "Comment gagner de l'argent"),
        ("7. Le Cashback Titelli", "Programme de fidélité"),
        ("8. Les Abonnements", "Formules disponibles"),
        ("9. Marketing & Publicité", "Promouvoir votre activité"),
        ("10. Tutoriels Complets", "Guide pas-à-pas"),
        ("11. Support & Contact", "Nous contacter"),
    ]
    
    for title, desc in toc_items:
        story.append(Paragraph(f"<b>{title}</b>", styles['Feature']))
        story.append(Paragraph(f"    {desc}", styles['TitelliBody']))
    
    story.append(PageBreak())


def section_presentation(story, styles):
    """Section 1: Présentation de Titelli"""
    story.append(Paragraph("1. PRÉSENTATION DE TITELLI", styles['SectionTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("<b>Qu'est-ce que Titelli ?</b>", styles['SubSection']))
    
    story.append(Paragraph(
        "Titelli est une plateforme suisse innovante de mise en relation entre "
        "prestataires de services et clients. Notre mission est de simplifier "
        "la découverte et la réservation de services de qualité en Suisse.",
        styles['TitelliBody']
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    # Ajouter screenshot de la page d'accueil
    add_screenshot(story, f'{SCREENSHOTS_DIR}/home_full.png', 
                   "Page d'accueil Titelli - Vue complète", width=15*cm, styles=styles)
    
    story.append(Paragraph("<b>Notre Vision</b>", styles['SubSection']))
    story.append(Paragraph(
        "• Connecter les meilleurs prestataires suisses avec leurs clients\n"
        "• Offrir une expérience de réservation simple et intuitive\n"
        "• Créer une communauté de confiance et de qualité\n"
        "• Soutenir l'économie locale et les entreprises suisses",
        styles['BulletPoint']
    ))
    
    story.append(Paragraph("<b>Les Catégories de Services</b>", styles['SubSection']))
    story.append(Paragraph(
        "Titelli couvre de nombreux secteurs d'activité :\n"
        "• Beauté & Bien-être (coiffure, esthétique, spa, massage)\n"
        "• Santé (médecins, thérapeutes, cliniques)\n"
        "• Artisanat (plombiers, électriciens, menuisiers)\n"
        "• Restauration (restaurants, traiteurs, cafés)\n"
        "• Commerce (boutiques, épiceries, produits locaux)\n"
        "• Services aux entreprises (consultants, avocats, comptables)\n"
        "• Et bien plus encore...",
        styles['BulletPoint']
    ))
    
    story.append(PageBreak())


def section_avantages(story, styles):
    """Section 2: Avantages pour les prestataires"""
    story.append(Paragraph("2. AVANTAGES POUR LES PRESTATAIRES", styles['SectionTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    avantages = [
        ("Visibilité Accrue", 
         "Votre profil est visible par des milliers de clients potentiels en Suisse. "
         "Notre référencement optimisé vous permet d'être trouvé facilement."),
        
        ("Gestion Simplifiée",
         "Un tableau de bord complet pour gérer vos services, produits, "
         "commandes, rendez-vous et finances en un seul endroit."),
        
        ("Système de Réservation",
         "Les clients peuvent réserver directement vos services en ligne. "
         "Plus besoin de gérer les appels téléphoniques."),
        
        ("Paiement Sécurisé",
         "Transactions sécurisées via Stripe. Recevez vos paiements "
         "directement sur votre compte bancaire."),
        
        ("Marketing Intégré",
         "Outils de publicité, promotions et offres spéciales pour "
         "attirer de nouveaux clients."),
        
        ("Statistiques Détaillées",
         "Suivez vos performances avec des tableaux de bord analytiques : "
         "vues, clics, conversions, revenus."),
        
        ("Programme de Cashback",
         "Vos clients bénéficient de cashback, ce qui les fidélise "
         "et les incite à revenir."),
        
        ("Support Dédié",
         "Une équipe à votre écoute pour vous accompagner dans "
         "votre développement sur la plateforme."),
    ]
    
    for titre, desc in avantages:
        story.append(Paragraph(f"✓ {titre}", styles['Feature']))
        story.append(Paragraph(desc, styles['TitelliBody']))
        story.append(Spacer(1, 0.3*cm))
    
    story.append(PageBreak())


def section_inscription(story, styles):
    """Section 3: Guide d'inscription"""
    story.append(Paragraph("3. GUIDE D'INSCRIPTION", styles['SectionTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("<b>Étape 1 : Accéder à la page de connexion</b>", styles['SubSection']))
    story.append(Paragraph(
        "Rendez-vous sur titelli.com et cliquez sur 'Connexion' en haut à droite "
        "de la page. Vous pouvez également cliquer sur 'Rejoindre Titelli' depuis "
        "la page d'accueil.",
        styles['TitelliBody']
    ))
    
    add_screenshot(story, f'{SCREENSHOTS_DIR}/login_page.png',
                   "Page de connexion - Entrez vos identifiants ici", width=12*cm, styles=styles)
    
    story.append(Paragraph("<b>Étape 2 : Créer un compte</b>", styles['SubSection']))
    story.append(Paragraph(
        "Si vous n'avez pas encore de compte, cliquez sur 'S'inscrire'. "
        "Remplissez le formulaire avec :\n"
        "• Votre adresse email professionnelle\n"
        "• Un mot de passe sécurisé (min. 8 caractères)\n"
        "• Sélectionnez 'Entreprise' comme type de compte",
        styles['BulletPoint']
    ))
    
    add_screenshot(story, f'{SCREENSHOTS_DIR}/register_page.png',
                   "Page d'inscription - Créez votre compte entreprise", width=12*cm, styles=styles)
    
    story.append(Paragraph("<b>Étape 3 : Compléter votre profil</b>", styles['SubSection']))
    story.append(Paragraph(
        "Après l'inscription, complétez votre profil entreprise avec :\n"
        "• Nom de votre entreprise\n"
        "• Description de vos services\n"
        "• Adresse et coordonnées\n"
        "• Horaires d'ouverture\n"
        "• Photos et logo",
        styles['BulletPoint']
    ))
    
    story.append(PageBreak())


def section_dashboard(story, styles):
    """Section 4: Le Dashboard Entreprise"""
    story.append(Paragraph("4. LE DASHBOARD ENTREPRISE", styles['SectionTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph(
        "Le Dashboard est votre centre de contrôle pour gérer toute votre activité "
        "sur Titelli. Voici les différentes sections disponibles :",
        styles['TitelliBody']
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    sections_dashboard = [
        ("Principal", [
            ("Accueil", "Vue d'ensemble de votre activité avec statistiques"),
            ("Profil entreprise", "Gérez les informations de votre entreprise"),
            ("Galerie média", "Ajoutez photos et vidéos de vos réalisations"),
            ("Mon fil d'actualité", "Publiez des actualités pour vos clients"),
        ]),
        ("Commercial", [
            ("Services & Produits", "Créez et gérez vos offres"),
            ("Mes commandes", "Suivez les commandes de vos clients"),
            ("Mes livraisons", "Gérez les livraisons en cours"),
            ("Gestion des stocks", "Contrôlez votre inventaire"),
        ]),
        ("Marketing", [
            ("Offres & Promotions", "Créez des offres spéciales"),
            ("Mes publicités", "Lancez des campagnes pub"),
            ("Tendances actuelles", "Découvrez ce qui marche"),
            ("IA Ciblage clients", "Utilisez l'IA pour cibler vos clients"),
        ]),
        ("RH & Finance", [
            ("Mon personnel", "Gérez votre équipe"),
            ("Emplois & Stages", "Publiez des offres d'emploi"),
            ("Mes finances", "Suivez vos revenus et dépenses"),
            ("Mes investissements", "Gérez vos investissements"),
        ]),
        ("Documents", [
            ("Abonnements", "Gérez votre abonnement Titelli"),
            ("Documents", "Stockez vos documents importants"),
            ("Paramètres", "Configurez votre compte"),
        ]),
    ]
    
    for section_name, items in sections_dashboard:
        story.append(Paragraph(f"<b>{section_name}</b>", styles['SubSection']))
        for item_name, item_desc in items:
            story.append(Paragraph(f"• <b>{item_name}</b> : {item_desc}", styles['BulletPoint']))
        story.append(Spacer(1, 0.3*cm))
    
    story.append(PageBreak())


def section_services_produits(story, styles):
    """Section 5: Services & Produits"""
    story.append(Paragraph("5. SERVICES & PRODUITS", styles['SectionTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("<b>Comment ajouter un service ?</b>", styles['SubSection']))
    story.append(Paragraph(
        "1. Accédez à votre Dashboard > Services & Produits\n"
        "2. Cliquez sur '+ Ajouter un service'\n"
        "3. Remplissez les informations :\n"
        "   • Nom du service\n"
        "   • Description détaillée\n"
        "   • Prix (en CHF)\n"
        "   • Durée estimée\n"
        "   • Catégorie\n"
        "4. Ajoutez des photos de qualité\n"
        "5. Définissez la disponibilité\n"
        "6. Publiez !",
        styles['BulletPoint']
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("<b>Comment ajouter un produit ?</b>", styles['SubSection']))
    story.append(Paragraph(
        "1. Accédez à votre Dashboard > Services & Produits\n"
        "2. Sélectionnez l'onglet 'Produits'\n"
        "3. Cliquez sur '+ Ajouter un produit'\n"
        "4. Remplissez :\n"
        "   • Nom du produit\n"
        "   • Description\n"
        "   • Prix de vente\n"
        "   • Quantité en stock\n"
        "   • Options de livraison\n"
        "5. Ajoutez des photos\n"
        "6. Publiez !",
        styles['BulletPoint']
    ))
    
    story.append(Paragraph(
        "<b>Conseil :</b> Des photos de qualité professionnelle augmentent "
        "significativement vos chances de conversion. Investissez dans de "
        "bonnes images de vos services et produits.",
        styles['Note']
    ))
    
    story.append(PageBreak())


def section_monetisation(story, styles):
    """Section 6: Système de monétisation"""
    story.append(Paragraph("6. SYSTÈME DE MONÉTISATION", styles['SectionTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph(
        "Titelli propose plusieurs moyens de monétisation pour les prestataires :",
        styles['TitelliBody']
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    monetisation = [
        ("Vente de Services",
         "Recevez des paiements pour chaque service réservé. Les clients "
         "peuvent payer en ligne de manière sécurisée via Stripe. Les fonds "
         "sont transférés sur votre compte après déduction de la commission."),
        
        ("Vente de Produits",
         "Vendez vos produits directement sur la plateforme. Gérez votre "
         "stock, les livraisons et les retours depuis votre Dashboard."),
        
        ("Commissions sur Recommandations",
         "Gagnez des commissions en recommandant d'autres prestataires "
         "à vos clients. Programme de parrainage intégré."),
        
        ("Programme Influenceur",
         "Collaborez avec des influenceurs Titelli pour promouvoir vos "
         "services et augmenter votre visibilité."),
        
        ("Publicité Premium",
         "Augmentez votre visibilité avec des emplacements publicitaires "
         "premium sur la plateforme."),
    ]
    
    for titre, desc in monetisation:
        story.append(Paragraph(f"<b>{titre}</b>", styles['Feature']))
        story.append(Paragraph(desc, styles['TitelliBody']))
        story.append(Spacer(1, 0.3*cm))
    
    story.append(Paragraph(
        "<b>Commission Titelli :</b> Titelli prélève une commission de 10% sur "
        "chaque transaction effectuée via la plateforme. Cette commission couvre "
        "les frais de paiement, d'hébergement et de support.",
        styles['Note']
    ))
    
    story.append(PageBreak())


def section_cashback(story, styles):
    """Section 7: Le Cashback Titelli"""
    story.append(Paragraph("7. LE CASHBACK TITELLI", styles['SectionTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph(
        "Le programme de cashback est un avantage unique pour fidéliser vos clients.",
        styles['TitelliBody']
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("<b>Comment ça fonctionne ?</b>", styles['SubSection']))
    story.append(Paragraph(
        "1. À chaque achat, le client cumule des points de cashback\n"
        "2. Les points sont convertibles en réductions\n"
        "3. Plus le client achète, plus il économise\n"
        "4. Le cashback est automatiquement crédité",
        styles['BulletPoint']
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("<b>Avantages pour vous</b>", styles['SubSection']))
    story.append(Paragraph(
        "• Fidélisation client accrue\n"
        "• Augmentation du panier moyen\n"
        "• Clients qui reviennent plus souvent\n"
        "• Différenciation par rapport à la concurrence",
        styles['BulletPoint']
    ))
    
    story.append(Paragraph("<b>Taux de Cashback</b>", styles['SubSection']))
    
    # Tableau des taux
    cashback_data = [
        ['Catégorie', 'Taux de Cashback'],
        ['Services Beauté', '5%'],
        ['Restauration', '3%'],
        ['Commerce', '4%'],
        ['Services Pro', '2%'],
    ]
    
    table = Table(cashback_data, colWidths=[8*cm, 5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TITELLI_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    
    story.append(table)
    
    story.append(PageBreak())


def section_abonnements(story, styles):
    """Section 8: Les Abonnements"""
    story.append(Paragraph("8. LES ABONNEMENTS", styles['SectionTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph(
        "Titelli propose différentes formules d'abonnement adaptées à vos besoins :",
        styles['TitelliBody']
    ))
    
    add_screenshot(story, f'{SCREENSHOTS_DIR}/abonnements.png',
                   "Page des abonnements Titelli", width=14*cm, styles=styles)
    
    story.append(Spacer(1, 0.5*cm))
    
    abonnements = [
        ("Gratuit - Guest", "0 CHF/mois", [
            "Profil basique visible",
            "3 services maximum",
            "Commission 15%",
        ]),
        ("Standard - Certifié", "29 CHF/mois", [
            "Profil complet",
            "Services illimités",
            "Commission 12%",
            "Badge 'Certifié'",
            "Statistiques basiques",
        ]),
        ("Premium - Labellisé", "79 CHF/mois", [
            "Tout Standard +",
            "Commission 10%",
            "Badge 'Labellisé'",
            "Publicité gratuite (100 CHF)",
            "Support prioritaire",
            "Statistiques avancées",
        ]),
        ("Pro - Exclusif", "149 CHF/mois", [
            "Tout Premium +",
            "Commission 8%",
            "Badge 'Exclusif'",
            "Publicité gratuite (300 CHF)",
            "Account manager dédié",
            "Formation personnalisée",
        ]),
    ]
    
    for nom, prix, features in abonnements:
        story.append(Paragraph(f"<b>{nom}</b> - {prix}", styles['Feature']))
        for feat in features:
            story.append(Paragraph(f"  ✓ {feat}", styles['BulletPoint']))
        story.append(Spacer(1, 0.3*cm))
    
    story.append(PageBreak())


def section_marketing(story, styles):
    """Section 9: Marketing & Publicité"""
    story.append(Paragraph("9. MARKETING & PUBLICITÉ", styles['SectionTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("<b>Créer une publicité</b>", styles['SubSection']))
    story.append(Paragraph(
        "Titelli offre des outils de publicité intégrés pour promouvoir votre activité :\n\n"
        "1. Accédez à Dashboard > Mes publicités\n"
        "2. Cliquez sur 'Créer une campagne'\n"
        "3. Définissez :\n"
        "   • Budget quotidien\n"
        "   • Durée de la campagne\n"
        "   • Zone géographique\n"
        "   • Public cible\n"
        "4. Créez votre visuel (ou utilisez l'IA)\n"
        "5. Lancez !",
        styles['BulletPoint']
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("<b>Offres & Promotions</b>", styles['SubSection']))
    story.append(Paragraph(
        "Créez des offres spéciales pour attirer de nouveaux clients :\n"
        "• Réductions en pourcentage (ex: -20%)\n"
        "• Offres à durée limitée\n"
        "• Packs promotionnels\n"
        "• Offres de bienvenue\n"
        "• Offres fidélité",
        styles['BulletPoint']
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("<b>IA Marketing</b>", styles['SubSection']))
    story.append(Paragraph(
        "Utilisez l'intelligence artificielle pour :\n"
        "• Cibler automatiquement les bons clients\n"
        "• Créer des visuels publicitaires\n"
        "• Générer des textes accrocheurs\n"
        "• Optimiser vos campagnes",
        styles['BulletPoint']
    ))
    
    story.append(PageBreak())


def section_tutoriels(story, styles):
    """Section 10: Tutoriels Complets"""
    story.append(Paragraph("10. TUTORIELS COMPLETS", styles['SectionTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    # Tutoriel connexion
    story.append(Paragraph("<b>Se connecter à Titelli</b>", styles['SubSection']))
    add_screenshot(story, f'{SCREENSHOTS_DIR}/login_page.png',
                   "Page de connexion", width=10*cm, styles=styles)
    story.append(Paragraph(
        "1. ➜ Entrez votre email dans le premier champ\n"
        "2. ➜ Entrez votre mot de passe dans le second champ\n"
        "3. ➜ Cliquez sur 'Se connecter'\n"
        "4. ➜ Si vous n'avez pas de compte, cliquez sur 'S'inscrire'",
        styles['BulletPoint']
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    # Tutoriel page d'accueil
    story.append(Paragraph("<b>Naviguer sur la page d'accueil</b>", styles['SubSection']))
    add_screenshot(story, f'{SCREENSHOTS_DIR}/home_hero.png',
                   "Page d'accueil - Section héro", width=12*cm, styles=styles)
    story.append(Paragraph(
        "La page d'accueil présente :\n"
        "• Le menu de navigation en haut\n"
        "• Les services populaires\n"
        "• Les prestataires mis en avant\n"
        "• Les offres du moment\n"
        "• Les témoignages clients",
        styles['BulletPoint']
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    # Tutoriel prestataires
    story.append(Paragraph("<b>Trouver des prestataires</b>", styles['SubSection']))
    add_screenshot(story, f'{SCREENSHOTS_DIR}/prestataires_list.png',
                   "Liste des prestataires", width=12*cm, styles=styles)
    story.append(Paragraph(
        "1. ➜ Utilisez la barre de recherche\n"
        "2. ➜ Filtrez par catégorie, lieu ou note\n"
        "3. ➜ Cliquez sur un prestataire pour voir ses détails\n"
        "4. ➜ Consultez les avis clients avant de réserver",
        styles['BulletPoint']
    ))
    
    story.append(PageBreak())


def section_support(story, styles):
    """Section 11: Support & Contact"""
    story.append(Paragraph("11. SUPPORT & CONTACT", styles['SectionTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    add_screenshot(story, f'{SCREENSHOTS_DIR}/contact.png',
                   "Page de contact Titelli", width=12*cm, styles=styles)
    
    story.append(Paragraph("<b>Comment nous contacter ?</b>", styles['SubSection']))
    story.append(Paragraph(
        "• Email : support@titelli.com\n"
        "• Téléphone : +41 XX XXX XX XX\n"
        "• Chat en ligne : disponible 7j/7\n"
        "• Formulaire de contact sur le site",
        styles['BulletPoint']
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("<b>FAQ - Questions Fréquentes</b>", styles['SubSection']))
    
    faq = [
        ("Comment modifier mes informations ?",
         "Rendez-vous dans Dashboard > Profil entreprise"),
        ("Comment gérer mes paiements ?",
         "Accédez à Dashboard > Mes finances"),
        ("Comment annuler une commande ?",
         "Dans Dashboard > Commandes, cliquez sur 'Annuler'"),
        ("Comment contacter le support ?",
         "Via le chat en ligne ou par email à support@titelli.com"),
    ]
    
    for question, reponse in faq:
        story.append(Paragraph(f"<b>Q: {question}</b>", styles['Feature']))
        story.append(Paragraph(f"R: {reponse}", styles['TitelliBody']))
        story.append(Spacer(1, 0.2*cm))
    
    story.append(Spacer(1, 1*cm))
    
    # Footer
    story.append(Paragraph(
        "Merci de faire partie de la communauté Titelli !",
        styles['TitelliSubtitle']
    ))
    story.append(Paragraph(
        "www.titelli.com",
        styles['TitelliSubtitle']
    ))


def generate_brochure():
    """Génère la brochure PDF complète"""
    print("=" * 70)
    print("   GÉNÉRATION BROCHURE TITELLI")
    print("=" * 70)
    
    output_path = f'{OUTPUT_DIR}/TITELLI_BROCHURE_ENTREPRISES.pdf'
    
    # Créer le document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Créer les styles
    styles = create_styles()
    
    # Story (contenu du document)
    story = []
    
    print("📄 Création de la page de couverture...")
    create_cover_page(story, styles)
    
    print("📄 Création de la table des matières...")
    create_table_of_contents(story, styles)
    
    print("📄 Section 1: Présentation...")
    section_presentation(story, styles)
    
    print("📄 Section 2: Avantages...")
    section_avantages(story, styles)
    
    print("📄 Section 3: Guide d'inscription...")
    section_inscription(story, styles)
    
    print("📄 Section 4: Dashboard...")
    section_dashboard(story, styles)
    
    print("📄 Section 5: Services & Produits...")
    section_services_produits(story, styles)
    
    print("📄 Section 6: Monétisation...")
    section_monetisation(story, styles)
    
    print("📄 Section 7: Cashback...")
    section_cashback(story, styles)
    
    print("📄 Section 8: Abonnements...")
    section_abonnements(story, styles)
    
    print("📄 Section 9: Marketing...")
    section_marketing(story, styles)
    
    print("📄 Section 10: Tutoriels...")
    section_tutoriels(story, styles)
    
    print("📄 Section 11: Support...")
    section_support(story, styles)
    
    # Générer le PDF
    print("\n📄 Génération du PDF...")
    doc.build(story)
    
    # Vérifier la taille
    size = os.path.getsize(output_path) / (1024 * 1024)
    
    print("\n" + "=" * 70)
    print(f"   ✅ BROCHURE GÉNÉRÉE !")
    print(f"   📁 {output_path}")
    print(f"   📦 Taille: {size:.1f} MB")
    print("=" * 70)
    
    return output_path


if __name__ == "__main__":
    generate_brochure()
