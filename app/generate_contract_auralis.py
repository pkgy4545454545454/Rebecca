#!/usr/bin/env python3
"""
Contrat Free-lance AURALIRIS
Juridiction Suisse - Développement Web/Application
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

# Couleurs professionnelles
PURPLE_DARK = colors.HexColor("#4c1d95")
PURPLE_MEDIUM = colors.HexColor("#7c3aed")
GOLD = colors.HexColor("#f59e0b")
GOLD_DARK = colors.HexColor("#d97706")
BLACK = colors.HexColor("#1f2937")
GREY = colors.HexColor("#6b7280")
GREY_LIGHT = colors.HexColor("#e5e7eb")

PAGE_WIDTH, PAGE_HEIGHT = A4


def create_styles():
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='ContractTitle', fontSize=20, textColor=PURPLE_DARK, alignment=TA_CENTER,
        fontName='Helvetica-Bold', spaceAfter=20, spaceBefore=10, leading=24
    ))
    
    styles.add(ParagraphStyle(
        name='SectionTitle', fontSize=12, textColor=PURPLE_DARK, alignment=TA_LEFT,
        fontName='Helvetica-Bold', spaceAfter=10, spaceBefore=15, leading=14
    ))
    
    styles.add(ParagraphStyle(
        name='SubTitle', fontSize=10, textColor=GOLD_DARK, alignment=TA_LEFT,
        fontName='Helvetica-Bold', spaceAfter=8, spaceBefore=10, leading=12
    ))
    
    styles.add(ParagraphStyle(
        name='Body', fontSize=9, textColor=BLACK, alignment=TA_JUSTIFY,
        fontName='Helvetica', spaceAfter=8, spaceBefore=4, leading=13
    ))
    
    styles.add(ParagraphStyle(
        name='BodyBold', fontSize=9, textColor=BLACK, alignment=TA_JUSTIFY,
        fontName='Helvetica-Bold', spaceAfter=8, spaceBefore=4, leading=13
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
    
    styles.add(ParagraphStyle(
        name='Small', fontSize=8, textColor=GREY, alignment=TA_LEFT,
        fontName='Helvetica', spaceAfter=4, spaceBefore=2, leading=10
    ))
    
    return styles


def generate_auralis_contract():
    """Génère le contrat Free-lance AURALIRIS"""
    output_path = "/app/backend/uploads/CONTRAT_FREELANCE_AURALIRIS.pdf"
    
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    
    styles = create_styles()
    story = []
    
    # En-tête
    story.append(Paragraph("AURALIRIS", ParagraphStyle('Logo', fontSize=28, textColor=PURPLE_DARK, alignment=TA_CENTER, fontName='Helvetica-Bold', leading=32)))
    story.append(Paragraph("Plateforme d'entraide communautaire", ParagraphStyle('Tagline', fontSize=10, textColor=PURPLE_MEDIUM, alignment=TA_CENTER, fontName='Helvetica-Oblique', spaceAfter=15, leading=12)))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=PURPLE_MEDIUM))
    story.append(Spacer(1, 0.5*cm))
    
    # Titre
    story.append(Paragraph("CONTRAT DE PRESTATION FREE-LANCE", styles['ContractTitle']))
    story.append(Paragraph("Développement Site Web / Application", ParagraphStyle('Sub', fontSize=12, textColor=PURPLE_MEDIUM, alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=15, leading=14)))
    
    story.append(HRFlowable(width="100%", thickness=1, color=GREY_LIGHT))
    story.append(Spacer(1, 0.5*cm))
    
    # Parties
    story.append(Paragraph("ENTRE LES PARTIES", styles['SectionTitle']))
    
    story.append(Paragraph("<b>L'EMPLOYEUR (Client) :</b>", styles['Body']))
    story.append(Paragraph(
        "<b>Monsieur Sultan BERISA</b><br/>"
        "Adresse : Route de Fribourg 64<br/>"
        "Ci-après dénommé « <b>l'Employeur</b> » ou « <b>le Client</b> »",
        styles['Body']
    ))
    
    story.append(Spacer(1, 0.3*cm))
    
    story.append(Paragraph("<b>LE DÉVELOPPEUR (Prestataire) :</b>", styles['Body']))
    story.append(Paragraph(
        "<b>Monsieur Bruno DA ROCHA TELES</b><br/>"
        "Activité : Développeur Web / Application Free-lance<br/>"
        "Ci-après dénommé « <b>le Développeur</b> » ou « <b>le Prestataire</b> »",
        styles['Body']
    ))
    
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Ci-après désignés ensemble « <b>les Parties</b> »", styles['Body']))
    
    # Préambule
    story.append(Paragraph("PRÉAMBULE", styles['SectionTitle']))
    story.append(Paragraph(
        "Le présent contrat est régi par le droit suisse, notamment les articles 394 et suivants du Code des Obligations "
        "relatifs au contrat de mandat. Le Développeur exerce son activité en qualité de travailleur indépendant (free-lance) "
        "et assume seul la responsabilité de son statut social et fiscal conformément à la législation suisse.",
        styles['Body']
    ))
    
    # Article 1 - Objet
    story.append(Paragraph("ARTICLE 1 – OBJET DU CONTRAT", styles['SectionTitle']))
    story.append(Paragraph(
        "L'Employeur confie au Développeur, qui accepte, la conception, le développement et le déploiement "
        "de la plateforme web/application « <b>AURALIRIS</b> », selon les spécifications décrites ci-après.",
        styles['Body']
    ))
    
    # Article 2 - Description du projet
    story.append(Paragraph("ARTICLE 2 – DESCRIPTION DU PROJET AURALIRIS", styles['SectionTitle']))
    story.append(Paragraph(
        "Le projet AURALIRIS est une plateforme complète structurée en trois parties distinctes mais interconnectées :",
        styles['Body']
    ))
    
    story.append(Paragraph("<b>2.1 Entraide communautaire rémunérée</b>", styles['SubTitle']))
    story.append(Paragraph(
        "Cette partie constitue le socle du projet. Elle est dédiée à l'entraide locale et humaine. "
        "Les utilisateurs peuvent proposer ou solliciter des services simples du quotidien : accompagnement, "
        "aide ponctuelle, soutien pratique ou social. L'entraide repose sur un système économique structuré où "
        "les services rendus sont validés via la plateforme, puis rémunérés. Il ne s'agit pas de bénévolat, mais "
        "d'un modèle qui reconnaît concrètement la valeur du temps, de l'attention et de l'aide apportée. "
        "L'objectif est de redonner une dignité économique à des gestes humains souvent invisibles.",
        styles['Body']
    ))
    
    story.append(Paragraph("<b>2.2 Espace dédié à l'autisme et aux troubles sévères</b>", styles['SubTitle']))
    story.append(Paragraph(
        "Une section entièrement consacrée aux personnes concernées par l'autisme et par des troubles "
        "psychiatriques, physiques ou handicapants, y compris dans leurs formes les plus sévères. "
        "Cet espace est spécifiquement conçu pour être accessible, sécurisé et modéré. Tous les profils peuvent s'y inscrire. "
        "Il ne s'agit pas d'un réseau social classique, mais d'un lieu pensé pour permettre des échanges adaptés, "
        "respectueux et structurants, favorisant la reconnaissance, l'expression et le lien social.",
        styles['Body']
    ))
    
    story.append(Paragraph("<b>2.3 Articles et partenariats commerciaux (Drop shipping)</b>", styles['SubTitle']))
    story.append(Paragraph(
        "Le site intégrera également une section articles, basée sur des partenariats commerciaux déjà établis. "
        "Ce volet fonctionnera sur un modèle de drop shipping et permettra de générer des revenus complémentaires "
        "afin de soutenir financièrement l'ensemble de la plateforme et d'assurer sa pérennité.",
        styles['Body']
    ))
    
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "<i>La vision globale d'AURALIRIS est de créer un écosystème équilibré, où l'entraide humaine devient une valeur reconnue, "
        "où les personnes souvent mises à l'écart trouvent un espace dédié, et où le modèle économique soutient le projet "
        "sans le dénaturer.</i>",
        styles['Body']
    ))
    
    story.append(PageBreak())
    
    # Article 3 - Obligations du développeur
    story.append(Paragraph("ARTICLE 3 – OBLIGATIONS DU DÉVELOPPEUR", styles['SectionTitle']))
    story.append(Paragraph("Le Développeur s'engage à :", styles['Body']))
    
    obligations = [
        "Concevoir et développer la plateforme AURALIRIS selon les spécifications définies à l'Article 2",
        "Assurer un travail sérieux, professionnel et honnête tout au long du projet",
        "Déployer le site dès qu'il est prêt, même si c'est avant la date maximale convenue",
        "Assurer un suivi quotidien du site après déploiement",
        "Répondre aux questions de l'Employeur et être disponible pour toute demande concernant le site",
        "Fournir les informations techniques nécessaires à l'Employeur",
        "Respecter les délais convenus et communiquer en cas de difficultés",
        "Garantir la qualité et la fonctionnalité du code livré",
    ]
    for o in obligations:
        story.append(Paragraph(f"• {o}", styles['BulletItem']))
    
    # Article 4 - Délais
    story.append(Paragraph("ARTICLE 4 – DÉLAIS DE RÉALISATION", styles['SectionTitle']))
    story.append(Paragraph("<b>4.1 Date de début</b>", styles['SubTitle']))
    story.append(Paragraph(
        "Le présent contrat prend effet à compter du <b>16 février 2026</b>.",
        styles['Body']
    ))
    story.append(Paragraph("<b>4.2 Date maximale de déploiement</b>", styles['SubTitle']))
    story.append(Paragraph(
        "Le site/application AURALIRIS devra être déployé et fonctionnel au plus tard le <b>1er septembre 2026</b>.",
        styles['Body']
    ))
    story.append(Paragraph("<b>4.3 Livraison anticipée</b>", styles['SubTitle']))
    story.append(Paragraph(
        "Le Développeur s'engage à déployer le site dès que celui-ci est prêt et fonctionnel, "
        "même si cette date est antérieure à la date maximale du 1er septembre 2026.",
        styles['Body']
    ))
    
    # Article 5 - Rémunération
    story.append(Paragraph("ARTICLE 5 – RÉMUNÉRATION", styles['SectionTitle']))
    
    story.append(Paragraph("<b>5.1 Montant mensuel</b>", styles['SubTitle']))
    story.append(Paragraph(
        "L'Employeur versera au Développeur une rémunération mensuelle de <b>CHF 480.-</b> (quatre cent quatre-vingts francs suisses).",
        styles['Body']
    ))
    
    story.append(Paragraph("<b>5.2 Échéance de paiement</b>", styles['SubTitle']))
    story.append(Paragraph(
        "Le paiement devra être effectué entre le <b>25 et le 31 de chaque mois</b>.",
        styles['Body']
    ))
    
    story.append(Paragraph("<b>5.3 Premier mois (Février 2026)</b>", styles['SubTitle']))
    story.append(Paragraph(
        "Pour le mois de février 2026, le montant à payer est de <b>CHF 120.-</b> (cent vingt francs suisses), "
        "correspondant à la période du 16 au 28 février 2026.",
        styles['Body']
    ))
    
    story.append(Paragraph("<b>5.4 Moyens de paiement acceptés</b>", styles['SubTitle']))
    
    # Tableau des moyens de paiement
    payment_data = [
        ['Moyen de paiement', 'Coordonnées'],
        ['Virement bancaire (IBAN)', '0900 0000 1619 6429 8'],
        ['TWINT', '+41 76 295 76 88'],
        ['Espèces', 'Si déplacement possible aux alentours de Genève'],
    ]
    payment_table = Table(payment_data, colWidths=[5*cm, 10*cm])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PURPLE_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, GREY),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(payment_table)
    
    story.append(PageBreak())
    
    # Article 6 - Conditions de travail
    story.append(Paragraph("ARTICLE 6 – CONDITIONS DE TRAVAIL", styles['SectionTitle']))
    story.append(Paragraph(
        "Le Développeur prend le soin d'exécuter l'application fonctionnelle et correcte dans le temps le plus rapide possible. "
        "Le Développeur assure un suivi quotidien du site, inclus dans la prestation.",
        styles['Body']
    ))
    story.append(Paragraph(
        "Le Développeur s'engage à donner les informations nécessaires, à répondre aux questions et à être disponible "
        "envers l'Employeur pour toute donnée concernant le site.",
        styles['Body']
    ))
    
    # Article 7 - Propriété intellectuelle
    story.append(Paragraph("ARTICLE 7 – PROPRIÉTÉ INTELLECTUELLE", styles['SectionTitle']))
    story.append(Paragraph(
        "À compter du paiement intégral des sommes dues, l'Employeur devient propriétaire exclusif "
        "du code source, du design et de l'ensemble des éléments développés dans le cadre du présent contrat. "
        "Le Développeur conserve le droit de mentionner sa participation au projet à titre de référence professionnelle.",
        styles['Body']
    ))
    
    # Article 8 - Confidentialité
    story.append(Paragraph("ARTICLE 8 – CONFIDENTIALITÉ", styles['SectionTitle']))
    story.append(Paragraph(
        "Les Parties s'engagent à maintenir strictement confidentielles toutes les informations échangées "
        "dans le cadre de ce contrat, notamment les données techniques, commerciales et stratégiques relatives au projet AURALIRIS. "
        "Cette obligation perdure pendant toute la durée du contrat et pendant une période de 2 ans après sa cessation.",
        styles['Body']
    ))
    
    # Article 9 - Droit applicable
    story.append(Paragraph("ARTICLE 9 – DROIT APPLICABLE ET JURIDICTION", styles['SectionTitle']))
    story.append(Paragraph(
        "Le présent contrat est régi par le droit suisse, notamment les dispositions du Code des Obligations. "
        "En cas de litige, les parties s'engagent à rechercher une solution amiable. "
        "À défaut d'accord amiable, les tribunaux compétents du Canton de Genève seront saisis.",
        styles['Body']
    ))
    
    # Article 10 - Dispositions finales
    story.append(Paragraph("ARTICLE 10 – DISPOSITIONS FINALES", styles['SectionTitle']))
    story.append(Paragraph(
        "Toute modification du présent contrat devra faire l'objet d'un avenant écrit signé par les deux Parties. "
        "Si une clause du présent contrat s'avérait nulle ou inapplicable, les autres clauses resteraient valides et applicables.",
        styles['Body']
    ))
    
    # Signatures
    story.append(Spacer(1, 0.8*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=GREY_LIGHT))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("SIGNATURES", styles['SectionTitle']))
    story.append(Paragraph("Fait en deux exemplaires originaux, un pour chaque partie.", styles['Body']))
    story.append(Paragraph(f"Date : ___________________", styles['Body']))
    story.append(Paragraph("Lieu : ___________________", styles['Body']))
    
    story.append(Spacer(1, 0.8*cm))
    
    sig_table = Table([
        [Paragraph("<b>L'EMPLOYEUR</b>", styles['Body']), Paragraph("<b>LE DÉVELOPPEUR</b>", styles['Body'])],
        [Paragraph("Sultan BERISA<br/>Route de Fribourg 64", styles['Body']), Paragraph("Bruno DA ROCHA TELES<br/>Développeur Free-lance", styles['Body'])],
        ["", ""],
        [Paragraph("Signature :", styles['Body']), Paragraph("Signature :", styles['Body'])],
        ["", ""],
        ["", ""],
        [Paragraph("_______________________", styles['Body']), Paragraph("_______________________", styles['Body'])],
    ], colWidths=[8*cm, 8*cm])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(sig_table)
    
    # Footer
    story.append(Spacer(1, 0.8*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=PURPLE_MEDIUM))
    story.append(Paragraph("AURALIRIS – Plateforme d'entraide communautaire", styles['Footer']))
    story.append(Paragraph("Contrat régi par le droit suisse", styles['Footer']))
    
    doc.build(story)
    print(f"Contrat AURALIRIS généré: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_auralis_contract()
    print("\n✅ Le contrat AURALIRIS a été généré avec succès!")
