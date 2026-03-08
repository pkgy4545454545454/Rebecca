#!/usr/bin/env python3
"""
Brochure Titelli V3 - Mise en page PREMIUM
Design professionnel et moderne
"""
import os
from datetime import datetime
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, 
    Table, TableStyle, PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, Line
from reportlab.graphics import renderPDF

SCREENSHOTS_DIR = '/app/backend/uploads/brochure_screenshots_v2'
OUTPUT_DIR = '/app/backend/uploads'

# Palette de couleurs professionnelle
COLORS = {
    'primary': colors.Color(0/255, 71/255, 171/255),      # Bleu Titelli
    'secondary': colors.Color(147/255, 51/255, 234/255),  # Violet
    'accent': colors.Color(255/255, 193/255, 7/255),      # Or
    'success': colors.Color(34/255, 197/255, 94/255),     # Vert
    'dark': colors.Color(15/255, 15/255, 20/255),         # Noir profond
    'light': colors.Color(248/255, 250/255, 252/255),     # Gris très clair
    'gray': colors.Color(100/255, 116/255, 139/255),      # Gris moyen
    'white': colors.white,
}


def create_professional_styles():
    """Crée des styles professionnels et modernes"""
    styles = getSampleStyleSheet()
    
    # Titre de couverture - Grand et impactant
    styles.add(ParagraphStyle(
        name='CoverMain',
        fontSize=56,
        textColor=COLORS['primary'],
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=60,
        spaceAfter=10
    ))
    
    # Sous-titre couverture
    styles.add(ParagraphStyle(
        name='CoverSub',
        fontSize=18,
        textColor=COLORS['gray'],
        alignment=TA_CENTER,
        fontName='Helvetica',
        spaceAfter=8,
        leading=24
    ))
    
    # Titre de section principal
    styles.add(ParagraphStyle(
        name='SectionMain',
        fontSize=28,
        textColor=COLORS['primary'],
        fontName='Helvetica-Bold',
        spaceBefore=0,
        spaceAfter=20,
        leading=32
    ))
    
    # Sous-titre de section
    styles.add(ParagraphStyle(
        name='SectionSub',
        fontSize=18,
        textColor=COLORS['dark'],
        fontName='Helvetica-Bold',
        spaceBefore=20,
        spaceAfter=12,
        leading=22
    ))
    
    # Numéro de section (petit, coloré)
    styles.add(ParagraphStyle(
        name='SectionNumber',
        fontSize=12,
        textColor=COLORS['secondary'],
        fontName='Helvetica-Bold',
        spaceBefore=0,
        spaceAfter=5,
        leading=14
    ))
    
    # Corps de texte - Lisible et aéré
    styles.add(ParagraphStyle(
        name='BodyMain',
        fontSize=11,
        textColor=COLORS['dark'],
        fontName='Helvetica',
        alignment=TA_JUSTIFY,
        spaceAfter=10,
        leading=16,
        firstLineIndent=0
    ))
    
    # Liste à puces élégante
    styles.add(ParagraphStyle(
        name='BulletPoint',
        fontSize=11,
        textColor=COLORS['dark'],
        fontName='Helvetica',
        leftIndent=20,
        spaceAfter=6,
        leading=15
    ))
    
    # Fonctionnalité mise en avant
    styles.add(ParagraphStyle(
        name='FeatureTitle',
        fontSize=12,
        textColor=COLORS['success'],
        fontName='Helvetica-Bold',
        spaceBefore=8,
        spaceAfter=4,
        leading=14
    ))
    
    # Conseil/Astuce avec style
    styles.add(ParagraphStyle(
        name='TipBox',
        fontSize=10,
        textColor=COLORS['primary'],
        fontName='Helvetica-Oblique',
        leftIndent=15,
        rightIndent=15,
        spaceBefore=15,
        spaceAfter=15,
        leading=14,
        backColor=colors.Color(240/255, 245/255, 255/255),
        borderWidth=0,
        borderPadding=12
    ))
    
    # Légende d'image
    styles.add(ParagraphStyle(
        name='ImageCaption',
        fontSize=9,
        textColor=COLORS['gray'],
        fontName='Helvetica-Oblique',
        alignment=TA_CENTER,
        spaceBefore=5,
        spaceAfter=15,
        leading=12
    ))
    
    # Table des matières - Titre
    styles.add(ParagraphStyle(
        name='TOCTitle',
        fontSize=14,
        textColor=COLORS['primary'],
        fontName='Helvetica-Bold',
        spaceBefore=20,
        spaceAfter=8,
        leading=16
    ))
    
    # Table des matières - Item
    styles.add(ParagraphStyle(
        name='TOCItem',
        fontSize=11,
        textColor=COLORS['dark'],
        fontName='Helvetica',
        leftIndent=15,
        spaceBefore=4,
        spaceAfter=4,
        leading=14
    ))
    
    # Numéro de page footer
    styles.add(ParagraphStyle(
        name='PageNumber',
        fontSize=9,
        textColor=COLORS['gray'],
        fontName='Helvetica',
        alignment=TA_CENTER
    ))
    
    return styles


def add_horizontal_line(story, color=None, width=17*cm, thickness=1):
    """Ajoute une ligne horizontale élégante"""
    if color is None:
        color = COLORS['light']
    story.append(Spacer(1, 5))
    story.append(HRFlowable(
        width=width,
        thickness=thickness,
        color=color,
        spaceBefore=5,
        spaceAfter=10
    ))


def add_image_with_frame(story, image_path, caption="", width=14*cm, max_height=10*cm, styles=None):
    """Ajoute une image avec un cadre élégant"""
    if not os.path.exists(image_path):
        return False
    
    try:
        img = Image.open(image_path)
        aspect = img.height / img.width
        height = width * aspect
        
        if height > max_height:
            height = max_height
            width = height / aspect
        
        # Créer un tableau avec bordure pour l'image
        img_flowable = RLImage(image_path, width=width, height=height)
        
        # Table avec padding et bordure arrondie simulée
        img_table = Table([[img_flowable]], colWidths=[width + 10])
        img_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.Color(230/255, 230/255, 230/255)),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ]))
        
        story.append(img_table)
        
        if caption and styles:
            story.append(Paragraph(caption, styles['ImageCaption']))
        else:
            story.append(Spacer(1, 15))
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur image: {e}")
        return False


def create_feature_box(story, title, items, styles):
    """Crée une boîte de fonctionnalités élégante"""
    # Créer le contenu
    content = []
    content.append(Paragraph(f"<b>{title}</b>", styles['FeatureTitle']))
    for item in items:
        content.append(Paragraph(f"• {item}", styles['BulletPoint']))
    
    # Table avec fond coloré
    data = [[content[0]]]
    for c in content[1:]:
        data.append([c])
    
    table = Table(data, colWidths=[15*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.Color(245/255, 250/255, 245/255)),
        ('BOX', (0, 0), (-1, -1), 1, COLORS['success']),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 15))


def create_tip_box(story, tip_text, styles):
    """Crée une boîte de conseil élégante"""
    tip_content = f"💡 <b>Conseil</b> : {tip_text}"
    
    data = [[Paragraph(tip_content, styles['TipBox'])]]
    table = Table(data, colWidths=[15*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.Color(240/255, 245/255, 255/255)),
        ('BOX', (0, 0), (-1, -1), 2, COLORS['primary']),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 15))


def create_section_header(story, number, title, styles):
    """Crée un en-tête de section élégant"""
    story.append(Paragraph(number, styles['SectionNumber']))
    story.append(Paragraph(title, styles['SectionMain']))
    add_horizontal_line(story, COLORS['primary'], thickness=2)


def create_subsection_header(story, title, styles):
    """Crée un sous-titre élégant"""
    story.append(Spacer(1, 10))
    story.append(Paragraph(title, styles['SectionSub']))
    add_horizontal_line(story, COLORS['light'], thickness=1)


def generate_premium_brochure():
    """Génère la brochure avec mise en page premium"""
    print("=" * 70)
    print("   GÉNÉRATION BROCHURE PREMIUM - ENTREPRISES")
    print("=" * 70)
    
    output_path = f'{OUTPUT_DIR}/TITELLI_BROCHURE_ENTREPRISES_PREMIUM.pdf'
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = create_professional_styles()
    story = []
    
    # ==================== PAGE DE COUVERTURE ====================
    print("📄 Couverture...")
    story.append(Spacer(1, 5*cm))
    story.append(Paragraph("TITELLI", styles['CoverMain']))
    story.append(Spacer(1, 0.5*cm))
    
    # Ligne décorative
    add_horizontal_line(story, COLORS['accent'], width=8*cm, thickness=3)
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("BROCHURE DE PRÉSENTATION", styles['CoverSub']))
    story.append(Paragraph("Guide Complet pour les Prestataires", styles['CoverSub']))
    story.append(Spacer(1, 1.5*cm))
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/accueil_hero.png', "", width=13*cm, max_height=8*cm, styles=styles)
    
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"Version {datetime.now().strftime('%B %Y')}", styles['CoverSub']))
    story.append(Paragraph("La plateforme suisse de mise en relation", styles['CoverSub']))
    story.append(PageBreak())
    
    # ==================== TABLE DES MATIÈRES ====================
    print("📄 Table des matières...")
    story.append(Paragraph("TABLE DES MATIÈRES", styles['SectionMain']))
    add_horizontal_line(story, COLORS['primary'], thickness=2)
    story.append(Spacer(1, 0.5*cm))
    
    toc_data = [
        ("01", "PRÉSENTATION GÉNÉRALE", ["Qu'est-ce que Titelli ?", "La page d'accueil"]),
        ("02", "INSCRIPTION", ["Créer un compte", "Compléter son profil"]),
        ("03", "DASHBOARD", ["Accueil", "Profil entreprise", "Galerie média"]),
        ("04", "COMMERCIAL", ["Services & Produits", "Commandes", "Stocks"]),
        ("05", "MARKETING", ["Offres & Promotions", "Publicités", "IA Ciblage"]),
        ("06", "FINANCES", ["Mes finances", "Abonnements"]),
        ("07", "COMMUNICATION", ["Messagerie", "Documents", "Support"]),
    ]
    
    for num, title, items in toc_data:
        # Numéro avec couleur
        num_para = Paragraph(f"<font color='#9333EA'><b>{num}</b></font>  {title}", styles['TOCTitle'])
        story.append(num_para)
        for item in items:
            story.append(Paragraph(f"• {item}", styles['TOCItem']))
    
    story.append(PageBreak())
    
    # ==================== PARTIE 1: PRÉSENTATION ====================
    print("📄 Partie 1...")
    create_section_header(story, "PARTIE 01", "PRÉSENTATION GÉNÉRALE", styles)
    
    story.append(Paragraph(
        "Titelli est une plateforme suisse innovante de mise en relation entre prestataires "
        "de services et clients. Notre mission est de simplifier la découverte et la réservation "
        "de services de qualité en Suisse.",
        styles['BodyMain']
    ))
    story.append(Spacer(1, 0.5*cm))
    
    create_subsection_header(story, "La page d'accueil", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/accueil_part1_hero.png',
                         "Page d'accueil Titelli - Section principale", width=14*cm, max_height=8*cm, styles=styles)
    
    story.append(Paragraph(
        "La page d'accueil présente les services populaires, les prestataires mis en avant "
        "et les offres du moment. C'est ici que vos futurs clients vous découvriront.",
        styles['BodyMain']
    ))
    
    create_feature_box(story, "Le menu de navigation propose :", [
        "Services : Accès à tous les services disponibles",
        "Produits : Catalogue des produits en vente",
        "Entreprises : Liste des prestataires inscrits",
        "Rdv : Système de prise de rendez-vous",
        "Pub IA : Création de publicités avec l'intelligence artificielle"
    ], styles)
    
    story.append(PageBreak())
    
    # ==================== PARTIE 2: INSCRIPTION ====================
    print("📄 Partie 2...")
    create_section_header(story, "PARTIE 02", "INSCRIPTION & CONNEXION", styles)
    
    story.append(Paragraph(
        "Pour commencer à utiliser Titelli en tant que prestataire, vous devez créer un compte "
        "entreprise. Le processus est simple et rapide.",
        styles['BodyMain']
    ))
    story.append(Spacer(1, 0.3*cm))
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/connexion.png',
                         "Page d'authentification", width=12*cm, max_height=8*cm, styles=styles)
    
    create_subsection_header(story, "Étapes d'inscription", styles)
    
    steps = [
        "Cliquez sur 'Connexion' en haut à droite de la page",
        "Sélectionnez l'onglet 'Inscription'",
        "Choisissez 'Entreprise' comme type de compte",
        "Remplissez votre email professionnel",
        "Créez un mot de passe sécurisé (min. 8 caractères)",
        "Renseignez vos informations personnelles",
        "Validez les conditions d'utilisation",
        "Cliquez sur 'S'inscrire'"
    ]
    
    for i, step in enumerate(steps, 1):
        story.append(Paragraph(f"<b>{i}.</b> ➜ {step}", styles['BulletPoint']))
    
    story.append(Spacer(1, 0.3*cm))
    create_tip_box(story, 
        "Utilisez une adresse email professionnelle (ex: contact@votreentreprise.ch) "
        "pour renforcer votre crédibilité auprès des clients.", styles)
    
    story.append(PageBreak())
    
    # ==================== PARTIE 3: DASHBOARD ====================
    print("📄 Partie 3...")
    create_section_header(story, "PARTIE 03", "LE DASHBOARD ENTREPRISE", styles)
    
    story.append(Paragraph(
        "Le Dashboard est votre centre de contrôle pour gérer toute votre activité sur Titelli. "
        "Toutes les fonctionnalités sont accessibles depuis le menu latéral.",
        styles['BodyMain']
    ))
    story.append(Spacer(1, 0.3*cm))
    
    # Accueil Dashboard
    create_subsection_header(story, "Accueil du Dashboard", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/dashboard_accueil.png',
                         "Tableau de bord principal", width=14*cm, max_height=8*cm, styles=styles)
    
    create_feature_box(story, "Fonctionnalités disponibles :", [
        "Vue des statistiques du mois (vues, commandes, revenus)",
        "Graphiques de performance",
        "Notifications importantes",
        "Raccourcis vers les actions fréquentes"
    ], styles)
    
    story.append(PageBreak())
    
    # Profil entreprise
    create_subsection_header(story, "Profil Entreprise", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/dashboard_profil.png',
                         "Gestion du profil entreprise", width=14*cm, max_height=8*cm, styles=styles)
    
    story.append(Paragraph(
        "La section Profil vous permet de gérer toutes les informations de votre entreprise "
        "visibles par les clients : nom, description, coordonnées, horaires d'ouverture, etc.",
        styles['BodyMain']
    ))
    
    create_tip_box(story,
        "Un profil complet avec photos et description détaillée génère 3x plus de contacts "
        "que les profils incomplets.", styles)
    
    story.append(PageBreak())
    
    # Galerie média
    create_subsection_header(story, "Galerie Média", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/dashboard_media.png',
                         "Gestion des médias", width=14*cm, max_height=8*cm, styles=styles)
    
    create_feature_box(story, "Ce que vous pouvez faire :", [
        "Télécharger des photos haute qualité",
        "Ajouter des vidéos de présentation",
        "Organiser les médias par catégories",
        "Définir une photo principale"
    ], styles)
    
    story.append(PageBreak())
    
    # ==================== PARTIE 4: COMMERCIAL ====================
    print("📄 Partie 4...")
    create_section_header(story, "PARTIE 04", "GESTION COMMERCIALE", styles)
    
    story.append(Paragraph(
        "Cette partie couvre toutes les fonctionnalités liées à la vente de vos services "
        "et produits : création d'offres, gestion des commandes et stocks.",
        styles['BodyMain']
    ))
    story.append(Spacer(1, 0.3*cm))
    
    # Services & Produits
    create_subsection_header(story, "Services & Produits", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/dashboard_services.png',
                         "Gestion des services et produits", width=14*cm, max_height=8*cm, styles=styles)
    
    story.append(Paragraph(
        "C'est ici que vous créez et gérez tous vos services et produits en vente. "
        "Chaque élément aura sa propre fiche visible par les clients.",
        styles['BodyMain']
    ))
    
    create_tip_box(story,
        "Des descriptions détaillées et des photos de qualité augmentent vos chances de vente de 80%.", styles)
    
    story.append(PageBreak())
    
    # Commandes
    create_subsection_header(story, "Mes Commandes", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/dashboard_commandes.png',
                         "Suivi des commandes", width=14*cm, max_height=8*cm, styles=styles)
    
    create_feature_box(story, "Fonctionnalités :", [
        "Voir toutes les commandes (en attente, validées, terminées)",
        "Filtrer par statut ou date",
        "Accepter ou refuser une commande",
        "Contacter le client directement"
    ], styles)
    
    story.append(PageBreak())
    
    # ==================== PARTIE 5: MARKETING ====================
    print("📄 Partie 5...")
    create_section_header(story, "PARTIE 05", "MARKETING & PUBLICITÉ", styles)
    
    # Offres
    create_subsection_header(story, "Offres & Promotions", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/dashboard_offres.png',
                         "Gestion des offres et promotions", width=14*cm, max_height=8*cm, styles=styles)
    
    story.append(Paragraph(
        "Créez des offres spéciales pour attirer de nouveaux clients et fidéliser les existants. "
        "Les promotions apparaissent en priorité dans les résultats de recherche.",
        styles['BodyMain']
    ))
    
    create_tip_box(story,
        "Les offres de bienvenue (-10% sur la première commande) convertissent 40% de nouveaux clients.", styles)
    
    story.append(PageBreak())
    
    # Publicités
    create_subsection_header(story, "Mes Publicités", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/dashboard_publicites.png',
                         "Gestion des campagnes publicitaires", width=14*cm, max_height=8*cm, styles=styles)
    
    create_feature_box(story, "Fonctionnalités :", [
        "Créer des campagnes pub",
        "Cibler par zone géographique",
        "Définir un budget quotidien",
        "Suivre les statistiques (impressions, clics)",
        "Générer des visuels avec l'IA"
    ], styles)
    
    story.append(PageBreak())
    
    # ==================== PARTIE 6: FINANCES ====================
    print("📄 Partie 6...")
    create_section_header(story, "PARTIE 06", "FINANCES & ABONNEMENTS", styles)
    
    # Finances
    create_subsection_header(story, "Mes Finances", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/dashboard_finances.png',
                         "Suivi financier", width=14*cm, max_height=8*cm, styles=styles)
    
    create_feature_box(story, "Ce que vous pouvez suivre :", [
        "Tableau de bord financier complet",
        "Historique des paiements reçus",
        "Revenus par période",
        "Export comptable (CSV, PDF)"
    ], styles)
    
    story.append(PageBreak())
    
    # Abonnements
    create_subsection_header(story, "Abonnements Titelli", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/dashboard_abonnements.png',
                         "Formules d'abonnement", width=14*cm, max_height=7*cm, styles=styles)
    
    story.append(Paragraph(
        "Choisissez la formule d'abonnement adaptée à vos besoins :",
        styles['BodyMain']
    ))
    story.append(Spacer(1, 0.3*cm))
    
    # Tableau des abonnements élégant
    abo_data = [
        ['FORMULE', 'PRIX', 'COMMISSION', 'AVANTAGES'],
        ['Guest', 'Gratuit', '15%', 'Profil basique, 3 services'],
        ['Certifié', '29 CHF/mois', '12%', 'Services illimités, Badge'],
        ['Labellisé', '79 CHF/mois', '10%', 'Pub gratuite, Support prioritaire'],
        ['Exclusif', '149 CHF/mois', '8%', 'Account manager dédié'],
    ]
    
    table = Table(abo_data, colWidths=[3.5*cm, 3*cm, 2.5*cm, 6*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLORS['primary']),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (2, -1), 'CENTER'),
        ('ALIGN', (3, 1), (3, -1), 'LEFT'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        
        ('GRID', (0, 0), (-1, -1), 1, colors.Color(230/255, 230/255, 230/255)),
        ('BOX', (0, 0), (-1, -1), 2, COLORS['primary']),
        
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(250/255, 250/255, 250/255)]),
    ]))
    
    story.append(table)
    story.append(PageBreak())
    
    # ==================== PARTIE 7: COMMUNICATION ====================
    print("📄 Partie 7...")
    create_section_header(story, "PARTIE 07", "COMMUNICATION & SUPPORT", styles)
    
    # Messagerie
    create_subsection_header(story, "Messagerie", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/dashboard_messagerie.png',
                         "Messagerie intégrée", width=14*cm, max_height=8*cm, styles=styles)
    
    create_feature_box(story, "Fonctionnalités :", [
        "Chat en temps réel avec les clients",
        "Historique des conversations",
        "Notifications de nouveaux messages",
        "Envoi de fichiers et images"
    ], styles)
    
    create_tip_box(story,
        "Un temps de réponse inférieur à 1 heure augmente vos chances de conversion de 70%.", styles)
    
    story.append(PageBreak())
    
    # ==================== PAGE FINALE ====================
    print("📄 Page finale...")
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("MERCI DE VOTRE CONFIANCE", styles['SectionMain']))
    add_horizontal_line(story, COLORS['accent'], width=10*cm, thickness=3)
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Nous espérons que cette brochure vous a permis de découvrir toutes les possibilités "
        "offertes par Titelli. Notre équipe est à votre disposition pour vous accompagner.",
        styles['BodyMain']
    ))
    
    story.append(Spacer(1, 1*cm))
    
    # Contact box
    contact_data = [
        [Paragraph("<b>CONTACT</b>", styles['SectionSub'])],
        [Paragraph("🌐  www.titelli.com", styles['BodyMain'])],
        [Paragraph("📧  support@titelli.com", styles['BodyMain'])],
        [Paragraph("📞  +41 XX XXX XX XX", styles['BodyMain'])],
    ]
    
    contact_table = Table(contact_data, colWidths=[10*cm])
    contact_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.Color(248/255, 250/255, 252/255)),
        ('BOX', (0, 0), (-1, -1), 2, COLORS['primary']),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    
    story.append(contact_table)
    
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        "Rejoignez la communauté Titelli et développez votre activité dès aujourd'hui !",
        styles['CoverSub']
    ))
    
    # ==================== GÉNÉRATION ====================
    print("\n📄 Génération du PDF...")
    doc.build(story)
    
    size = os.path.getsize(output_path) / (1024 * 1024)
    
    print("\n" + "=" * 70)
    print(f"   ✅ BROCHURE PREMIUM GÉNÉRÉE !")
    print(f"   📁 {output_path}")
    print(f"   📦 Taille: {size:.1f} MB")
    print("=" * 70)
    
    return output_path


if __name__ == "__main__":
    generate_premium_brochure()
