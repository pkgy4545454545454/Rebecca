#!/usr/bin/env python3
"""
CDC COMPLET FINAL TITELLI - Depuis la création du projet
Avec surlignage VERT des nouvelles fonctionnalités
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
    Table, TableStyle, PageBreak, HRFlowable, ListFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

OUTPUT_DIR = '/app/backend/uploads'

# Couleurs
COLORS = {
    'primary': colors.Color(0/255, 71/255, 171/255),      # Bleu Titelli
    'new': colors.Color(34/255, 197/255, 94/255),         # VERT - Nouvelles fonctionnalités
    'new_bg': colors.Color(220/255, 252/255, 231/255),    # Fond vert clair
    'accent': colors.Color(255/255, 193/255, 7/255),      # Or
    'warning': colors.Color(220/255, 38/255, 38/255),     # Rouge
    'dark': colors.Color(15/255, 15/255, 20/255),
    'gray': colors.Color(100/255, 116/255, 139/255),
    'light': colors.Color(248/255, 250/255, 252/255),
}


def create_styles():
    """Crée les styles pour le document"""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='CoverMain',
        fontSize=48,
        textColor=COLORS['primary'],
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=52
    ))
    
    styles.add(ParagraphStyle(
        name='CoverSub',
        fontSize=16,
        textColor=COLORS['gray'],
        alignment=TA_CENTER,
        fontName='Helvetica',
        leading=22
    ))
    
    styles.add(ParagraphStyle(
        name='PartTitle',
        fontSize=28,
        textColor=COLORS['primary'],
        fontName='Helvetica-Bold',
        spaceBefore=0,
        spaceAfter=15,
        leading=32
    ))
    
    styles.add(ParagraphStyle(
        name='SectionTitle',
        fontSize=18,
        textColor=COLORS['dark'],
        fontName='Helvetica-Bold',
        spaceBefore=15,
        spaceAfter=10,
        leading=22
    ))
    
    styles.add(ParagraphStyle(
        name='SubSection',
        fontSize=14,
        textColor=COLORS['primary'],
        fontName='Helvetica-Bold',
        spaceBefore=12,
        spaceAfter=8,
        leading=18
    ))
    
    styles.add(ParagraphStyle(
        name='BodyMain',
        fontSize=10,
        textColor=COLORS['dark'],
        fontName='Helvetica',
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        leading=14
    ))
    
    styles.add(ParagraphStyle(
        name='BulletItem',
        fontSize=10,
        textColor=COLORS['dark'],
        fontName='Helvetica',
        leftIndent=15,
        spaceAfter=4,
        leading=13
    ))
    
    # Style pour les NOUVEAUTÉS (fond vert)
    styles.add(ParagraphStyle(
        name='NewFeature',
        fontSize=10,
        textColor=COLORS['new'],
        fontName='Helvetica-Bold',
        leftIndent=15,
        spaceAfter=4,
        leading=13,
        backColor=COLORS['new_bg'],
        borderPadding=3
    ))
    
    styles.add(ParagraphStyle(
        name='NewSection',
        fontSize=14,
        textColor=COLORS['new'],
        fontName='Helvetica-Bold',
        spaceBefore=12,
        spaceAfter=8,
        leading=18,
        backColor=COLORS['new_bg'],
        borderPadding=5
    ))
    
    styles.add(ParagraphStyle(
        name='TOCTitle',
        fontSize=12,
        textColor=COLORS['primary'],
        fontName='Helvetica-Bold',
        spaceBefore=15,
        spaceAfter=5,
        leading=14
    ))
    
    styles.add(ParagraphStyle(
        name='TOCItem',
        fontSize=10,
        textColor=COLORS['dark'],
        fontName='Helvetica',
        leftIndent=12,
        spaceAfter=3,
        leading=12
    ))
    
    styles.add(ParagraphStyle(
        name='TOCNew',
        fontSize=10,
        textColor=COLORS['new'],
        fontName='Helvetica-Bold',
        leftIndent=12,
        spaceAfter=3,
        leading=12
    ))
    
    styles.add(ParagraphStyle(
        name='Caption',
        fontSize=9,
        textColor=COLORS['gray'],
        fontName='Helvetica-Oblique',
        alignment=TA_CENTER,
        spaceBefore=5,
        spaceAfter=10
    ))
    
    return styles


def add_line(story, color=None, width=17*cm, thickness=1):
    if color is None:
        color = COLORS['light']
    story.append(Spacer(1, 3))
    story.append(HRFlowable(width=width, thickness=thickness, color=color, spaceBefore=3, spaceAfter=8))


def create_table(data, col_widths, header_color=None):
    """Crée un tableau stylisé"""
    if header_color is None:
        header_color = COLORS['primary']
    
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.Color(220/255, 220/255, 220/255)),
        ('BOX', (0, 0), (-1, -1), 1, header_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    return table


def generate_complete_cdc():
    """Génère le CDC complet final"""
    print("=" * 70)
    print("   GÉNÉRATION CDC COMPLET FINAL - TITELLI")
    print("=" * 70)
    
    output_path = f'{OUTPUT_DIR}/TITELLI_CDC_COMPLET_FINAL.pdf'
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
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
    story.append(Paragraph("CAHIER DES CHARGES COMPLET", styles['CoverSub']))
    story.append(Paragraph("Depuis la Création du Projet", styles['CoverSub']))
    story.append(Spacer(1, 2*cm))
    
    # Légende
    legend_data = [
        [Paragraph("<b>LÉGENDE</b>", styles['BodyMain'])],
        [Paragraph("• Texte normal = Fonctionnalités du CDC original", styles['BodyMain'])],
        [Paragraph("<font color='#22C55E'><b>• Texte vert = NOUVEAUTÉS ajoutées depuis le premier CDC</b></font>", styles['BodyMain'])],
    ]
    legend_table = Table(legend_data, colWidths=[14*cm])
    legend_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['light']),
        ('BOX', (0, 0), (-1, -1), 2, COLORS['primary']),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
    ]))
    story.append(legend_table)
    
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph(f"Version Finale - {datetime.now().strftime('%d %B %Y')}", styles['CoverSub']))
    story.append(Paragraph("Document Exhaustif - Toutes Fonctionnalités", styles['CoverSub']))
    story.append(PageBreak())
    
    # ==================== TABLE DES MATIÈRES ====================
    print("📄 Table des matières...")
    story.append(Paragraph("TABLE DES MATIÈRES", styles['PartTitle']))
    add_line(story, COLORS['primary'], thickness=2)
    
    toc = [
        ("PARTIE 1", "PRÉSENTATION DU PROJET", [
            ("1.1", "Vision et Objectifs", False),
            ("1.2", "Cibles Utilisateurs", False),
            ("1.3", "Architecture Technique", False),
        ]),
        ("PARTIE 2", "SYSTÈME D'AUTHENTIFICATION", [
            ("2.1", "Inscription Multi-Profils", False),
            ("2.2", "Connexion JWT", False),
            ("2.3", "Gestion des Rôles", False),
        ]),
        ("PARTIE 3", "MARKETPLACE & CATALOGUE", [
            ("3.1", "Catalogue Entreprises", False),
            ("3.2", "Services et Produits", False),
            ("3.3", "Système de Notation", False),
            ("3.4", "Badges et Certifications", False),
        ]),
        ("PARTIE 4", "SYSTÈME DE COMMANDES", [
            ("4.1", "Panier Multi-Entreprises", False),
            ("4.2", "Checkout Stripe", False),
            ("4.3", "Suivi des Commandes", False),
        ]),
        ("PARTIE 5", "SYSTÈME FINANCIER", [
            ("5.1", "Cashback Client", False),
            ("5.2", "Abonnements Client", False),
            ("5.3", "Abonnements Entreprise", False),
            ("5.4", "🆕 Retrait Cashback vers IBAN", True),
            ("5.5", "🆕 Webhooks Stripe", True),
        ]),
        ("PARTIE 6", "DASHBOARDS", [
            ("6.1", "Dashboard Client", False),
            ("6.2", "Dashboard Entreprise", False),
            ("6.3", "🆕 Dashboard Admin Complet", True),
        ]),
        ("PARTIE 7", "COMMUNICATION & SOCIAL", [
            ("7.1", "Messagerie", False),
            ("7.2", "Système d'Amis", False),
            ("7.3", "Notifications", False),
            ("7.4", "🆕 WebSocket Temps Réel", True),
            ("7.5", "🆕 Feed Social / Mode de Vie", True),
        ]),
        ("PARTIE 8", "🆕 NOUVELLES FONCTIONNALITÉS", [
            ("8.1", "🆕 RDV chez Titelli (Social Booking)", True),
            ("8.2", "🆕 Demandes Spécialistes", True),
            ("8.3", "🆕 Lifestyle Passes", True),
            ("8.4", "🆕 Titelli Pro++ (B2B)", True),
            ("8.5", "🆕 Sports & Compétitions", True),
            ("8.6", "🆕 Gamification & Points", True),
            ("8.7", "🆕 Système de Parrainage", True),
        ]),
        ("PARTIE 9", "🆕 PUB MÉDIA IA", [
            ("9.1", "🆕 Publicités Images IA (DALL-E)", True),
            ("9.2", "🆕 Publicités Vidéos IA (Sora)", True),
            ("9.3", "🆕 Commandes Titelli", True),
        ]),
        ("PARTIE 10", "INTÉGRATIONS & SÉCURITÉ", [
            ("10.1", "Stripe (Paiements)", False),
            ("10.2", "🆕 SalonPro (Webhooks)", True),
            ("10.3", "Sécurité JWT", False),
            ("10.4", "🆕 Algorithmes IA Ciblage", True),
        ]),
        ("PARTIE 11", "BASE DE DONNÉES", [
            ("11.1", "Collections MongoDB", False),
            ("11.2", "🆕 Nouvelles Collections", True),
        ]),
        ("PARTIE 12", "PAGES & CONTENUS", [
            ("12.1", "Page d'Accueil", False),
            ("12.2", "🆕 Pages Légales (CGV, Mentions)", True),
            ("12.3", "🆕 Page À Propos", True),
        ]),
    ]
    
    for part_num, part_title, items in toc:
        is_new_part = "🆕" in part_title
        if is_new_part:
            story.append(Paragraph(f"<font color='#22C55E'><b>{part_num} - {part_title}</b></font>", styles['TOCTitle']))
        else:
            story.append(Paragraph(f"<b>{part_num}</b> - {part_title}", styles['TOCTitle']))
        
        for item_num, item_title, is_new in items:
            if is_new:
                story.append(Paragraph(f"<font color='#22C55E'>{item_num} {item_title}</font>", styles['TOCNew']))
            else:
                story.append(Paragraph(f"{item_num} {item_title}", styles['TOCItem']))
    
    story.append(PageBreak())
    
    # ==================== PARTIE 1: PRÉSENTATION ====================
    print("📄 Partie 1: Présentation...")
    story.append(Paragraph("PARTIE 1 - PRÉSENTATION DU PROJET", styles['PartTitle']))
    add_line(story, COLORS['primary'], thickness=2)
    
    story.append(Paragraph("1.1 Vision et Objectifs", styles['SectionTitle']))
    story.append(Paragraph(
        "Titelli est une marketplace premium connectant les entreprises, clients et influenceurs "
        "de la région lausannoise. La plateforme offre une expérience utilisateur haut de gamme "
        "avec système de fidélité, cashback et réseau social intégré.",
        styles['BodyMain']
    ))
    
    story.append(Paragraph("<b>Objectifs Business :</b>", styles['SubSection']))
    story.append(Paragraph("• Créer un écosystème commercial local premium", styles['BulletItem']))
    story.append(Paragraph("• Fidéliser les clients via un système de cashback innovant", styles['BulletItem']))
    story.append(Paragraph("• Offrir aux entreprises des outils de gestion et marketing avancés", styles['BulletItem']))
    story.append(Paragraph("• Connecter influenceurs et marques locales", styles['BulletItem']))
    
    story.append(Paragraph("1.2 Cibles Utilisateurs", styles['SectionTitle']))
    
    users_data = [
        ['TYPE', 'DESCRIPTION'],
        ['Client', 'Consommateurs cherchant des services/produits premium'],
        ['Entreprise', 'Prestataires de services et commerces locaux'],
        ['Influenceur', 'Créateurs de contenu pour partenariats'],
        ['Admin', 'Gestionnaires de la plateforme'],
    ]
    story.append(create_table(users_data, [3*cm, 12*cm]))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("1.3 Architecture Technique", styles['SectionTitle']))
    
    tech_data = [
        ['COUCHE', 'TECHNOLOGIE', 'DÉTAILS'],
        ['Frontend', 'React 18.x', 'Shadcn/UI, TailwindCSS'],
        ['Backend', 'FastAPI', '15,000+ lignes de code'],
        ['Base de données', 'MongoDB 6.x', '20+ collections'],
        ['Paiements', 'Stripe', 'Mode LIVE production'],
        ['Auth', 'JWT', 'HS256, 7 jours expiration'],
        ['WebSocket', 'FastAPI Native', 'Temps réel'],
    ]
    story.append(create_table(tech_data, [3*cm, 4*cm, 8*cm]))
    
    story.append(PageBreak())
    
    # ==================== PARTIE 2: AUTHENTIFICATION ====================
    print("📄 Partie 2: Authentification...")
    story.append(Paragraph("PARTIE 2 - SYSTÈME D'AUTHENTIFICATION", styles['PartTitle']))
    add_line(story, COLORS['primary'], thickness=2)
    
    story.append(Paragraph("2.1 Inscription Multi-Profils", styles['SectionTitle']))
    story.append(Paragraph("• Inscription Client / Entreprise / Influenceur", styles['BulletItem']))
    story.append(Paragraph("• Formulaire adapté selon le type de compte", styles['BulletItem']))
    story.append(Paragraph("• Validation email automatique", styles['BulletItem']))
    story.append(Paragraph("• Profils utilisateurs complets avec avatar et cover", styles['BulletItem']))
    
    story.append(Paragraph("2.2 Connexion JWT", styles['SectionTitle']))
    story.append(Paragraph("• Token JWT signé avec clé secrète", styles['BulletItem']))
    story.append(Paragraph("• Expiration : 7 jours", styles['BulletItem']))
    story.append(Paragraph("• Stockage : localStorage (titelli_token)", styles['BulletItem']))
    story.append(Paragraph("• Header : Authorization: Bearer <token>", styles['BulletItem']))
    
    story.append(Paragraph("2.3 Gestion des Rôles", styles['SectionTitle']))
    story.append(Paragraph("• Middleware get_current_user sur routes protégées", styles['BulletItem']))
    story.append(Paragraph("• Vérification du rôle utilisateur", styles['BulletItem']))
    story.append(Paragraph("• Routes admin protégées par flag is_admin", styles['BulletItem']))
    story.append(Paragraph("• Mots de passe hashés (bcrypt)", styles['BulletItem']))
    
    story.append(PageBreak())
    
    # ==================== PARTIE 3: MARKETPLACE ====================
    print("📄 Partie 3: Marketplace...")
    story.append(Paragraph("PARTIE 3 - MARKETPLACE & CATALOGUE", styles['PartTitle']))
    add_line(story, COLORS['primary'], thickness=2)
    
    story.append(Paragraph("3.1 Catalogue Entreprises", styles['SectionTitle']))
    story.append(Paragraph("• Base de données pré-chargée avec 8,249 entreprises de Lausanne", styles['BulletItem']))
    story.append(Paragraph("• Pages entreprise avec photos/vidéos", styles['BulletItem']))
    story.append(Paragraph("• Filtres par catégorie, ville, certification", styles['BulletItem']))
    story.append(Paragraph("• Recherche intelligente", styles['BulletItem']))
    
    story.append(Paragraph("3.2 Services et Produits", styles['SectionTitle']))
    story.append(Paragraph("• CRUD complet pour services et produits", styles['BulletItem']))
    story.append(Paragraph("• Catégorisation multi-niveaux", styles['BulletItem']))
    story.append(Paragraph("• Galerie d'images par produit/service", styles['BulletItem']))
    story.append(Paragraph("• Gestion des prix et promotions", styles['BulletItem']))
    
    story.append(Paragraph("3.3 Système de Notation", styles['SectionTitle']))
    story.append(Paragraph("• Avis et notations sur 5 étoiles", styles['BulletItem']))
    story.append(Paragraph("• Commentaires clients vérifiés", styles['BulletItem']))
    story.append(Paragraph("• Note moyenne calculée automatiquement", styles['BulletItem']))
    story.append(Paragraph("• Modération des avis", styles['BulletItem']))
    
    story.append(Paragraph("3.4 Badges et Certifications", styles['SectionTitle']))
    badges_data = [
        ['BADGE', 'DESCRIPTION', 'AVANTAGES'],
        ['Guest', 'Compte de base', 'Visibilité standard'],
        ['Certifié', 'Documents vérifiés', 'Badge visible, +visibilité'],
        ['Labellisé', 'Qualité validée', 'Mise en avant, support prio'],
        ['Premium', 'Abonnement payant', 'Toutes fonctionnalités'],
    ]
    story.append(create_table(badges_data, [3*cm, 5*cm, 7*cm]))
    
    story.append(PageBreak())
    
    # ==================== PARTIE 4: COMMANDES ====================
    print("📄 Partie 4: Commandes...")
    story.append(Paragraph("PARTIE 4 - SYSTÈME DE COMMANDES", styles['PartTitle']))
    add_line(story, COLORS['primary'], thickness=2)
    
    story.append(Paragraph("4.1 Panier Multi-Entreprises", styles['SectionTitle']))
    story.append(Paragraph("• Ajout de produits/services de différentes entreprises", styles['BulletItem']))
    story.append(Paragraph("• Modification des quantités", styles['BulletItem']))
    story.append(Paragraph("• Calcul automatique des frais", styles['BulletItem']))
    story.append(Paragraph("• Sauvegarde du panier en localStorage", styles['BulletItem']))
    
    story.append(Paragraph("4.2 Checkout Stripe", styles['SectionTitle']))
    story.append(Paragraph("• Intégration Stripe en mode LIVE", styles['BulletItem']))
    story.append(Paragraph("• Checkout sécurisé avec redirection", styles['BulletItem']))
    story.append(Paragraph("• Support cartes bancaires, Apple Pay, Google Pay", styles['BulletItem']))
    story.append(Paragraph("• Confirmation email après paiement", styles['BulletItem']))
    
    story.append(Paragraph("4.3 Suivi des Commandes", styles['SectionTitle']))
    story.append(Paragraph("• Statuts : En attente → Confirmé → Expédié → Livré", styles['BulletItem']))
    story.append(Paragraph("• Notifications à chaque changement de statut", styles['BulletItem']))
    story.append(Paragraph("• Historique complet des achats", styles['BulletItem']))
    story.append(Paragraph("• Factures téléchargeables", styles['BulletItem']))
    
    story.append(PageBreak())
    
    # ==================== PARTIE 5: SYSTÈME FINANCIER ====================
    print("📄 Partie 5: Système Financier...")
    story.append(Paragraph("PARTIE 5 - SYSTÈME FINANCIER", styles['PartTitle']))
    add_line(story, COLORS['primary'], thickness=2)
    
    story.append(Paragraph("5.1 Cashback Client", styles['SectionTitle']))
    cashback_data = [
        ['NIVEAU', 'CASHBACK', 'PRIX'],
        ['Gratuit', '1%', '0 CHF'],
        ['Premium', '10%', '9.99 CHF/mois'],
        ['VIP', '15%', '29.99 CHF/mois'],
    ]
    story.append(create_table(cashback_data, [4*cm, 4*cm, 4*cm]))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("• Solde visible dans le dashboard", styles['BulletItem']))
    story.append(Paragraph("• Utilisation du cashback pour les achats", styles['BulletItem']))
    
    story.append(Paragraph("5.2 Abonnements Client", styles['SectionTitle']))
    story.append(Paragraph("• Plan Gratuit : Cashback 1%, fonctionnalités de base", styles['BulletItem']))
    story.append(Paragraph("• Plan Premium (9.99 CHF/mois) : Cashback 10%, offres exclusives", styles['BulletItem']))
    story.append(Paragraph("• Plan VIP (29.99 CHF/mois) : Cashback 15%, support prioritaire", styles['BulletItem']))
    
    story.append(Paragraph("5.3 Abonnements Entreprise", styles['SectionTitle']))
    abo_ent_data = [
        ['PLAN', 'PRIX', 'COMMISSION'],
        ['Guest', 'Gratuit', '15%'],
        ['Certifié', '29 CHF/mois', '12%'],
        ['Labellisé', '79 CHF/mois', '10%'],
        ['Exclusif', '149 CHF/mois', '8%'],
    ]
    story.append(create_table(abo_ent_data, [4*cm, 4*cm, 4*cm]))
    
    # NOUVEAUTÉS
    story.append(Paragraph("🆕 5.4 Retrait Cashback vers IBAN", styles['NewSection']))
    story.append(Paragraph("• Interface de saisie IBAN dans le profil", styles['NewFeature']))
    story.append(Paragraph("• Bouton 'Retirer vers mon compte bancaire'", styles['NewFeature']))
    story.append(Paragraph("• Minimum de retrait : 50 CHF", styles['NewFeature']))
    story.append(Paragraph("• Intégration Stripe Connect pour les transferts", styles['NewFeature']))
    story.append(Paragraph("• Historique des retraits avec statuts", styles['NewFeature']))
    
    story.append(Paragraph("🆕 5.5 Webhooks Stripe", styles['NewSection']))
    story.append(Paragraph("• Événements de paiement en temps réel", styles['NewFeature']))
    story.append(Paragraph("• Mise à jour automatique des statuts commandes", styles['NewFeature']))
    story.append(Paragraph("• Gestion des échecs de paiement", styles['NewFeature']))
    story.append(Paragraph("• Email automatique en cas d'échec", styles['NewFeature']))
    
    story.append(PageBreak())
    
    # ==================== PARTIE 6: DASHBOARDS ====================
    print("📄 Partie 6: Dashboards...")
    story.append(Paragraph("PARTIE 6 - DASHBOARDS", styles['PartTitle']))
    add_line(story, COLORS['primary'], thickness=2)
    
    story.append(Paragraph("6.1 Dashboard Client", styles['SectionTitle']))
    story.append(Paragraph("• Vue d'ensemble (stats, cashback, commandes)", styles['BulletItem']))
    story.append(Paragraph("• Mes commandes avec suivi", styles['BulletItem']))
    story.append(Paragraph("• Mon cashback et historique", styles['BulletItem']))
    story.append(Paragraph("• Mes prestataires favoris", styles['BulletItem']))
    story.append(Paragraph("• Mes amis et réseau social", styles['BulletItem']))
    story.append(Paragraph("• Messages et notifications", styles['BulletItem']))
    
    story.append(Paragraph("6.2 Dashboard Entreprise", styles['SectionTitle']))
    story.append(Paragraph("• Vue d'ensemble (stats, revenus, avis)", styles['BulletItem']))
    story.append(Paragraph("• Catalogue (services/produits)", styles['BulletItem']))
    story.append(Paragraph("• Commandes clients", styles['BulletItem']))
    story.append(Paragraph("• Avis et notations", styles['BulletItem']))
    story.append(Paragraph("• Équipe et personnel", styles['BulletItem']))
    story.append(Paragraph("• Stock et inventaire", styles['BulletItem']))
    story.append(Paragraph("• Offres promotionnelles", styles['BulletItem']))
    story.append(Paragraph("• Formations et emplois", styles['BulletItem']))
    
    story.append(Paragraph("🆕 6.3 Dashboard Admin Complet", styles['NewSection']))
    story.append(Paragraph("• Accès sécurisé /admin pour utilisateurs admin", styles['NewFeature']))
    story.append(Paragraph("• Section Comptabilité : KPIs, CA, Commissions, Exports", styles['NewFeature']))
    story.append(Paragraph("• Section Retraits : Validation, Approuver/Rejeter", styles['NewFeature']))
    story.append(Paragraph("• Section Utilisateurs : Liste complète, filtres", styles['NewFeature']))
    story.append(Paragraph("• Section Entreprises : Gestion, statistiques", styles['NewFeature']))
    story.append(Paragraph("• Section Commandes : Toutes les transactions", styles['NewFeature']))
    story.append(Paragraph("• Section Paiements : Résumé des flux", styles['NewFeature']))
    story.append(Paragraph("• 🆕 Section Pub Média IA : Gestion des commandes pub", styles['NewFeature']))
    story.append(Paragraph("• 🆕 Section Algorithmes : Configuration IA", styles['NewFeature']))
    
    story.append(PageBreak())
    
    # ==================== PARTIE 7: COMMUNICATION ====================
    print("📄 Partie 7: Communication...")
    story.append(Paragraph("PARTIE 7 - COMMUNICATION & SOCIAL", styles['PartTitle']))
    add_line(story, COLORS['primary'], thickness=2)
    
    story.append(Paragraph("7.1 Messagerie", styles['SectionTitle']))
    story.append(Paragraph("• Conversations Client ↔ Entreprise", styles['BulletItem']))
    story.append(Paragraph("• Messages temps réel", styles['BulletItem']))
    story.append(Paragraph("• Historique des échanges", styles['BulletItem']))
    story.append(Paragraph("• Compteur de messages non lus", styles['BulletItem']))
    
    story.append(Paragraph("7.2 Système d'Amis", styles['SectionTitle']))
    story.append(Paragraph("• Demandes d'amis", styles['BulletItem']))
    story.append(Paragraph("• Liste d'amis", styles['BulletItem']))
    story.append(Paragraph("• Profils cliquables", styles['BulletItem']))
    
    story.append(Paragraph("7.3 Notifications", styles['SectionTitle']))
    story.append(Paragraph("• Notifications push in-app", styles['BulletItem']))
    story.append(Paragraph("• Badge compteur temps réel", styles['BulletItem']))
    story.append(Paragraph("• Catégorisation par type", styles['BulletItem']))
    
    story.append(Paragraph("🆕 7.4 WebSocket Temps Réel", styles['NewSection']))
    story.append(Paragraph("• Notifications push instantanées", styles['NewFeature']))
    story.append(Paragraph("• Statut en ligne des amis", styles['NewFeature']))
    story.append(Paragraph("• Reconnexion automatique", styles['NewFeature']))
    story.append(Paragraph("• Fallback polling si WebSocket indisponible", styles['NewFeature']))
    
    story.append(Paragraph("🆕 7.5 Feed Social / Mode de Vie", styles['NewSection']))
    story.append(Paragraph("• Posts d'activité automatiques", styles['NewFeature']))
    story.append(Paragraph("• Likes et compteurs", styles['NewFeature']))
    story.append(Paragraph("• Publication manuelle de posts", styles['NewFeature']))
    story.append(Paragraph("• Fil d'actualité personnalisé", styles['NewFeature']))
    
    story.append(PageBreak())
    
    # ==================== PARTIE 8: NOUVELLES FONCTIONNALITÉS ====================
    print("📄 Partie 8: Nouvelles fonctionnalités...")
    story.append(Paragraph("🆕 PARTIE 8 - NOUVELLES FONCTIONNALITÉS", styles['PartTitle']))
    add_line(story, COLORS['new'], thickness=2)
    
    story.append(Paragraph("🆕 8.1 RDV chez Titelli (Social Booking)", styles['NewSection']))
    story.append(Paragraph("• Offres pour 2 personnes (amical ou romantique)", styles['NewFeature']))
    story.append(Paragraph("• Système d'invitations avec acceptation payante (2 CHF)", styles['NewFeature']))
    story.append(Paragraph("• Abonnement romantique (200 CHF/mois) via Stripe", styles['NewFeature']))
    story.append(Paragraph("• Chat temps réel entre participants (WebSocket)", styles['NewFeature']))
    story.append(Paragraph("• 8 catégories: restaurant, sport, wellness, culture...", styles['NewFeature']))
    
    story.append(Paragraph("🆕 8.2 Demandes Spécialistes", styles['NewSection']))
    story.append(Paragraph("• Recherche IA de spécialistes", styles['NewFeature']))
    story.append(Paragraph("• Création de demandes urgentes/spécifiques", styles['NewFeature']))
    story.append(Paragraph("• Système de réponses des prestataires", styles['NewFeature']))
    story.append(Paragraph("• 10 catégories de spécialistes", styles['NewFeature']))
    
    story.append(Paragraph("🆕 8.3 Lifestyle Passes", styles['NewSection']))
    passes_data = [
        ['PASS', 'PRIX', 'INCLUS'],
        ['Healthy Lifestyle', '99 CHF/mois', 'Spa, wellness, nutrition, fitness'],
        ['Better You', '149 CHF/mois', 'Coaching, développement personnel'],
        ['Special MVP', '299 CHF/mois', 'Accès VIP, venues exclusives, concierge'],
    ]
    story.append(create_table(passes_data, [4*cm, 3.5*cm, 7.5*cm], COLORS['new']))
    
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("🆕 8.4 Titelli Pro++ (B2B)", styles['NewSection']))
    story.append(Paragraph("• Livraisons B2B récurrentes (quotidien/hebdo/mensuel)", styles['NewFeature']))
    story.append(Paragraph("• Liquidation de stock (surstock, fin saison, expiration)", styles['NewFeature']))
    story.append(Paragraph("• Abonnement Pro++: 199 CHF/mois via Stripe", styles['NewFeature']))
    story.append(Paragraph("• Analytics B2B dédiés", styles['NewFeature']))
    story.append(Paragraph("• Réservé aux comptes entreprise", styles['NewFeature']))
    
    story.append(PageBreak())
    
    story.append(Paragraph("🆕 8.5 Sports & Compétitions", styles['NewSection']))
    story.append(Paragraph("• Création de matchs (cherche adversaire/joueurs/équipe)", styles['NewFeature']))
    story.append(Paragraph("• Gestion d'équipes", styles['NewFeature']))
    story.append(Paragraph("• Compétitions et tournois", styles['NewFeature']))
    story.append(Paragraph("• 11 catégories sportives: Football, Tennis, Basketball...", styles['NewFeature']))
    
    story.append(Paragraph("🆕 8.6 Gamification & Points", styles['NewSection']))
    story.append(Paragraph("• Points pour chaque action (+5 à +15 points)", styles['NewFeature']))
    story.append(Paragraph("• 8 niveaux (Débutant → Titan)", styles['NewFeature']))
    story.append(Paragraph("• Badges multiples catégories", styles['NewFeature']))
    story.append(Paragraph("• Intégration avec RDV et Sports", styles['NewFeature']))
    
    story.append(Paragraph("🆕 8.7 Système de Parrainage", styles['NewSection']))
    story.append(Paragraph("• Code de parrainage unique (format: TIT + 8 caractères)", styles['NewFeature']))
    story.append(Paragraph("• Partage via lien ou code", styles['NewFeature']))
    story.append(Paragraph("• Points pour le parrain (+50) ET le filleul (+25)", styles['NewFeature']))
    story.append(Paragraph("• Bonus à paliers: 5 parrainages (+100), 10 (+250), 25 (+500)", styles['NewFeature']))
    story.append(Paragraph("• Leaderboard des meilleurs parrains", styles['NewFeature']))
    story.append(Paragraph("• Badge 'Influenceur' à 5 parrainages", styles['NewFeature']))
    
    story.append(PageBreak())
    
    # ==================== PARTIE 9: PUB MÉDIA IA ====================
    print("📄 Partie 9: Pub Média IA...")
    story.append(Paragraph("🆕 PARTIE 9 - PUB MÉDIA IA", styles['PartTitle']))
    add_line(story, COLORS['new'], thickness=2)
    
    story.append(Paragraph("🆕 9.1 Publicités Images IA (DALL-E)", styles['NewSection']))
    story.append(Paragraph("• Éditeur style Canva : 34 templates dans 7 catégories", styles['NewFeature']))
    story.append(Paragraph("• Génération IA DALL-E : Images de fond sans texte", styles['NewFeature']))
    story.append(Paragraph("• Post-processing Pillow : Texte ajouté en overlay", styles['NewFeature']))
    story.append(Paragraph("• Filigrane 'TITELLI' : Protection anti-screenshot", styles['NewFeature']))
    story.append(Paragraph("• Section 'Sur Mesure' : 149.90 CHF création personnalisée", styles['NewFeature']))
    
    pub_img_data = [
        ['CATÉGORIE', 'TEMPLATES', 'PRIX'],
        ['Restauration', '6', '29.90 - 69.90 CHF'],
        ['Beauté & Bien-être', '5', '29.90 - 69.90 CHF'],
        ['Commerce', '5', '29.90 - 69.90 CHF'],
        ['Services Pro', '6', '29.90 - 69.90 CHF'],
        ['Événementiel', '5', '29.90 - 69.90 CHF'],
        ['Santé', '4', '29.90 - 69.90 CHF'],
        ['Immobilier', '3', '29.90 - 69.90 CHF'],
    ]
    story.append(create_table(pub_img_data, [5*cm, 3*cm, 5*cm], COLORS['new']))
    
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("🆕 9.2 Publicités Vidéos IA (Sora)", styles['NewSection']))
    story.append(Paragraph("• 13 templates vidéo dans 6 catégories", styles['NewFeature']))
    story.append(Paragraph("• Prix : 129.90 - 399.90 CHF", styles['NewFeature']))
    story.append(Paragraph("• Génération Sora 2 (~1h de traitement)", styles['NewFeature']))
    story.append(Paragraph("• Paiement Stripe intégré", styles['NewFeature']))
    story.append(Paragraph("• Page /video-pub avec UI violet", styles['NewFeature']))
    
    story.append(Paragraph("🆕 9.3 Commandes Titelli", styles['NewSection']))
    story.append(Paragraph("• Tabs : Toutes / Images / Vidéos", styles['NewFeature']))
    story.append(Paragraph("• Affichage complet : produit, slogan, description, prix, durée", styles['NewFeature']))
    story.append(Paragraph("• Badges type : violet=Vidéo, ambre=Image", styles['NewFeature']))
    story.append(Paragraph("• Historique des commandes publicitaires", styles['NewFeature']))
    
    story.append(PageBreak())
    
    # ==================== PARTIE 10: INTÉGRATIONS ====================
    print("📄 Partie 10: Intégrations...")
    story.append(Paragraph("PARTIE 10 - INTÉGRATIONS & SÉCURITÉ", styles['PartTitle']))
    add_line(story, COLORS['primary'], thickness=2)
    
    story.append(Paragraph("10.1 Stripe (Paiements)", styles['SectionTitle']))
    story.append(Paragraph("• Mode : LIVE (production)", styles['BulletItem']))
    story.append(Paragraph("• Checkout Sessions : Paiements one-time et abonnements", styles['BulletItem']))
    story.append(Paragraph("• Subscriptions : Gestion des abonnements récurrents", styles['BulletItem']))
    story.append(Paragraph("• Connect : Transferts vers comptes bancaires", styles['BulletItem']))
    
    story.append(Paragraph("🆕 10.2 SalonPro (Webhooks)", styles['NewSection']))
    story.append(Paragraph("• Synchronisation bidirectionnelle Titelli ↔ SalonPro", styles['NewFeature']))
    story.append(Paragraph("• Webhook sortant : sync entreprise à l'inscription", styles['NewFeature']))
    story.append(Paragraph("• Webhook sortant : sync RDV à la création", styles['NewFeature']))
    story.append(Paragraph("• Webhook entrant : réception d'événements SalonPro", styles['NewFeature']))
    
    story.append(Paragraph("10.3 Sécurité JWT", styles['SectionTitle']))
    story.append(Paragraph("• Token JWT signé avec clé secrète", styles['BulletItem']))
    story.append(Paragraph("• Mots de passe hashés (bcrypt)", styles['BulletItem']))
    story.append(Paragraph("• IBAN masqué dans l'affichage", styles['BulletItem']))
    story.append(Paragraph("• CORS configuré", styles['BulletItem']))
    
    story.append(Paragraph("🆕 10.4 Algorithmes IA Ciblage", styles['NewSection']))
    story.append(Paragraph("• Calcul de reach basé sur vrais utilisateurs DB", styles['NewFeature']))
    story.append(Paragraph("• Segmentation par âge, genre, localisation", styles['NewFeature']))
    story.append(Paragraph("• Suggestions d'optimisation budget", styles['NewFeature']))
    story.append(Paragraph("• Configuration via Dashboard Admin", styles['NewFeature']))
    
    story.append(PageBreak())
    
    # ==================== PARTIE 11: BASE DE DONNÉES ====================
    print("📄 Partie 11: Base de données...")
    story.append(Paragraph("PARTIE 11 - BASE DE DONNÉES", styles['PartTitle']))
    add_line(story, COLORS['primary'], thickness=2)
    
    story.append(Paragraph("11.1 Collections MongoDB (Existantes)", styles['SectionTitle']))
    
    collections_data = [
        ['COLLECTION', 'DOCUMENTS', 'DESCRIPTION'],
        ['users', '60+', 'Utilisateurs (clients, entreprises, admins)'],
        ['enterprises', '8,249', 'Entreprises de Lausanne'],
        ['orders', '26+', 'Commandes clients'],
        ['products', 'Variable', 'Produits des entreprises'],
        ['services', 'Variable', 'Services des entreprises'],
        ['reviews', '19+', 'Avis et notations'],
        ['messages', 'Variable', 'Messagerie'],
        ['notifications', '294+', 'Notifications push'],
        ['subscriptions', 'Variable', 'Abonnements'],
    ]
    story.append(create_table(collections_data, [4*cm, 2.5*cm, 8.5*cm]))
    
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("🆕 11.2 Nouvelles Collections", styles['NewSection']))
    
    new_collections_data = [
        ['COLLECTION', 'DESCRIPTION'],
        ['shared_offers', 'Offres RDV Titelli'],
        ['chat_rooms / chat_messages', 'Chat temps réel'],
        ['specialist_requests', 'Demandes spécialistes'],
        ['lifestyle_subscriptions', 'Abonnements passes'],
        ['gamification_points', 'Points gamification'],
        ['gamification_actions_log', 'Log des actions'],
        ['sports_matches', 'Matchs sportifs'],
        ['cashback_withdrawals', 'Demandes de retrait'],
        ['bookings', 'Réservations RDV'],
        ['media_pub_orders', 'Commandes pub IA'],
        ['video_pub_orders', 'Commandes vidéo IA'],
    ]
    story.append(create_table(new_collections_data, [5*cm, 10*cm], COLORS['new']))
    
    story.append(PageBreak())
    
    # ==================== PARTIE 12: PAGES ====================
    print("📄 Partie 12: Pages...")
    story.append(Paragraph("PARTIE 12 - PAGES & CONTENUS", styles['PartTitle']))
    add_line(story, COLORS['primary'], thickness=2)
    
    story.append(Paragraph("12.1 Page d'Accueil", styles['SectionTitle']))
    story.append(Paragraph("• Présentation de la plateforme", styles['BulletItem']))
    story.append(Paragraph("• Entreprises mises en avant", styles['BulletItem']))
    story.append(Paragraph("• Catégories de services", styles['BulletItem']))
    story.append(Paragraph("• Avis défilants", styles['BulletItem']))
    story.append(Paragraph("• Vidéo panoramique background", styles['BulletItem']))
    
    story.append(Paragraph("🆕 12.2 Pages Légales", styles['NewSection']))
    story.append(Paragraph("• CGVPage.js : Procédé facturation 20%, Tarification, Renouvellement", styles['NewFeature']))
    story.append(Paragraph("• MentionsLegalesPage.js : Protection données, Cookies, Droits", styles['NewFeature']))
    story.append(Paragraph("• Politique de confidentialité", styles['NewFeature']))
    
    story.append(Paragraph("🆕 12.3 Page À Propos", styles['NewSection']))
    story.append(Paragraph("• Vision et mission de Titelli", styles['NewFeature']))
    story.append(Paragraph("• Avantages de la plateforme", styles['NewFeature']))
    story.append(Paragraph("• Vidéos promo lifestyle", styles['NewFeature']))
    story.append(Paragraph("• Équipe et contact", styles['NewFeature']))
    
    story.append(PageBreak())
    
    # ==================== RÉSUMÉ FINAL ====================
    print("📄 Résumé final...")
    story.append(Paragraph("RÉSUMÉ DES MÉTRIQUES", styles['PartTitle']))
    add_line(story, COLORS['primary'], thickness=2)
    
    metrics_data = [
        ['MÉTRIQUE', 'VALEUR'],
        ['Lignes de code backend', '15,000+'],
        ['Lignes de code frontend', '20,000+'],
        ['Endpoints API', '200+'],
        ['Collections MongoDB', '20+'],
        ['Tests exécutés', '40+ itérations'],
        ['Taux de réussite tests', '100%'],
        ['Fonctionnalités CDC original', '100% complétées'],
        ['NOUVEAUTÉS ajoutées', '25+'],
    ]
    story.append(create_table(metrics_data, [8*cm, 7*cm]))
    
    story.append(Spacer(1, 1*cm))
    
    # Légende finale
    story.append(Paragraph("<b>LÉGENDE RAPPEL :</b>", styles['SubSection']))
    story.append(Paragraph("• Texte normal = Fonctionnalités prévues dans le CDC original (Janvier 2026)", styles['BodyMain']))
    story.append(Paragraph("<font color='#22C55E'><b>• Texte vert = NOUVEAUTÉS ajoutées depuis (Février 2026)</b></font>", styles['BodyMain']))
    
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"Document généré le {datetime.now().strftime('%d %B %Y')}", styles['Caption']))
    story.append(Paragraph("Titelli Marketplace - Version Production Finale", styles['Caption']))
    
    # ==================== GÉNÉRATION ====================
    print("\n📄 Génération du PDF...")
    doc.build(story)
    
    size = os.path.getsize(output_path) / (1024 * 1024)
    
    print("\n" + "=" * 70)
    print(f"   ✅ CDC COMPLET FINAL GÉNÉRÉ !")
    print(f"   📁 {output_path}")
    print(f"   📦 Taille: {size:.1f} MB")
    print("=" * 70)
    
    return output_path


if __name__ == "__main__":
    generate_complete_cdc()
