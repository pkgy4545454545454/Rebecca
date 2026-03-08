#!/usr/bin/env python3
"""
Brochure Monétisation Titelli V4 COMPLÈTE
Design du PDF de référence + Contenu complet de la V3
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from PIL import Image as PILImage
import os
from datetime import datetime

OUTPUT_PATH = "/app/backend/uploads/TITELLI_BROCHURE_MONETISATION_V4.pdf"
SCREENSHOTS_DIR = "/app/brochure_screenshots"

# Couleurs du design de référence
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
MARGIN = 1.2*cm
COL_WIDTH = (PAGE_WIDTH - 2*MARGIN - 0.5*cm) / 2

def create_styles():
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='MainTitle', fontSize=22, textColor=GOLD_DARK, alignment=TA_CENTER,
        fontName='Helvetica-Bold', spaceAfter=12, spaceBefore=6, leading=26
    ))
    
    styles.add(ParagraphStyle(
        name='SectionTitle', fontSize=13, textColor=BLUE_DARK, alignment=TA_LEFT,
        fontName='Helvetica-Bold', spaceAfter=10, spaceBefore=14, leading=16
    ))
    
    styles.add(ParagraphStyle(
        name='SubSection', fontSize=10, textColor=GOLD_DARK, alignment=TA_LEFT,
        fontName='Helvetica-Bold', spaceAfter=6, spaceBefore=10, leading=12
    ))
    
    styles.add(ParagraphStyle(
        name='Body', fontSize=8, textColor=BLACK, alignment=TA_JUSTIFY,
        fontName='Helvetica', spaceAfter=6, spaceBefore=2, leading=11
    ))
    
    styles.add(ParagraphStyle(
        name='BodySmall', fontSize=7, textColor=GREY_DARK, alignment=TA_JUSTIFY,
        fontName='Helvetica', spaceAfter=5, spaceBefore=2, leading=10
    ))
    
    styles.add(ParagraphStyle(
        name='Slogan', fontSize=10, textColor=BLUE_MEDIUM, alignment=TA_CENTER,
        fontName='Helvetica-BoldOblique', spaceAfter=10, spaceBefore=6, leading=13
    ))
    
    styles.add(ParagraphStyle(
        name='Quote', fontSize=8, textColor=GOLD_DARK, alignment=TA_CENTER,
        fontName='Helvetica-Oblique', spaceAfter=8, spaceBefore=6, leading=11
    ))
    
    styles.add(ParagraphStyle(
        name='Feature', fontSize=7, textColor=BLACK, alignment=TA_LEFT,
        fontName='Helvetica', leftIndent=5, spaceAfter=4, spaceBefore=1, leading=10
    ))
    
    styles.add(ParagraphStyle(
        name='Accroche', fontSize=7, textColor=GREY_MEDIUM, alignment=TA_LEFT,
        fontName='Helvetica-Oblique', spaceAfter=5, spaceBefore=2, leading=10
    ))
    
    styles.add(ParagraphStyle(
        name='Stats', fontSize=6, textColor=BLUE_MEDIUM, alignment=TA_LEFT,
        fontName='Helvetica', leading=8
    ))
    
    styles.add(ParagraphStyle(
        name='Footer', fontSize=6, textColor=GREY_MEDIUM, alignment=TA_CENTER,
        fontName='Helvetica', spaceAfter=3, spaceBefore=3
    ))
    
    styles.add(ParagraphStyle(
        name='Contact', fontSize=8, textColor=WHITE, alignment=TA_LEFT,
        fontName='Helvetica', spaceAfter=3, leading=11
    ))
    
    return styles


def add_stats_footer(story, stats, styles):
    story.append(Spacer(1, 4*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BLUE_MEDIUM))
    story.append(Spacer(1, 1*mm))
    stats_table = Table([
        [Paragraph("<b>STATS:</b>", styles['Stats']), Paragraph(stats, styles['Stats'])]
    ], colWidths=[1.5*cm, 15*cm])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), BLUE_PALE),
        ('BACKGROUND', (1, 0), (1, 0), GREY_LIGHT),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(stats_table)


def add_image(story, path, caption, styles, width=13*cm, max_height=5*cm):
    if os.path.exists(path):
        try:
            with PILImage.open(path) as img:
                aspect = img.size[1] / img.size[0]
            img_h = min(width * aspect, max_height)
            img_w = img_h / aspect if img_h == max_height else width
            
            img = Image(path, width=img_w, height=img_h)
            img_table = Table([[img]], colWidths=[img_w + 4*mm])
            img_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, GOLD),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            story.append(img_table)
            story.append(Spacer(1, 1*mm))
            story.append(Paragraph(f"<i>{caption}</i>", styles['Footer']))
            story.append(Spacer(1, 4*mm))
        except Exception as e:
            print(f"Image error: {e}")


def generate_brochure():
    doc = SimpleDocTemplate(
        OUTPUT_PATH, pagesize=A4,
        rightMargin=MARGIN, leftMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN
    )
    
    styles = create_styles()
    story = []
    
    # ========== PAGE 1: COUVERTURE ==========
    story.append(Paragraph("Découvrez le plein potentiel de votre commerce et dévoilez-en sa meilleure version.", styles['Slogan']))
    story.append(Paragraph("Notre objectif? Connecter nos clients aux meilleurs prestataires sur Titelli, faites-en partie!", styles['Body']))
    
    add_image(story, f"{SCREENSHOTS_DIR}/homepage.jpeg", "Plateforme Titelli", styles, width=14*cm, max_height=6*cm)
    
    title_table = Table([
        [Paragraph("<b>TITELLI</b>", ParagraphStyle('T', fontSize=26, textColor=GOLD_DARK, alignment=TA_CENTER, fontName='Helvetica-Bold', leading=30))],
        [Paragraph("Guide Complet de Monétisation V4", ParagraphStyle('S', fontSize=12, textColor=BLUE_DARK, alignment=TA_CENTER, fontName='Helvetica-Bold', leading=16))],
        [Paragraph('"Connectez-vous véritablement à vos clients"', ParagraphStyle('SL', fontSize=10, textColor=BLUE_MEDIUM, alignment=TA_CENTER, fontName='Helvetica-BoldOblique', leading=14))]
    ], colWidths=[PAGE_WIDTH - 2*MARGIN])
    title_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(title_table)
    
    story.append(Spacer(1, 0.3*cm))
    
    # Messages clés
    messages = [
        "« Ne cherchez plus vos clients, laissez-les vous trouver ! »",
        "« Ne manquez plus aucune occasion de vendre. »",
        "« Connectez-vous véritablement à vos clients. »"
    ]
    msg_style = ParagraphStyle('MSG', fontSize=8, textColor=GOLD_DARK, alignment=TA_CENTER, fontName='Helvetica-Oblique', leading=12)
    msg_table = Table([[Paragraph(m, msg_style)] for m in messages], colWidths=[PAGE_WIDTH - 2*MARGIN])
    msg_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), GOLD_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1, GOLD),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(msg_table)
    
    story.append(Spacer(1, 0.3*cm))
    
    # Contact
    contact_data = [
        [Paragraph("<b>Contactez-nous</b>", ParagraphStyle('CT', fontSize=10, textColor=WHITE, fontName='Helvetica-Bold')), ""],
        [Paragraph("info@titelli.com | +41 79 895 03 13", styles['Contact']), 
         Paragraph("Port-Franc 22, 1003 Lausanne | www.Titelli.com", styles['Contact'])],
    ]
    contact_table = Table(contact_data, colWidths=[8*cm, 8.5*cm])
    contact_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BLUE_DARK),
        ('SPAN', (0, 0), (1, 0)),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(contact_table)
    
    add_stats_footer(story, "Marché services locaux Suisse: 2.3 Mrd CHF | Croissance: +18%/an | Taux adoption smartphone: 92%", styles)
    story.append(PageBreak())
    
    # ========== PAGE 2: VISION & PHILOSOPHIE ==========
    story.append(Paragraph("PARTIE 1: VISION & PHILOSOPHIE", styles['MainTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    
    story.append(Paragraph("Notre But, Vos Intérêts | Notre Objectif, Vos Bénéfices", styles['SectionTitle']))
    
    vision_data = [
        ["NOTRE VISION", "Rendre le client toujours plus proche de ses prestataires préférés."],
        ["NOTRE MISSION", "Valoriser le savoir-faire et les produits de nos prestataires régionaux."],
        ["NOTRE OBJECTIF", "Connecter nos clients aux meilleurs prestataires sur Titelli."],
    ]
    vision_table = Table(vision_data, colWidths=[3.5*cm, 13*cm])
    vision_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), BLUE_MEDIUM),
        ('TEXTCOLOR', (0, 0), (0, -1), WHITE),
        ('BACKGROUND', (1, 0), (1, -1), GREY_LIGHT),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, GOLD),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (1, 0), (1, -1), 8),
    ]))
    story.append(vision_table)
    
    story.append(Spacer(1, 0.4*cm))
    
    story.append(Paragraph(
        "Titelli voit et croit en le véritable potentiel de votre entreprise ainsi qu'en votre plus-value. "
        "Nous avons réuni pour vous les meilleurs experts de divers domaines afin de vous permettre "
        "d'optimiser de la plus importante des manières votre entreprise.", styles['Body']))
    
    story.append(Paragraph("« Découvrez le plein potentiel de votre commerce et dévoilez-en sa meilleure version. »", styles['Quote']))
    
    # 4 Piliers en grille 2x2
    pillar_title = ParagraphStyle('PT', fontSize=9, textColor=WHITE, fontName='Helvetica-Bold', alignment=TA_CENTER)
    pillar_body = ParagraphStyle('PB', fontSize=7, textColor=BLACK, fontName='Helvetica', alignment=TA_JUSTIFY, leading=9)
    
    def make_pillar(title, text, bg_title, bg_body):
        return Table([
            [Paragraph(title, pillar_title)],
            [Paragraph(text, pillar_body)]
        ], colWidths=[7.8*cm])
    
    pillar1 = make_pillar("Promotion", "Proposer une offre reste le meilleur moyen d'attirer de nouveaux clients afin de faire découvrir son produit ou son savoir-faire.", BLUE_MEDIUM, BLUE_PALE)
    pillar1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), BLUE_MEDIUM),
        ('BACKGROUND', (0, 1), (0, 1), BLUE_PALE),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    pillar2 = make_pillar("Visibilité", "Rendre accessible son service/produit au monde. Faites valoir votre savoir-faire et vos produits à un public inattendu.", BLUE_MEDIUM, BLUE_PALE)
    pillar2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), BLUE_MEDIUM),
        ('BACKGROUND', (0, 1), (0, 1), BLUE_PALE),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    pillar3 = make_pillar("Cash-Back", "Un moyen attrayant de rappeler au client qu'il dispose d'un certain montant à consommer auprès de ses prestataires préférés.", GOLD_DARK, GOLD_LIGHT)
    pillar3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), GOLD_DARK),
        ('BACKGROUND', (0, 1), (0, 1), GOLD_LIGHT),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    pillar4 = make_pillar("Livraison", "Proposez votre savoir-faire ou produit en service à domicile. N'attendez plus, de nouveaux clients vous ouvrent leurs portes.", GOLD_DARK, GOLD_LIGHT)
    pillar4.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), GOLD_DARK),
        ('BACKGROUND', (0, 1), (0, 1), GOLD_LIGHT),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    pillars = Table([[pillar1, pillar2], [pillar3, pillar4]], colWidths=[8.25*cm, 8.25*cm])
    pillars.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(pillars)
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("◆ Gestion Entreprise Complète", styles['SubSection']))
    story.append(Paragraph("N'avez-vous pas rêvé de prendre des vacances, lâcher vos comptes et dépenser sans compter !?", styles['Accroche']))
    story.append(Paragraph("Titelli s'occupe de réaliser votre rêve pendant qu'elle rentabilise votre business !", styles['Body']))
    story.append(Paragraph("« Oser Titelli, c'est Oser une nouvelle vie ! »", styles['Quote']))
    
    add_stats_footer(story, "PME suisses: 600'000 | Digitalisation PME: 45% vs 78% grandes | Potentiel: +25% CA | CAC: 40-70 CHF", styles)
    story.append(PageBreak())
    
    # ========== PAGE 3: FORFAITS DE BASE ==========
    story.append(Paragraph("PARTIE 2: FORFAITS ENTREPRISES", styles['MainTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    
    story.append(Paragraph("Forfaits de Base: STANDARD & GUEST", styles['SectionTitle']))
    
    add_image(story, f"{SCREENSHOTS_DIR}/subscriptions_basic.jpeg", "Interface Abonnements", styles, width=14*cm, max_height=5*cm)
    
    # STANDARD
    story.append(Paragraph("◆ Forfait STANDARD — 200 CHF/mois", styles['SubSection']))
    story.append(Paragraph("C'est apaisant de pouvoir économiser mon énergie, lorsque Titelli s'occupe de tout.", styles['Accroche']))
    
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
    std_table = Table(standard_table, colWidths=[3*cm, 6.5*cm, 3*cm])
    std_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE_MEDIUM),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, GOLD),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(std_table)
    
    story.append(Spacer(1, 0.5*cm))
    
    # GUEST
    story.append(Paragraph("◆ Forfait GUEST — 250 CHF/mois ⭐ POPULAIRE", styles['SubSection']))
    story.append(Paragraph("Tous les prestataires certifiés se voient suggérer continuellement aux clients.", styles['Accroche']))
    
    guest_extras = ["✓ Profil professionnel complet et book attrayant", "✓ Référencement préférentiel (apparition prioritaire)",
                   "✓ Publicités ILLIMITÉES", "✓ Statistiques avancées et indicateurs", "✓ Badge 'Guest' distinctif"]
    for e in guest_extras:
        story.append(Paragraph(e, styles['Feature']))
    
    add_stats_footer(story, "Amazon: 39€/mois + 15% | Uber Eats: 0€ + 30% | Titelli: 200 CHF + 5-15% → Économie: 40-60%", styles)
    story.append(PageBreak())
    
    # ========== PAGE 4: FORFAITS PREMIUM ==========
    story.append(Paragraph("Forfaits PREMIUM & PREMIUM MVP", styles['SectionTitle']))
    
    add_image(story, f"{SCREENSHOTS_DIR}/subscriptions_premium.jpeg", "Forfaits Premium", styles, width=14*cm, max_height=5*cm)
    
    # PREMIUM
    story.append(Paragraph("◆ Forfait PREMIUM — 500 CHF/mois", styles['SubSection']))
    story.append(Paragraph("Le service Premium permet de répondre à une clientèle plus exigeante.", styles['Accroche']))
    
    premium_features = [
        ("4 publicités/mois", "Plus de visibilité, plus d'opportunités"),
        ("Accès Investisseurs", "Proposez des parts sur bénéfice contre investissement"),
        ("Livraison 24/24", "Service à domicile permanent, clients privilégiés"),
        ("Gestion personnel", "Cahiers des charges, ordres instantanés, suivi performance"),
        ("Indicateurs perf.", "KPIs temps réel pour optimiser votre activité"),
    ]
    for title, desc in premium_features:
        story.append(Paragraph(f"• <b>{title}:</b> {desc}", styles['Feature']))
    
    story.append(Paragraph("« Ce que vous voulez, où vous le voulez, quand vous le voulez et comme vous le voulez ! »", styles['Quote']))
    
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
        story.append(Paragraph(f"• <b>{title}:</b> {desc}", styles['Feature']))
    
    add_stats_footer(story, "ROI Premium: +35% CA après 6 mois | Rétention: 94% | LTV MVP: 12'000 CHF/an", styles)
    story.append(PageBreak())
    
    # ========== PAGE 5: OPTIMISATION D'ENTREPRISE ==========
    story.append(Paragraph("Optimisation d'Entreprise (2K-50K)", styles['SectionTitle']))
    
    add_image(story, f"{SCREENSHOTS_DIR}/subscriptions_optimisation.jpeg", "Forfaits Optimisation", styles, width=14*cm, max_height=4.5*cm)
    
    opti_data = [
        ['Forfait', 'Prix/mois', 'Publicités', 'Prestations', 'Liquidités'],
        ['Starter 2K', '2\'000 CHF', '8/mois', 'Formations, Immobilier, Conseil', '-'],
        ['Starter+ 3K', '3\'000 CHF', '15/mois', '5h prestations OU 2 déjeuners équipe', '-'],
        ['Opti 5K', '5\'000 CHF', 'Illimitées', '10h prestations, accès premium complet', '3\'000 CHF'],
        ['Opti 10K', '10\'000 CHF', 'Illimitées', '20h prestations + fiscaliste dédié', '7\'000 CHF'],
        ['Opti 20K', '20\'000 CHF', '25/mois', '40h prestations complètes', '15\'000 CHF'],
        ['Opti 50K', '50\'000 CHF', 'Illimitées', '80h prestations + conciergerie', '40\'000 CHF'],
    ]
    opti_table = Table(opti_data, colWidths=[2*cm, 2*cm, 2*cm, 6*cm, 2*cm])
    opti_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GOLD),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, BLUE_MEDIUM),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(opti_table)
    
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("◆ Optimisation Fiscale", styles['SubSection']))
    story.append(Paragraph("Un expert comptable et juridique se chargent d'une optimisation fiscale reflétant directement sur vos bénéfices.", styles['Body']))
    
    story.append(Paragraph("◆ Concept 'Prestations Liquidées'", styles['SubSection']))
    story.append(Paragraph("Montant en CHF utilisable pour: heures de conseil, campagnes publicitaires, services de livraison, formations spécialisées, événements networking. Ex: Opti 10K = 7'000 CHF de prestations libres.", styles['Body']))
    
    add_stats_footer(story, "Cabinet comptable: 200-400 CHF/h | Opti 10K: valeur ~25'000 CHF pour 10'000 CHF → Économie 60%", styles)
    story.append(PageBreak())
    
    # ========== PAGE 6: CASH-BACK SECRET VIP ==========
    story.append(Paragraph("PARTIE 3: MONÉTISATION AVANCÉE", styles['MainTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    
    story.append(Paragraph("Cash-Back Secret VIP Entreprise", styles['SectionTitle']))
    story.append(Paragraph("Votre cash-back entreprise pour plus d'initiatives qui rapportent plus pour votre entreprise.", styles['Accroche']))
    story.append(Paragraph("Cash-Back entreprise te permet un accès illimité à une unité interne Titelli.", styles['Body']))
    
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
    vip_table = Table(vip_benefits, colWidths=[4*cm, 12.5*cm])
    vip_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GOLD_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, GOLD),
        ('BACKGROUND', (0, 1), (0, -1), GOLD_LIGHT),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(vip_table)
    
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("« Titelli s'occupe de tout, plus qu'à choisir votre nouvelle vie ! »", styles['Quote']))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("<b>Taux Cash-Back VIP:</b> À partir de 20% jusqu'à 99% avec possibilité de combiner système client + système entreprise à partir de 60% !", styles['Body']))
    
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("◆ Prestations VIP incluses:", styles['SubSection']))
    vip_prestations = [
        "Premium + livraison instantanée | Recrutement personnel instantané",
        "+ Pub 2M (2 millions impressions) | Immobilier accès VIP 2M & 20M",
        "Premium dépôt 24/24 | Fournisseurs Premium + 20% net",
        "Investissements Premium + 20% net | Expert Marketing Premium +",
        "Expert gestion contrats & entreprise | Liquidation stock dès 20'000.-",
    ]
    for p in vip_prestations:
        story.append(Paragraph(f"→ {p}", styles['Feature']))
    
    add_stats_footer(story, "Amex cashback: 1-2% | Banques: 0.5-1.5% | Titelli VIP: 20-99% réinvesti | Valeur: 50'000-200'000 CHF/an", styles)
    story.append(PageBreak())
    
    # ========== PAGE 7: OPTIONS À LA CARTE ==========
    story.append(Paragraph("Options à la Carte", styles['SectionTitle']))
    
    add_image(story, f"{SCREENSHOTS_DIR}/subscriptions_addons.jpeg", "Modules complémentaires", styles, width=14*cm, max_height=4.5*cm)
    
    alacarte = [
        ['OPTION', 'PRIX', 'UTILITÉ & AVANTAGES'],
        ['Publicités extra', '200 CHF/mois', '+2 pubs + 1 vidéo/mois'],
        ['Accès Investisseurs', '300 CHF/mois', 'Réseau investisseurs - Financement'],
        ['Livraison 24/24', '300 CHF/mois', 'Service permanent - Clients privilégiés'],
        ['Local commercial', '300 CHF/mois', 'Accès espace 24h/24'],
        ['Accès Fournisseurs', '500 CHF/mois', 'Réseau exclusif - Tarifs préférentiels'],
        ['Formations', '200 CHF/mois', 'Business mensuelles'],
        ['Recrutement', '200 CHF/mois', 'Aide recrutement'],
        ['Immobilier', '200 CHF/mois', 'Annonces immobilières'],
        ['Expert conseil', '1\'000 CHF/mois', 'Conseiller dédié'],
        ['Fiscaliste', '4\'000 CHF/mois', 'Optimisation fiscale'],
        ['Prestations liquidées', '1\'000 CHF/mois', '800 CHF de prestations libres'],
        ['Expert labellisation', '400 CHF ponctuel', 'Accompagnement certification'],
        ['20h Prestations', '1\'000 CHF ponctuel', '20 heures services experts'],
        ['20 déjeuners équipe', '2\'000 CHF ponctuel', 'Team building'],
    ]
    alacarte_table = Table(alacarte, colWidths=[3.5*cm, 3*cm, 10*cm])
    alacarte_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE_MEDIUM),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, GOLD),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(alacarte_table)
    
    add_stats_footer(story, "Expert conseil externe: 150-300 CHF/h | Fiscaliste: 250-500 CHF/h | Économie moyenne: 40-70%", styles)
    story.append(PageBreak())
    
    # ========== PAGE 8: PUBLICITÉ IA MÉDIA ==========
    story.append(Paragraph("Publicité IA - Média Pub", styles['SectionTitle']))
    
    add_image(story, f"{SCREENSHOTS_DIR}/monetization_media_pub.jpeg", "Interface Média Pub IA", styles, width=14*cm, max_height=5*cm)
    
    story.append(Paragraph("« Titelli accompagne son client tout au long de sa journée de consommation ! »", styles['Quote']))
    
    story.append(Paragraph("◆ Processus de création:", styles['SubSection']))
    process = ["1. Sélection template (Instagram, Story, Flyer, Email)", "2. Personnalisation (nom, slogan, couleurs)",
               "3. Génération IA haute qualité", "4. Livraison instantanée - Prêt à publier"]
    for p in process:
        story.append(Paragraph(p, styles['Feature']))
    
    media_pricing = [
        ['FORMAT', 'PRIX', 'USAGE'],
        ['Instagram Post', 'Dès 19.90 CHF', 'Réseaux sociaux'],
        ['Story Instagram/FB', 'Dès 14.90 CHF', 'Stories éphémères'],
        ['Bannière Web', 'Dès 24.90 CHF', 'Sites web, emails'],
        ['Flyer A4/A5', 'Dès 29.90 CHF', 'Print, distribution'],
        ['Email Marketing', 'Dès 19.90 CHF', 'Campagnes email'],
        ['Sur Mesure', 'Dès 49.90 CHF', 'Création personnalisée'],
    ]
    media_table = Table(media_pricing, colWidths=[4*cm, 3.5*cm, 6*cm])
    media_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GOLD),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, BLUE_MEDIUM),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(media_table)
    
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("◆ Rentabilité Média Pub:", styles['SubSection']))
    story.append(Paragraph("<b>Coût production IA:</b> ~0.50-2.00 CHF | <b>Prix vente moyen:</b> ~25 CHF | <b>Marge:</b> 90-95%", styles['Body']))
    story.append(Paragraph("<b>Volume estimé:</b> 500-1000 créations/mois | <b>Revenu potentiel:</b> 12'500-25'000 CHF/mois", styles['Body']))
    
    add_stats_footer(story, "Graphiste freelance: 50-150 CHF | Agence: 200-500 CHF | Titelli IA: 15-50 CHF | Temps: 2 min vs 2-4h", styles)
    story.append(PageBreak())
    
    # ========== PAGE 9: PUBLICITÉ IA VIDÉO ==========
    story.append(Paragraph("Publicité IA - Vidéo Pub", styles['SectionTitle']))
    
    add_image(story, f"{SCREENSHOTS_DIR}/monetization_video_pub.jpeg", "Interface Vidéo Pub IA", styles, width=14*cm, max_height=5*cm)
    
    story.append(Paragraph("« Nos tendances actuelles viennent guider nos clients sur les meilleures suggestions ! »", styles['Quote']))
    
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
    video_table = Table(video_pricing, colWidths=[5*cm, 2.5*cm, 3*cm])
    video_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE_MEDIUM),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, GOLD),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(video_table)
    
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("◆ Rentabilité Vidéo Pub:", styles['SubSection']))
    story.append(Paragraph("<b>Coût production IA:</b> ~5-15 CHF | <b>Prix vente moyen:</b> ~200 CHF | <b>Marge:</b> 92-97%", styles['Body']))
    story.append(Paragraph("<b>Volume:</b> 100-300 vidéos/mois | <b>Revenu potentiel:</b> 20'000-60'000 CHF/mois", styles['Body']))
    
    add_stats_footer(story, "CPM Instagram: 5-15 CHF | YouTube: 8-20 CHF | TikTok: 3-10 CHF", styles)
    story.append(PageBreak())
    
    # ========== PAGE 10: GLOSSAIRE CPM + COMMISSION 45% ==========
    story.append(Paragraph("Glossaire Publicitaire & Rémunération", styles['SectionTitle']))
    
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
    cpm_table = Table(cpm_data, colWidths=[2*cm, 2.8*cm, 11.7*cm])
    cpm_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE_MEDIUM),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, GOLD),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(cpm_table)
    
    story.append(Spacer(1, 0.5*cm))
    
    # Commission 45%
    commission_box = [
        [Paragraph("<b>⚠️ COMMISSION PARTENARIAT & RÉMUNÉRATION VIDÉO</b>", ParagraphStyle('CB', fontSize=9, textColor=WHITE, fontName='Helvetica-Bold', alignment=TA_CENTER))],
        [Paragraph(
            "Si vous concluez un partenariat sur Titelli ou si vous percevez une rémunération sur une vidéo "
            "diffusée sur la plateforme Titelli, <b>Titelli prélève une commission de 45%</b> sur les revenus générés. "
            "Cette commission couvre les services de mise en relation, la diffusion, le ciblage algorithmique, "
            "et l'infrastructure technique de la plateforme.", styles['Body'])],
        [Paragraph("<b>Exemple:</b> Vous générez 1'000 CHF de revenus via un partenariat vidéo → Vous percevez 550 CHF, Titelli retient 450 CHF.", styles['Body'])],
    ]
    comm_table = Table(commission_box, colWidths=[PAGE_WIDTH - 2*MARGIN - 0.5*cm])
    comm_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), GOLD_DARK),
        ('BACKGROUND', (0, 1), (0, -1), GOLD_LIGHT),
        ('BOX', (0, 0), (-1, -1), 2, GOLD),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(comm_table)
    
    story.append(Spacer(1, 0.5*cm))
    
    # Comparaison CPM marché
    story.append(Paragraph("◆ Comparaison CPM du marché:", styles['SubSection']))
    story.append(Spacer(1, 0.2*cm))
    cpm_comparison = [
        ['PLATEFORME', 'CPM MOYEN', 'COMMISSION'],
        ['Instagram Ads', '5-15 CHF', '~30%'],
        ['YouTube Ads', '8-20 CHF', '~45%'],
        ['TikTok Ads', '3-10 CHF', '~20-30%'],
        ['Facebook Ads', '4-12 CHF', '~30%'],
        ['TITELLI', '5-15 CHF', '45% (services complets)'],
    ]
    cpm_comp_table = Table(cpm_comparison, colWidths=[5*cm, 3.5*cm, 5*cm])
    cpm_comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE_MEDIUM),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, GOLD),
        ('BACKGROUND', (0, -1), (-1, -1), GOLD_LIGHT),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(cpm_comp_table)
    
    add_stats_footer(story, "Commission plateforme influenceurs: 20-50% | Titelli: 45% (services complets inclus)", styles)
    story.append(PageBreak())
    
    # ========== PAGE 11: FONCTIONNALITÉS ENTREPRISE ==========
    story.append(Paragraph("PARTIE 4: FONCTIONNALITÉS ENTREPRISE", styles['MainTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    
    # Colonne gauche
    left_features = [
        ("Gestion du Personnel", "Ils savent et comprennent ce que vous attendez d'eux exactement.", 
         "La gestion du personnel vous permet d'établir des cahiers des charges journaliers, hebdomadaires ou mensuels et de gérer instantanément l'évolution de votre personnel."),
        ("Gestion des Stocks", "C'est apaisant de pouvoir économiser mon énergie, lorsque Titelli s'occupe de tout.",
         "Accès commandes actives, automatisation selon budget, statistiques de ventes, alertes instantanées, inventaires facilités, suggestions algorithmes pour liquidations."),
        ("Espace Finance", "Une vue sur ce qu'il se passe dans mes activités financières ?",
         "L'espace finance vous permet d'évaluer votre rentabilité, vos investissements. Détail de vos finances, factures, investissements, gestion portefeuille."),
    ]
    
    # Colonne droite
    right_features = [
        ("Espace Cartes", "Conserver mes ressources en un espace c'est magique.",
         "Toutes vos cartes, réductions, moyens de paiement, visibles en un seul endroit."),
        ("Mes Investissements", "Recevoir un investissement sur du court ou long terme.",
         "Proposez des parts sur bénéfice sur un temps défini contre investissement. Fixez un prix, un temps, une part et recevez le budget tant attendu !"),
        ("Feed Entreprises", "Entre entreprises, je vois ce qu'il se passe sur le marché.",
         "Le feed permet de voir ce qui se fait de nouveau dans votre domaine et d'élargir votre réseau !"),
    ]
    
    left_content = []
    for title, accroche, desc in left_features:
        left_content.append(Paragraph(f"◆ {title}", styles['SubSection']))
        left_content.append(Paragraph(accroche, styles['Accroche']))
        left_content.append(Paragraph(desc, styles['BodySmall']))
        left_content.append(Spacer(1, 2*mm))
    
    right_content = []
    for title, accroche, desc in right_features:
        right_content.append(Paragraph(f"◆ {title}", styles['SubSection']))
        right_content.append(Paragraph(accroche, styles['Accroche']))
        right_content.append(Paragraph(desc, styles['BodySmall']))
        right_content.append(Spacer(1, 2*mm))
    
    features_table = Table([[left_content, right_content]], colWidths=[8.25*cm, 8.25*cm])
    features_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(features_table)
    
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("« Automatisez votre réassort ! »", styles['Quote']))
    
    add_stats_footer(story, "Logiciel gestion: 30-200 CHF/mois | ERP: 500-5'000 CHF/mois | Titelli: tout inclus | Économie: 3'000-15'000 CHF/an", styles)
    story.append(PageBreak())
    
    # ========== PAGE 12: FONCTIONNALITÉS SUITE ==========
    story.append(Paragraph("Fonctionnalités Entreprise (Suite)", styles['SectionTitle']))
    
    more_features_left = [
        ("Actualités Clients", "Permettre à de nouveaux clients de vous découvrir par des clients satisfaits!"),
        ("Formations", "Des formations en constante évolution. Restez connecté aux dernières évolutions techniques !"),
        ("Business News", "Qui investit dans quoi actuellement ? Ne vous laissez plus dépasser par la concurrence !"),
        ("Messagerie & Contacts", "Communiquez en tout temps avec vos équipes, partenaires, fournisseurs ou clients spéciaux."),
    ]
    
    more_features_right = [
        ("Page Pub Spontanée", "Proposer un teaser aux investisseurs ? Envoyer une invitation à 200 clients ? Cibler des nouveaux clients dépensiers ?"),
        ("Mes Offres d'Emplois", "Proposer un emploi instantanément ou sur la durée, contre du cash-back ou rémunération."),
        ("Une Exposition sur Titelli", "Être présent de manière régulière et forte aux yeux des clients et se voir recommander constamment."),
        ("Spécialiste Marketing", "Reprend en main votre communication. Révision ou création de votre image et site web vitrine."),
    ]
    
    left_col = []
    for title, desc in more_features_left:
        left_col.append(Paragraph(f"◆ {title}", styles['SubSection']))
        left_col.append(Paragraph(desc, styles['BodySmall']))
        left_col.append(Spacer(1, 2*mm))
    
    right_col = []
    for title, desc in more_features_right:
        right_col.append(Paragraph(f"◆ {title}", styles['SubSection']))
        right_col.append(Paragraph(desc, styles['BodySmall']))
        right_col.append(Spacer(1, 2*mm))
    
    more_table = Table([[left_col, right_col]], colWidths=[8.25*cm, 8.25*cm])
    more_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(more_table)
    
    story.append(Spacer(1, 0.5*cm))
    
    # Marketing & Visibilité
    story.append(Paragraph("Marketing & Visibilité", styles['SubSection']))
    story.append(Spacer(1, 0.2*cm))
    marketing_features = [
        "◆ Référencement Préférentiel: Apparaître aux bons endroits au bon moment",
        "◆ Offres Illimitées: Fidéliser clientèle et attirer de nouveaux clients",
        "◆ Mention Certifié/Labellisé: Revaloriser un savoir-faire et reconnaître des produits haut-standing",
        "◆ Livraison Standard ou 24/24: Service à domicile, livraison poste ou instantanée en 1-2h",
        "◆ Donations: Faire valoir votre image dans des événements pour des valeurs qui vous ressemblent",
    ]
    for f in marketing_features:
        story.append(Paragraph(f, styles['Feature']))
    
    story.append(Paragraph("« Être exposé sur son propre site uniquement limite l'accès à ceux qui vous connaissent déjà. »", styles['Quote']))
    
    add_stats_footer(story, "Agence marketing: 2'000-10'000 CHF/mois | SEO local: 500-2'000 CHF/mois | Titelli Guest: 250 CHF/mois tout inclus", styles)
    story.append(PageBreak())
    
    # ========== PAGE 13: CÔTÉ CLIENT ==========
    story.append(Paragraph("PARTIE 5: CÔTÉ CLIENT", styles['MainTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    
    story.append(Paragraph("Les avantages qui s'offrent gratuitement avec votre compte Titelli:", styles['Accroche']))
    
    story.append(Paragraph("◆ Cash-Back Client", styles['SubSection']))
    story.append(Paragraph("Si la concurrence en a un, j'en veux un aussi !", styles['Accroche']))
    story.append(Paragraph("Le Système de Cash-Back permet aux utilisateurs de bénéficier d'un retour sur leur achat s'élevant à 10% du montant total facturé. Accessible au client chaque début de mois suivant. Utilisable sur l'ensemble de la plateforme.", styles['Body']))
    
    cashback_table = [
        ['FORFAIT', 'TAUX', 'EXEMPLE 100 CHF'],
        ['Standard', '10%', '10 CHF crédités'],
        ['Guest', '12%', '12 CHF crédités'],
        ['Premium', '15%', '15 CHF crédités'],
        ['Premium MVP', '20%', '20 CHF crédités'],
    ]
    cb_table = Table(cashback_table, colWidths=[4*cm, 3*cm, 5*cm])
    cb_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GOLD),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, BLUE_MEDIUM),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(cb_table)
    
    story.append(Spacer(1, 0.5*cm))
    
    client_features_left = [
        ("Fiches d'Exigences Clients", "Les fiches regroupent leurs attentes et vous permettent de proposer une expérience client inoubliable !"),
        ("Lifestyle Pass", "Accès au client à un nouveau mode de vie. Profiter des meilleurs services de leurs régions !"),
        ("Healthy Lifestyle Pass", "Prestataires qui répondent aux exigences spécifiques de santé. Services et produits qui prennent véritablement soin."),
    ]
    
    client_features_right = [
        ("Liquidez Votre Stock", "Titelli livre votre service ou produit quotidiennement. Proposez dans le cadre du lifestyle pass !"),
        ("Accueil Titelli", "Suggérer chaque jour une vidéo qui promeut un prestataire ou des suggestions d'offres qui défilent."),
        ("Tendances Actuelles", "Guider nos clients sur les meilleures suggestions du moment parmi nos prestataires labellisés !"),
    ]
    
    left_client = []
    for title, desc in client_features_left:
        left_client.append(Paragraph(f"◆ {title}", styles['SubSection']))
        left_client.append(Paragraph(desc, styles['BodySmall']))
        left_client.append(Spacer(1, 2*mm))
    
    right_client = []
    for title, desc in client_features_right:
        right_client.append(Paragraph(f"◆ {title}", styles['SubSection']))
        right_client.append(Paragraph(desc, styles['BodySmall']))
        right_client.append(Spacer(1, 2*mm))
    
    client_table = Table([[left_client, right_client]], colWidths=[8.25*cm, 8.25*cm])
    client_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(client_table)
    
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("« CE QUE VOUS VOULEZ, OÙ VOUS LE VOULEZ, QUAND VOUS LE VOULEZ ET COMME VOUS LE VOULEZ ! »", styles['Quote']))
    
    add_stats_footer(story, "Programme fidélité: 1-3% | Apps concurrentes: 0-5% | Titelli: 10-20% | Rétention: +45% | Panier: +22%", styles)
    story.append(PageBreak())
    
    # ========== PAGE 14: PARTENAIRES & COMMISSIONS ==========
    story.append(Paragraph("PARTIE 6: PARTENAIRES & PRESTATIONS", styles['MainTitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    
    partner_features = [
        ("Services", "Tous les services sont répertoriés et leur référencement dépend du contrat partenarial avec Titelli. Reconnaissance 'certifiés' ou 'labellisés'."),
        ("Produits", "Tous les produits sont répertoriés. Reconnaissance professionnelle 'certifiés' ou 'labellisés' ou exposition simple."),
        ("Labellisés", "Nos prestations les plus prestigieuses répondent à des exigences particulières faites par des experts attitrés du domaine."),
        ("Certifiés", "Nos meilleurs prestataires se voient certifiés par des experts Titelli spécialisés et reconnus par des professionnels."),
        ("Profil Entreprise", "Un book attrayant qui permet de faire découvrir au mieux votre enseigne et vos prestations."),
    ]
    
    for title, desc in partner_features:
        story.append(Paragraph(f"◆ {title}", styles['SubSection']))
        story.append(Paragraph(desc, styles['BodySmall']))
        story.append(Spacer(1, 2*mm))
    
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("Commissions & Transactions", styles['SectionTitle']))
    
    commission_data = [
        ['TYPE DE FRAIS', 'TAUX/MONTANT', 'PAYÉ PAR', 'DESCRIPTION'],
        ['Commission entreprise', '5-15%', 'Entreprise', 'Sur chaque vente via Titelli'],
        ['Frais de service', '2-5 CHF', 'Client', 'Frais fixes par commande'],
        ['Frais de livraison', '3-10 CHF', 'Client', 'Variable selon distance'],
        ['Frais de paiement', '1.5-3%', 'Partagé', 'Frais Stripe/paiement'],
    ]
    comm_data_table = Table(commission_data, colWidths=[3.5*cm, 2.5*cm, 2*cm, 5.5*cm])
    comm_data_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GOLD),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, BLUE_MEDIUM),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(comm_data_table)
    
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("◆ Comparaison avec le marché:", styles['SubSection']))
    story.append(Spacer(1, 0.2*cm))
    
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
        ('BACKGROUND', (0, 0), (-1, 0), BLUE_MEDIUM),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, GOLD),
        ('BACKGROUND', (0, -1), (-1, -1), GOLD_LIGHT),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(comp_table)
    
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("<b>Avantage Titelli:</b> Commissions nettement inférieures (5-15% vs 25-35%), permettant aux entreprises de préserver leurs marges.", styles['Body']))
    
    add_stats_footer(story, "Restaurant CA via apps: 15'000 CHF | Uber Eats (30%): 4'500 CHF | Titelli (10%): 1'750 CHF | Économie: 33'000 CHF/an", styles)
    story.append(PageBreak())
    
    # ========== PAGE 15: CONDITIONS LÉGALES ==========
    story.append(Paragraph("Conditions & Informations Légales", styles['SectionTitle']))
    
    legal_box = [
        [Paragraph("<b>CONDITIONS GÉNÉRALES</b>", ParagraphStyle('LT', fontSize=10, textColor=WHITE, fontName='Helvetica-Bold', alignment=TA_CENTER))],
        [Paragraph("• Le système de cash-back autorise à prélever 10% du montant total facturé par le prestataire à chaque transaction afin de le reverser au client à chaque début du mois suivant.", styles['BodySmall'])],
        [Paragraph("• Le prestataire perçoit le revenu de ses prestations du mois effectif à chaque début du mois suivant.", styles['BodySmall'])],
        [Paragraph("• <b>Frais de gestion:</b> Titelli perçoit 10% de frais de gestion afin de répondre au mieux aux attentes.", styles['BodySmall'])],
        [Paragraph("• <b>Frais de transaction:</b> chaque transaction engage des frais qui s'élèvent à 2,9%.", styles['BodySmall'])],
        [Paragraph("• <b>Service client et responsabilité:</b> Titelli se positionnant comme un intermédiaire sur le marché entre les clients et les revendeurs, Titelli décline alors toute responsabilité liée à d'éventuels litiges.", styles['BodySmall'])],
        [Paragraph("• L'activation du compte peut être tenue sous réserve jusqu'à 2 mois dès lors de la création de ce dernier.", styles['BodySmall'])],
        [Paragraph("• *Toutes nos offres sont valables sur une durée d'une année.", styles['BodySmall'])],
    ]
    legal_table = Table(legal_box, colWidths=[PAGE_WIDTH - 2*MARGIN - 0.5*cm])
    legal_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), BLUE_DARK),
        ('BACKGROUND', (0, 1), (0, -1), GREY_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1, BLUE_DARK),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(legal_table)
    
    story.append(Spacer(1, 0.6*cm))
    
    # Code promo
    story.append(Paragraph("◆ Code Promo Bienvenue", styles['SubSection']))
    story.append(Spacer(1, 0.1*cm))
    story.append(Paragraph("Le code <b>BIENVENUE100</b> offre 100 CHF de crédit publicitaire aux nouvelles entreprises.", styles['Body']))
    
    promo_benefits = [
        "✓ Réduire la barrière à l'entrée pour les nouvelles entreprises",
        "✓ Permettre de tester les services de publicité IA sans risque",
        "✓ Créer un premier contact positif avec la plateforme",
        "✓ Augmenter le taux de conversion en abonnement payant",
    ]
    for b in promo_benefits:
        story.append(Paragraph(b, styles['Feature']))
    
    story.append(Spacer(1, 0.5*cm))
    
    cac_data = [
        ['INDICATEUR', 'VALEUR'],
        ['Valeur crédit offert', '100 CHF'],
        ['Coût réel pour Titelli', '~10-15 CHF (production IA)'],
        ['Taux conversion en abonné', '~15-25% estimé'],
        ['CAC effectif', '~40-70 CHF par client converti'],
        ['LTV moyenne abonné', '3\'000-6\'000 CHF'],
        ['Ratio LTV/CAC', '50-150x (excellent)'],
    ]
    cac_table = Table(cac_data, colWidths=[5*cm, 8*cm])
    cac_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GOLD),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, BLUE_MEDIUM),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(cac_table)
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"© {datetime.now().year} Titelli - Tous droits réservés", styles['Footer']))
    story.append(Paragraph("www.titelli.com | info@titelli.com | +41 79 895 03 13", styles['Footer']))
    story.append(Paragraph("Port-Franc 22, 1003 Lausanne, Suisse", styles['Footer']))
    
    # Build document
    doc.build(story)
    print(f"Brochure V4 Complète générée: {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    generate_brochure()
