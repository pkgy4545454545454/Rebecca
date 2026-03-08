#!/usr/bin/env python3
"""
Brochure Titelli V3 - VERSION CLIENT - Mise en page PREMIUM
Design professionnel et moderne pour les utilisateurs
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

SCREENSHOTS_DIR = '/app/backend/uploads/brochure_client_screenshots'
OUTPUT_DIR = '/app/backend/uploads'

# Palette de couleurs - Version Client (plus chaleureuse)
COLORS = {
    'primary': colors.Color(147/255, 51/255, 234/255),    # Violet
    'secondary': colors.Color(0/255, 71/255, 171/255),    # Bleu
    'accent': colors.Color(255/255, 193/255, 7/255),      # Or
    'success': colors.Color(34/255, 197/255, 94/255),     # Vert
    'pink': colors.Color(236/255, 72/255, 153/255),       # Rose
    'dark': colors.Color(15/255, 15/255, 20/255),
    'light': colors.Color(248/255, 250/255, 252/255),
    'gray': colors.Color(100/255, 116/255, 139/255),
}


def create_professional_styles():
    """Crée des styles professionnels"""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='CoverMain',
        fontSize=56,
        textColor=COLORS['primary'],
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=60,
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
        fontSize=28,
        textColor=COLORS['primary'],
        fontName='Helvetica-Bold',
        spaceBefore=0,
        spaceAfter=20,
        leading=32
    ))
    
    styles.add(ParagraphStyle(
        name='SectionSub',
        fontSize=18,
        textColor=COLORS['dark'],
        fontName='Helvetica-Bold',
        spaceBefore=20,
        spaceAfter=12,
        leading=22
    ))
    
    styles.add(ParagraphStyle(
        name='SectionNumber',
        fontSize=12,
        textColor=COLORS['pink'],
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
        name='TipBox',
        fontSize=10,
        textColor=COLORS['primary'],
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


def add_horizontal_line(story, color=None, width=17*cm, thickness=1):
    """Ajoute une ligne horizontale"""
    if color is None:
        color = COLORS['light']
    story.append(Spacer(1, 5))
    story.append(HRFlowable(width=width, thickness=thickness, color=color, spaceBefore=5, spaceAfter=10))


def add_image_with_frame(story, image_path, caption="", width=14*cm, max_height=10*cm, styles=None):
    """Ajoute une image avec cadre"""
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
        print(f"   ❌ Erreur: {e}")
        return False


def create_feature_box(story, title, items, styles):
    """Crée une boîte de fonctionnalités"""
    content = []
    content.append(Paragraph(f"<b>{title}</b>", styles['FeatureTitle']))
    for item in items:
        content.append(Paragraph(f"• {item}", styles['BulletPoint']))
    
    data = [[content[0]]]
    for c in content[1:]:
        data.append([c])
    
    table = Table(data, colWidths=[15*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.Color(250/255, 245/255, 255/255)),
        ('BOX', (0, 0), (-1, -1), 1, COLORS['primary']),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 15))


def create_tip_box(story, tip_text, styles):
    """Crée une boîte de conseil"""
    tip_content = f"💡 <b>Astuce</b> : {tip_text}"
    
    data = [[Paragraph(tip_content, styles['TipBox'])]]
    table = Table(data, colWidths=[15*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.Color(250/255, 240/255, 255/255)),
        ('BOX', (0, 0), (-1, -1), 2, COLORS['primary']),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 15))


def create_section_header(story, number, title, styles):
    """Crée un en-tête de section"""
    story.append(Paragraph(number, styles['SectionNumber']))
    story.append(Paragraph(title, styles['SectionMain']))
    add_horizontal_line(story, COLORS['primary'], thickness=2)


def create_subsection_header(story, title, styles):
    """Crée un sous-titre"""
    story.append(Spacer(1, 10))
    story.append(Paragraph(title, styles['SectionSub']))
    add_horizontal_line(story, COLORS['light'], thickness=1)


def generate_client_premium_brochure():
    """Génère la brochure client premium"""
    print("=" * 70)
    print("   GÉNÉRATION BROCHURE PREMIUM - CLIENT")
    print("=" * 70)
    
    output_path = f'{OUTPUT_DIR}/TITELLI_BROCHURE_CLIENT_PREMIUM.pdf'
    
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
    
    # ==================== COUVERTURE ====================
    print("📄 Couverture...")
    story.append(Spacer(1, 5*cm))
    story.append(Paragraph("TITELLI", styles['CoverMain']))
    story.append(Spacer(1, 0.5*cm))
    add_horizontal_line(story, COLORS['accent'], width=8*cm, thickness=3)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("GUIDE UTILISATEUR", styles['CoverSub']))
    story.append(Paragraph("Tout ce que vous pouvez faire sur Titelli", styles['CoverSub']))
    story.append(Spacer(1, 1.5*cm))
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/accueil.png', "", width=13*cm, max_height=8*cm, styles=styles)
    
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"Version {datetime.now().strftime('%B %Y')}", styles['CoverSub']))
    story.append(PageBreak())
    
    # ==================== TABLE DES MATIÈRES ====================
    print("📄 Table des matières...")
    story.append(Paragraph("TABLE DES MATIÈRES", styles['SectionMain']))
    add_horizontal_line(story, COLORS['primary'], thickness=2)
    story.append(Spacer(1, 0.5*cm))
    
    toc_data = [
        ("01", "DÉCOUVRIR TITELLI", ["Présentation", "Naviguer sur le site"]),
        ("02", "CRÉER SON COMPTE", ["S'inscrire", "Compléter son profil"]),
        ("03", "VOTRE ESPACE", ["Dashboard", "Mon Profil", "Mon mode de vie"]),
        ("04", "VOS AVANTAGES", ["Cash-back", "Parrainage", "Premium"]),
        ("05", "COMMANDER", ["Passer une commande", "Suivre ses commandes"]),
        ("06", "GÉRER SON COMPTE", ["Agenda", "Cartes", "Documents"]),
        ("07", "COMMUNIQUER", ["Messagerie", "Contacts"]),
        ("08", "AIDE", ["Support", "Paramètres"]),
    ]
    
    for num, title, items in toc_data:
        num_para = Paragraph(f"<font color='#EC4899'><b>{num}</b></font>  {title}", styles['TOCTitle'])
        story.append(num_para)
        for item in items:
            story.append(Paragraph(f"• {item}", styles['TOCItem']))
    
    story.append(PageBreak())
    
    # ==================== PARTIE 1: DÉCOUVRIR ====================
    print("📄 Partie 1...")
    create_section_header(story, "PARTIE 01", "DÉCOUVRIR TITELLI", styles)
    
    story.append(Paragraph(
        "Titelli est une plateforme suisse qui vous permet de découvrir et réserver les meilleurs "
        "services près de chez vous. Profitez de cashback sur vos achats, d'offres exclusives "
        "et d'une expérience simplifiée.",
        styles['BodyMain']
    ))
    story.append(Spacer(1, 0.3*cm))
    
    create_feature_box(story, "Vos avantages en tant que client :", [
        "Trouvez facilement des prestataires de qualité",
        "Profitez de cashback sur vos achats",
        "Accédez à des offres exclusives",
        "Gérez vos rendez-vous en un clic",
        "Parrainez vos amis et gagnez des récompenses"
    ], styles)
    
    create_subsection_header(story, "Naviguer sur le site", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/accueil.png',
                         "Page d'accueil Titelli", width=14*cm, max_height=8*cm, styles=styles)
    
    story.append(PageBreak())
    
    # ==================== PARTIE 2: INSCRIPTION ====================
    print("📄 Partie 2...")
    create_section_header(story, "PARTIE 02", "CRÉER SON COMPTE", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/connexion.png',
                         "Page de connexion et d'inscription", width=12*cm, max_height=8*cm, styles=styles)
    
    create_subsection_header(story, "Étapes d'inscription", styles)
    
    steps = [
        "Cliquez sur 'Connexion' en haut à droite",
        "Sélectionnez 'S'inscrire'",
        "Choisissez 'Client' comme type de compte",
        "Entrez votre email et créez un mot de passe",
        "Renseignez vos informations personnelles",
        "Validez et c'est parti !"
    ]
    
    for i, step in enumerate(steps, 1):
        story.append(Paragraph(f"<b>{i}.</b> ➜ {step}", styles['BulletPoint']))
    
    create_tip_box(story,
        "Utilisez un email que vous consultez régulièrement pour ne pas manquer les offres exclusives.", styles)
    
    story.append(PageBreak())
    
    # ==================== PARTIE 3: ESPACE PERSONNEL ====================
    print("📄 Partie 3...")
    create_section_header(story, "PARTIE 03", "VOTRE ESPACE PERSONNEL", styles)
    
    story.append(Paragraph(
        "Votre dashboard est votre espace personnel pour gérer toutes vos activités sur Titelli.",
        styles['BodyMain']
    ))
    story.append(Spacer(1, 0.3*cm))
    
    # Accueil
    create_subsection_header(story, "Accueil du Dashboard", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/client_accueil.png',
                         "Votre tableau de bord personnel", width=14*cm, max_height=8*cm, styles=styles)
    
    create_feature_box(story, "Ce que vous y trouvez :", [
        "Votre solde de cashback",
        "Vos dernières commandes",
        "Les offres personnalisées",
        "Vos statistiques"
    ], styles)
    
    story.append(PageBreak())
    
    # Profil
    create_subsection_header(story, "Mon Profil", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/client_profil.png',
                         "Gestion de votre profil", width=14*cm, max_height=8*cm, styles=styles)
    
    create_tip_box(story,
        "Un profil complet vous permet de recevoir des offres personnalisées adaptées à vos goûts.", styles)
    
    story.append(PageBreak())
    
    # ==================== PARTIE 4: AVANTAGES ====================
    print("📄 Partie 4...")
    create_section_header(story, "PARTIE 04", "VOS AVANTAGES", styles)
    
    story.append(Paragraph(
        "En tant que client Titelli, vous bénéficiez de nombreux avantages exclusifs.",
        styles['BodyMain']
    ))
    story.append(Spacer(1, 0.3*cm))
    
    # Cashback
    create_subsection_header(story, "Le Cash-back", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/client_cashback.png',
                         "Votre espace Cash-back", width=14*cm, max_height=8*cm, styles=styles)
    
    story.append(Paragraph(
        "Gagnez du cashback sur chaque achat effectué sur Titelli ! L'argent est crédité "
        "sur votre compte et peut être utilisé pour vos prochains achats.",
        styles['BodyMain']
    ))
    
    create_feature_box(story, "Comment ça marche :", [
        "Achetez chez un prestataire Titelli",
        "Le cashback est automatiquement crédité",
        "Utilisez-le lors de votre prochain achat"
    ], styles)
    
    story.append(PageBreak())
    
    # Parrainage
    create_subsection_header(story, "Le Parrainage", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/client_parrainage.png',
                         "Programme de parrainage", width=14*cm, max_height=8*cm, styles=styles)
    
    create_tip_box(story,
        "Plus vous parrainez, plus vous gagnez ! Partagez sur vos réseaux sociaux.", styles)
    
    story.append(PageBreak())
    
    # Premium
    create_subsection_header(story, "Premium Titelli", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/client_premium.png',
                         "Avantages Premium", width=14*cm, max_height=8*cm, styles=styles)
    
    create_feature_box(story, "Avantages Premium :", [
        "Cashback augmenté sur tous les achats",
        "Accès aux offres exclusives",
        "Support client prioritaire",
        "Invitations aux événements VIP"
    ], styles)
    
    story.append(PageBreak())
    
    # ==================== PARTIE 5: COMMANDER ====================
    print("📄 Partie 5...")
    create_section_header(story, "PARTIE 05", "COMMANDER", styles)
    
    story.append(Paragraph(
        "Commander sur Titelli est simple et rapide. Trouvez, réservez et payez en quelques clics.",
        styles['BodyMain']
    ))
    story.append(Spacer(1, 0.3*cm))
    
    # Commandes
    create_subsection_header(story, "Suivre vos Commandes", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/client_commandes.png',
                         "Historique des commandes", width=14*cm, max_height=8*cm, styles=styles)
    
    create_feature_box(story, "Fonctionnalités :", [
        "Voir toutes vos commandes passées",
        "Suivre le statut en temps réel",
        "Contacter le prestataire directement",
        "Laisser un avis après le service"
    ], styles)
    
    story.append(PageBreak())
    
    # ==================== PARTIE 6: GESTION ====================
    print("📄 Partie 6...")
    create_section_header(story, "PARTIE 06", "GÉRER VOTRE COMPTE", styles)
    
    # Agenda
    create_subsection_header(story, "Mon Agenda", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/client_agenda.png',
                         "Votre agenda personnel", width=14*cm, max_height=8*cm, styles=styles)
    
    create_feature_box(story, "Ce que vous pouvez faire :", [
        "Voir tous vos rendez-vous",
        "Ajouter des événements personnels",
        "Recevoir des rappels",
        "Synchroniser avec votre calendrier"
    ], styles)
    
    story.append(PageBreak())
    
    # Cartes
    create_subsection_header(story, "Mes Cartes", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/client_cartes.png',
                         "Gestion des moyens de paiement", width=14*cm, max_height=8*cm, styles=styles)
    
    create_tip_box(story,
        "Vos données bancaires sont sécurisées et cryptées. Titelli ne stocke jamais vos numéros complets.", styles)
    
    story.append(PageBreak())
    
    # ==================== PARTIE 7: COMMUNICATION ====================
    print("📄 Partie 7...")
    create_section_header(story, "PARTIE 07", "COMMUNIQUER", styles)
    
    # Messagerie
    create_subsection_header(story, "Messagerie", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/client_messages.png',
                         "Messagerie intégrée", width=14*cm, max_height=8*cm, styles=styles)
    
    create_feature_box(story, "Fonctionnalités :", [
        "Envoyer des messages aux prestataires",
        "Recevoir des réponses en temps réel",
        "Partager des photos ou fichiers",
        "Historique des conversations"
    ], styles)
    
    story.append(PageBreak())
    
    # Contacts
    create_subsection_header(story, "Contacts et Amis", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/client_contacts.png',
                         "Gestion des contacts", width=14*cm, max_height=8*cm, styles=styles)
    
    story.append(PageBreak())
    
    # ==================== PARTIE 8: AIDE ====================
    print("📄 Partie 8...")
    create_section_header(story, "PARTIE 08", "AIDE & SUPPORT", styles)
    
    # Support
    create_subsection_header(story, "Service Client", styles)
    
    add_image_with_frame(story, f'{SCREENSHOTS_DIR}/client_support.png',
                         "Support client", width=14*cm, max_height=8*cm, styles=styles)
    
    create_feature_box(story, "Comment nous contacter :", [
        "Chat en direct avec le support",
        "FAQ complète",
        "Email de contact",
        "Aide personnalisée"
    ], styles)
    
    create_tip_box(story,
        "La FAQ répond à 80% des questions. Consultez-la d'abord pour une réponse immédiate !", styles)
    
    story.append(PageBreak())
    
    # ==================== PAGE FINALE ====================
    print("📄 Page finale...")
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("BIENVENUE SUR TITELLI !", styles['SectionMain']))
    add_horizontal_line(story, COLORS['accent'], width=10*cm, thickness=3)
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Nous espérons que ce guide vous aidera à profiter pleinement de tous les avantages "
        "offerts par Titelli. Notre équipe est à votre disposition pour toute question.",
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
        ('BACKGROUND', (0, 0), (-1, -1), colors.Color(250/255, 245/255, 255/255)),
        ('BOX', (0, 0), (-1, -1), 2, COLORS['primary']),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    
    story.append(contact_table)
    
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        "Profitez de vos avantages et découvrez les meilleurs prestataires près de chez vous !",
        styles['CoverSub']
    ))
    
    # ==================== GÉNÉRATION ====================
    print("\n📄 Génération du PDF...")
    doc.build(story)
    
    size = os.path.getsize(output_path) / (1024 * 1024)
    
    print("\n" + "=" * 70)
    print(f"   ✅ BROCHURE CLIENT PREMIUM GÉNÉRÉE !")
    print(f"   📁 {output_path}")
    print(f"   📦 Taille: {size:.1f} MB")
    print("=" * 70)
    
    return output_path


if __name__ == "__main__":
    generate_client_premium_brochure()
