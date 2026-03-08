#!/usr/bin/env python3
"""
Contrats Titelli - Manager et Commercial
Juridiction Suisse - Free-lance
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from datetime import datetime

# Couleurs
BLUE_DARK = colors.HexColor("#1a365d")
BLUE_MEDIUM = colors.HexColor("#2c5282")
GOLD = colors.HexColor("#d69e2e")
GOLD_DARK = colors.HexColor("#b7791f")
BLACK = colors.HexColor("#1a202c")
GREY = colors.HexColor("#4a5568")
GREY_LIGHT = colors.HexColor("#e2e8f0")

PAGE_WIDTH, PAGE_HEIGHT = A4


def create_styles():
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='ContractTitle', fontSize=18, textColor=BLUE_DARK, alignment=TA_CENTER,
        fontName='Helvetica-Bold', spaceAfter=20, spaceBefore=10, leading=22
    ))
    
    styles.add(ParagraphStyle(
        name='SectionTitle', fontSize=12, textColor=BLUE_DARK, alignment=TA_LEFT,
        fontName='Helvetica-Bold', spaceAfter=10, spaceBefore=15, leading=14
    ))
    
    styles.add(ParagraphStyle(
        name='SubTitle', fontSize=10, textColor=GOLD_DARK, alignment=TA_LEFT,
        fontName='Helvetica-Bold', spaceAfter=8, spaceBefore=10, leading=12
    ))
    
    styles.add(ParagraphStyle(
        name='Body', fontSize=9, textColor=BLACK, alignment=TA_JUSTIFY,
        fontName='Helvetica', spaceAfter=8, spaceBefore=4, leading=12
    ))
    
    styles.add(ParagraphStyle(
        name='BodyBold', fontSize=9, textColor=BLACK, alignment=TA_JUSTIFY,
        fontName='Helvetica-Bold', spaceAfter=8, spaceBefore=4, leading=12
    ))
    
    styles.add(ParagraphStyle(
        name='BulletItem', fontSize=9, textColor=BLACK, alignment=TA_LEFT,
        fontName='Helvetica', leftIndent=15, spaceAfter=4, spaceBefore=2, leading=12
    ))
    
    styles.add(ParagraphStyle(
        name='Footer', fontSize=8, textColor=GREY, alignment=TA_CENTER,
        fontName='Helvetica', spaceAfter=5, spaceBefore=5, leading=10
    ))
    
    styles.add(ParagraphStyle(
        name='Header', fontSize=8, textColor=GREY, alignment=TA_RIGHT,
        fontName='Helvetica-Oblique', leading=10
    ))
    
    return styles


def generate_manager_contract():
    """Génère le contrat Manager"""
    output_path = "/app/backend/uploads/CONTRAT_MANAGER_TITELLI.pdf"
    
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    
    styles = create_styles()
    story = []
    
    # En-tête
    story.append(Paragraph("TITELLI", ParagraphStyle('Logo', fontSize=24, textColor=GOLD_DARK, alignment=TA_CENTER, fontName='Helvetica-Bold', leading=28)))
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    story.append(Spacer(1, 0.5*cm))
    
    # Titre
    story.append(Paragraph("CONTRAT DE MANDAT FREE-LANCE", styles['ContractTitle']))
    story.append(Paragraph("MANAGER COMMERCIAL", ParagraphStyle('Sub', fontSize=14, textColor=BLUE_MEDIUM, alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=15, leading=16)))
    
    story.append(HRFlowable(width="100%", thickness=1, color=GREY_LIGHT))
    story.append(Spacer(1, 0.5*cm))
    
    # Parties
    story.append(Paragraph("ENTRE LES PARTIES", styles['SectionTitle']))
    
    story.append(Paragraph("<b>LE MANDANT :</b>", styles['Body']))
    story.append(Paragraph(
        "<b>TITELLI</b>, société représentée par sa représentante légale <b>Madame Leïla Hassini</b>, "
        "domiciliée à Rue du Port-Franc 22, 1003 Lausanne, Suisse.",
        styles['Body']
    ))
    story.append(Paragraph("Ci-après dénommé « <b>le Mandant</b> » ou « <b>Titelli</b> »", styles['Body']))
    
    story.append(Spacer(1, 0.3*cm))
    
    story.append(Paragraph("<b>LE MANDATAIRE :</b>", styles['Body']))
    story.append(Paragraph(
        "Nom : _________________________________ Prénom : _________________________________",
        styles['Body']
    ))
    story.append(Paragraph(
        "Adresse : _______________________________________________________________________",
        styles['Body']
    ))
    story.append(Paragraph(
        "Date de naissance : _________________ Nationalité : _________________________________",
        styles['Body']
    ))
    story.append(Paragraph(
        "N° AVS : _________________________________ Téléphone : ____________________________",
        styles['Body']
    ))
    story.append(Paragraph("Ci-après dénommé « <b>le Manager</b> » ou « <b>le Mandataire</b> »", styles['Body']))
    
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Ci-après désignés ensemble « <b>les Parties</b> »", styles['Body']))
    
    # Préambule
    story.append(Paragraph("PRÉAMBULE", styles['SectionTitle']))
    story.append(Paragraph(
        "Le présent contrat est régi par le droit suisse et soumis à la juridiction des tribunaux compétents "
        "du Canton de Vaud, Suisse. Le Mandataire exerce son activité en qualité de travailleur indépendant (free-lance) "
        "et assume seul la responsabilité de son statut social et fiscal.",
        styles['Body']
    ))
    
    # Article 1 - Objet
    story.append(Paragraph("ARTICLE 1 – OBJET DU CONTRAT", styles['SectionTitle']))
    story.append(Paragraph(
        "Le Mandant confie au Manager, qui accepte, la mission de développer et gérer une équipe commerciale "
        "pour le compte de Titelli, dans le respect des conditions définies ci-après.",
        styles['Body']
    ))
    
    # Article 2 - Missions
    story.append(Paragraph("ARTICLE 2 – MISSIONS DU MANAGER", styles['SectionTitle']))
    story.append(Paragraph("Le Manager s'engage à accomplir les missions suivantes :", styles['Body']))
    
    missions = [
        "Recruter entre 6 à 10 commerciaux pour constituer son équipe",
        "Former les recrues aux outils et techniques de vente Titelli",
        "Manager son équipe : 2 prises de contact par jour + 1 réunion hebdomadaire de 45 minutes",
        "Remplir les objectifs commerciaux définis (25 ventes/mois minimum)",
        "Effectuer une prospection personnelle de 25 rendez-vous clients par mois",
        "Rédiger un compte rendu journalier (débriefing)",
        "Participer à la réunion des responsables 1 fois par semaine",
        "Assurer le service client partenaires et gérer les litiges",
        "Faire respecter l'image et les valeurs de Titelli",
        "Préparer 2 futurs managers au sein de son équipe et leurs remplaçants",
        "Se servir des outils de prise de rendez-vous mis à disposition",
        "Fournir ses propres outils pour se déplacer et contacter les clients",
    ]
    for m in missions:
        story.append(Paragraph(f"• {m}", styles['BulletItem']))
    
    story.append(PageBreak())
    
    # Article 3 - Horaires
    story.append(Paragraph("ARTICLE 3 – ORGANISATION DU TRAVAIL", styles['SectionTitle']))
    story.append(Paragraph(
        "Le Manager exercera son activité selon les modalités suivantes :",
        styles['Body']
    ))
    story.append(Paragraph("• <b>Jours de travail :</b> 5 jours sur 7 (du lundi au vendredi)", styles['BulletItem']))
    story.append(Paragraph("• <b>Horaires :</b> 8 heures par jour, de 9h00 à 18h00 ou 19h00", styles['BulletItem']))
    story.append(Paragraph("• <b>Pause :</b> Minimum 1 heure de pause obligatoire", styles['BulletItem']))
    story.append(Paragraph("• <b>Réunions :</b> Présence obligatoire aux réunions hebdomadaires", styles['BulletItem']))
    
    # Article 4 - Rémunération
    story.append(Paragraph("ARTICLE 4 – RÉMUNÉRATION", styles['SectionTitle']))
    
    story.append(Paragraph("<b>4.1 Salaire fixe de base</b>", styles['SubTitle']))
    story.append(Paragraph(
        "Le Manager percevra un salaire fixe mensuel de <b>CHF 2'500.-</b> correspondant à l'atteinte "
        "de ses objectifs commerciaux personnels de 25 ventes par mois.",
        styles['Body']
    ))
    
    story.append(Paragraph("<b>4.2 Commissions sur équipe (objectifs atteints)</b>", styles['SubTitle']))
    story.append(Paragraph(
        "En sus du salaire fixe, le Manager perçoit une commission sur les ventes de son équipe :",
        styles['Body']
    ))
    story.append(Paragraph("• <b>CHF 10.-</b> par vente réalisée par chacune de ses recrues", styles['BulletItem']))
    story.append(Paragraph("• <b>CHF 20.-</b> par vente au-delà de l'objectif de 25 ventes par commercial", styles['BulletItem']))
    story.append(Paragraph("• Le Manager peut recruter jusqu'à <b>10 commerciaux</b> maximum", styles['BulletItem']))
    
    story.append(Paragraph("<b>4.3 Commissions personnelles (au-delà de 25 ventes)</b>", styles['SubTitle']))
    story.append(Paragraph(
        "Au-delà de 25 ventes personnelles réalisées, le Manager bénéficie du système de commissions suivant :",
        styles['Body']
    ))
    
    # Tableau commissions
    comm_data = [
        ['Abonnement mensuel', 'Commission'],
        ['50 à 100 CHF/mois', '70 CHF'],
        ['200 à 300 CHF/mois', '75 CHF'],
        ['400 à 500 CHF/mois', '80 CHF'],
        ['600 à 700 CHF/mois', '85 CHF'],
        ['800 à 900 CHF/mois', '90 CHF'],
        ['1\'000 CHF/mois', '100 CHF'],
    ]
    comm_table = Table(comm_data, colWidths=[7*cm, 5*cm])
    comm_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, GREY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(comm_table)
    story.append(Spacer(1, 0.3*cm))
    
    story.append(Paragraph("<b>Commissions sur Packs :</b>", styles['SubTitle']))
    pack_data = [
        ['Pack', 'Commission'],
        ['Pack 1\'000 CHF', '100 CHF'],
        ['Pack 2\'000 CHF', '120 CHF'],
        ['Pack 3\'000 CHF', '150 CHF'],
        ['Pack 5\'000 CHF', '170 CHF'],
        ['Pack 10\'000 CHF', '200 CHF'],
        ['Pack 20\'000 CHF', '250 CHF'],
    ]
    pack_table = Table(pack_data, colWidths=[7*cm, 5*cm])
    pack_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GOLD_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, GREY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(pack_table)
    
    story.append(Paragraph("<b>4.4 Non-atteinte des objectifs</b>", styles['SubTitle']))
    story.append(Paragraph(
        "Si le Manager ne remplit pas ses objectifs de 25 ventes par mois, il sera rémunéré "
        "uniquement à la commission, évaluée à hauteur de <b>CHF 75.-</b> par vente réalisée.",
        styles['Body']
    ))
    
    story.append(PageBreak())
    
    # Article 5 - Bonus et promotions
    story.append(Paragraph("ARTICLE 5 – BONUS ET PROMOTIONS", styles['SectionTitle']))
    story.append(Paragraph(
        "Les performances accomplies avant l'activation des commissions sont répertoriées pour :",
        styles['Body']
    ))
    story.append(Paragraph("• <b>Promotions :</b> Évaluations tous les 3 mois", styles['BulletItem']))
    story.append(Paragraph("• <b>Distribution des bonus :</b> Tous les 6 mois", styles['BulletItem']))
    story.append(Paragraph("• <b>Bonus maximal :</b> CHF 15'000.- pour le meilleur performeur", styles['BulletItem']))
    
    # Article 6 - Confidentialité
    story.append(Paragraph("ARTICLE 6 – CONFIDENTIALITÉ ET NON-CONCURRENCE", styles['SectionTitle']))
    story.append(Paragraph(
        "Le Manager s'engage à respecter une stricte confidentialité concernant toutes les informations "
        "relatives à l'activité de Titelli, ses clients, ses méthodes commerciales et ses partenaires. "
        "Cette obligation de confidentialité perdure pendant toute la durée du contrat et pendant une période "
        "de 2 ans après sa cessation.",
        styles['Body']
    ))
    story.append(Paragraph(
        "Le Manager s'engage également à ne pas exercer d'activité concurrente directe ou indirecte "
        "pendant la durée du contrat et pendant une période de 12 mois suivant la fin du présent contrat.",
        styles['Body']
    ))
    
    # Article 7 - Image
    story.append(Paragraph("ARTICLE 7 – RESPECT DE L'IMAGE TITELLI", styles['SectionTitle']))
    story.append(Paragraph(
        "Le Manager s'engage à représenter dignement l'image de Titelli et à agir conformément aux valeurs "
        "et à l'éthique de l'entreprise. Tout comportement portant atteinte à la réputation de Titelli "
        "pourra entraîner la résiliation immédiate du présent contrat.",
        styles['Body']
    ))
    
    # Article 8 - Durée
    story.append(Paragraph("ARTICLE 8 – DURÉE ET RÉSILIATION", styles['SectionTitle']))
    story.append(Paragraph(
        "Le présent contrat est conclu pour une durée indéterminée à compter de sa signature. "
        "Chaque partie peut y mettre fin moyennant un préavis d'un mois, notifié par écrit.",
        styles['Body']
    ))
    
    # Article 9 - Juridiction
    story.append(Paragraph("ARTICLE 9 – DROIT APPLICABLE ET JURIDICTION", styles['SectionTitle']))
    story.append(Paragraph(
        "Le présent contrat est régi par le droit suisse. En cas de litige, les parties s'engagent "
        "à rechercher une solution amiable. À défaut, les tribunaux du Canton de Vaud seront seuls compétents.",
        styles['Body']
    ))
    
    # Signatures
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=GREY_LIGHT))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("SIGNATURES", styles['SectionTitle']))
    story.append(Paragraph(f"Fait à Lausanne, le ___________________", styles['Body']))
    story.append(Paragraph("En deux exemplaires originaux, un pour chaque partie.", styles['Body']))
    
    story.append(Spacer(1, 1*cm))
    
    sig_table = Table([
        [Paragraph("<b>Pour Titelli</b>", styles['Body']), Paragraph("<b>Le Manager</b>", styles['Body'])],
        [Paragraph("Leïla Hassini<br/>Représentante légale", styles['Body']), Paragraph("Nom : _______________________<br/>Prénom : _______________________", styles['Body'])],
        ["", ""],
        [Paragraph("Signature :", styles['Body']), Paragraph("Signature :", styles['Body'])],
        ["", ""],
        ["", ""],
        ["", ""],
    ], colWidths=[8*cm, 8*cm])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(sig_table)
    
    # Footer
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=GOLD))
    story.append(Paragraph("TITELLI – Rue du Port-Franc 22, 1003 Lausanne, Suisse", styles['Footer']))
    story.append(Paragraph("www.titelli.com | info@titelli.com | +41 79 895 03 13", styles['Footer']))
    
    doc.build(story)
    print(f"Contrat Manager généré: {output_path}")
    return output_path


def generate_commercial_contract():
    """Génère le contrat Commercial"""
    output_path = "/app/backend/uploads/CONTRAT_COMMERCIAL_TITELLI.pdf"
    
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    
    styles = create_styles()
    story = []
    
    # En-tête
    story.append(Paragraph("TITELLI", ParagraphStyle('Logo', fontSize=24, textColor=GOLD_DARK, alignment=TA_CENTER, fontName='Helvetica-Bold', leading=28)))
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    story.append(Spacer(1, 0.5*cm))
    
    # Titre
    story.append(Paragraph("CONTRAT DE MANDAT FREE-LANCE", styles['ContractTitle']))
    story.append(Paragraph("COMMERCIAL", ParagraphStyle('Sub', fontSize=14, textColor=BLUE_MEDIUM, alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=15, leading=16)))
    
    story.append(HRFlowable(width="100%", thickness=1, color=GREY_LIGHT))
    story.append(Spacer(1, 0.5*cm))
    
    # Parties
    story.append(Paragraph("ENTRE LES PARTIES", styles['SectionTitle']))
    
    story.append(Paragraph("<b>LE MANDANT :</b>", styles['Body']))
    story.append(Paragraph(
        "<b>TITELLI</b>, société représentée par sa représentante légale <b>Madame Leïla Hassini</b>, "
        "domiciliée à Rue du Port-Franc 22, 1003 Lausanne, Suisse.",
        styles['Body']
    ))
    story.append(Paragraph("Ci-après dénommé « <b>le Mandant</b> » ou « <b>Titelli</b> »", styles['Body']))
    
    story.append(Spacer(1, 0.3*cm))
    
    story.append(Paragraph("<b>LE MANDATAIRE :</b>", styles['Body']))
    story.append(Paragraph(
        "Nom : _________________________________ Prénom : _________________________________",
        styles['Body']
    ))
    story.append(Paragraph(
        "Adresse : _______________________________________________________________________",
        styles['Body']
    ))
    story.append(Paragraph(
        "Date de naissance : _________________ Nationalité : _________________________________",
        styles['Body']
    ))
    story.append(Paragraph(
        "N° AVS : _________________________________ Téléphone : ____________________________",
        styles['Body']
    ))
    story.append(Paragraph("Ci-après dénommé « <b>le Commercial</b> » ou « <b>le Mandataire</b> »", styles['Body']))
    
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Ci-après désignés ensemble « <b>les Parties</b> »", styles['Body']))
    
    # Préambule
    story.append(Paragraph("PRÉAMBULE", styles['SectionTitle']))
    story.append(Paragraph(
        "Le présent contrat est régi par le droit suisse et soumis à la juridiction des tribunaux compétents "
        "du Canton de Vaud, Suisse. Le Mandataire exerce son activité en qualité de travailleur indépendant (free-lance) "
        "et assume seul la responsabilité de son statut social et fiscal.",
        styles['Body']
    ))
    
    # Article 1 - Objet
    story.append(Paragraph("ARTICLE 1 – OBJET DU CONTRAT", styles['SectionTitle']))
    story.append(Paragraph(
        "Le Mandant confie au Commercial, qui accepte, la mission de prospecter et conclure des ventes "
        "d'abonnements et de services pour le compte de Titelli, dans le respect des conditions définies ci-après.",
        styles['Body']
    ))
    
    # Article 2 - Obligations
    story.append(Paragraph("ARTICLE 2 – OBLIGATIONS DU COMMERCIAL", styles['SectionTitle']))
    story.append(Paragraph("Le Commercial s'engage à :", styles['Body']))
    
    obligations = [
        "Respecter les termes contractuels commerciaux suisses",
        "Respecter la confidentialité et la clause de non-concurrence",
        "Respecter et promouvoir l'image de Titelli",
        "Remplir les objectifs commerciaux fixés à 25 signatures par mois",
        "Remplir le débriefing journalier",
        "Se servir des outils de prise de rendez-vous mis à disposition",
        "Se présenter aux réunions hebdomadaires",
        "Répondre aux attentes des managers dans le cadre professionnel",
        "Fournir ses propres outils pour se déplacer et contacter les clients",
    ]
    for o in obligations:
        story.append(Paragraph(f"• {o}", styles['BulletItem']))
    
    # Article 3 - Horaires
    story.append(Paragraph("ARTICLE 3 – ORGANISATION DU TRAVAIL", styles['SectionTitle']))
    story.append(Paragraph(
        "Le Commercial exercera son activité selon les modalités suivantes :",
        styles['Body']
    ))
    story.append(Paragraph("• <b>Jours de travail :</b> 5 jours sur 7 (du lundi au vendredi)", styles['BulletItem']))
    story.append(Paragraph("• <b>Horaires :</b> 8 heures par jour, de 9h00 à 18h00 ou 19h00", styles['BulletItem']))
    story.append(Paragraph("• <b>Pause :</b> Minimum 1 heure de pause obligatoire", styles['BulletItem']))
    story.append(Paragraph("• <b>Réunions :</b> Présence obligatoire 1 fois par semaine", styles['BulletItem']))
    
    story.append(PageBreak())
    
    # Article 4 - Rémunération
    story.append(Paragraph("ARTICLE 4 – RÉMUNÉRATION", styles['SectionTitle']))
    
    story.append(Paragraph("<b>4.1 Salaire fixe de base</b>", styles['SubTitle']))
    story.append(Paragraph(
        "Le Commercial percevra un salaire fixe mensuel de <b>CHF 2'500.-</b> correspondant à l'atteinte "
        "de ses objectifs commerciaux de 25 ventes par mois.",
        styles['Body']
    ))
    
    story.append(Paragraph("<b>4.2 Commissions (au-delà de 25 ventes)</b>", styles['SubTitle']))
    story.append(Paragraph(
        "Au-delà de 25 ventes réalisées, le Commercial enclenche le processus de commissions suivant :",
        styles['Body']
    ))
    
    # Tableau commissions
    comm_data = [
        ['Abonnement mensuel vendu', 'Commission'],
        ['50 à 100 CHF/mois', '70 CHF'],
        ['200 à 300 CHF/mois', '75 CHF'],
        ['400 à 500 CHF/mois', '80 CHF'],
        ['600 à 700 CHF/mois', '85 CHF'],
        ['800 à 900 CHF/mois', '90 CHF'],
        ['1\'000 CHF/mois', '100 CHF'],
    ]
    comm_table = Table(comm_data, colWidths=[7*cm, 5*cm])
    comm_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, GREY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(comm_table)
    story.append(Spacer(1, 0.3*cm))
    
    story.append(Paragraph("<b>Commissions sur Packs :</b>", styles['SubTitle']))
    pack_data = [
        ['Pack vendu', 'Commission'],
        ['Pack 1\'000 CHF', '100 CHF'],
        ['Pack 2\'000 CHF', '120 CHF'],
        ['Pack 3\'000 CHF', '150 CHF'],
        ['Pack 5\'000 CHF', '170 CHF'],
        ['Pack 10\'000 CHF', '200 CHF'],
        ['Pack 20\'000 CHF', '250 CHF'],
    ]
    pack_table = Table(pack_data, colWidths=[7*cm, 5*cm])
    pack_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GOLD_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, GREY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(pack_table)
    
    story.append(Paragraph("<b>4.3 Non-atteinte des objectifs</b>", styles['SubTitle']))
    story.append(Paragraph(
        "Si le Commercial ne remplit pas ses objectifs de 25 ventes par mois, il sera rémunéré "
        "uniquement à la commission, évaluée à hauteur de <b>CHF 75.-</b> par vente réalisée.",
        styles['Body']
    ))
    
    # Article 5 - Bonus et promotions
    story.append(Paragraph("ARTICLE 5 – BONUS ET PROMOTIONS", styles['SectionTitle']))
    story.append(Paragraph(
        "Les performances accomplies avant l'activation des commissions sont répertoriées pour :",
        styles['Body']
    ))
    story.append(Paragraph("• <b>Promotions :</b> Évaluations tous les 3 mois", styles['BulletItem']))
    story.append(Paragraph("• <b>Distribution des bonus :</b> Tous les 6 mois", styles['BulletItem']))
    story.append(Paragraph("• <b>Bonus maximal :</b> CHF 15'000.- pour le meilleur performeur", styles['BulletItem']))
    
    # Article 6 - Confidentialité
    story.append(Paragraph("ARTICLE 6 – CONFIDENTIALITÉ ET NON-CONCURRENCE", styles['SectionTitle']))
    story.append(Paragraph(
        "Le Commercial s'engage à respecter une stricte confidentialité concernant toutes les informations "
        "relatives à l'activité de Titelli, ses clients, ses méthodes commerciales et ses partenaires. "
        "Cette obligation de confidentialité perdure pendant toute la durée du contrat et pendant une période "
        "de 2 ans après sa cessation.",
        styles['Body']
    ))
    story.append(Paragraph(
        "Le Commercial s'engage également à ne pas exercer d'activité concurrente directe ou indirecte "
        "pendant la durée du contrat et pendant une période de 12 mois suivant la fin du présent contrat.",
        styles['Body']
    ))
    
    # Article 7 - Image
    story.append(Paragraph("ARTICLE 7 – RESPECT DE L'IMAGE TITELLI", styles['SectionTitle']))
    story.append(Paragraph(
        "Le Commercial s'engage à représenter dignement l'image de Titelli et à agir conformément aux valeurs "
        "et à l'éthique de l'entreprise. Tout comportement portant atteinte à la réputation de Titelli "
        "pourra entraîner la résiliation immédiate du présent contrat.",
        styles['Body']
    ))
    
    story.append(PageBreak())
    
    # Article 8 - Durée
    story.append(Paragraph("ARTICLE 8 – DURÉE ET RÉSILIATION", styles['SectionTitle']))
    story.append(Paragraph(
        "Le présent contrat est conclu pour une durée indéterminée à compter de sa signature. "
        "Chaque partie peut y mettre fin moyennant un préavis d'un mois, notifié par écrit.",
        styles['Body']
    ))
    
    # Article 9 - Juridiction
    story.append(Paragraph("ARTICLE 9 – DROIT APPLICABLE ET JURIDICTION", styles['SectionTitle']))
    story.append(Paragraph(
        "Le présent contrat est régi par le droit suisse. En cas de litige, les parties s'engagent "
        "à rechercher une solution amiable. À défaut, les tribunaux du Canton de Vaud seront seuls compétents.",
        styles['Body']
    ))
    
    # Signatures
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=GREY_LIGHT))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("SIGNATURES", styles['SectionTitle']))
    story.append(Paragraph(f"Fait à Lausanne, le ___________________", styles['Body']))
    story.append(Paragraph("En deux exemplaires originaux, un pour chaque partie.", styles['Body']))
    
    story.append(Spacer(1, 1*cm))
    
    sig_table = Table([
        [Paragraph("<b>Pour Titelli</b>", styles['Body']), Paragraph("<b>Le Commercial</b>", styles['Body'])],
        [Paragraph("Leïla Hassini<br/>Représentante légale", styles['Body']), Paragraph("Nom : _______________________<br/>Prénom : _______________________", styles['Body'])],
        ["", ""],
        [Paragraph("Signature :", styles['Body']), Paragraph("Signature :", styles['Body'])],
        ["", ""],
        ["", ""],
        ["", ""],
    ], colWidths=[8*cm, 8*cm])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(sig_table)
    
    # Footer
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=GOLD))
    story.append(Paragraph("TITELLI – Rue du Port-Franc 22, 1003 Lausanne, Suisse", styles['Footer']))
    story.append(Paragraph("www.titelli.com | info@titelli.com | +41 79 895 03 13", styles['Footer']))
    
    doc.build(story)
    print(f"Contrat Commercial généré: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_manager_contract()
    generate_commercial_contract()
    print("\n✅ Les deux contrats ont été générés avec succès!")
