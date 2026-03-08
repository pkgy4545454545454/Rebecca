#!/usr/bin/env python3
"""
Cahier des Charges MANAGER/ADMIN Titelli
Documentation complète pour l'administration de la plateforme
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
    Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

SCREENSHOTS_DIR = '/app/backend/uploads/brochure_admin_screenshots'
OUTPUT_DIR = '/app/backend/uploads'

# Palette de couleurs - Version Admin (professionnelle, sérieuse)
COLORS = {
    'primary': colors.Color(220/255, 38/255, 38/255),     # Rouge admin
    'secondary': colors.Color(0/255, 71/255, 171/255),    # Bleu
    'accent': colors.Color(255/255, 193/255, 7/255),      # Or
    'success': colors.Color(34/255, 197/255, 94/255),     # Vert
    'warning': colors.Color(245/255, 158/255, 11/255),    # Orange
    'dark': colors.Color(15/255, 15/255, 20/255),
    'light': colors.Color(248/255, 250/255, 252/255),
    'gray': colors.Color(100/255, 116/255, 139/255),
}


def create_styles():
    """Crée des styles professionnels pour admin"""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='CoverMain',
        fontSize=48,
        textColor=COLORS['primary'],
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=52,
        spaceAfter=10
    ))
    
    styles.add(ParagraphStyle(
        name='CoverSub',
        fontSize=18,
        textColor=COLORS['gray'],
        alignment=TA_CENTER,
        fontName='Helvetica',
        spaceAfter=8,
        leading=24
    ))
    
    styles.add(ParagraphStyle(
        name='SectionMain',
        fontSize=26,
        textColor=COLORS['primary'],
        fontName='Helvetica-Bold',
        spaceBefore=0,
        spaceAfter=20,
        leading=30
    ))
    
    styles.add(ParagraphStyle(
        name='SectionSub',
        fontSize=16,
        textColor=COLORS['dark'],
        fontName='Helvetica-Bold',
        spaceBefore=20,
        spaceAfter=12,
        leading=20
    ))
    
    styles.add(ParagraphStyle(
        name='SectionNumber',
        fontSize=12,
        textColor=COLORS['primary'],
        fontName='Helvetica-Bold',
        spaceBefore=0,
        spaceAfter=5,
        leading=14
    ))
    
    styles.add(ParagraphStyle(
        name='BodyMain',
        fontSize=11,
        textColor=COLORS['dark'],
        fontName='Helvetica',
        alignment=TA_JUSTIFY,
        spaceAfter=10,
        leading=16
    ))
    
    styles.add(ParagraphStyle(
        name='BulletPoint',
        fontSize=11,
        textColor=COLORS['dark'],
        fontName='Helvetica',
        leftIndent=20,
        spaceAfter=6,
        leading=15
    ))
    
    styles.add(ParagraphStyle(
        name='FeatureTitle',
        fontSize=12,
        textColor=COLORS['success'],
        fontName='Helvetica-Bold',
        spaceBefore=8,
        spaceAfter=4,
        leading=14
    ))
    
    styles.add(ParagraphStyle(
        name='WarningBox',
        fontSize=10,
        textColor=COLORS['warning'],
        fontName='Helvetica-Bold',
        leftIndent=15,
        rightIndent=15,
        spaceBefore=15,
        spaceAfter=15,
        leading=14
    ))
    
    styles.add(ParagraphStyle(
        name='TipBox',
        fontSize=10,
        textColor=COLORS['secondary'],
        fontName='Helvetica-Oblique',
        leftIndent=15,
        rightIndent=15,
        spaceBefore=15,
        spaceAfter=15,
        leading=14
    ))
    
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
    
    styles.add(ParagraphStyle(
        name='TOCTitle',
        fontSize=14,
        textColor=COLORS['primary'],
        fontName='Helvetica-Bold',
        spaceBefore=20,
        spaceAfter=8,
        leading=16
    ))
    
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
    
    return styles


def add_line(story, color=None, width=17*cm, thickness=1):
    if color is None:
        color = COLORS['light']
    story.append(Spacer(1, 5))
    story.append(HRFlowable(width=width, thickness=thickness, color=color, spaceBefore=5, spaceAfter=10))


def add_image(story, image_path, caption="", width=14*cm, max_height=10*cm, styles=None):
    if not os.path.exists(image_path):
        return False
    try:
        img = Image.open(image_path)
        aspect = img.height / img.width
        height = width * aspect
        if height > max_height:
            height = max_height
            width = height / aspect
        
        img_flowable = RLImage(image_path, width=width, height=height)
        img_table = Table([[img_flowable]], colWidths=[width + 10])
        img_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOX', (0, 0), (-1, -1), 1, colors.Color(220/255, 220/255, 220/255)),
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
        print(f"   ❌ Erreur: {e}")
        return False


def create_feature_box(story, title, items, styles, color=None):
    if color is None:
        color = COLORS['success']
    
    content = [Paragraph(f"<b>{title}</b>", styles['FeatureTitle'])]
    for item in items:
        content.append(Paragraph(f"• {item}", styles['BulletPoint']))
    
    data = [[c] for c in content]
    table = Table(data, colWidths=[15*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.Color(245/255, 250/255, 245/255)),
        ('BOX', (0, 0), (-1, -1), 1, color),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(table)
    story.append(Spacer(1, 15))


def create_warning_box(story, text, styles):
    data = [[Paragraph(f"⚠️ <b>IMPORTANT</b> : {text}", styles['WarningBox'])]]
    table = Table(data, colWidths=[15*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.Color(255/255, 250/255, 240/255)),
        ('BOX', (0, 0), (-1, -1), 2, COLORS['warning']),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
    ]))
    story.append(table)
    story.append(Spacer(1, 15))


def create_tip_box(story, text, styles):
    data = [[Paragraph(f"💡 <b>Conseil</b> : {text}", styles['TipBox'])]]
    table = Table(data, colWidths=[15*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.Color(240/255, 245/255, 255/255)),
        ('BOX', (0, 0), (-1, -1), 2, COLORS['secondary']),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
    ]))
    story.append(table)
    story.append(Spacer(1, 15))


def create_section(story, number, title, styles):
    story.append(Paragraph(number, styles['SectionNumber']))
    story.append(Paragraph(title, styles['SectionMain']))
    add_line(story, COLORS['primary'], thickness=2)


def create_subsection(story, title, styles):
    story.append(Spacer(1, 10))
    story.append(Paragraph(title, styles['SectionSub']))
    add_line(story, COLORS['light'], thickness=1)


def generate_admin_brochure():
    """Génère le cahier des charges admin"""
    print("=" * 70)
    print("   GÉNÉRATION CAHIER DES CHARGES - MANAGER/ADMIN")
    print("=" * 70)
    
    output_path = f'{OUTPUT_DIR}/TITELLI_CAHIER_CHARGES_MANAGER.pdf'
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = create_styles()
    story = []
    
    # ==================== COUVERTURE ====================
    print("📄 Couverture...")
    story.append(Spacer(1, 4*cm))
    story.append(Paragraph("TITELLI", styles['CoverMain']))
    story.append(Spacer(1, 0.5*cm))
    add_line(story, COLORS['accent'], width=8*cm, thickness=3)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("CAHIER DES CHARGES", styles['CoverSub']))
    story.append(Paragraph("Guide Complet pour les Managers & Administrateurs", styles['CoverSub']))
    story.append(Spacer(1, 1.5*cm))
    
    add_image(story, f'{SCREENSHOTS_DIR}/admin_overview.png', "", width=13*cm, max_height=8*cm, styles=styles)
    
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"Version {datetime.now().strftime('%B %Y')}", styles['CoverSub']))
    story.append(Paragraph("Document confidentiel - Usage interne", styles['CoverSub']))
    story.append(PageBreak())
    
    # ==================== TABLE DES MATIÈRES ====================
    print("📄 Table des matières...")
    story.append(Paragraph("TABLE DES MATIÈRES", styles['SectionMain']))
    add_line(story, COLORS['primary'], thickness=2)
    story.append(Spacer(1, 0.5*cm))
    
    toc_data = [
        ("01", "INTRODUCTION", ["Rôle du manager", "Accès administrateur"]),
        ("02", "VUE D'ENSEMBLE", ["Statistiques globales", "Indicateurs clés"]),
        ("03", "INSCRIPTIONS", ["Validation des entreprises", "Gestion des demandes"]),
        ("04", "PUB MÉDIA IA", ["Commandes publicitaires", "Validation des créations"]),
        ("05", "ALGORITHMES", ["Configuration IA", "Paramètres de ciblage"]),
        ("06", "ABONNEMENTS", ["Formules disponibles", "Gestion des plans"]),
        ("07", "COMPTABILITÉ", ["Suivi financier", "Rapports et exports"]),
        ("08", "RETRAITS", ["Validation des demandes", "Processus de paiement"]),
        ("09", "UTILISATEURS", ["Liste complète", "Gestion des comptes"]),
        ("10", "ENTREPRISES", ["Suivi des prestataires", "Statistiques"]),
        ("11", "COMMANDES", ["Toutes les transactions", "Suivi des ventes"]),
        ("12", "PARAMÈTRES", ["Configuration générale", "Personnalisation"]),
    ]
    
    for num, title, items in toc_data:
        story.append(Paragraph(f"<font color='#DC2626'><b>{num}</b></font>  {title}", styles['TOCTitle']))
        for item in items:
            story.append(Paragraph(f"• {item}", styles['TOCItem']))
    
    story.append(PageBreak())
    
    # ==================== PARTIE 1: INTRODUCTION ====================
    print("📄 Partie 1...")
    create_section(story, "PARTIE 01", "INTRODUCTION", styles)
    
    story.append(Paragraph(
        "Ce cahier des charges est destiné aux managers et administrateurs de la plateforme Titelli. "
        "Il détaille l'ensemble des fonctionnalités de gestion et d'administration disponibles.",
        styles['BodyMain']
    ))
    story.append(Spacer(1, 0.3*cm))
    
    create_subsection(story, "Rôle du Manager", styles)
    
    story.append(Paragraph(
        "En tant que manager Titelli, vous avez accès à l'ensemble des outils d'administration "
        "de la plateforme. Vos responsabilités incluent :",
        styles['BodyMain']
    ))
    
    create_feature_box(story, "Responsabilités principales :", [
        "Valider les inscriptions des nouvelles entreprises",
        "Gérer les demandes de retrait des prestataires",
        "Superviser les commandes et transactions",
        "Configurer les algorithmes de recommandation",
        "Suivre la comptabilité et les finances",
        "Gérer les abonnements et formules",
        "Assurer le support aux utilisateurs"
    ], styles)
    
    create_warning_box(story, 
        "L'accès au dashboard admin est réservé aux emails autorisés. Tout accès non autorisé "
        "sera automatiquement bloqué et signalé.", styles)
    
    story.append(PageBreak())
    
    # ==================== PARTIE 2: VUE D'ENSEMBLE ====================
    print("📄 Partie 2...")
    create_section(story, "PARTIE 02", "VUE D'ENSEMBLE", styles)
    
    story.append(Paragraph(
        "La vue d'ensemble vous donne un aperçu complet de l'activité de la plateforme en temps réel.",
        styles['BodyMain']
    ))
    story.append(Spacer(1, 0.3*cm))
    
    add_image(story, f'{SCREENSHOTS_DIR}/admin_overview.png',
              "Tableau de bord administrateur", width=14*cm, max_height=9*cm, styles=styles)
    
    create_feature_box(story, "Indicateurs affichés :", [
        "Nombre total d'utilisateurs inscrits",
        "Nombre d'entreprises enregistrées",
        "Nombre de commandes passées",
        "Nombre d'avis déposés",
        "Utilisateurs récents avec leur type (client/entreprise)",
        "Commandes récentes avec montants"
    ], styles)
    
    create_tip_box(story,
        "Consultez cette page chaque matin pour avoir une vision rapide de l'activité de la veille.", styles)
    
    story.append(PageBreak())
    
    # ==================== PARTIE 3: INSCRIPTIONS ====================
    print("📄 Partie 3...")
    create_section(story, "PARTIE 03", "INSCRIPTIONS EN ATTENTE", styles)
    
    add_image(story, f'{SCREENSHOTS_DIR}/admin_inscriptions.png',
              "Gestion des inscriptions", width=14*cm, max_height=8*cm, styles=styles)
    
    story.append(Paragraph(
        "Cette section vous permet de valider ou refuser les demandes d'inscription des entreprises.",
        styles['BodyMain']
    ))
    
    create_subsection(story, "Processus de validation", styles)
    
    steps = [
        "Consulter la liste des demandes en attente",
        "Vérifier les informations fournies par l'entreprise",
        "Contrôler les documents justificatifs si requis",
        "Valider ou refuser la demande",
        "En cas de refus, préciser le motif"
    ]
    for i, step in enumerate(steps, 1):
        story.append(Paragraph(f"<b>{i}.</b> {step}", styles['BulletPoint']))
    
    create_warning_box(story,
        "Toute validation engage la responsabilité de Titelli. Vérifiez soigneusement les informations "
        "avant d'approuver une inscription.", styles)
    
    story.append(PageBreak())
    
    # ==================== PARTIE 4: PUB MÉDIA IA ====================
    print("📄 Partie 4...")
    create_section(story, "PARTIE 04", "PUB MÉDIA IA", styles)
    
    add_image(story, f'{SCREENSHOTS_DIR}/admin_pub_media.png',
              "Gestion des publicités IA", width=14*cm, max_height=8*cm, styles=styles)
    
    story.append(Paragraph(
        "Cette section permet de gérer les commandes de publicités générées par intelligence artificielle.",
        styles['BodyMain']
    ))
    
    create_feature_box(story, "Fonctionnalités :", [
        "Voir toutes les commandes de pub IA",
        "Filtrer par statut (en attente, validé, refusé)",
        "Consulter les visuels générés",
        "Valider ou refuser les créations",
        "Suivre les statistiques de performance"
    ], styles)
    
    story.append(PageBreak())
    
    # ==================== PARTIE 5: ALGORITHMES ====================
    print("📄 Partie 5...")
    create_section(story, "PARTIE 05", "ALGORITHMES", styles)
    
    add_image(story, f'{SCREENSHOTS_DIR}/admin_algorithmes.png',
              "Configuration des algorithmes", width=14*cm, max_height=8*cm, styles=styles)
    
    story.append(Paragraph(
        "Configurez les algorithmes d'intelligence artificielle qui régissent les recommandations "
        "et le ciblage sur la plateforme.",
        styles['BodyMain']
    ))
    
    create_feature_box(story, "Algorithmes disponibles :", [
        "Recommandations de services personnalisées",
        "Ciblage publicitaire intelligent",
        "Score de pertinence des prestataires",
        "Détection des tendances",
        "Analyse du comportement utilisateur"
    ], styles)
    
    create_warning_box(story,
        "La modification des algorithmes peut impacter significativement l'expérience utilisateur. "
        "Testez toujours les changements avant de les déployer en production.", styles)
    
    story.append(PageBreak())
    
    # ==================== PARTIE 6: ABONNEMENTS ====================
    print("📄 Partie 6...")
    create_section(story, "PARTIE 06", "ABONNEMENTS", styles)
    
    add_image(story, f'{SCREENSHOTS_DIR}/admin_abonnements.png',
              "Gestion des abonnements", width=14*cm, max_height=8*cm, styles=styles)
    
    story.append(Paragraph(
        "Gérez les différentes formules d'abonnement proposées aux entreprises.",
        styles['BodyMain']
    ))
    
    create_subsection(story, "Formules d'abonnement", styles)
    
    # Tableau des abonnements
    abo_data = [
        ['FORMULE', 'PRIX', 'COMMISSION', 'AVANTAGES PRINCIPAUX'],
        ['Guest', 'Gratuit', '15%', 'Profil basique'],
        ['Certifié', '29 CHF/mois', '12%', 'Services illimités + Badge'],
        ['Labellisé', '79 CHF/mois', '10%', 'Pub gratuite + Support prio'],
        ['Exclusif', '149 CHF/mois', '8%', 'Account manager dédié'],
    ]
    
    table = Table(abo_data, colWidths=[3*cm, 3*cm, 2.5*cm, 6.5*cm])
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
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.Color(230/255, 230/255, 230/255)),
        ('BOX', (0, 0), (-1, -1), 2, COLORS['primary']),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.5*cm))
    
    create_tip_box(story,
        "Vous pouvez modifier les tarifs et avantages de chaque formule directement depuis cette interface.", styles)
    
    story.append(PageBreak())
    
    # ==================== PARTIE 7: COMPTABILITÉ ====================
    print("📄 Partie 7...")
    create_section(story, "PARTIE 07", "COMPTABILITÉ", styles)
    
    add_image(story, f'{SCREENSHOTS_DIR}/admin_comptabilite.png',
              "Suivi comptable", width=14*cm, max_height=8*cm, styles=styles)
    
    story.append(Paragraph(
        "Suivez l'ensemble des flux financiers de la plateforme : revenus, commissions, paiements.",
        styles['BodyMain']
    ))
    
    create_feature_box(story, "Fonctionnalités comptables :", [
        "Tableau de bord financier global",
        "Historique de toutes les transactions",
        "Filtrage par période, type, statut",
        "Export des données (CSV, PDF)",
        "Graphiques et tendances",
        "Calcul automatique des commissions"
    ], styles)
    
    create_subsection(story, "Types de transactions", styles)
    
    story.append(Paragraph("• <b>Ventes</b> : Commandes payées par les clients", styles['BulletPoint']))
    story.append(Paragraph("• <b>Commissions</b> : Part Titelli sur chaque vente", styles['BulletPoint']))
    story.append(Paragraph("• <b>Abonnements</b> : Paiements mensuels des entreprises", styles['BulletPoint']))
    story.append(Paragraph("• <b>Retraits</b> : Versements aux prestataires", styles['BulletPoint']))
    story.append(Paragraph("• <b>Publicités</b> : Revenus publicitaires", styles['BulletPoint']))
    
    story.append(PageBreak())
    
    # ==================== PARTIE 8: RETRAITS ====================
    print("📄 Partie 8...")
    create_section(story, "PARTIE 08", "RETRAITS", styles)
    
    add_image(story, f'{SCREENSHOTS_DIR}/admin_retraits.png',
              "Gestion des demandes de retrait", width=14*cm, max_height=8*cm, styles=styles)
    
    story.append(Paragraph(
        "Validez les demandes de retrait des prestataires souhaitant récupérer leurs gains.",
        styles['BodyMain']
    ))
    
    create_subsection(story, "Processus de validation des retraits", styles)
    
    steps = [
        "Consulter les demandes de retrait en attente",
        "Vérifier le solde disponible du prestataire",
        "Contrôler les informations bancaires (IBAN)",
        "Valider le montant demandé",
        "Effectuer le virement bancaire",
        "Marquer comme traité dans le système"
    ]
    for i, step in enumerate(steps, 1):
        story.append(Paragraph(f"<b>{i}.</b> {step}", styles['BulletPoint']))
    
    create_warning_box(story,
        "Le montant minimum de retrait est de 50 CHF. Vérifiez toujours l'IBAN avant d'effectuer un virement.", styles)
    
    story.append(PageBreak())
    
    # ==================== PARTIE 9: UTILISATEURS ====================
    print("📄 Partie 9...")
    create_section(story, "PARTIE 09", "UTILISATEURS", styles)
    
    add_image(story, f'{SCREENSHOTS_DIR}/admin_utilisateurs.png',
              "Liste des utilisateurs", width=14*cm, max_height=8*cm, styles=styles)
    
    story.append(Paragraph(
        "Consultez et gérez tous les utilisateurs de la plateforme.",
        styles['BodyMain']
    ))
    
    create_feature_box(story, "Informations disponibles :", [
        "Liste complète des utilisateurs",
        "Type de compte (client, entreprise, admin)",
        "Date d'inscription",
        "Statut du compte (actif, suspendu)",
        "Coordonnées de contact",
        "Historique d'activité"
    ], styles)
    
    create_subsection(story, "Actions possibles", styles)
    
    story.append(Paragraph("• Rechercher un utilisateur par email ou nom", styles['BulletPoint']))
    story.append(Paragraph("• Consulter le profil détaillé", styles['BulletPoint']))
    story.append(Paragraph("• Modifier les informations si nécessaire", styles['BulletPoint']))
    story.append(Paragraph("• Suspendre ou désactiver un compte", styles['BulletPoint']))
    story.append(Paragraph("• Envoyer un message direct", styles['BulletPoint']))
    
    story.append(PageBreak())
    
    # ==================== PARTIE 10: ENTREPRISES ====================
    print("📄 Partie 10...")
    create_section(story, "PARTIE 10", "ENTREPRISES", styles)
    
    add_image(story, f'{SCREENSHOTS_DIR}/admin_entreprises.png',
              "Liste des entreprises", width=14*cm, max_height=8*cm, styles=styles)
    
    story.append(Paragraph(
        "Suivez toutes les entreprises inscrites sur la plateforme.",
        styles['BodyMain']
    ))
    
    create_feature_box(story, "Informations sur les entreprises :", [
        "Nom et description de l'entreprise",
        "Catégorie d'activité",
        "Formule d'abonnement actuelle",
        "Nombre de services/produits publiés",
        "Chiffre d'affaires généré",
        "Note moyenne des avis"
    ], styles)
    
    story.append(PageBreak())
    
    # ==================== PARTIE 11: COMMANDES ====================
    print("📄 Partie 11...")
    create_section(story, "PARTIE 11", "COMMANDES", styles)
    
    add_image(story, f'{SCREENSHOTS_DIR}/admin_commandes.png',
              "Suivi des commandes", width=14*cm, max_height=8*cm, styles=styles)
    
    story.append(Paragraph(
        "Consultez toutes les commandes passées sur la plateforme.",
        styles['BodyMain']
    ))
    
    create_feature_box(story, "Informations sur les commandes :", [
        "Numéro de commande unique",
        "Client et entreprise concernés",
        "Montant total et commission",
        "Statut (en attente, validée, terminée, annulée)",
        "Date de création",
        "Détail des articles commandés"
    ], styles)
    
    story.append(PageBreak())
    
    # ==================== PARTIE 12: PARAMÈTRES ====================
    print("📄 Partie 12...")
    create_section(story, "PARTIE 12", "PARAMÈTRES", styles)
    
    add_image(story, f'{SCREENSHOTS_DIR}/admin_parametres.png',
              "Paramètres généraux", width=14*cm, max_height=8*cm, styles=styles)
    
    story.append(Paragraph(
        "Configurez les paramètres généraux de la plateforme.",
        styles['BodyMain']
    ))
    
    create_feature_box(story, "Options de configuration :", [
        "Paramètres de la plateforme",
        "Configuration des emails",
        "Gestion des notifications",
        "Paramètres de paiement",
        "Options de sécurité",
        "Personnalisation de l'interface"
    ], styles)
    
    create_warning_box(story,
        "Toute modification des paramètres peut impacter le fonctionnement de la plateforme. "
        "Consultez l'équipe technique avant tout changement majeur.", styles)
    
    story.append(PageBreak())
    
    # ==================== PAGE FINALE ====================
    print("📄 Page finale...")
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("DOCUMENT CONFIDENTIEL", styles['SectionMain']))
    add_line(story, COLORS['primary'], width=10*cm, thickness=3)
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Ce cahier des charges est destiné exclusivement aux managers et administrateurs "
        "de la plateforme Titelli. Toute diffusion non autorisée est strictement interdite.",
        styles['BodyMain']
    ))
    
    story.append(Spacer(1, 1*cm))
    
    contact_data = [
        [Paragraph("<b>SUPPORT TECHNIQUE</b>", styles['SectionSub'])],
        [Paragraph("📧  tech@titelli.com", styles['BodyMain'])],
        [Paragraph("📞  +41 XX XXX XX XX (ligne directe)", styles['BodyMain'])],
        [Paragraph("🔒  Accès VPN requis pour les opérations sensibles", styles['BodyMain'])],
    ]
    
    contact_table = Table(contact_data, colWidths=[12*cm])
    contact_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.Color(255/255, 245/255, 245/255)),
        ('BOX', (0, 0), (-1, -1), 2, COLORS['primary']),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(contact_table)
    
    # ==================== GÉNÉRATION ====================
    print("\n📄 Génération du PDF...")
    doc.build(story)
    
    size = os.path.getsize(output_path) / (1024 * 1024)
    
    print("\n" + "=" * 70)
    print(f"   ✅ CAHIER DES CHARGES MANAGER GÉNÉRÉ !")
    print(f"   📁 {output_path}")
    print(f"   📦 Taille: {size:.1f} MB")
    print("=" * 70)
    
    return output_path


if __name__ == "__main__":
    generate_admin_brochure()
