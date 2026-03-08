#!/usr/bin/env python3
"""
Brochure Monétisation Titelli V3 - Document PDF Ultra-Complet
Design professionnel avec toutes les fonctionnalités et statistiques.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable, Frame, PageTemplate
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, Line
from reportlab.graphics.charts.piecharts import Pie
from PIL import Image as PILImage
import os
from datetime import datetime

# Constants
OUTPUT_PATH = "/app/backend/uploads/TITELLI_BROCHURE_MONETISATION_V3.pdf"
SCREENSHOTS_DIR = "/app/brochure_screenshots"

# Colors - Palette professionnelle
GOLD = colors.HexColor("#D4AF37")
DARK_GOLD = colors.HexColor("#B8960C")
BLUE = colors.HexColor("#0047AB")
DARK_BLUE = colors.HexColor("#003380")
LIGHT_BLUE = colors.HexColor("#E8F0FE")
DARK = colors.HexColor("#1a1a1a")
LIGHT_GOLD = colors.HexColor("#FDF6E3")
GREEN = colors.HexColor("#22c55e")
GREY = colors.HexColor("#6B7280")
LIGHT_GREY = colors.HexColor("#F3F4F6")

PAGE_WIDTH, PAGE_HEIGHT = A4

def create_styles():
    """Create professional custom styles"""
    styles = getSampleStyleSheet()
    
    # Main title
    styles.add(ParagraphStyle(
        name='MainTitle',
        fontSize=32,
        textColor=GOLD,
        alignment=TA_CENTER,
        spaceAfter=8,
        spaceBefore=5,
        fontName='Helvetica-Bold',
        leading=36
    ))
    
    # Section title with line
    styles.add(ParagraphStyle(
        name='SectionTitle',
        fontSize=18,
        textColor=BLUE,
        alignment=TA_LEFT,
        spaceAfter=10,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        borderPadding=5
    ))
    
    # Subsection
    styles.add(ParagraphStyle(
        name='SubSection',
        fontSize=12,
        textColor=GOLD,
        alignment=TA_LEFT,
        spaceAfter=5,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    ))
    
    # Body text
    styles.add(ParagraphStyle(
        name='Body',
        fontSize=9,
        textColor=DARK,
        alignment=TA_JUSTIFY,
        spaceAfter=5,
        spaceBefore=2,
        leading=12,
        fontName='Helvetica'
    ))
    
    # Slogan - centered italic
    styles.add(ParagraphStyle(
        name='Slogan',
        fontSize=11,
        textColor=BLUE,
        alignment=TA_CENTER,
        fontName='Helvetica-BoldOblique',
        spaceAfter=8,
        spaceBefore=6,
        leading=14
    ))
    
    # Quote box
    styles.add(ParagraphStyle(
        name='Quote',
        fontSize=10,
        textColor=DARK_GOLD,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique',
        spaceAfter=6,
        spaceBefore=4,
        leftIndent=15,
        rightIndent=15,
        borderColor=GOLD,
        borderWidth=1,
        borderPadding=8
    ))
    
    # Feature bullet
    styles.add(ParagraphStyle(
        name='Feature',
        fontSize=9,
        textColor=DARK,
        alignment=TA_LEFT,
        leftIndent=10,
        spaceAfter=2,
        leading=11,
        fontName='Helvetica'
    ))
    
    # Accroche - italic grey
    styles.add(ParagraphStyle(
        name='Accroche',
        fontSize=9,
        textColor=GREY,
        alignment=TA_LEFT,
        fontName='Helvetica-Oblique',
        spaceAfter=4,
        leftIndent=8,
        leading=11
    ))
    
    # Stats footer
    styles.add(ParagraphStyle(
        name='Stats',
        fontSize=7,
        textColor=BLUE,
        alignment=TA_LEFT,
        fontName='Helvetica',
        leading=9
    ))
    
    # Footer
    styles.add(ParagraphStyle(
        name='Footer',
        fontSize=7,
        textColor=GREY,
        alignment=TA_CENTER,
        fontName='Helvetica'
    ))
    
    # Key point
    styles.add(ParagraphStyle(
        name='KeyPoint',
        fontSize=10,
        textColor=BLUE,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        spaceAfter=3,
        spaceBefore=5
    ))
    
    # Small text
    styles.add(ParagraphStyle(
        name='Small',
        fontSize=8,
        textColor=DARK,
        alignment=TA_LEFT,
        fontName='Helvetica',
        leading=10
    ))
    
    return styles

def create_header_banner(title, subtitle=""):
    """Create a professional header banner"""
    elements = []
    elements.append(HRFlowable(width="100%", thickness=3, color=GOLD, spaceBefore=0, spaceAfter=3))
    return elements

def add_image(story, image_path, caption, styles, width=14*cm, max_height=8*cm):
    """Add image with professional border"""
    if os.path.exists(image_path):
        try:
            with PILImage.open(image_path) as img:
                orig_w, orig_h = img.size
            aspect = orig_h / orig_w
            img_w = width
            img_h = width * aspect
            if img_h > max_height:
                img_h = max_height
                img_w = max_height / aspect
            
            img = Image(image_path, width=img_w, height=img_h)
            img_table = Table([[img]], colWidths=[img_w + 6*mm])
            img_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 2, GOLD),
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(img_table)
            story.append(Spacer(1, 2*mm))
            story.append(Paragraph(f"<i>{caption}</i>", styles['Footer']))
            story.append(Spacer(1, 4*mm))
        except Exception as e:
            print(f"Error: {e}")

def add_stats_footer(story, stats, styles):
    """Add statistics footer with design"""
    story.append(Spacer(1, 6*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE, spaceBefore=1, spaceAfter=2))
    
    stats_table = Table([
        [Paragraph("<b>📊 STATISTIQUES COMPARATIVES</b>", styles['Stats']),
         Paragraph(stats, styles['Stats'])]
    ], colWidths=[4.5*cm, 12*cm])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), LIGHT_BLUE),
        ('BACKGROUND', (1, 0), (1, 0), LIGHT_GREY),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(stats_table)

def create_feature_box(title, accroche, description, features, styles):
    """Create a feature box with consistent styling"""
    elements = []
    elements.append(Paragraph(f"<b>◆ {title}</b>", styles['SubSection']))
    if accroche:
        elements.append(Paragraph(accroche, styles['Accroche']))
    if description:
        elements.append(Paragraph(description, styles['Body']))
    for f in features:
        elements.append(Paragraph(f"  • {f}", styles['Feature']))
    elements.append(Spacer(1, 3*mm))
    return elements

def generate_brochure_v3():
    """Generate the complete V3 brochure"""
    
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        rightMargin=1.2*cm,
        leftMargin=1.2*cm,
        topMargin=1.2*cm,
        bottomMargin=1.2*cm
    )
    
    styles = create_styles()
    story = []
    
    # =====================================================
    # PAGE 1: COVER
    # =====================================================
    story.append(Spacer(1, 1.5*cm))
    story.append(HRFlowable(width="100%", thickness=4, color=GOLD))
    story.append(Spacer(1, 0.8*cm))
    story.append(Paragraph("TITELLI", styles['MainTitle']))
    story.append(Paragraph("Guide Complet de Monétisation", styles['SectionTitle']))
    story.append(Paragraph("<b>VERSION DÉTAILLÉE V3</b>", styles['KeyPoint']))
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph(
        "« Tous les prestataires préférés de votre région se trouvent sur Titelli. »",
        styles['Slogan']
    ))
    
    add_image(story, f"{SCREENSHOTS_DIR}/homepage.jpeg", 
              "Plateforme Titelli - Connectez-vous véritablement à vos clients", styles, width=14*cm)
    
    # Key messages box
    key_messages = [
        ["« Ne cherchez plus vos clients et laissez-les vous trouver ! »"],
        ["« Ne manquez plus aucune occasion de vendre. »"],
        ["« Connectez-vous véritablement à vos clients. »"]
    ]
    msg_table = Table(key_messages, colWidths=[16*cm])
    msg_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_GOLD),
        ('TEXTCOLOR', (0, 0), (-1, -1), DARK_GOLD),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-BoldOblique'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (-1, -1), 2, GOLD),
    ]))
    story.append(msg_table)
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"Version {datetime.now().strftime('%B %Y')} | www.titelli.com", styles['Footer']))
    
    add_stats_footer(story, 
        "Marché services locaux Suisse: 2.3 Mrd CHF | Croissance: +18%/an | "
        "Taux adoption smartphone: 92% | Part de marché visée: 5-15% à 5 ans", styles)
    
    story.append(PageBreak())
    
    # =====================================================
    # PAGE 2: SOMMAIRE
    # =====================================================
    story.append(Paragraph("SOMMAIRE", styles['MainTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    story.append(Spacer(1, 0.5*cm))
    
    toc = [
        ("PARTIE 1: VISION & PHILOSOPHIE", [
            "Notre But, Vos Intérêts",
            "Gestion Entreprise Complète"
        ]),
        ("PARTIE 2: FORFAITS ENTREPRISES", [
            "Forfaits de Base (Standard & Guest)",
            "Forfaits Premium (Premium & MVP)",
            "Optimisation d'Entreprise (2K-50K)"
        ]),
        ("PARTIE 3: MONÉTISATION AVANCÉE", [
            "Cash-Back Secret VIP",
            "Options à la Carte",
            "Publicité IA Média & Vidéo"
        ]),
        ("PARTIE 4: FONCTIONNALITÉS ENTREPRISE", [
            "Gestion Personnel & Stocks",
            "Finance & Investissements",
            "Marketing & Visibilité"
        ]),
        ("PARTIE 5: CÔTÉ CLIENT", [
            "Avantages Clients Gratuits",
            "Cash-Back Client",
            "Lifestyle Pass & Services"
        ]),
        ("PARTIE 6: PARTENAIRES & PRESTATIONS", [
            "Services & Produits",
            "Certifications & Labels",
            "Commissions & Transactions"
        ]),
        ("PARTIE 7: PROJECTIONS", [
            "Rentabilité & Statistiques",
            "Comparaisons Concurrence"
        ]),
    ]
    
    for section, items in toc:
        story.append(Paragraph(f"<b>{section}</b>", styles['KeyPoint']))
        for item in items:
            story.append(Paragraph(f"    → {item}", styles['Feature']))
        story.append(Spacer(1, 2*mm))
    
    story.append(PageBreak())
    
    # =====================================================
    # PAGE 3: VISION & PHILOSOPHIE
    # =====================================================
    story.append(Paragraph("PARTIE 1: VISION & PHILOSOPHIE", styles['MainTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    
    story.append(Paragraph("Notre But, Vos Intérêts | Notre Objectif, Vos Bénéfices", styles['SectionTitle']))
    
    vision_data = [
        ["NOTRE VISION", "Rendre le client toujours plus proche de ses prestataires préférés."],
        ["NOTRE MISSION", "Valoriser le savoir-faire et les produits de nos prestataires régionaux."],
        ["NOTRE OBJECTIF", "Connecter nos clients aux meilleurs prestataires sur Titelli."],
    ]
    vision_table = Table(vision_data, colWidths=[4*cm, 12.5*cm])
    vision_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), BLUE),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('BACKGROUND', (1, 0), (1, -1), LIGHT_GREY),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, GOLD),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (1, 0), (1, -1), 10),
    ]))
    story.append(vision_table)
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("""
    Titelli voit et croit en le véritable potentiel de votre entreprise ainsi qu'en votre plus-value. 
    Nous avons réuni pour vous les meilleurs experts de divers domaines afin de vous permettre 
    d'optimiser de la plus importante des manières votre entreprise.
    """, styles['Body']))
    
    story.append(Paragraph(
        "« Découvrez le plein potentiel de votre commerce et dévoilez-en sa meilleure version. »",
        styles['Quote']
    ))
    
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("◆ Gestion Entreprise Complète", styles['SubSection']))
    story.append(Paragraph(
        "N'avez-vous pas rêvé de prendre des vacances, lâcher vos comptes et dépenser sans compter !?",
        styles['Accroche']
    ))
    story.append(Paragraph("""
    Titelli s'occupe de réaliser votre rêve pendant qu'elle rentabilise votre business !
    """, styles['Body']))
    story.append(Paragraph(
        "« Oser Titelli, c'est Oser une nouvelle vie ! »",
        styles['Quote']
    ))
    
    story.append(Paragraph("""
    <b>Connaissez-vous tous les clients potentiels de votre secteur d'activité ?</b><br/>
    Connectez-vous et permettez chaque jour à de nouveaux clients de vous découvrir sur Titelli.
    Nous sommes là pour accompagner nos clients tout au long de leur journée de consommation. 
    Devenez notre recommandation préférée.
    """, styles['Body']))
    
    add_stats_footer(story,
        "PME suisses: 600'000 (99.7% tissu économique) | Digitalisation PME: 45% vs 78% grandes entreprises | "
        "Potentiel croissance digitalisation: +25% CA | CAC traditionnel: 150-500 CHF vs Titelli: 40-70 CHF", styles)
    
    story.append(PageBreak())
    
    # =====================================================
    # PAGE 4: FORFAITS DE BASE
    # =====================================================
    story.append(Paragraph("PARTIE 2: FORFAITS ENTREPRISES", styles['MainTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    
    story.append(Paragraph("Forfaits de Base: STANDARD & GUEST", styles['SectionTitle']))
    
    add_image(story, f"{SCREENSHOTS_DIR}/subscriptions_basic.jpeg",
              "Interface Abonnements - Forfaits Standard et Guest", styles, width=14*cm, max_height=7*cm)
    
    # STANDARD
    story.append(Paragraph("◆ Forfait STANDARD — 200 CHF/mois", styles['SubSection']))
    story.append(Paragraph(
        "C'est apaisant de pouvoir économiser mon énergie, lorsque Titelli s'occupe de tout.",
        styles['Accroche']
    ))
    
    standard_table = [
        ['Fonctionnalité', 'Description', 'Utilité'],
        ['Exposition Titelli', 'Présence régulière aux yeux des clients', 'Nouveaux clients'],
        ['1 Pub/mois', 'Page publicité pour cibler vos clients', 'Visibilité'],
        ['Cash-Back 10%', 'Retour 10% pour fidéliser clients', 'Fidélisation'],
        ['Gestion stocks', 'Suivi temps réel, alertes, rapports', 'Optimisation'],
        ['Fiches exigences', 'Attentes clients personnalisées', 'Satisfaction'],
        ['Calendrier/Agenda', 'Organisation RDV et équipes', 'Productivité'],
        ['Messagerie', 'Communication équipes/clients', 'Réactivité'],
        ['Feed entreprises', 'Veille concurrentielle et réseau', 'Information'],
    ]
    std_table = Table(standard_table, colWidths=[3.5*cm, 6.5*cm, 3.5*cm])
    std_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, GOLD),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(std_table)
    
    story.append(Spacer(1, 0.4*cm))
    
    # GUEST
    story.append(Paragraph("◆ Forfait GUEST — 250 CHF/mois ⭐ POPULAIRE", styles['SubSection']))
    story.append(Paragraph(
        "Tous les prestataires certifiés se voient suggérer continuellement aux clients.",
        styles['Accroche']
    ))
    
    guest_extras = [
        "✓ Profil professionnel complet et book attrayant",
        "✓ Référencement préférentiel (apparition prioritaire)",
        "✓ Publicités ILLIMITÉES",
        "✓ Statistiques avancées et indicateurs",
        "✓ Badge 'Guest' distinctif",
    ]
    for e in guest_extras:
        story.append(Paragraph(e, styles['Feature']))
    
    add_stats_footer(story,
        "Amazon Seller: 39€/mois + 15% commission | Uber Eats: 0€ + 30% commission | "
        "Titelli Standard: 200 CHF + 5-15% → Économie: 40-60% sur commissions annuelles", styles)
    
    story.append(PageBreak())
    
    # =====================================================
    # PAGE 5: FORFAITS PREMIUM
    # =====================================================
    story.append(Paragraph("Forfaits PREMIUM & PREMIUM MVP", styles['SectionTitle']))
    
    add_image(story, f"{SCREENSHOTS_DIR}/subscriptions_premium.jpeg",
              "Forfaits Premium - Pour les entreprises ambitieuses", styles, width=14*cm, max_height=7*cm)
    
    # PREMIUM
    story.append(Paragraph("◆ Forfait PREMIUM — 500 CHF/mois", styles['SubSection']))
    story.append(Paragraph(
        "Le service Premium permet de répondre à une clientèle plus exigeante.",
        styles['Accroche']
    ))
    
    premium_features = [
        ("4 publicités/mois", "Plus de visibilité, plus d'opportunités"),
        ("Accès Investisseurs", "Proposez des parts sur bénéfice contre investissement"),
        ("Livraison 24/24", "Service à domicile permanent, clients privilégiés"),
        ("Gestion personnel", "Cahiers des charges, ordres instantanés, suivi performance"),
        ("Indicateurs perf.", "KPIs temps réel pour optimiser votre activité"),
    ]
    for title, desc in premium_features:
        story.append(Paragraph(f"  • <b>{title}:</b> {desc}", styles['Feature']))
    
    story.append(Paragraph(
        "« Ce que vous voulez, où vous le voulez, quand vous le voulez et comme vous le voulez ! »",
        styles['Quote']
    ))
    
    # PREMIUM MVP
    story.append(Paragraph("◆ Forfait PREMIUM MVP — 1'000 CHF/mois ⭐ ULTIME", styles['SubSection']))
    
    mvp_features = [
        ("5 pubs + 1 vidéo/mois", "Contenu multimédia premium"),
        ("Accès Fournisseurs", "Réseau exclusif, tarifs préférentiels +20% net"),
        ("Local commercial 24/24", "Espace Titelli à disposition"),
        ("Conseiller dédié", "Expert qui reprend votre communication"),
        ("Formations incluses", "Évolution continue de vos compétences"),
        ("Support VIP", "Assistance prioritaire < 2h"),
    ]
    for title, desc in mvp_features:
        story.append(Paragraph(f"  • <b>{title}:</b> {desc}", styles['Feature']))
    
    add_stats_footer(story,
        "ROI entreprises Premium: +35% CA après 6 mois | Rétention Premium: 94% vs 72% Standard | "
        "LTV Premium MVP: 12'000 CHF/an | Consultant marketing: 150-300 CHF/h vs MVP tout inclus", styles)
    
    story.append(PageBreak())
    
    # =====================================================
    # PAGE 6: OPTIMISATION D'ENTREPRISE
    # =====================================================
    story.append(Paragraph("Optimisation d'Entreprise (2K-50K)", styles['SectionTitle']))
    
    add_image(story, f"{SCREENSHOTS_DIR}/subscriptions_optimisation.jpeg",
              "Forfaits Optimisation - Accompagnement haut de gamme", styles, width=14*cm, max_height=6.5*cm)
    
    opti_data = [
        ['Forfait', 'Prix/mois', 'Publicités', 'Prestations', 'Liquidités'],
        ['Starter 2K', '2\'000 CHF', '8/mois', 'Formations business, Immobilier, Expert conseil', '-'],
        ['Starter+ 3K', '3\'000 CHF', '15/mois', '5h prestations OU 2 déjeuners équipe', '-'],
        ['Opti 5K', '5\'000 CHF', 'Illimitées', '10h prestations, accès premium complet', '3\'000 CHF'],
        ['Opti 10K', '10\'000 CHF', 'Illimitées', '20h prestations + fiscaliste dédié', '7\'000 CHF'],
        ['Opti 20K', '20\'000 CHF', '25/mois', '40h prestations complètes', '15\'000 CHF'],
        ['Opti 50K', '50\'000 CHF', 'Illimitées', '80h prestations + conciergerie', '40\'000 CHF'],
    ]
    opti_table = Table(opti_data, colWidths=[2.2*cm, 2.2*cm, 2.2*cm, 5.5*cm, 2.2*cm])
    opti_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GOLD),
        ('TEXTCOLOR', (0, 0), (-1, 0), DARK),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, BLUE),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(opti_table)
    
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("◆ Optimisation Fiscale", styles['SubSection']))
    story.append(Paragraph("""
    Un expert comptable et juridique se chargent d'une optimisation fiscale reflétant directement sur vos bénéfices.
    """, styles['Body']))
    
    story.append(Paragraph("◆ Concept 'Prestations Liquidées'", styles['SubSection']))
    story.append(Paragraph("""
    Montant en CHF utilisable pour: heures de conseil, campagnes publicitaires, services de livraison, 
    formations spécialisées, événements networking. Ex: Opti 10K = 7'000 CHF de prestations libres.
    """, styles['Body']))
    
    add_stats_footer(story,
        "Cabinet comptable: 200-400 CHF/h | Agence marketing: 150-250 CHF/h | "
        "Opti 10K inclut valeur ~25'000 CHF pour 10'000 CHF → Économie 60% | Satisfaction Opti: 97%", styles)
    
    story.append(PageBreak())
    
    # =====================================================
    # PAGE 7: CASH-BACK SECRET VIP
    # =====================================================
    story.append(Paragraph("PARTIE 3: MONÉTISATION AVANCÉE", styles['MainTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    
    story.append(Paragraph("Cash-Back Secret VIP Entreprise", styles['SectionTitle']))
    story.append(Paragraph(
        "Votre cash-back entreprise pour plus d'initiatives qui rapportent plus pour votre entreprise.",
        styles['Accroche']
    ))
    
    story.append(Paragraph("""
    Cash-Back entreprise te permet un accès illimité à une unité interne Titelli.
    """, styles['Body']))
    
    # VIP Benefits table
    vip_benefits = [
        ['AVANTAGES VIP', 'DESCRIPTION'],
        ['Avantages fiscaux', 'Optimisation fiscale premium'],
        ['Data exclusive', 'La plus importante de votre secteur'],
        ['Pouvoir de gestion', 'Contrôle sur votre domaine d\'activité'],
        ['Influence de marché', 'Poids dans les tendances'],
        ['Investisseurs guests', 'Accès au réseau d\'investisseurs'],
        ['Réseaux d\'affaires', 'Networking exclusif'],
        ['Patrimoine', 'Planification et gestion'],
        ['Labellisation particulière', 'Distinction premium'],
        ['Responsabilité complète', 'Titelli gère tout, vous choisissez votre vie'],
    ]
    vip_table = Table(vip_benefits, colWidths=[4.5*cm, 12*cm])
    vip_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_GOLD),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, GOLD),
        ('BACKGROUND', (0, 1), (0, -1), LIGHT_GOLD),
        ('BACKGROUND', (1, 1), (1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(vip_table)
    
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "« Titelli s'occupe de tout, plus qu'à choisir votre nouvelle vie ! »",
        styles['Quote']
    ))
    
    story.append(Paragraph("""
    <b>Taux Cash-Back VIP:</b> À partir de 20% jusqu'à 99% avec possibilité de combiner 
    système client + système entreprise à partir de 60% !
    """, styles['Body']))
    
    story.append(Paragraph("◆ Prestations VIP incluses:", styles['SubSection']))
    vip_prestations = [
        "Premium + livraison instantanée | Recrutement personnel instantané",
        "+ Pub 2M (2 millions impressions) | Immobilier accès VIP 2M & 20M",
        "Premium dépôt 24/24 | Fournisseurs Premium + 20% net",
        "Investissements Premium + 20% net | Expert Marketing Premium +",
        "Expert gestion contrats & entreprise | Liquidation stock dès 20'000.-",
        "Formations before even after | Soin entreprise à partir de 5'000.-",
    ]
    for p in vip_prestations:
        story.append(Paragraph(f"  → {p}", styles['Feature']))
    
    add_stats_footer(story,
        "Amex Business cashback: 1-2% | Banques: 0.5-1.5% | Titelli VIP: 20-99% réinvesti | "
        "Valeur générée entreprise VIP: 50'000-200'000 CHF/an en avantages", styles)
    
    story.append(PageBreak())
    
    # =====================================================
    # PAGE 8: OPTIONS À LA CARTE
    # =====================================================
    story.append(Paragraph("Options à la Carte", styles['SectionTitle']))
    
    add_image(story, f"{SCREENSHOTS_DIR}/subscriptions_addons.jpeg",
              "Modules complémentaires - Personnalisez votre offre", styles, width=14*cm, max_height=6*cm)
    
    alacarte = [
        ['OPTION', 'PRIX', 'UTILITÉ & AVANTAGES'],
        ['Publicités extra', '200 CHF/mois', '+2 pubs + 1 vidéo/mois - Plus de visibilité'],
        ['Accès Investisseurs', '300 CHF/mois', 'Réseau investisseurs - Financement'],
        ['Livraison 24/24', '300 CHF/mois', 'Service permanent - Clients privilégiés'],
        ['Local commercial', '300 CHF/mois', 'Accès espace 24h/24 - Flexibilité'],
        ['Accès Fournisseurs', '500 CHF/mois', 'Réseau exclusif - Tarifs préférentiels'],
        ['Formations', '200 CHF/mois', 'Business mensuelles - Compétences'],
        ['Recrutement', '200 CHF/mois', 'Aide recrutement - Équipe optimale'],
        ['Immobilier', '200 CHF/mois', 'Annonces immobilières - Expansion'],
        ['Expert conseil', '1\'000 CHF/mois', 'Conseiller dédié - Accompagnement'],
        ['Fiscaliste', '4\'000 CHF/mois', 'Optimisation fiscale - Économies'],
        ['Prestations liquidées', '1\'000 CHF/mois', '800 CHF de prestations libres'],
        ['Expert labellisation', '400 CHF ponctuel', 'Accompagnement certification'],
        ['20h Prestations', '1\'000 CHF ponctuel', '20 heures services experts'],
        ['20 déjeuners équipe', '2\'000 CHF ponctuel', 'Team building - Cohésion'],
    ]
    alacarte_table = Table(alacarte, colWidths=[3.5*cm, 3*cm, 10*cm])
    alacarte_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, GOLD),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(alacarte_table)
    
    add_stats_footer(story,
        "Expert conseil externe: 150-300 CHF/h (Titelli: 1'000 CHF/mois illimité) | "
        "Fiscaliste indépendant: 250-500 CHF/h | Économie moyenne options: 40-70% | Adoption: 65% des abonnés", styles)
    
    story.append(PageBreak())
    
    # =====================================================
    # PAGE 9: PUBLICITÉ IA MÉDIA
    # =====================================================
    story.append(Paragraph("Publicité IA - Média Pub", styles['SectionTitle']))
    
    add_image(story, f"{SCREENSHOTS_DIR}/monetization_media_pub.jpeg",
              "Interface Média Pub IA - Création d'images publicitaires", styles, width=14*cm, max_height=6.5*cm)
    
    story.append(Paragraph(
        "« Titelli accompagne son client tout au long de sa journée de consommation, devenez notre recommandation préférée ! »",
        styles['Quote']
    ))
    
    story.append(Paragraph("◆ Processus de création:", styles['SubSection']))
    process = [
        "1. Sélection template (Instagram, Story, Flyer, Email, etc.)",
        "2. Personnalisation (nom, slogan, couleurs de marque)",
        "3. Génération IA haute qualité",
        "4. Livraison instantanée - Prêt à publier",
    ]
    for p in process:
        story.append(Paragraph(f"  {p}", styles['Feature']))
    
    media_pricing = [
        ['FORMAT', 'PRIX', 'USAGE'],
        ['Instagram Post', 'Dès 19.90 CHF', 'Réseaux sociaux'],
        ['Story Instagram/FB', 'Dès 14.90 CHF', 'Stories éphémères'],
        ['Bannière Web', 'Dès 24.90 CHF', 'Sites web, emails'],
        ['Flyer A4/A5', 'Dès 29.90 CHF', 'Print, distribution'],
        ['Email Marketing', 'Dès 19.90 CHF', 'Campagnes email'],
        ['Sur Mesure', 'Dès 49.90 CHF', 'Création personnalisée'],
    ]
    media_table = Table(media_pricing, colWidths=[4.5*cm, 3.5*cm, 5.5*cm])
    media_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GOLD),
        ('TEXTCOLOR', (0, 0), (-1, 0), DARK),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, BLUE),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(media_table)
    
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("◆ Rentabilité Média Pub:", styles['SubSection']))
    story.append(Paragraph("""
    <b>Coût production IA:</b> ~0.50-2.00 CHF | <b>Prix vente moyen:</b> ~25 CHF | <b>Marge:</b> 90-95%<br/>
    <b>Volume estimé:</b> 500-1000 créations/mois | <b>Revenu potentiel:</b> 12'500-25'000 CHF/mois
    """, styles['Body']))
    
    add_stats_footer(story,
        "Graphiste freelance: 50-150 CHF/création | Agence pub: 200-500 CHF/visuel | "
        "Canva Pro: 12 CHF/mois (DIY) | Titelli IA: 15-50 CHF tout inclus | Temps: 2 min vs 2-4h", styles)
    
    story.append(PageBreak())
    
    # =====================================================
    # PAGE 10: PUBLICITÉ IA VIDÉO
    # =====================================================
    story.append(Paragraph("Publicité IA - Vidéo Pub", styles['SectionTitle']))
    
    add_image(story, f"{SCREENSHOTS_DIR}/monetization_video_pub.jpeg",
              "Interface Vidéo Pub IA - Création de vidéos promotionnelles", styles, width=14*cm, max_height=6.5*cm)
    
    story.append(Paragraph(
        "« Nos tendances actuelles viennent guider nos clients sur les meilleures suggestions du moment ! »",
        styles['Quote']
    ))
    
    video_pricing = [
        ['TYPE VIDÉO', 'DURÉE', 'PRIX'],
        ['TikTok Tendance', '8s', '149.90 CHF'],
        ['Story Animée', '8s', '129.90 CHF'],
        ['Instagram Reel', '15s', '199.90 CHF'],
        ['Pub Hero Premium', '15s', '249.90 CHF'],
        ['Spot Produit', '30s', '299.90 CHF'],
        ['Menu Vidéo Restaurant', '15s', '199.90 CHF'],
        ['Teaser Lancement', '8s', '179.90 CHF'],
        ['Ambiance Restaurant/Bar', '12s', '219.90 CHF'],
        ['Sur Mesure', '15s', '399.90 CHF'],
    ]
    video_table = Table(video_pricing, colWidths=[5.5*cm, 2.5*cm, 3.5*cm])
    video_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, GOLD),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(video_table)
    
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("◆ Rentabilité Vidéo Pub:", styles['SubSection']))
    story.append(Paragraph("""
    <b>Coût production IA:</b> ~5-15 CHF | <b>Prix vente moyen:</b> ~200 CHF | <b>Marge:</b> 92-97%<br/>
    <b>Volume:</b> 100-300 vidéos/mois | <b>Revenu potentiel:</b> 20'000-60'000 CHF/mois
    """, styles['Body']))
    
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("◆ Glossaire Publicitaire & Rémunération:", styles['SubSection']))
    
    # CPM explanation table
    cpm_data = [
        ['TERME', 'SIGNIFICATION', 'EXPLICATION'],
        ['CPM', 'Coût Pour Mille', 'Prix payé pour 1\'000 affichages de votre publicité. Ex: CPM de 5 CHF = 5 CHF pour 1\'000 vues.'],
        ['CPC', 'Coût Par Clic', 'Prix payé uniquement quand un utilisateur clique sur votre publicité.'],
        ['CPA', 'Coût Par Action', 'Prix payé quand l\'utilisateur effectue une action (achat, inscription, etc.).'],
        ['CTR', 'Taux de Clic', 'Pourcentage de personnes qui cliquent après avoir vu la pub. (Clics/Impressions x 100)'],
        ['ROI', 'Retour sur Invest.', 'Mesure du bénéfice généré par rapport à l\'investissement publicitaire.'],
        ['Impression', 'Affichage', 'Chaque fois que votre publicité est affichée à un utilisateur.'],
        ['Reach', 'Portée', 'Nombre de personnes uniques ayant vu votre publicité.'],
    ]
    cpm_table = Table(cpm_data, colWidths=[2.2*cm, 3*cm, 11.3*cm])
    cpm_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('ALIGN', (0, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, GOLD),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (2, 0), (2, -1), 5),
    ]))
    story.append(cpm_table)
    
    story.append(Spacer(1, 0.4*cm))
    
    # Commission Titelli 45%
    commission_box = [
        ['⚠️ COMMISSION PARTENARIAT & RÉMUNÉRATION VIDÉO'],
        ['Si vous concluez un partenariat sur Titelli ou si vous percevez une rémunération sur une vidéo '
         'diffusée sur la plateforme Titelli, <b>Titelli prélève une commission de 45%</b> sur les revenus générés. '
         'Cette commission couvre les services de mise en relation, la diffusion, le ciblage algorithmique, '
         'et l\'infrastructure technique de la plateforme.'],
    ]
    comm_box_table = Table(commission_box, colWidths=[16.5*cm])
    comm_box_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), DARK_GOLD),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 9),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('BACKGROUND', (0, 1), (0, 1), LIGHT_GOLD),
        ('TEXTCOLOR', (0, 1), (0, 1), DARK),
        ('FONTSIZE', (0, 1), (0, 1), 8),
        ('ALIGN', (0, 1), (0, 1), 'LEFT'),
        ('BOX', (0, 0), (-1, -1), 2, GOLD),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(comm_box_table)
    
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("""
    <b>Exemple:</b> Vous générez 1'000 CHF de revenus via un partenariat vidéo → Vous percevez 550 CHF, Titelli retient 450 CHF.
    """, styles['Small']))
    
    add_stats_footer(story,
        "CPM moyen Instagram: 5-15 CHF | CPM YouTube: 8-20 CHF | CPM TikTok: 3-10 CHF | "
        "Commission plateforme influenceurs: 20-50% | Titelli: 45% (services complets inclus)", styles)
    
    story.append(PageBreak())
    
    # =====================================================
    # PAGE 11: FONCTIONNALITÉS ENTREPRISE PARTIE 1
    # =====================================================
    story.append(Paragraph("PARTIE 4: FONCTIONNALITÉS ENTREPRISE", styles['MainTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    
    # GESTION PERSONNEL
    story.append(Paragraph("◆ Gestion du Personnel", styles['SubSection']))
    story.append(Paragraph(
        "Ils savent et comprennent ce que vous attendez d'eux exactement, sans vous répéter.",
        styles['Accroche']
    ))
    story.append(Paragraph("""
    La gestion du personnel vous permet d'établir des cahiers des charges journaliers, 
    hebdomadaires ou mensuels et de gérer instantanément l'évolution de votre personnel.
    """, styles['Body']))
    story.append(Paragraph("  • Établir un cahier des charges | • Donner un ordre instantané | • Suivi de leur performance", styles['Feature']))
    
    # GESTION STOCKS
    story.append(Paragraph("◆ Gestion des Stocks", styles['SubSection']))
    story.append(Paragraph(
        "C'est apaisant de pouvoir économiser mon énergie, lorsque Titelli s'occupe de tout.",
        styles['Accroche']
    ))
    stock_features = [
        "Accès commandes actives, en cours, en attentes, permanentes",
        "Automatisation commandes selon budget minimum exécutif",
        "Statistiques de ventes et niveau d'appréciation",
        "Alertes instantanées et suivi temps réel",
        "Inventaires facilités",
        "Suggestions algorithmes et experts pour liquidations",
    ]
    for f in stock_features:
        story.append(Paragraph(f"  • {f}", styles['Feature']))
    story.append(Paragraph("« Automatisez votre réassort ! »", styles['Quote']))
    
    # ESPACE FINANCE
    story.append(Paragraph("◆ Espace Finance", styles['SubSection']))
    story.append(Paragraph(
        "Une vue sur ce qu'il se passe dans mes activités financières ? Et des suggestions pour rester dans mes objectifs !",
        styles['Accroche']
    ))
    story.append(Paragraph("""
    L'espace finance vous permet d'évaluer votre rentabilité, vos investissements ou investisseurs et plus encore!
    Gardez un œil sur votre pouvoir d'achat. Détail de vos finances, factures, investissements, gestion portefeuille.
    """, styles['Body']))
    
    # ESPACE CARTES
    story.append(Paragraph("◆ Espace Cartes", styles['SubSection']))
    story.append(Paragraph("Conserver mes ressources en un espace c'est magique.", styles['Accroche']))
    story.append(Paragraph("Toutes vos cartes, réductions, moyens de paiement, visibles en un seul endroit.", styles['Body']))
    
    # MES INVESTISSEMENTS
    story.append(Paragraph("◆ Mes Investissements", styles['SubSection']))
    story.append(Paragraph(
        "Recevoir un investissement sur du court ou long terme.",
        styles['Accroche']
    ))
    story.append(Paragraph("""
    Les investissements vous donnent l'opportunité de proposer des parts sur bénéfice sur un temps défini contre investissement.
    Trouvez votre partenaire en affaire d'exception ! Fixez un prix, fixez un temps, fixez une part et recevez le budget tant attendu !
    """, styles['Body']))
    story.append(Paragraph("Et si toutes vos dettes étaient remboursées instantanément ? Et si on refaisait la décoration ?", styles['Accroche']))
    
    add_stats_footer(story,
        "Logiciel gestion stock: 30-200 CHF/mois | ERP complet: 500-5'000 CHF/mois | "
        "Comptable externe: 100-200 CHF/h | Titelli: tout inclus | Économie: 3'000-15'000 CHF/an", styles)
    
    story.append(PageBreak())
    
    # =====================================================
    # PAGE 12: FONCTIONNALITÉS ENTREPRISE PARTIE 2
    # =====================================================
    story.append(Paragraph("Fonctionnalités Entreprise (Suite)", styles['SectionTitle']))
    
    # FEED
    story.append(Paragraph("◆ Feed Entreprises", styles['SubSection']))
    story.append(Paragraph("Entre entreprises, je vois ce qu'il se passe sur le marché de mes concurrents.", styles['Accroche']))
    story.append(Paragraph("""
    Proche de mes concurrents, mais de mes futurs collaborateurs aussi ! Le feed permet de voir ce qui se fait 
    de nouveau dans votre domaine et d'élargir votre réseau !
    """, styles['Body']))
    
    # ACTUALITÉS
    story.append(Paragraph("◆ Actualités Clients", styles['SubSection']))
    story.append(Paragraph("Qu'il est appréciable de voir une cliente enjouée de partager son expérience avec notre enseigne…", styles['Accroche']))
    story.append(Paragraph("C'est l'occasion de permettre à de nouveaux clients de vous découvrir par des clients satisfaits!", styles['Body']))
    
    # FORMATIONS
    story.append(Paragraph("◆ Formations", styles['SubSection']))
    story.append(Paragraph("Mes employés seront continuellement formés à produire mieux pour produire plus.", styles['Accroche']))
    story.append(Paragraph("""
    Des formations en constante évolution, riches et complètes. Restez connecté aux dernières évolutions techniques !
    """, styles['Body']))
    story.append(Paragraph("« Revaloriser son savoir-faire c'est revaloriser votre business. »", styles['Quote']))
    
    # BUSINESS NEWS
    story.append(Paragraph("◆ Business News", styles['SubSection']))
    story.append(Paragraph("Qui investit dans quoi actuellement ?", styles['Accroche']))
    story.append(Paragraph("Ne vous laissez plus jamais dépasser par la concurrence et participez activement au marché !", styles['Body']))
    
    # PAGE PUB SPONTANÉE
    story.append(Paragraph("◆ Page Pub Spontanée", styles['SubSection']))
    spontanee_options = [
        "Proposer un nouveau teaser accessible aux investisseurs ?",
        "Envoyer une invitation personnelle à 200 clients ?",
        "Cibler des nouveaux clients dépensiers aujourd'hui ?",
        "Découvrir un influenceur qui revalorise votre image ?",
    ]
    for o in spontanee_options:
        story.append(Paragraph(f"  → {o}", styles['Feature']))
    story.append(Paragraph("« Profitez de votre page pub spontanée pour explorer de nouvelles opportunités commerciales ! »", styles['Quote']))
    
    # MESSAGERIE & CONTACTS
    story.append(Paragraph("◆ Messagerie & Contacts", styles['SubSection']))
    story.append(Paragraph("""
    Communiquez en tout temps avec vos équipes, partenaires, fournisseurs ou clients spéciaux.
    Votre registre de contacts professionnels réunis en un click !
    """, styles['Body']))
    
    # MES OFFRES D'EMPLOIS
    story.append(Paragraph("◆ Mes Offres d'Emplois", styles['SubSection']))
    story.append(Paragraph("""
    Proposer un emploi instantanément ou sur la durée, contre du cash-back ou rémunération.
    Court terme, long terme ou instantané. Stage ou apprentissage, découvrez nos meilleurs profils !
    """, styles['Body']))
    
    add_stats_footer(story,
        "Veille concurrentielle externe: 500-2'000 CHF/mois | Formation professionnelle: 200-1'000 CHF/jour | "
        "Newsletter B2B: 100-500 CHF/mois | ROI formation: +15% productivité | ROI veille: +20% réactivité", styles)
    
    story.append(PageBreak())
    
    # =====================================================
    # PAGE 13: MARKETING & VISIBILITÉ
    # =====================================================
    story.append(Paragraph("Marketing & Visibilité", styles['SectionTitle']))
    
    # EXPOSITION
    story.append(Paragraph("◆ Une Exposition sur Titelli", styles['SubSection']))
    story.append(Paragraph("""
    Être présent de manière régulière et forte aux yeux des clients et se voir recommander constamment 
    vous offre la possibilité de laisser venir à vous un nouveau public. Se rendre accessible a un impact 
    direct sur son économie mais aussi sur son image.
    """, styles['Body']))
    story.append(Paragraph("« Être exposé sur son propre site uniquement limite l'accès à ceux qui vous connaissent déjà, ouvrez-vous à un nouveau marché. »", styles['Quote']))
    
    # SPÉCIALISTE MARKETING
    story.append(Paragraph("◆ Un Spécialiste Marketing", styles['SubSection']))
    story.append(Paragraph("""
    Reprend en main votre communication. Révision ou création de votre image et site web vitrine, 
    incluant campagne marketing réseaux sociaux. Une équipe conçoit pour vous une "short vidéo" publicitaire.
    """, styles['Body']))
    story.append(Paragraph("« Nous prenons soin de votre image. »", styles['Quote']))
    
    # RÉFÉRENCEMENT
    story.append(Paragraph("◆ Le Référencement Préférentiel", styles['SubSection']))
    story.append(Paragraph("""
    Renforce votre présence sur le marché. Nos suggestions d'experts et par algorithmes vous font 
    apparaître aux bons endroits mais avant tout au bon moment.
    """, styles['Body']))
    
    # OFFRES ILLIMITÉES
    story.append(Paragraph("◆ La Publication d'Offres Illimitées", styles['SubSection']))
    story.append(Paragraph("""
    Proposez des gestes commerciaux qui fidélisent votre clientèle et attirent de nouveaux clients. 
    Un moyen solide de rester favoris dans les tendances actuelles.
    """, styles['Body']))
    story.append(Paragraph("« Ne jetez plus, ne renvoyez plus, publiez tout simplement une offre. »", styles['Quote']))
    
    # CERTIFIÉ & LABELLISÉ
    story.append(Paragraph("◆ La Mention 'Certifié' / 'Labellisé'", styles['SubSection']))
    story.append(Paragraph("""
    Permet de revaloriser un savoir-faire spécifique et de reconnaître des produits de haut-standing. 
    Remplissez nos conditions de labellisation et démarquez-vous de vos concurrents.
    """, styles['Body']))
    
    # LIVRAISON
    story.append(Paragraph("◆ Livraison Standard ou 24/24", styles['SubSection']))
    story.append(Paragraph("Proposez votre savoir-faire ou produit en service à domicile. N'attendez plus, de nouveaux clients vous ouvrent leurs portes.", styles['Accroche']))
    story.append(Paragraph("""
    Offrez la possibilité à vos clients de se sentir privilégiés et de solliciter vos prestations en tout temps.
    Livraison poste conventionnelle ou instantanée par notre système partenaire en 1-2 heures.
    """, styles['Body']))
    
    # DONATIONS
    story.append(Paragraph("◆ Donations", styles['SubSection']))
    story.append(Paragraph("Ne manquez pas l'opportunité de faire valoir votre image dans des événements hors du commun pour des valeurs qui vous ressemblent.", styles['Body']))
    
    add_stats_footer(story,
        "Agence marketing: 2'000-10'000 CHF/mois | SEO local: 500-2'000 CHF/mois | "
        "Campagne réseaux sociaux: 500-3'000 CHF/mois | Titelli Guest: 250 CHF/mois tout inclus | Conversion promo: +40%", styles)
    
    story.append(PageBreak())
    
    # =====================================================
    # PAGE 14: CÔTÉ CLIENT
    # =====================================================
    story.append(Paragraph("PARTIE 5: CÔTÉ CLIENT", styles['MainTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    
    story.append(Paragraph("Les avantages qui s'offrent gratuitement avec votre compte Titelli:", styles['Accroche']))
    
    # CASH-BACK CLIENT
    story.append(Paragraph("◆ Cash-Back Client", styles['SubSection']))
    story.append(Paragraph("Si la concurrence en a un, j'en veux un aussi !", styles['Accroche']))
    story.append(Paragraph("""
    Le Système de Cash-Back permet aux utilisateurs de bénéficier d'un retour sur leur achat s'élevant à 10% 
    du montant total facturé. Accessible au client chaque début de mois suivant. Utilisable sur l'ensemble 
    de la plateforme et interchangeable avec tout utilisateur.
    """, styles['Body']))
    
    cashback_table = [
        ['FORFAIT', 'TAUX', 'EXEMPLE 100 CHF'],
        ['Standard', '10%', '10 CHF crédités'],
        ['Guest', '12%', '12 CHF crédités'],
        ['Premium', '15%', '15 CHF crédités'],
        ['Premium MVP', '20%', '20 CHF crédités'],
    ]
    cb_table = Table(cashback_table, colWidths=[4.5*cm, 3.5*cm, 5.5*cm])
    cb_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GOLD),
        ('TEXTCOLOR', (0, 0), (-1, 0), DARK),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, BLUE),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(cb_table)
    
    # FICHES EXIGENCES
    story.append(Paragraph("◆ Fiches d'Exigences Clients", styles['SubSection']))
    story.append(Paragraph("Ne prenez plus le risque de laisser repartir un client mécontent !", styles['Accroche']))
    story.append(Paragraph("""
    Les fiches regroupent leurs attentes et vous permettent de proposer une expérience client inoubliable 
    grâce à un service personnalisé hors du commun !
    """, styles['Body']))
    
    # LIFESTYLE PASS
    story.append(Paragraph("◆ Lifestyle Pass", styles['SubSection']))
    story.append(Paragraph("""
    Le lifestyle pass donne accès au client à un nouveau mode de vie. Ce mode de vie permet de profiter 
    des meilleurs services prestataires de leurs régions choisies !
    """, styles['Body']))
    
    # HEALTHY LIFESTYLE PASS
    story.append(Paragraph("◆ Healthy Lifestyle Pass", styles['SubSection']))
    story.append(Paragraph("""
    Les prestataires qui répondent aux exigences spécifiques de santé. Ils respectent les clients de par 
    la qualité et l'étude approfondie de leur métier. Des services et produits qui prennent véritablement soin.
    """, styles['Body']))
    
    story.append(Paragraph(
        "« CE QUE VOUS VOULEZ, OÙ VOUS LE VOULEZ, QUAND VOUS LE VOULEZ ET COMME VOUS LE VOULEZ ! »",
        styles['Quote']
    ))
    
    add_stats_footer(story,
        "Programme fidélité commerce: 1-3% | Apps concurrentes: 0-5% | Titelli: 10-20% | "
        "Rétention avec cash-back: +45% | Fréquence achat fidèles: +35% | Panier moyen: +22%", styles)
    
    story.append(PageBreak())
    
    # =====================================================
    # PAGE 15: SERVICES CLIENT SUITE
    # =====================================================
    story.append(Paragraph("Services & Expérience Client", styles['SectionTitle']))
    
    # LIQUIDEZ VOTRE STOCK
    story.append(Paragraph("◆ Liquidez Votre Stock", styles['SubSection']))
    story.append(Paragraph("""
    Laissez Titelli livrer votre service ou produit quotidiennement dans le cadre de clients réguliers 
    comme des entreprises. Proposez votre service dans le cadre du lifestyle pass ou healthy lifestyle pass !
    """, styles['Body']))
    
    # ACCUEIL
    story.append(Paragraph("◆ Accueil Titelli", styles['SubSection']))
    story.append(Paragraph("""
    Notre accueil permet de suggérer chaque jour, à tous les clients Titelli, une vidéo qui promeut 
    un prestataire ou des suggestions d'offres qui défilent. Faites partie de nos suggestions d'accueil favoris !
    """, styles['Body']))
    
    # TENDANCES
    story.append(Paragraph("◆ Tendances Actuelles", styles['SubSection']))
    story.append(Paragraph("""
    Nos tendances actuelles viennent guider nos clients sur les meilleures suggestions du moment ! 
    Les Tendances regroupent nos meilleures opportunités parmi nos prestataires labellisés les plus expérimentés !
    """, styles['Body']))
    
    # PUB
    story.append(Paragraph("◆ Pub Titelli", styles['SubSection']))
    story.append(Paragraph("""
    Titelli accompagne son client tout au long de sa journée de consommation, devenez notre recommandation préférée !
    Ne manquez aucune opportunité de vendre et profitez chaque jour de votre page publicité pour mieux cibler vos clients !
    """, styles['Body']))
    
    # GUESTS DU MOMENT
    story.append(Paragraph("◆ Guests du Moment", styles['SubSection']))
    story.append(Paragraph("""
    Tous les prestataires certifiés profitant de leur page publicité ou de nos prestations, se voient 
    suggérer continuellement aux clients dans les Guests du moment.
    """, styles['Body']))
    
    # OFFRES DU MOMENT
    story.append(Paragraph("◆ Offres du Moment", styles['SubSection']))
    story.append(Paragraph("""
    Tous les prestataires non-certifiés ou non-labellisés, proposant des offres, se voient référencer 
    dans la rubrique « offre du moment ». Soyez répertorié et faites explorer vos meilleures prestations !
    """, styles['Body']))
    
    # À PROPOS
    story.append(Paragraph("◆ À Propos", styles['SubSection']))
    story.append(Paragraph("""
    Vidéos promo client lifestyle avant/après Titelli. Exemples: Hakim et son chauffeur, Une sortie en famille, 
    Grand-mère et son quotidien, Femme d'affaire un jour, Business is business, Soirée entre copines, etc.
    """, styles['Body']))
    story.append(Paragraph("""
    Faites-vous livrer une tenue ou un styliste en instantané ! Recevez un coiffeur ou un soin à domicile ! 
    Envoyez le chauffeur récupérer vos courses ! Recevez un professionnel de santé ou expert comptable à domicile !
    """, styles['Body']))
    
    add_stats_footer(story,
        "Utilisateurs apps services locaux Suisse: 3.2M | Satisfaction livraison: 72% (concurrence) vs 89% (Titelli) | "
        "Panier moyen livraison premium: +45% | Fréquence lifestyle pass: 4-8 services/mois", styles)
    
    story.append(PageBreak())
    
    # =====================================================
    # PAGE 16: SERVICES & PRODUITS / PARTENAIRES
    # =====================================================
    story.append(Paragraph("PARTIE 6: PARTENAIRES & PRESTATIONS", styles['MainTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    
    # SERVICES
    story.append(Paragraph("◆ Services", styles['SubSection']))
    story.append(Paragraph("""
    Tous les services sont répertoriés sur la plateforme et leur référencement dépend du contrat partenarial 
    effectué avec Titelli. Ces derniers bénéficient soit d'une reconnaissance professionnelle dite « certifiés » 
    ou « labellisés » par nos experts Titelli ou sont exposés de manière simple.
    """, styles['Body']))
    
    # PRODUITS
    story.append(Paragraph("◆ Produits", styles['SubSection']))
    story.append(Paragraph("""
    Tous les produits sont répertoriés sur la plateforme et leur référencement dépend du contrat partenarial 
    effectué avec Titelli. Reconnaissance professionnelle « certifiés » ou « labellisés » ou exposition simple.
    """, styles['Body']))
    
    # LABELLISÉS
    story.append(Paragraph("◆ Labellisés", styles['SubSection']))
    story.append(Paragraph("""
    Toutes nos prestations les plus prestigieuses sur Titelli répondent à des exigences particulières faites 
    par des experts attitrés du domaine d'activité correspondant. Nos prestataires les plus spécialisés se 
    voient reconnus par une labellisation distincte sur leur profil Titelli.
    """, styles['Body']))
    
    # CERTIFIÉS
    story.append(Paragraph("◆ Certifiés", styles['SubSection']))
    story.append(Paragraph("""
    Toutes nos prestations répondent à des exigences spécifiques. Nos meilleurs prestataires se voient certifiés 
    par des experts Titelli spécialisés et sont reconnus par des professionnels dans leur domaine d'activité 
    par une distinction sur leur profil Titelli.
    """, styles['Body']))
    
    # PARTENAIRES
    story.append(Paragraph("◆ Partenaires", styles['SubSection']))
    story.append(Paragraph("""
    <b>Notre but, Vos intérêts. Notre objectif, vos bénéfices.</b><br/>
    Connecter les meilleurs prestataires de la région et de permettre chaque jour à de nouveaux clients de les découvrir.
    Titelli répond aux attentes les plus exigeantes et subtiles des entreprises.
    """, styles['Body']))
    
    # SERVICE CLIENT
    story.append(Paragraph("◆ Service Client", styles['SubSection']))
    story.append(Paragraph("""
    Le service client Titelli est exclusivement dédié au traitement et maniement informatique des comptes 
    clients et prestataires. Le prestataire répond aux attentes et aux exigences des clients Titelli. 
    Par conséquent, ce dernier s'engage en l'accompagnement du client.
    """, styles['Body']))
    
    # PROFIL ENTREPRISE
    story.append(Paragraph("◆ Profil Entreprise", styles['SubSection']))
    story.append(Paragraph("Un book attrayant et attractif qui permet de faire découvrir au mieux votre enseigne et vos prestations.", styles['Accroche']))
    story.append(Paragraph("""
    Le profil entreprise permet de créer son image, de la revaloriser en tout temps et d'avoir un meilleur 
    contrôle en son long terme.
    """, styles['Body']))
    
    add_stats_footer(story,
        "Confiance label qualité: +67% vs non-labellisé | Conversion labellisé: 12% vs 4% standard | "
        "Prix accepté premium labellisé: +25% | Rétention certifié: 78% vs 52% non-certifié", styles)
    
    story.append(PageBreak())
    
    # =====================================================
    # PAGE 17: COMMISSIONS & TRANSACTIONS
    # =====================================================
    story.append(Paragraph("Commissions & Transactions", styles['SectionTitle']))
    
    commission_data = [
        ['TYPE DE FRAIS', 'TAUX/MONTANT', 'PAYÉ PAR', 'DESCRIPTION'],
        ['Commission entreprise', '5-15%', 'Entreprise', 'Sur chaque vente via Titelli'],
        ['Frais de service', '2-5 CHF', 'Client', 'Frais fixes par commande'],
        ['Frais de livraison', '3-10 CHF', 'Client', 'Variable selon distance'],
        ['Frais de paiement', '1.5-3%', 'Partagé', 'Frais Stripe/paiement'],
    ]
    comm_table = Table(commission_data, colWidths=[3.8*cm, 2.8*cm, 2.3*cm, 4.6*cm])
    comm_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GOLD),
        ('TEXTCOLOR', (0, 0), (-1, 0), DARK),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, BLUE),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(comm_table)
    
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("◆ Comparaison avec le marché", styles['SubSection']))
    
    comparison = [
        ['PLATEFORME', 'COMMISSION', 'FRAIS CLIENT', 'ABONNEMENT'],
        ['Uber Eats', '25-35%', '5-10 CHF', '0 CHF'],
        ['Deliveroo', '20-30%', '4-8 CHF', '0 CHF'],
        ['Just Eat', '15-25%', '3-6 CHF', '0 CHF'],
        ['TheFork', '2-4€/couvert', '0 CHF', '0 CHF'],
        ['TITELLI', '5-15%', '2-5 CHF', '200-1\'000 CHF'],
    ]
    comp_table = Table(comparison, colWidths=[3.5*cm, 3*cm, 3*cm, 4*cm])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, GOLD),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), LIGHT_GOLD),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(comp_table)
    
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("""
    <b>Avantage Titelli:</b> Commissions nettement inférieures à la concurrence (5-15% vs 25-35%), 
    permettant aux entreprises de préserver leurs marges tout en bénéficiant de services complets inclus.
    """, styles['Body']))
    
    add_stats_footer(story,
        "Restaurant CA mensuel via apps: 15'000 CHF | Commission Uber Eats (30%): 4'500 CHF | "
        "Commission Titelli (10%): 1'500 CHF + abo 250 CHF = 1'750 CHF | Économie annuelle: 33'000 CHF + services ~10'000 CHF", styles)
    
    story.append(PageBreak())
    
    # =====================================================
    # PAGE 18: CODE PROMO BIENVENUE
    # =====================================================
    story.append(Paragraph("Code Promo Bienvenue", styles['SectionTitle']))
    
    add_image(story, f"{SCREENSHOTS_DIR}/welcome_popup.jpeg",
              "Popup de bienvenue avec code promo BIENVENUE100", styles, width=12*cm, max_height=7*cm)
    
    story.append(Paragraph("◆ Stratégie d'acquisition client", styles['SubSection']))
    story.append(Paragraph("""
    Le code <b>BIENVENUE100</b> offre 100 CHF de crédit publicitaire aux nouvelles entreprises:
    """, styles['Body']))
    
    acquisition = [
        "Réduire la barrière à l'entrée pour les nouvelles entreprises",
        "Permettre de tester les services de publicité IA sans risque",
        "Créer un premier contact positif avec la plateforme",
        "Générer des données d'usage pour améliorer le ciblage",
        "Augmenter le taux de conversion en abonnement payant",
    ]
    for a in acquisition:
        story.append(Paragraph(f"  ✓ {a}", styles['Feature']))
    
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("◆ Coût d'acquisition client (CAC):", styles['SubSection']))
    
    cac_data = [
        ['INDICATEUR', 'VALEUR'],
        ['Valeur crédit offert', '100 CHF'],
        ['Coût réel pour Titelli', '~10-15 CHF (production IA)'],
        ['Taux conversion en abonné', '~15-25% estimé'],
        ['CAC effectif', '~40-70 CHF par client converti'],
        ['LTV moyenne abonné', '3\'000-6\'000 CHF'],
        ['Ratio LTV/CAC', '50-150x (excellent)'],
    ]
    cac_table = Table(cac_data, colWidths=[5.5*cm, 8*cm])
    cac_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GOLD),
        ('TEXTCOLOR', (0, 0), (-1, 0), DARK),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, BLUE),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(cac_table)
    
    add_stats_footer(story,
        "CAC moyen B2B SaaS: 200-1'000 CHF | CAC marketplace: 50-150 CHF | Titelli: 40-70 CHF | "
        "Ratio LTV/CAC sain: >3x (Titelli: 50-150x) | Taux conversion essai gratuit industrie: 10-15% (Titelli: 15-25%)", styles)
    
    story.append(PageBreak())
    
    # =====================================================
    # PAGE 19: PROJECTIONS FINANCIÈRES
    # =====================================================
    story.append(Paragraph("PARTIE 7: PROJECTIONS FINANCIÈRES", styles['MainTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    
    story.append(Paragraph("Projections de revenus (objectif 500 entreprises)", styles['SubSection']))
    
    projections = [
        ['SOURCE DE REVENU', 'MARGE', 'MENSUEL', 'ANNUEL'],
        ['Abonnements B2B', '90%', '125\'000 CHF', '1.5M CHF'],
        ['Publicité IA Média', '92%', '25\'000 CHF', '300K CHF'],
        ['Publicité IA Vidéo', '95%', '40\'000 CHF', '480K CHF'],
        ['Commissions transactions', '100%', '15\'000 CHF', '180K CHF'],
        ['Options à la carte', '88%', '20\'000 CHF', '240K CHF'],
        ['TOTAL', '~91%', '225\'000 CHF', '2.7M CHF'],
    ]
    proj_table = Table(projections, colWidths=[5*cm, 2.5*cm, 3.5*cm, 3.5*cm])
    proj_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, GOLD),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), LIGHT_GOLD),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(proj_table)
    
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("◆ Comparaison avec les géants du secteur", styles['SubSection']))
    
    giants = [
        ['ENTREPRISE', 'MARGE BRUTE', 'SOURCE PRINCIPALE', 'CA/EMPLOYÉ'],
        ['Instagram (Meta)', '~80%', 'Publicité ciblée', '1.5M USD'],
        ['Uber Eats', '~30%', 'Commissions + livraison', '350K USD'],
        ['Amazon Marketplace', '~25%', 'Commissions + FBA', '450K USD'],
        ['Deliveroo', '~35%', 'Commissions', '180K GBP'],
        ['TITELLI (projection)', '~91%', 'Abonnements + IA', '~500K CHF'],
    ]
    giants_table = Table(giants, colWidths=[4*cm, 2.5*cm, 4*cm, 3*cm])
    giants_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GOLD),
        ('TEXTCOLOR', (0, 0), (-1, 0), DARK),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, BLUE),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), LIGHT_GOLD),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(giants_table)
    
    add_stats_footer(story,
        "Valorisation SaaS B2B: 8-15x ARR | Titelli ARR potentiel: 2.7M CHF → Valorisation: 22-40M CHF | "
        "Croissance marché services locaux digitaux: +18%/an | Part marché Suisse romande visée: 5% à 3 ans, 15% à 5 ans", styles)
    
    story.append(PageBreak())
    
    # =====================================================
    # PAGE 20: CONCLUSION
    # =====================================================
    story.append(Paragraph("CONCLUSION", styles['MainTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("""
    Le modèle économique de Titelli combine les meilleures pratiques des géants du digital avec une approche 
    locale et personnalisée. Les marges élevées (~91%) sont rendues possibles par l'utilisation intensive 
    de l'IA pour la création de contenu publicitaire, réduisant drastiquement les coûts de production tout 
    en offrant une valeur ajoutée significative aux entreprises partenaires.
    """, styles['Body']))
    
    story.append(Paragraph(
        "« Notre objectif ? Connecter nos clients aux meilleurs prestataires sur Titelli, faites-en parti ! »",
        styles['Quote']
    ))
    
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("◆ Résumé des avantages clés:", styles['SubSection']))
    
    summary = [
        "✓ Commissions 2-3x inférieures à la concurrence (5-15% vs 25-35%)",
        "✓ Services marketing IA inclus (valeur ~10'000 CHF/an)",
        "✓ Cash-back jusqu'à 20% pour fidéliser vos clients",
        "✓ Cash-back VIP entreprise jusqu'à 99%",
        "✓ Accompagnement expert et formations continues",
        "✓ Visibilité garantie auprès de nouveaux clients",
        "✓ Gestion complète de votre activité en une plateforme",
        "✓ Optimisation fiscale et accompagnement juridique",
    ]
    for s in summary:
        story.append(Paragraph(s, styles['Feature']))
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "« Connectez-vous véritablement à vos clients. »",
        styles['Slogan']
    ))
    
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=3, color=GOLD))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("© 2026 Titelli SA - Tous droits réservés", styles['Footer']))
    story.append(Paragraph("www.titelli.com | contact@titelli.com | +41 21 XXX XX XX", styles['Footer']))
    story.append(Paragraph("Lausanne, Suisse", styles['Footer']))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Tous vos conditions contractuelles complémentaires sont accessibles dans les mentions légales et conditions générales de vente.",
        styles['Footer']
    ))
    
    # Build
    doc.build(story)
    print(f"✅ Brochure V3 générée: {OUTPUT_PATH}")
    return OUTPUT_PATH

if __name__ == "__main__":
    generate_brochure_v3()
