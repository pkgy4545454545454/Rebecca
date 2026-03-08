#!/usr/bin/env python3
"""
Brochure Monétisation Titelli V4
Format identique au PDF de référence fourni par l'utilisateur
Structure: 4 pages, mise en page deux colonnes, design professionnel
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, HRFlowable, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from PIL import Image as PILImage
import os
from datetime import datetime

OUTPUT_PATH = "/app/backend/uploads/TITELLI_BROCHURE_MONETISATION_V4.pdf"
SCREENSHOTS_DIR = "/app/brochure_screenshots"

BLUE_DARK = colors.HexColor("#1a365d")
BLUE_MEDIUM = colors.HexColor("#2c5282")
BLUE_LIGHT = colors.HexColor("#4299e1")
BLUE_PALE = colors.HexColor("#ebf8ff")
GOLD = colors.HexColor("#d69e2e")
GOLD_DARK = colors.HexColor("#b7791f")
GOLD_LIGHT = colors.HexColor("#faf089")
BLACK = colors.HexColor("#1a202c")
GREY_DARK = colors.HexColor("#4a5568")
GREY_MEDIUM = colors.HexColor("#718096")
GREY_LIGHT = colors.HexColor("#e2e8f0")
WHITE = colors.white

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 1.5*cm

def create_styles():
    """Créer les styles selon le PDF de référence"""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='MainTitle',
        fontSize=24,
        textColor=BLUE_DARK,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=10,
        leading=28
    ))
    
    styles.add(ParagraphStyle(
        name='Slogan',
        fontSize=14,
        textColor=BLUE_MEDIUM,
        alignment=TA_CENTER,
        fontName='Helvetica-BoldOblique',
        spaceAfter=8,
        spaceBefore=8,
        leading=18
    ))
    
    styles.add(ParagraphStyle(
        name='SectionTitle',
        fontSize=16,
        textColor=BLUE_DARK,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        spaceAfter=8,
        spaceBefore=12,
        leading=20
    ))
    
    styles.add(ParagraphStyle(
        name='SubTitle',
        fontSize=12,
        textColor=GOLD_DARK,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        spaceAfter=4,
        spaceBefore=8,
        leading=14
    ))
    
    styles.add(ParagraphStyle(
        name='Body',
        fontSize=9,
        textColor=BLACK,
        alignment=TA_JUSTIFY,
        fontName='Helvetica',
        spaceAfter=6,
        leading=12
    ))
    
    styles.add(ParagraphStyle(
        name='BodySmall',
        fontSize=8,
        textColor=GREY_DARK,
        alignment=TA_JUSTIFY,
        fontName='Helvetica',
        spaceAfter=4,
        leading=10
    ))
    
    styles.add(ParagraphStyle(
        name='Quote',
        fontSize=10,
        textColor=BLUE_MEDIUM,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique',
        spaceAfter=8,
        spaceBefore=6,
        leading=13
    ))
    
    styles.add(ParagraphStyle(
        name='Price',
        fontSize=14,
        textColor=GOLD_DARK,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=4,
        leading=16
    ))
    
    styles.add(ParagraphStyle(
        name='PriceOld',
        fontSize=10,
        textColor=GREY_MEDIUM,
        alignment=TA_CENTER,
        fontName='Helvetica',
        spaceAfter=2,
        leading=12
    ))
    
    styles.add(ParagraphStyle(
        name='Feature',
        fontSize=9,
        textColor=BLACK,
        alignment=TA_LEFT,
        fontName='Helvetica',
        leftIndent=8,
        spaceAfter=2,
        leading=11
    ))
    
    styles.add(ParagraphStyle(
        name='Contact',
        fontSize=9,
        textColor=WHITE,
        alignment=TA_LEFT,
        fontName='Helvetica',
        spaceAfter=3,
        leading=12
    ))
    
    styles.add(ParagraphStyle(
        name='Footer',
        fontSize=7,
        textColor=GREY_MEDIUM,
        alignment=TA_CENTER,
        fontName='Helvetica',
        spaceAfter=2,
        leading=9
    ))
    
    styles.add(ParagraphStyle(
        name='Highlight',
        fontSize=10,
        textColor=BLUE_DARK,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        spaceAfter=4,
        leading=12
    ))
    
    return styles


def add_cover_image(story, styles):
    """Ajouter l'image de couverture si disponible"""
    image_path = f"{SCREENSHOTS_DIR}/homepage.jpeg"
    if os.path.exists(image_path):
        try:
            with PILImage.open(image_path) as img:
                orig_w, orig_h = img.size
            aspect = orig_h / orig_w
            img_w = PAGE_WIDTH - 2*MARGIN
            img_h = img_w * aspect
            if img_h > 8*cm:
                img_h = 8*cm
                img_w = img_h / aspect
            
            img = Image(image_path, width=img_w, height=img_h)
            story.append(img)
            story.append(Spacer(1, 0.5*cm))
        except Exception as e:
            print(f"Erreur image: {e}")


def create_page1(story, styles):
    """PAGE 1: Couverture - Identique au format de référence"""
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph(
        "Découvrez le plein potentiel de votre commerce et dévoilez-en sa meilleure version.",
        styles['Slogan']
    ))
    
    story.append(Paragraph(
        "Notre objectif? Connecter nos clients aux meilleurs prestataires sur Titelli, faites-en partie!",
        styles['Body']
    ))
    
    story.append(Paragraph(
        "<b>Tous les prestataires préférés de votre région se trouvent sur Titelli.</b>",
        styles['Body']
    ))
    
    story.append(Spacer(1, 0.3*cm))
    
    add_cover_image(story, styles)
    
    intro_text = """
    Connaissez-vous tous les clients potentiels de votre secteur d'activité? Ne manquez plus aucune occasion de vendre avec Titelli.
    Connectez-vous et permettez chaque jour à de nouveaux clients de vous découvrir sur Titelli.
    """
    story.append(Paragraph(intro_text, styles['Body']))
    
    story.append(Spacer(1, 0.5*cm))
    
    title_table = Table([
        [Paragraph("<b>TITELLI</b>", ParagraphStyle('BigTitle', fontSize=28, textColor=GOLD_DARK, alignment=TA_CENTER, fontName='Helvetica-Bold'))],
        [Paragraph("Business Application Mobile", ParagraphStyle('SubBig', fontSize=14, textColor=BLUE_DARK, alignment=TA_CENTER, fontName='Helvetica-Bold'))],
        [Paragraph('"Connectez-vous véritablement à vos clients"', styles['Quote'])]
    ], colWidths=[PAGE_WIDTH - 2*MARGIN])
    title_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(title_table)
    
    story.append(Spacer(1, 0.5*cm))
    
    contact_data = [
        [Paragraph("<b>Contactez-nous</b>", ParagraphStyle('ContactTitle', fontSize=12, textColor=WHITE, fontName='Helvetica-Bold')), ""],
        [Paragraph("info@titelli.com", styles['Contact']), Paragraph("Tous les prestataires préférés de votre région se trouvent sur Titelli.", ParagraphStyle('White', fontSize=9, textColor=WHITE, fontName='Helvetica'))],
        [Paragraph("+41 79 895 03 13", styles['Contact']), Paragraph("Ne cherchez plus vos clients, laissez-les vous trouver.", ParagraphStyle('White', fontSize=9, textColor=WHITE, fontName='Helvetica'))],
        [Paragraph("Port-Franc 22, 1003 Lausanne", styles['Contact']), Paragraph("Ne manquez plus aucune occasion de vendre.", ParagraphStyle('White', fontSize=9, textColor=WHITE, fontName='Helvetica'))],
        [Paragraph("www.Titelli.com", styles['Contact']), Paragraph("Nous sommes là pour vous permettre d'oser la meilleure version de votre business.", ParagraphStyle('White', fontSize=9, textColor=WHITE, fontName='Helvetica'))],
    ]
    
    contact_table = Table(contact_data, colWidths=[6*cm, 10.5*cm])
    contact_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BLUE_DARK),
        ('TEXTCOLOR', (0, 0), (-1, -1), WHITE),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('SPAN', (0, 0), (1, 0)),
    ]))
    story.append(contact_table)
    
    story.append(PageBreak())


def create_page2(story, styles):
    """PAGE 2: Notre but, Vos intérêts + Notre objectif, Vos bénéfices"""
    
    story.append(Paragraph("Notre but, Vos intérêts.", styles['SectionTitle']))
    story.append(Paragraph(
        "Nous sommes là pour accompagner nos clients tout au long de leur journée de consommation. Devenez notre recommandation préférée.",
        styles['Body']
    ))
    
    vision_data = [
        [Paragraph("<b>Notre Vision</b>", styles['SubTitle']), 
         Paragraph("<b>Notre Mission</b>", styles['SubTitle'])],
        [Paragraph("Rendre le client toujours plus proche de ses prestataires préférés.", styles['Body']),
         Paragraph("Valoriser le savoir-faire et les produits de nos prestataires régionaux.", styles['Body'])]
    ]
    vision_table = Table(vision_data, colWidths=[8.25*cm, 8.25*cm])
    vision_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(vision_table)
    
    story.append(Spacer(1, 0.3*cm))
    
    pillar_style_title = ParagraphStyle('PillarTitle', fontSize=11, textColor=WHITE, fontName='Helvetica-Bold', alignment=TA_CENTER)
    pillar_style_body = ParagraphStyle('PillarBody', fontSize=8, textColor=BLACK, fontName='Helvetica', alignment=TA_JUSTIFY, leading=10)
    
    pillars_row1 = [
        [Paragraph("Promotion", pillar_style_title)],
        [Paragraph("Proposer une offre reste le meilleur moyen d'attirer de nouveaux clients afin de faire découvrir son produit ou son savoir-faire.", pillar_style_body)]
    ]
    
    pillars_row2 = [
        [Paragraph("Visibilité", pillar_style_title)],
        [Paragraph("Rendre accessible son service/produit au monde. Faites valoir votre savoir-faire et vos produits à un public inattendu.", pillar_style_body)]
    ]
    
    pillar1 = Table(pillars_row1, colWidths=[8*cm])
    pillar1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), BLUE_MEDIUM),
        ('BACKGROUND', (0, 1), (0, 1), BLUE_PALE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    pillar2 = Table(pillars_row2, colWidths=[8*cm])
    pillar2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), BLUE_MEDIUM),
        ('BACKGROUND', (0, 1), (0, 1), BLUE_PALE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    pillars_table1 = Table([[pillar1, pillar2]], colWidths=[8.25*cm, 8.25*cm])
    pillars_table1.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(pillars_table1)
    
    story.append(Spacer(1, 0.4*cm))
    
    story.append(Paragraph("Notre objectif, vos bénéfices.", styles['SectionTitle']))
    story.append(Paragraph(
        "Connecter les meilleurs prestataires de la région et de permettre chaque jour à de nouveaux clients de les découvrir.",
        styles['Body']
    ))
    
    story.append(Paragraph(
        "Titelli répond aux attentes les plus exigeantes et subtiles des entreprises. "
        "Titelli voit et croit en le véritable potentiel de votre entreprise ainsi qu'en votre plus-value. "
        "Nous avons réuni pour vous les meilleurs experts de divers domaines afin de vous permettre "
        "d'optimiser de la plus importante des manières votre entreprise.",
        styles['Body']
    ))
    
    story.append(Spacer(1, 0.3*cm))
    
    pillars_row3 = [
        [Paragraph("Cash-Back", pillar_style_title)],
        [Paragraph("Un moyen attrayant de rappeler au client qu'il dispose d'un certain montant à consommer auprès de ses prestataires préférés sur l'ensemble de la plateforme.", pillar_style_body)]
    ]
    
    pillars_row4 = [
        [Paragraph("Livraison", pillar_style_title)],
        [Paragraph("Proposez votre savoir-faire ou votre produit en service à domicile. N'attendez plus, de nouveaux clients vous ouvrent leurs portes.", pillar_style_body)]
    ]
    
    pillar3 = Table(pillars_row3, colWidths=[8*cm])
    pillar3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), GOLD_DARK),
        ('BACKGROUND', (0, 1), (0, 1), GOLD_LIGHT),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    pillar4 = Table(pillars_row4, colWidths=[8*cm])
    pillar4.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), GOLD_DARK),
        ('BACKGROUND', (0, 1), (0, 1), GOLD_LIGHT),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    pillars_table2 = Table([[pillar3, pillar4]], colWidths=[8.25*cm, 8.25*cm])
    pillars_table2.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(pillars_table2)
    
    story.append(PageBreak())


def create_page3(story, styles):
    """PAGE 3: Nos prestations + Nos services"""
    
    story.append(Paragraph("Nos prestations", styles['SectionTitle']))
    
    def create_offer_box(title, features, price_new, price_old=None, highlight=False):
        """Créer un bloc d'offre"""
        content = []
        
        title_style = ParagraphStyle('OfferTitle', fontSize=12, textColor=WHITE, fontName='Helvetica-Bold', alignment=TA_CENTER)
        content.append([Paragraph(title, title_style)])
        
        for f in features:
            content.append([Paragraph(f"• {f}", ParagraphStyle('OfferFeature', fontSize=8, textColor=BLACK, fontName='Helvetica', leftIndent=5, leading=10))])
        
        if price_old:
            content.append([Paragraph(f"<strike>CHF {price_old}</strike>", styles['PriceOld'])])
        content.append([Paragraph(f"<b>CHF {price_new}</b>", styles['Price'])])
        
        box = Table(content, colWidths=[7.8*cm])
        bg_color = GOLD_DARK if highlight else BLUE_MEDIUM
        box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), bg_color),
            ('BACKGROUND', (0, 1), (0, -1), GREY_LIGHT),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (0, -2), (0, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, GREY_MEDIUM),
        ]))
        return box
    
    standard_features = [
        "Exposition standard",
        "Une publication mensuelle",
        "Système de Cash-Back 10%",
        "Système de gestion des stocks"
    ]
    standard_box = create_offer_box("Standard", standard_features, "200.00", "400.00")
    
    guest_features = [
        "Référencement préférentiel",
        "Publication d'offres illimitées",
        "Système de Cash-Back 12%",
        "Système de gestion des stocks",
        "Badge Guest distinctif"
    ]
    guest_box = create_offer_box("Guest", guest_features, "250.00", "500.00")
    
    offers_row1 = Table([[standard_box, guest_box]], colWidths=[8.25*cm, 8.25*cm])
    offers_row1.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(offers_row1)
    
    story.append(Spacer(1, 0.3*cm))
    
    starter_features = [
        "Référencement préférentiel",
        "Publication d'offres illimitées",
        "Système de Cash-Back 15%",
        "Système de gestion des stocks",
        "Spécialiste marketing dédié"
    ]
    starter_box = create_offer_box("Optimisation Starter", starter_features, "2'900.00", highlight=True)
    
    elite_features = [
        "Référencement préférentiel",
        "Publication d'offres illimitées",
        "Système de Cash-Back 20%",
        "Système de gestion des stocks",
        "Campagne marketing complète",
        "Optimisation fiscale"
    ]
    elite_box = create_offer_box("Optimisation Elite", elite_features, "à partir de 4'900.00", highlight=True)
    
    offers_row2 = Table([[starter_box, elite_box]], colWidths=[8.25*cm, 8.25*cm])
    offers_row2.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(offers_row2)
    
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("*Toutes nos offres sont valables sur une durée d'une année.", styles['Footer']))
    
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("Nos services", styles['SectionTitle']))
    
    services_left = [
        ("Une exposition standard sur Titelli", 
         "Être présent de manière régulière et forte aux yeux des clients et de se voir recommander constamment vous offre la possibilité de laisser venir à vous un nouveau public. Se rendre accessible à de nouveaux clients a un impact direct sur son économie mais aussi sur son image."),
        ("Le référencement préférentiel",
         "permet de renforcer votre présence sur le marché. Nos suggestions d'experts et par algorithmes vous donneront la possibilité d'apparaître aux bons endroits mais avant tout au bon moment.")
    ]
    
    services_right = [
        ("La publication d'offres illimitées",
         "vous permet de proposer des gestes commerciaux, ce qui fidélise votre clientèle déjà existante en vous donnant l'opportunité d'attirer de nouveaux clients. Un moyen solide de rester favoris dans les tendances actuelles."),
        ("Un spécialiste marketing",
         "reprend en main votre communication. Une nouvelle exposition reste le meilleur moyen de renouveler et contrôler son image. Cela comprend la révision ou création de votre image ainsi que de votre site web vitrine.")
    ]
    
    left_content = []
    for title, desc in services_left:
        left_content.append(Paragraph(f"<b>{title}</b>", styles['SubTitle']))
        left_content.append(Paragraph(desc, styles['BodySmall']))
        left_content.append(Spacer(1, 0.2*cm))
    
    right_content = []
    for title, desc in services_right:
        right_content.append(Paragraph(f"<b>{title}</b>", styles['SubTitle']))
        right_content.append(Paragraph(desc, styles['BodySmall']))
        right_content.append(Spacer(1, 0.2*cm))
    
    services_table = Table([[left_content, right_content]], colWidths=[8.25*cm, 8.25*cm])
    services_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(services_table)
    
    story.append(PageBreak())


def create_page4(story, styles):
    """PAGE 4: Services suite + Avantages clients + Notes légales"""
    
    services_col1 = [
        ("Le système de gestion des stocks",
         "vous donne accès instantanément à toutes les informations nécessaires. Vous pouvez également suivre en temps réel les mouvements de vos stocks, recevoir des alertes en cas de fluctuations inattendues, et même générer des rapports détaillés pour une analyse plus approfondie de vos performances."),
        ("La mention \"Certifié\"",
         "permet de revaloriser un savoir-faire spécifique et de reconnaître des produits de haut-standing. Remplissez nos conditions de labellisation et démarquez-vous de vos concurrents."),
        ("Le système de Cash-Back",
         "permet aux utilisateurs de bénéficier d'un retour sur leur achat s'élevant à 10% du montant total facturé par le prestataire. Ce dernier est accessible au client à chaque début du mois suivant la facturation.")
    ]
    
    services_col2 = [
        ("Optimisation fiscale",
         "Un expert comptable et juridique se chargent d'une optimisation fiscale reflétant directement sur vos bénéfices. Économisez sur vos charges et maximisez vos revenus."),
        ("Le service Premium",
         'permet de renforcer votre accessibilité sur le marché ainsi que de répondre à une clientèle plus exigeante. "Ce que vous voulez, quand vous le voulez, où vous le voulez et comme vous le voulez."'),
        ("Livraison",
         "Proposez votre produit ou votre service à domicile moyennant un supplément. Faites livrer votre produit par la poste en temps conventionnel ou proposez-le instantanément par notre système de livraison partenaire en seulement une heure ou deux.")
    ]
    
    left_elements = []
    for title, desc in services_col1:
        left_elements.append(Paragraph(f"<b>{title}</b>", styles['SubTitle']))
        left_elements.append(Paragraph(desc, styles['BodySmall']))
        left_elements.append(Spacer(1, 0.15*cm))
    
    right_elements = []
    for title, desc in services_col2:
        right_elements.append(Paragraph(f"<b>{title}</b>", styles['SubTitle']))
        right_elements.append(Paragraph(desc, styles['BodySmall']))
        right_elements.append(Spacer(1, 0.15*cm))
    
    services_table = Table([[left_elements, right_elements]], colWidths=[8.25*cm, 8.25*cm])
    services_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(services_table)
    
    story.append(Spacer(1, 0.4*cm))
    
    story.append(Paragraph("Les avantages clients", styles['SectionTitle']))
    
    advantages_text = """
    Les utilisateurs ont accès à des offres promotionnelles toute l'année ainsi qu'à un cash-back sur chacun de leur achat.
    Ce dernier est utilisable et interchangeable sur l'ensemble de la plateforme.
    Le client a accès à un filtre de recherches de prestations plus précis, ce qui contribue à répondre plus attentivement à leurs attentes.
    """
    story.append(Paragraph(advantages_text, styles['Body']))
    
    story.append(Paragraph(
        "<b>Titelli est conçu à des fins d'utilité publique.</b>",
        styles['Highlight']
    ))
    
    story.append(Paragraph(
        "Le service premium répond à la clientèle la plus exigeante, en proposant un accès à un service de prestation vérifié et labellisé. "
        "Titelli valorise un accès à des prestations en tout temps et tout lieu.",
        styles['Body']
    ))
    
    story.append(Paragraph(
        "Le client a de plus accès à ses dépenses, ses lieux de fréquentations, accès à son profil mode de vie, feed-back, "
        "au répertoire de ses cartes de fidélité, bancaires, factures et preuves de paiements.",
        styles['Body']
    ))
    
    story.append(Paragraph(
        '"Connectez-vous et profitez-en aussi!"',
        styles['Quote']
    ))
    
    story.append(Spacer(1, 0.4*cm))
    
    legal_box_content = [
        [Paragraph("<b>Conditions et frais</b>", ParagraphStyle('LegalTitle', fontSize=10, textColor=WHITE, fontName='Helvetica-Bold', alignment=TA_CENTER))]
    ]
    
    legal_texts = [
        "Le système de cash-back autorise à prélever 10% du montant total facturé par le prestataire à chaque transaction afin de le reverser au client à chaque début du mois suivant la facturation.",
        "Le prestataire perçoit le revenu de ses prestations du mois effectif à chaque début du mois suivant.",
        "<b>Frais de gestion:</b> Titelli perçoit 10% de frais de gestion afin de répondre au mieux aux attentes et de vous rendre le service le plus efficace possible.",
        "<b>Frais de transaction:</b> chaque transaction engage des frais qui s'élèvent à 2,9%.",
        "<b>Service client et responsabilité:</b> Titelli se positionnant comme un intermédiaire sur le marché entre les clients et les revendeurs, Titelli décline alors toute responsabilité liée à d'éventuels litiges. Les commerçants garantissent un service et des produits de qualité.",
        "L'activation du compte peut être tenue sous réserve jusqu'à 2 mois dès lors de la création de ce dernier."
    ]
    
    for text in legal_texts:
        legal_box_content.append([Paragraph(text, styles['BodySmall'])])
    
    legal_table = Table(legal_box_content, colWidths=[PAGE_WIDTH - 2*MARGIN - 1*cm])
    legal_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), BLUE_DARK),
        ('BACKGROUND', (0, 1), (0, -1), GREY_LIGHT),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 1, BLUE_DARK),
    ]))
    story.append(legal_table)
    
    story.append(PageBreak())


def create_page5(story, styles):
    """PAGE 5: Glossaire publicitaire + Commission 45%"""
    
    story.append(Paragraph("Glossaire Publicitaire & Monétisation", styles['SectionTitle']))
    
    story.append(Paragraph(
        "Comprendre les termes publicitaires essentiels pour maximiser vos revenus sur Titelli.",
        styles['Body']
    ))
    
    story.append(Spacer(1, 0.3*cm))
    
    # Tableau glossaire CPM
    glossary_data = [
        ['TERME', 'SIGNIFICATION', 'EXPLICATION'],
        ['CPM', 'Coût Pour Mille', 'Prix payé pour 1\'000 affichages de votre publicité. Ex: CPM de 5 CHF = 5 CHF pour 1\'000 vues.'],
        ['CPC', 'Coût Par Clic', 'Prix payé uniquement quand un utilisateur clique sur votre publicité.'],
        ['CPA', 'Coût Par Action', 'Prix payé quand l\'utilisateur effectue une action (achat, inscription, etc.).'],
        ['CTR', 'Taux de Clic', 'Pourcentage de personnes qui cliquent après avoir vu la pub. (Clics/Impressions x 100)'],
        ['ROI', 'Retour sur Invest.', 'Mesure du bénéfice généré par rapport à l\'investissement publicitaire.'],
        ['Impression', 'Affichage', 'Chaque fois que votre publicité est affichée à un utilisateur.'],
        ['Reach', 'Portée', 'Nombre de personnes uniques ayant vu votre publicité.'],
    ]
    
    glossary_table = Table(glossary_data, colWidths=[2.5*cm, 3.2*cm, 10.8*cm])
    glossary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, GREY_MEDIUM),
        ('BACKGROUND', (0, 1), (-1, -1), WHITE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (2, 0), (2, -1), 6),
    ]))
    story.append(glossary_table)
    
    story.append(Spacer(1, 0.5*cm))
    
    # Box Commission 45%
    commission_title = ParagraphStyle('CommTitle', fontSize=11, textColor=WHITE, fontName='Helvetica-Bold', alignment=TA_CENTER)
    commission_body = ParagraphStyle('CommBody', fontSize=9, textColor=BLACK, fontName='Helvetica', alignment=TA_JUSTIFY, leading=12)
    
    commission_content = [
        [Paragraph("⚠️ COMMISSION PARTENARIAT & RÉMUNÉRATION VIDÉO", commission_title)],
        [Paragraph(
            "Si vous concluez un <b>partenariat sur Titelli</b> ou si vous percevez une <b>rémunération sur une vidéo "
            "diffusée sur la plateforme Titelli</b>, <b>Titelli prélève une commission de 45%</b> sur les revenus générés.",
            commission_body
        )],
        [Paragraph(
            "Cette commission couvre les services de mise en relation, la diffusion, le ciblage algorithmique, "
            "et l'infrastructure technique de la plateforme.",
            commission_body
        )],
        [Paragraph(
            "<b>Exemple:</b> Vous générez 1'000 CHF de revenus via un partenariat vidéo → "
            "Vous percevez <b>550 CHF</b>, Titelli retient <b>450 CHF</b>.",
            commission_body
        )],
    ]
    
    commission_table = Table(commission_content, colWidths=[PAGE_WIDTH - 2*MARGIN - 0.5*cm])
    commission_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), GOLD_DARK),
        ('BACKGROUND', (0, 1), (0, -1), GOLD_LIGHT),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 2, GOLD_DARK),
    ]))
    story.append(commission_table)
    
    story.append(Spacer(1, 0.5*cm))
    
    # Comparaison CPM marché
    story.append(Paragraph("Comparaison CPM du marché", styles['SubTitle']))
    
    cpm_comparison = [
        ['PLATEFORME', 'CPM MOYEN', 'COMMISSION'],
        ['Instagram Ads', '5-15 CHF', '~30%'],
        ['YouTube Ads', '8-20 CHF', '~45%'],
        ['TikTok Ads', '3-10 CHF', '~20-30%'],
        ['Facebook Ads', '4-12 CHF', '~30%'],
        ['TITELLI', '5-15 CHF', '45% (services complets inclus)'],
    ]
    
    cpm_table = Table(cpm_comparison, colWidths=[5.5*cm, 4*cm, 7*cm])
    cpm_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE_MEDIUM),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, GREY_MEDIUM),
        ('BACKGROUND', (0, 1), (-1, -2), WHITE),
        ('BACKGROUND', (0, -1), (-1, -1), GOLD_LIGHT),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(cpm_table)
    
    story.append(Spacer(1, 0.5*cm))
    
    # Publicité IA
    story.append(Paragraph("Publicité IA - Média & Vidéo", styles['SubTitle']))
    
    story.append(Paragraph(
        "Titelli propose des services de création publicitaire par Intelligence Artificielle:",
        styles['Body']
    ))
    
    ia_services = [
        "<b>Images IA:</b> Instagram Post (19.90 CHF), Story (14.90 CHF), Bannière Web (24.90 CHF), Flyer (29.90 CHF)",
        "<b>Vidéos IA:</b> TikTok Tendance (149.90 CHF), Story Animée (129.90 CHF), Instagram Reel (199.90 CHF), Pub Premium (249.90 CHF)",
        "<b>Sur Mesure:</b> Création personnalisée selon vos besoins spécifiques"
    ]
    
    for service in ia_services:
        story.append(Paragraph(f"• {service}", styles['Feature']))
    
    story.append(Spacer(1, 0.4*cm))
    
    story.append(Paragraph(
        '"Titelli accompagne son client tout au long de sa journée de consommation, devenez notre recommandation préférée!"',
        styles['Quote']
    ))
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        f"© {datetime.now().year} Titelli - Tous droits réservés | www.titelli.com | info@titelli.com",
        styles['Footer']
    ))


def generate_brochure_v4():
    """Générer la brochure V4"""
    
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        rightMargin=MARGIN,
        leftMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN
    )
    
    styles = create_styles()
    story = []
    
    create_page1(story, styles)
    create_page2(story, styles)
    create_page3(story, styles)
    create_page4(story, styles)
    create_page5(story, styles)
    
    doc.build(story)
    print(f"Brochure V4 générée: {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    generate_brochure_v4()
