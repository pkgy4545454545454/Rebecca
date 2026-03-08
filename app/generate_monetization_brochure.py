#!/usr/bin/env python3
"""
Brochure Monétisation Titelli - Document PDF détaillé
Génère une brochure professionnelle détaillant tous les systèmes de monétisation
avec des screenshots réels et des explications complètes.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage
import os
from datetime import datetime

# Constants
OUTPUT_PATH = "/app/uploads/TITELLI_BROCHURE_MONETISATION.pdf"
SCREENSHOTS_DIR = "/app/brochure_screenshots"

# Colors
TITELLI_GOLD = colors.HexColor("#D4AF37")
TITELLI_BLUE = colors.HexColor("#0047AB")
TITELLI_DARK = colors.HexColor("#1a1a1a")
TITELLI_LIGHT_GOLD = colors.HexColor("#F5E6B8")
GREEN_HIGHLIGHT = colors.HexColor("#22c55e")

def create_styles():
    """Create custom paragraph styles"""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='TitelliTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=TITELLI_GOLD,
        alignment=TA_CENTER,
        spaceAfter=20,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='SectionTitle',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=TITELLI_BLUE,
        alignment=TA_LEFT,
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='SubSection',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=TITELLI_GOLD,
        alignment=TA_LEFT,
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='TitelliBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        spaceBefore=4,
        leading=14
    ))
    
    styles.add(ParagraphStyle(
        name='PriceHighlight',
        parent=styles['Normal'],
        fontSize=16,
        textColor=TITELLI_GOLD,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=8
    ))
    
    styles.add(ParagraphStyle(
        name='FeatureItem',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        alignment=TA_LEFT,
        leftIndent=15,
        spaceAfter=4,
        bulletIndent=5,
        leading=12
    ))
    
    styles.add(ParagraphStyle(
        name='KeyPoint',
        parent=styles['Normal'],
        fontSize=11,
        textColor=TITELLI_BLUE,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        spaceAfter=4
    ))
    
    styles.add(ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    ))
    
    styles.add(ParagraphStyle(
        name='TableHeader',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.white,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    return styles

def add_image_with_caption(story, image_path, caption, styles, width=16*cm, max_height=10*cm):
    """Add an image with a caption below"""
    if os.path.exists(image_path):
        try:
            # Get image dimensions
            with PILImage.open(image_path) as img:
                orig_width, orig_height = img.size
            
            # Calculate aspect ratio
            aspect = orig_height / orig_width
            img_width = width
            img_height = width * aspect
            
            # Limit height if too tall
            if img_height > max_height:
                img_height = max_height
                img_width = max_height / aspect
            
            img = Image(image_path, width=img_width, height=img_height)
            
            # Create table to add border
            img_table = Table([[img]], colWidths=[img_width + 4*mm])
            img_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, TITELLI_GOLD),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            
            story.append(img_table)
            story.append(Spacer(1, 4*mm))
            story.append(Paragraph(f"<i>{caption}</i>", styles['Footer']))
            story.append(Spacer(1, 8*mm))
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
    else:
        print(f"Image not found: {image_path}")

def create_monetization_brochure():
    """Generate the complete monetization brochure"""
    
    # Create document
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = create_styles()
    story = []
    
    # ===================
    # PAGE 1: COVER
    # ===================
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("TITELLI", styles['TitelliTitle']))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Guide Complet de Monétisation", styles['SectionTitle']))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Document détaillé présentant tous les systèmes de revenus<br/>et modèles économiques de la plateforme Titelli",
        styles['TitelliBody']
    ))
    story.append(Spacer(1, 1*cm))
    
    # Add homepage screenshot
    add_image_with_caption(
        story, 
        f"{SCREENSHOTS_DIR}/homepage.jpeg",
        "Page d'accueil Titelli - La plateforme qui connecte entreprises et clients",
        styles,
        width=15*cm
    )
    
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"Version: {datetime.now().strftime('%B %Y')}", styles['Footer']))
    story.append(Paragraph("www.titelli.com", styles['Footer']))
    story.append(PageBreak())
    
    # ===================
    # PAGE 2: TABLE OF CONTENTS
    # ===================
    story.append(Paragraph("Table des Matières", styles['TitelliTitle']))
    story.append(Spacer(1, 1*cm))
    
    toc_items = [
        ("1. Modèle Économique Global", "Vue d'ensemble de la stratégie de revenus"),
        ("2. Abonnements Entreprises - Forfaits de Base", "Standard & Guest"),
        ("3. Abonnements Premium", "Premium & Premium MVP"),
        ("4. Optimisation d'Entreprise", "Forfaits 2K à 50K"),
        ("5. Options à la Carte", "Modules complémentaires"),
        ("6. Publicité IA - Média Pub", "Génération d'images publicitaires"),
        ("7. Publicité IA - Vidéo Pub", "Génération de vidéos promotionnelles"),
        ("8. Commissions & Transactions", "Frais de gestion Titelli"),
        ("9. Cash-Back & Fidélisation", "Système de récompenses clients"),
        ("10. Code Promo Bienvenue", "Acquisition de nouveaux clients"),
        ("11. Taux de Rentabilité", "Analyses et projections"),
    ]
    
    for title, description in toc_items:
        story.append(Paragraph(f"<b>{title}</b>", styles['KeyPoint']))
        story.append(Paragraph(description, styles['TitelliBody']))
        story.append(Spacer(1, 3*mm))
    
    story.append(PageBreak())
    
    # ===================
    # PAGE 3: MODÈLE ÉCONOMIQUE GLOBAL
    # ===================
    story.append(Paragraph("1. Modèle Économique Global", styles['TitelliTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("Vue d'ensemble de la stratégie de revenus Titelli", styles['SubSection']))
    
    story.append(Paragraph("""
    Titelli adopte un modèle économique multi-sources inspiré des meilleures pratiques des géants du digital 
    (Instagram/Meta, Uber, Amazon) tout en l'adaptant au marché suisse et aux besoins locaux.
    """, styles['TitelliBody']))
    
    # Revenue sources table
    revenue_data = [
        ['Source de Revenu', 'Description', 'Part Estimée'],
        ['Abonnements B2B', 'Forfaits mensuels pour entreprises', '40-50%'],
        ['Publicité IA', 'Création de contenus pub (images/vidéos)', '20-25%'],
        ['Commissions', 'Frais sur transactions et paiements', '15-20%'],
        ['Options à la carte', 'Modules complémentaires', '10-15%'],
        ['Services Premium', 'Conseils, formations, accompagnement', '5-10%'],
    ]
    
    revenue_table = Table(revenue_data, colWidths=[5*cm, 7*cm, 3.5*cm])
    revenue_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TITELLI_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, TITELLI_GOLD),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    
    story.append(revenue_table)
    story.append(Spacer(1, 1*cm))
    
    story.append(Paragraph("Principe clé: Double monétisation", styles['SubSection']))
    story.append(Paragraph("""
    <b>→ Côté Entreprises (B2B):</b> Abonnements mensuels, options à la carte, services premium, publicité IA.<br/>
    <b>→ Côté Clients (B2C):</b> Frais de livraison, frais de service, commissions sur achats.
    """, styles['TitelliBody']))
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("""
    Ce modèle "des deux côtés" (comme Uber Eats ou Amazon) permet de maximiser les revenus tout en offrant 
    de la valeur aux deux parties. L'entreprise gagne en visibilité et en outils, le client bénéficie 
    de promotions et d'un accès facilité aux services locaux.
    """, styles['TitelliBody']))
    
    story.append(PageBreak())
    
    # ===================
    # PAGE 4-5: ABONNEMENTS DE BASE
    # ===================
    story.append(Paragraph("2. Abonnements Entreprises - Forfaits de Base", styles['TitelliTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    add_image_with_caption(
        story,
        f"{SCREENSHOTS_DIR}/subscriptions_basic.jpeg",
        "Interface des abonnements - Forfaits Standard et Guest",
        styles,
        width=16*cm
    )
    
    story.append(Paragraph("Forfait STANDARD - 200 CHF/mois", styles['SubSection']))
    story.append(Paragraph("""
    Le forfait d'entrée idéal pour les entreprises souhaitant découvrir Titelli.
    """, styles['TitelliBody']))
    
    standard_features = [
        "Exposition standard sur la plateforme",
        "1 publicité par mois",
        "Système Cash-Back (10% pour les clients)",
        "Gestion des stocks intégrée",
        "Accès aux fonctionnalités de base (agenda, messagerie, contacts)",
    ]
    
    for feature in standard_features:
        story.append(Paragraph(f"• {feature}", styles['FeatureItem']))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("Forfait GUEST - 250 CHF/mois (POPULAIRE)", styles['SubSection']))
    story.append(Paragraph("""
    Le forfait recommandé pour une visibilité optimale et une croissance accélérée.
    """, styles['TitelliBody']))
    
    guest_features = [
        "Profil professionnel complet et personnalisé",
        "Référencement préférentiel (apparition en priorité)",
        "Publicités illimitées",
        "Statistiques avancées et indicateurs de performance",
        "Badge 'Guest' sur le profil",
    ]
    
    for feature in guest_features:
        story.append(Paragraph(f"• {feature}", styles['FeatureItem']))
    
    story.append(Spacer(1, 0.5*cm))
    
    # Profitability analysis
    story.append(Paragraph("Analyse de rentabilité - Forfaits de Base", styles['SubSection']))
    
    profitability_base = [
        ['Indicateur', 'Standard', 'Guest'],
        ['Prix mensuel', '200 CHF', '250 CHF'],
        ['Coût technique Titelli', '~15 CHF', '~20 CHF'],
        ['Marge brute', '185 CHF (92.5%)', '230 CHF (92%)'],
        ['Valeur client/an', '2\'400 CHF', '3\'000 CHF'],
        ['ROI marketing estimé', '5-10x', '8-15x'],
    ]
    
    profit_table = Table(profitability_base, colWidths=[6*cm, 4.5*cm, 4.5*cm])
    profit_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TITELLI_GOLD),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, TITELLI_BLUE),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(profit_table)
    story.append(PageBreak())
    
    # ===================
    # PAGE 6: ABONNEMENTS PREMIUM
    # ===================
    story.append(Paragraph("3. Abonnements Premium", styles['TitelliTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    add_image_with_caption(
        story,
        f"{SCREENSHOTS_DIR}/subscriptions_premium.jpeg",
        "Forfaits Premium et Premium MVP",
        styles,
        width=16*cm
    )
    
    story.append(Paragraph("Forfait PREMIUM - 500 CHF/mois", styles['SubSection']))
    
    premium_features = [
        "4 publicités par mois incluses",
        "Accès au réseau d'investisseurs Titelli",
        "Service de livraison 24h/24",
        "Module de gestion du personnel",
        "Indicateurs de performance avancés",
    ]
    
    for feature in premium_features:
        story.append(Paragraph(f"• {feature}", styles['FeatureItem']))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("Forfait PREMIUM MVP - 1'000 CHF/mois", styles['SubSection']))
    story.append(Paragraph("""
    Le forfait ultime pour les entreprises ambitieuses visant l'excellence.
    """, styles['TitelliBody']))
    
    mvp_features = [
        "5 publicités + 1 vidéo promotionnelle par mois",
        "Accès au réseau de fournisseurs exclusifs",
        "Accès au local commercial 24h/24",
        "Conseiller dédié et personnalisé",
        "Formations business incluses",
        "Support prioritaire VIP",
    ]
    
    for feature in mvp_features:
        story.append(Paragraph(f"• {feature}", styles['FeatureItem']))
    
    story.append(Spacer(1, 0.5*cm))
    
    # Premium profitability
    story.append(Paragraph("Rentabilité des forfaits Premium", styles['SubSection']))
    
    premium_profit = [
        ['Forfait', 'Prix', 'Marge estimée', 'LTV annuelle'],
        ['Premium', '500 CHF/mois', '~450 CHF (90%)', '6\'000 CHF'],
        ['Premium MVP', '1\'000 CHF/mois', '~880 CHF (88%)', '12\'000 CHF'],
    ]
    
    premium_table = Table(premium_profit, colWidths=[4*cm, 3.5*cm, 4*cm, 4*cm])
    premium_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TITELLI_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, TITELLI_GOLD),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(premium_table)
    story.append(PageBreak())
    
    # ===================
    # PAGE 7: OPTIMISATION D'ENTREPRISE
    # ===================
    story.append(Paragraph("4. Optimisation d'Entreprise", styles['TitelliTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    add_image_with_caption(
        story,
        f"{SCREENSHOTS_DIR}/subscriptions_optimisation.jpeg",
        "Forfaits d'Optimisation - De 2'000 à 50'000 CHF/mois",
        styles,
        width=16*cm
    )
    
    story.append(Paragraph("""
    Les forfaits d'optimisation sont conçus pour les entreprises en forte croissance 
    cherchant un accompagnement complet et des prestations haut de gamme.
    """, styles['TitelliBody']))
    
    # Optimization packages table
    opti_data = [
        ['Forfait', 'Prix/mois', 'Publicités', 'Prestations', 'Liquidités'],
        ['Starter 2K', '2\'000 CHF', '8/mois', 'Formations business', '-'],
        ['Starter+ 3K', '3\'000 CHF', '15/mois', '5h OU 2 déjeuners', '-'],
        ['Opti 5K', '5\'000 CHF', 'Illimitées', '10h prestations', '3\'000 CHF'],
        ['Opti 10K', '10\'000 CHF', 'Illimitées', '20h + fiscaliste', '7\'000 CHF'],
        ['Opti 20K', '20\'000 CHF', '25/mois', '40h prestations', '15\'000 CHF'],
        ['Opti 50K', '50\'000 CHF', 'Illimitées', '80h + conciergerie', '40\'000 CHF'],
    ]
    
    opti_table = Table(opti_data, colWidths=[2.8*cm, 2.5*cm, 2.5*cm, 4*cm, 2.7*cm])
    opti_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TITELLI_GOLD),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, TITELLI_BLUE),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    story.append(opti_table)
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("Concept des 'Prestations Liquidées'", styles['SubSection']))
    story.append(Paragraph("""
    Les prestations liquidées représentent un montant en CHF que l'entreprise peut utiliser 
    pour des services Titelli ou partenaires. Par exemple, avec Opti 10K, l'entreprise reçoit 
    7'000 CHF utilisables pour:
    """, styles['TitelliBody']))
    
    liquidees = [
        "Heures de conseil avec experts",
        "Campagnes publicitaires supplémentaires",
        "Services de livraison",
        "Formations spécialisées",
        "Événements networking",
    ]
    
    for item in liquidees:
        story.append(Paragraph(f"• {item}", styles['FeatureItem']))
    
    story.append(PageBreak())
    
    # ===================
    # PAGE 8: OPTIONS À LA CARTE
    # ===================
    story.append(Paragraph("5. Options à la Carte", styles['TitelliTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    add_image_with_caption(
        story,
        f"{SCREENSHOTS_DIR}/subscriptions_addons.jpeg",
        "Modules complémentaires - Personnalisez votre offre",
        styles,
        width=16*cm
    )
    
    story.append(Paragraph("""
    Les options à la carte permettent aux entreprises de personnaliser leur abonnement 
    en ajoutant des modules spécifiques selon leurs besoins.
    """, styles['TitelliBody']))
    
    # A la carte options
    alacarte_data = [
        ['Option', 'Prix', 'Description'],
        ['Publicités extra', '200 CHF/mois', '+2 publicités + 1 vidéo/mois'],
        ['Accès Investisseurs', '300 CHF/mois', 'Visibilité réseau investisseurs'],
        ['Livraison 24/24', '300 CHF/mois', 'Service de livraison permanent'],
        ['Local commercial', '300 CHF/mois', 'Accès local 24h/24'],
        ['Accès Fournisseurs', '500 CHF/mois', 'Réseau fournisseurs exclusifs'],
        ['Formations', '200 CHF/mois', 'Formations business mensuelles'],
        ['Recrutement', '200 CHF/mois', 'Aide au recrutement'],
        ['Immobilier', '200 CHF/mois', 'Accès annonces immobilières'],
        ['Expert conseil', '1\'000 CHF/mois', 'Conseiller dédié'],
        ['Fiscaliste', '4\'000 CHF/mois', 'Accompagnement fiscal'],
    ]
    
    alacarte_table = Table(alacarte_data, colWidths=[4*cm, 3.5*cm, 8*cm])
    alacarte_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TITELLI_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, TITELLI_GOLD),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(alacarte_table)
    story.append(PageBreak())
    
    # ===================
    # PAGE 9: PUBLICITÉ IA - MÉDIA PUB
    # ===================
    story.append(Paragraph("6. Publicité IA - Média Pub", styles['TitelliTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    add_image_with_caption(
        story,
        f"{SCREENSHOTS_DIR}/monetization_media_pub.jpeg",
        "Interface Média Pub IA - Création d'images publicitaires",
        styles,
        width=16*cm
    )
    
    story.append(Paragraph("Fonctionnement du système", styles['SubSection']))
    story.append(Paragraph("""
    Le système Média Pub IA permet aux entreprises de créer des publicités visuelles 
    professionnelles en quelques clics grâce à l'intelligence artificielle.
    """, styles['TitelliBody']))
    
    story.append(Paragraph("Processus de création:", styles['KeyPoint']))
    media_process = [
        "1. L'entreprise sélectionne un template (Instagram, Story, Flyer, etc.)",
        "2. Elle personnalise le contenu (nom, slogan, couleurs de marque)",
        "3. L'IA génère l'image publicitaire en haute qualité",
        "4. Livraison instantanée - Prêt à publier",
    ]
    
    for step in media_process:
        story.append(Paragraph(f"  {step}", styles['TitelliBody']))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("Tarification Média Pub", styles['SubSection']))
    
    media_pricing = [
        ['Format', 'Prix', 'Usage'],
        ['Instagram Post', 'Dès 19.90 CHF', 'Réseaux sociaux'],
        ['Story Instagram/FB', 'Dès 14.90 CHF', 'Stories éphémères'],
        ['Bannière Web', 'Dès 24.90 CHF', 'Sites web, emails'],
        ['Flyer A4/A5', 'Dès 29.90 CHF', 'Print, distribution'],
        ['Email Marketing', 'Dès 19.90 CHF', 'Campagnes email'],
        ['Sur Mesure', 'Dès 49.90 CHF', 'Création personnalisée'],
    ]
    
    media_table = Table(media_pricing, colWidths=[4.5*cm, 4*cm, 6*cm])
    media_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TITELLI_GOLD),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, TITELLI_BLUE),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(media_table)
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Rentabilité Média Pub", styles['SubSection']))
    story.append(Paragraph("""
    <b>Coût de production IA:</b> ~0.50-2.00 CHF par image<br/>
    <b>Prix de vente moyen:</b> ~25 CHF<br/>
    <b>Marge brute:</b> ~90-95%<br/>
    <b>Volume estimé:</b> 500-1000 créations/mois à terme<br/>
    <b>Revenu mensuel potentiel:</b> 12'500 - 25'000 CHF
    """, styles['TitelliBody']))
    
    story.append(PageBreak())
    
    # ===================
    # PAGE 10: PUBLICITÉ IA - VIDÉO PUB
    # ===================
    story.append(Paragraph("7. Publicité IA - Vidéo Pub", styles['TitelliTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    add_image_with_caption(
        story,
        f"{SCREENSHOTS_DIR}/monetization_video_pub.jpeg",
        "Interface Vidéo Pub IA - Création de vidéos promotionnelles",
        styles,
        width=16*cm
    )
    
    story.append(Paragraph("Service de création vidéo", styles['SubSection']))
    story.append(Paragraph("""
    Le service Vidéo Pub IA permet de commander des vidéos publicitaires professionnelles 
    générées par intelligence artificielle. Livraison en ~1 heure.
    """, styles['TitelliBody']))
    
    story.append(Paragraph("Tarification Vidéo Pub", styles['SubSection']))
    
    video_pricing = [
        ['Type de vidéo', 'Durée', 'Prix'],
        ['TikTok Tendance', '8 secondes', '149.90 CHF'],
        ['Story Animée', '8 secondes', '129.90 CHF'],
        ['Instagram Reel', '15 secondes', '199.90 CHF'],
        ['Pub Hero Premium', '15 secondes', '249.90 CHF'],
        ['Spot Produit', '30 secondes', '299.90 CHF'],
        ['Menu Vidéo Restaurant', '15 secondes', '199.90 CHF'],
        ['Teaser Lancement', '8 secondes', '179.90 CHF'],
        ['Ambiance Restaurant/Bar', '12 secondes', '219.90 CHF'],
        ['Sur Mesure', '15 secondes', '399.90 CHF'],
    ]
    
    video_table = Table(video_pricing, colWidths=[5.5*cm, 3.5*cm, 4*cm])
    video_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TITELLI_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, TITELLI_GOLD),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    story.append(video_table)
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Rentabilité Vidéo Pub", styles['SubSection']))
    story.append(Paragraph("""
    <b>Coût de production IA:</b> ~5-15 CHF par vidéo<br/>
    <b>Prix de vente moyen:</b> ~200 CHF<br/>
    <b>Marge brute:</b> ~92-97%<br/>
    <b>Volume estimé:</b> 100-300 vidéos/mois à terme<br/>
    <b>Revenu mensuel potentiel:</b> 20'000 - 60'000 CHF
    """, styles['TitelliBody']))
    
    story.append(PageBreak())
    
    # ===================
    # PAGE 11: COMMISSIONS & TRANSACTIONS
    # ===================
    story.append(Paragraph("8. Commissions & Transactions", styles['TitelliTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("Structure des frais Titelli", styles['SubSection']))
    story.append(Paragraph("""
    Titelli applique des frais de gestion et de transaction sur les paiements effectués 
    via la plateforme, similaire aux modèles Uber Eats ou Deliveroo.
    """, styles['TitelliBody']))
    
    # Commission structure
    commission_data = [
        ['Type de frais', 'Taux/Montant', 'Payé par', 'Description'],
        ['Commission entreprise', '5-15%', 'Entreprise', 'Sur chaque vente via Titelli'],
        ['Frais de service', '2-5 CHF', 'Client', 'Frais fixes par commande'],
        ['Frais de livraison', '3-10 CHF', 'Client', 'Variable selon distance'],
        ['Frais de paiement', '1.5-3%', 'Partagé', 'Frais Stripe/paiement'],
    ]
    
    commission_table = Table(commission_data, colWidths=[4*cm, 3*cm, 2.5*cm, 5.5*cm])
    commission_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TITELLI_GOLD),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, TITELLI_BLUE),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(commission_table)
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("Comparaison avec le marché", styles['SubSection']))
    
    comparison_data = [
        ['Plateforme', 'Commission restaurant', 'Frais client'],
        ['Uber Eats', '25-35%', '5-10 CHF'],
        ['Deliveroo', '20-30%', '4-8 CHF'],
        ['Just Eat', '15-25%', '3-6 CHF'],
        ['Titelli', '5-15%', '2-5 CHF'],
    ]
    
    comparison_table = Table(comparison_data, colWidths=[5*cm, 5*cm, 5*cm])
    comparison_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TITELLI_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, TITELLI_GOLD),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('BACKGROUND', (0, 4), (-1, 4), TITELLI_LIGHT_GOLD),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(comparison_table)
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("""
    <b>Avantage Titelli:</b> Commissions nettement inférieures à la concurrence, 
    ce qui permet aux entreprises de préserver leurs marges tout en bénéficiant 
    d'une visibilité accrue.
    """, styles['TitelliBody']))
    
    story.append(PageBreak())
    
    # ===================
    # PAGE 12: CASH-BACK & FIDÉLISATION
    # ===================
    story.append(Paragraph("9. Cash-Back & Fidélisation", styles['TitelliTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("Système de Cash-Back client", styles['SubSection']))
    story.append(Paragraph("""
    Le système de Cash-Back Titelli récompense les clients fidèles et incite à la 
    récurrence des achats. Chaque achat génère un pourcentage de retour en crédit Titelli.
    """, styles['TitelliBody']))
    
    cashback_data = [
        ['Forfait entreprise', 'Taux Cash-Back', 'Exemple (achat 100 CHF)'],
        ['Standard', '10%', '10 CHF crédités au client'],
        ['Guest', '12%', '12 CHF crédités au client'],
        ['Premium', '15%', '15 CHF crédités au client'],
        ['Premium MVP', '20%', '20 CHF crédités au client'],
    ]
    
    cashback_table = Table(cashback_data, colWidths=[5*cm, 4*cm, 6*cm])
    cashback_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TITELLI_GOLD),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, TITELLI_BLUE),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(cashback_table)
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("Impact sur la fidélisation", styles['SubSection']))
    story.append(Paragraph("""
    Le Cash-Back crée un cercle vertueux:
    """, styles['TitelliBody']))
    
    fidelisation_points = [
        "→ Le client accumule des crédits à chaque achat",
        "→ Ces crédits ne sont utilisables que sur Titelli",
        "→ Incitation à revenir pour utiliser les crédits",
        "→ Augmentation de la fréquence d'achat (+30-50% en moyenne)",
        "→ Lifetime Value client multipliée par 2 à 3",
    ]
    
    for point in fidelisation_points:
        story.append(Paragraph(point, styles['FeatureItem']))
    
    story.append(PageBreak())
    
    # ===================
    # PAGE 13: CODE PROMO BIENVENUE
    # ===================
    story.append(Paragraph("10. Code Promo Bienvenue", styles['TitelliTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    add_image_with_caption(
        story,
        f"{SCREENSHOTS_DIR}/welcome_popup.jpeg",
        "Popup de bienvenue avec code promo BIENVENUE100",
        styles,
        width=14*cm
    )
    
    story.append(Paragraph("Stratégie d'acquisition client", styles['SubSection']))
    story.append(Paragraph("""
    Le code <b>BIENVENUE100</b> offre 100 CHF de crédit publicitaire aux nouvelles entreprises. 
    Cette stratégie vise à:
    """, styles['TitelliBody']))
    
    acquisition_points = [
        "Réduire la barrière à l'entrée pour les nouvelles entreprises",
        "Permettre de tester les services de publicité IA sans risque",
        "Créer un premier contact positif avec la plateforme",
        "Générer des données d'usage pour améliorer le ciblage",
        "Augmenter le taux de conversion en abonnement payant",
    ]
    
    for point in acquisition_points:
        story.append(Paragraph(f"• {point}", styles['FeatureItem']))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("Coût d'acquisition client (CAC)", styles['SubSection']))
    story.append(Paragraph("""
    <b>Valeur du crédit offert:</b> 100 CHF<br/>
    <b>Coût réel pour Titelli:</b> ~10-15 CHF (coût de production IA)<br/>
    <b>Taux de conversion en abonné:</b> ~15-25% estimé<br/>
    <b>CAC effectif:</b> ~40-70 CHF par client converti<br/>
    <b>LTV moyenne d'un abonné:</b> 3'000-6'000 CHF<br/>
    <b>Ratio LTV/CAC:</b> 50-150x (excellent)
    """, styles['TitelliBody']))
    
    story.append(PageBreak())
    
    # ===================
    # PAGE 14: TAUX DE RENTABILITÉ
    # ===================
    story.append(Paragraph("11. Taux de Rentabilité", styles['TitelliTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("Projections financières", styles['SubSection']))
    
    # Projections table
    projections_data = [
        ['Source de revenu', 'Marge brute', 'Potentiel mensuel', 'Potentiel annuel'],
        ['Abonnements (500 entreprises)', '90%', '125\'000 CHF', '1.5M CHF'],
        ['Publicité IA Média', '92%', '25\'000 CHF', '300K CHF'],
        ['Publicité IA Vidéo', '95%', '40\'000 CHF', '480K CHF'],
        ['Commissions transactions', '100%', '15\'000 CHF', '180K CHF'],
        ['Options à la carte', '88%', '20\'000 CHF', '240K CHF'],
        ['TOTAL', '~91%', '225\'000 CHF', '2.7M CHF'],
    ]
    
    projections_table = Table(projections_data, colWidths=[5.5*cm, 2.5*cm, 3.5*cm, 3.5*cm])
    projections_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TITELLI_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, TITELLI_GOLD),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), TITELLI_LIGHT_GOLD),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(projections_table)
    story.append(Spacer(1, 1*cm))
    
    story.append(Paragraph("Comparaison avec les géants du secteur", styles['SubSection']))
    
    comparison_giants = [
        ['Entreprise', 'Marge brute', 'Source principale'],
        ['Instagram (Meta)', '~80%', 'Publicité ciblée'],
        ['Uber Eats', '~30%', 'Commissions + livraison'],
        ['Amazon Marketplace', '~25%', 'Commissions + FBA'],
        ['Deliveroo', '~35%', 'Commissions'],
        ['Titelli (projection)', '~91%', 'Abonnements + IA'],
    ]
    
    giants_table = Table(comparison_giants, colWidths=[5*cm, 3*cm, 7*cm])
    giants_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TITELLI_GOLD),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, TITELLI_BLUE),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), TITELLI_LIGHT_GOLD),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(giants_table)
    story.append(Spacer(1, 1*cm))
    
    story.append(Paragraph("Conclusion", styles['SubSection']))
    story.append(Paragraph("""
    Le modèle économique de Titelli combine les meilleures pratiques des géants du digital 
    avec une approche locale et personnalisée. Les marges élevées (~91%) sont rendues possibles 
    par l'utilisation intensive de l'IA pour la création de contenu publicitaire, réduisant 
    drastiquement les coûts de production tout en offrant une valeur ajoutée significative 
    aux entreprises partenaires.
    """, styles['TitelliBody']))
    
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("© 2026 Titelli SA - Tous droits réservés", styles['Footer']))
    story.append(Paragraph("www.titelli.com | contact@titelli.com", styles['Footer']))
    
    # Build PDF
    doc.build(story)
    print(f"✅ Brochure générée avec succès: {OUTPUT_PATH}")
    return OUTPUT_PATH

if __name__ == "__main__":
    create_monetization_brochure()
