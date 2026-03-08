#!/usr/bin/env python3
"""
Génération de la Brochure Titelli - VERSION CLIENT
Guide complet pour les utilisateurs/clients de Titelli
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
    Table, TableStyle, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

SCREENSHOTS_DIR = '/app/backend/uploads/brochure_client_screenshots'
OUTPUT_DIR = '/app/backend/uploads'

# Couleurs Titelli
TITELLI_BLUE = colors.Color(0, 71/255, 171/255)
TITELLI_PURPLE = colors.Color(147/255, 51/255, 234/255)
TITELLI_GREEN = colors.Color(34/255, 197/255, 94/255)

def create_styles():
    """Crée les styles personnalisés"""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='CoverTitle',
        fontSize=42,
        textColor=TITELLI_PURPLE,
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='CoverSubtitle',
        fontSize=20,
        textColor=colors.gray,
        spaceAfter=15,
        alignment=TA_CENTER,
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        name='SectionTitle',
        fontSize=24,
        textColor=TITELLI_PURPLE,
        spaceBefore=0,
        spaceAfter=15,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='SubTitle',
        fontSize=16,
        textColor=colors.black,
        spaceBefore=15,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='Body',
        fontSize=11,
        textColor=colors.black,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        fontName='Helvetica',
        leading=14
    ))
    
    styles.add(ParagraphStyle(
        name='BulletItem',
        fontSize=11,
        textColor=colors.black,
        leftIndent=15,
        spaceAfter=4,
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        name='Tip',
        fontSize=10,
        textColor=TITELLI_PURPLE,
        leftIndent=10,
        rightIndent=10,
        spaceBefore=10,
        spaceAfter=10,
        fontName='Helvetica-Oblique',
        backColor=colors.Color(0.97, 0.95, 1.0),
        borderWidth=1,
        borderColor=TITELLI_PURPLE,
        borderPadding=8
    ))
    
    styles.add(ParagraphStyle(
        name='Feature',
        fontSize=12,
        textColor=TITELLI_GREEN,
        spaceBefore=5,
        spaceAfter=3,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='Caption',
        fontSize=9,
        textColor=colors.gray,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    ))
    
    styles.add(ParagraphStyle(
        name='TOCItem',
        fontSize=12,
        textColor=colors.black,
        spaceBefore=8,
        spaceAfter=4,
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        name='TOCSection',
        fontSize=14,
        textColor=TITELLI_PURPLE,
        spaceBefore=15,
        spaceAfter=5,
        fontName='Helvetica-Bold'
    ))
    
    return styles


def add_image(story, image_path, caption="", width=15*cm, max_height=12*cm, styles=None):
    """Ajoute une image avec gestion de la taille"""
    if not os.path.exists(image_path):
        print(f"   ⚠️ Image non trouvée: {image_path}")
        return False
    
    try:
        img = Image.open(image_path)
        aspect = img.height / img.width
        height = width * aspect
        
        if height > max_height:
            height = max_height
            width = height / aspect
        
        img_flowable = RLImage(image_path, width=width, height=height)
        story.append(img_flowable)
        
        if caption and styles:
            story.append(Spacer(1, 3))
            story.append(Paragraph(caption, styles['Caption']))
        
        story.append(Spacer(1, 10))
        return True
    except Exception as e:
        print(f"   ❌ Erreur image: {e}")
        return False


def section_page(story, styles, title, image_name, description, features=None, tips=None, how_to=None):
    """Crée une page de section standardisée"""
    story.append(Paragraph(title, styles['SectionTitle']))
    story.append(Spacer(1, 0.3*cm))
    
    story.append(Paragraph(description, styles['Body']))
    story.append(Spacer(1, 0.3*cm))
    
    img_path = f'{SCREENSHOTS_DIR}/{image_name}.png'
    add_image(story, img_path, f"Capture d'écran : {title}", width=14*cm, max_height=9*cm, styles=styles)
    
    if features:
        story.append(Paragraph("Ce que vous pouvez faire :", styles['SubTitle']))
        for feat in features:
            story.append(Paragraph(f"✓ {feat}", styles['BulletItem']))
    
    if how_to:
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("Comment utiliser :", styles['SubTitle']))
        for i, step in enumerate(how_to, 1):
            story.append(Paragraph(f"{i}. {step}", styles['BulletItem']))
    
    if tips:
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(f"💡 Astuce : {tips}", styles['Tip']))
    
    story.append(PageBreak())


def generate_client_brochure():
    """Génère la brochure client complète"""
    print("=" * 70)
    print("   GÉNÉRATION BROCHURE TITELLI - VERSION CLIENT")
    print("=" * 70)
    
    output_path = f'{OUTPUT_DIR}/TITELLI_BROCHURE_CLIENT.pdf'
    
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
    print("📄 Page de couverture...")
    story.append(Spacer(1, 4*cm))
    story.append(Paragraph("TITELLI", styles['CoverTitle']))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("GUIDE UTILISATEUR", styles['CoverSubtitle']))
    story.append(Paragraph("Tout ce que vous pouvez faire sur Titelli", styles['CoverSubtitle']))
    story.append(Spacer(1, 1*cm))
    
    add_image(story, f'{SCREENSHOTS_DIR}/accueil.png', "", width=14*cm, max_height=10*cm, styles=styles)
    
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"Version {datetime.now().strftime('%B %Y')}", styles['CoverSubtitle']))
    story.append(PageBreak())
    
    # ==================== TABLE DES MATIÈRES ====================
    print("📄 Table des matières...")
    story.append(Paragraph("TABLE DES MATIÈRES", styles['SectionTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    toc_sections = [
        ("PARTIE 1 - DÉCOUVRIR TITELLI", [
            "1.1 Qu'est-ce que Titelli ?",
            "1.2 Naviguer sur le site",
            "1.3 Trouver des services",
        ]),
        ("PARTIE 2 - CRÉER SON COMPTE", [
            "2.1 S'inscrire",
            "2.2 Compléter son profil",
        ]),
        ("PARTIE 3 - VOTRE ESPACE PERSONNEL", [
            "3.1 Accueil du dashboard",
            "3.2 Mon Profil",
            "3.3 Mon mode de vie",
        ]),
        ("PARTIE 4 - VOS AVANTAGES", [
            "4.1 Le Cash-back",
            "4.2 Le Parrainage",
            "4.3 Premium Titelli",
            "4.4 Offres et Invitations",
        ]),
        ("PARTIE 5 - COMMANDER", [
            "5.1 Passer une commande",
            "5.2 Suivre vos commandes",
            "5.3 Votre panier",
        ]),
        ("PARTIE 6 - GÉRER VOTRE COMPTE", [
            "6.1 Agenda",
            "6.2 Cartes de paiement",
            "6.3 Documents",
            "6.4 Finances",
        ]),
        ("PARTIE 7 - COMMUNIQUER", [
            "7.1 Messagerie",
            "7.2 Contacts et Amis",
        ]),
        ("PARTIE 8 - AIDE", [
            "8.1 Support client",
            "8.2 Paramètres",
        ]),
    ]
    
    for section_title, items in toc_sections:
        story.append(Paragraph(section_title, styles['TOCSection']))
        for item in items:
            story.append(Paragraph(f"    {item}", styles['TOCItem']))
    
    story.append(PageBreak())
    
    # ==================== PARTIE 1: DÉCOUVRIR ====================
    print("📄 Partie 1: Découvrir Titelli...")
    
    story.append(Paragraph("PARTIE 1 - DÉCOUVRIR TITELLI", styles['SectionTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("1.1 Qu'est-ce que Titelli ?", styles['SubTitle']))
    story.append(Paragraph(
        "Titelli est une plateforme suisse qui vous permet de découvrir et réserver les meilleurs "
        "services près de chez vous : coiffeurs, restaurants, spas, artisans et bien plus encore. "
        "Profitez de cashback sur vos achats, d'offres exclusives et d'une expérience simplifiée.",
        styles['Body']
    ))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("Vos avantages en tant que client :", styles['Body']))
    story.append(Paragraph("• Trouvez facilement des prestataires de qualité", styles['BulletItem']))
    story.append(Paragraph("• Profitez de cashback sur vos achats", styles['BulletItem']))
    story.append(Paragraph("• Accédez à des offres exclusives", styles['BulletItem']))
    story.append(Paragraph("• Gérez vos rendez-vous en un clic", styles['BulletItem']))
    story.append(Paragraph("• Parrainez vos amis et gagnez des récompenses", styles['BulletItem']))
    
    story.append(PageBreak())
    
    # 1.2 Naviguer sur le site
    story.append(Paragraph("1.2 Naviguer sur le site", styles['SubTitle']))
    add_image(story, f'{SCREENSHOTS_DIR}/accueil.png', 
              "Page d'accueil Titelli", width=14*cm, max_height=9*cm, styles=styles)
    
    story.append(Paragraph("Le menu principal vous permet d'accéder à :", styles['Body']))
    story.append(Paragraph("• Services : Tous les services disponibles", styles['BulletItem']))
    story.append(Paragraph("• Produits : Les produits en vente", styles['BulletItem']))
    story.append(Paragraph("• Entreprises : Les prestataires inscrits", styles['BulletItem']))
    story.append(Paragraph("• Rdv : Prendre rendez-vous", styles['BulletItem']))
    story.append(Paragraph("• Connexion : Accéder à votre compte", styles['BulletItem']))
    
    story.append(PageBreak())
    
    # 1.3 Trouver des services
    story.append(Paragraph("1.3 Trouver des services", styles['SubTitle']))
    add_image(story, f'{SCREENSHOTS_DIR}/services.png',
              "Page des services", width=14*cm, max_height=9*cm, styles=styles)
    
    story.append(Paragraph(
        "Utilisez la barre de recherche pour trouver un service spécifique, ou parcourez "
        "les catégories pour découvrir ce qui est disponible près de chez vous.",
        styles['Body']
    ))
    
    story.append(Paragraph("Comment trouver un service :", styles['SubTitle']))
    story.append(Paragraph("1. Tapez votre recherche (ex: 'coiffeur', 'massage')", styles['BulletItem']))
    story.append(Paragraph("2. Filtrez par localisation, prix ou note", styles['BulletItem']))
    story.append(Paragraph("3. Consultez les avis des autres clients", styles['BulletItem']))
    story.append(Paragraph("4. Cliquez sur un service pour voir les détails", styles['BulletItem']))
    story.append(Paragraph("5. Réservez directement en ligne", styles['BulletItem']))
    
    story.append(PageBreak())
    
    # ==================== PARTIE 2: CRÉER SON COMPTE ====================
    print("📄 Partie 2: Créer son compte...")
    
    story.append(Paragraph("PARTIE 2 - CRÉER SON COMPTE", styles['SectionTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("2.1 S'inscrire sur Titelli", styles['SubTitle']))
    add_image(story, f'{SCREENSHOTS_DIR}/connexion.png',
              "Page de connexion et d'inscription", width=12*cm, max_height=9*cm, styles=styles)
    
    story.append(Paragraph("Étapes d'inscription :", styles['SubTitle']))
    story.append(Paragraph("1. ➜ Cliquez sur 'Connexion' en haut à droite", styles['BulletItem']))
    story.append(Paragraph("2. ➜ Sélectionnez 'S'inscrire'", styles['BulletItem']))
    story.append(Paragraph("3. ➜ Choisissez 'Client' comme type de compte", styles['BulletItem']))
    story.append(Paragraph("4. ➜ Entrez votre email et créez un mot de passe", styles['BulletItem']))
    story.append(Paragraph("5. ➜ Renseignez vos informations personnelles", styles['BulletItem']))
    story.append(Paragraph("6. ➜ Validez et c'est parti !", styles['BulletItem']))
    
    story.append(Paragraph(
        "💡 Astuce : Utilisez un email que vous consultez régulièrement pour ne pas manquer "
        "les offres exclusives et notifications importantes.",
        styles['Tip']
    ))
    
    story.append(PageBreak())
    
    # ==================== PARTIE 3: ESPACE PERSONNEL ====================
    print("📄 Partie 3: Espace personnel...")
    
    story.append(Paragraph("PARTIE 3 - VOTRE ESPACE PERSONNEL", styles['SectionTitle']))
    story.append(Paragraph(
        "Votre dashboard est votre espace personnel pour gérer toutes vos activités sur Titelli : "
        "commandes, cashback, profil, agenda et bien plus.",
        styles['Body']
    ))
    story.append(PageBreak())
    
    # 3.1 Accueil Dashboard
    section_page(story, styles,
        "3.1 Accueil du Dashboard",
        "client_accueil",
        "L'accueil de votre dashboard vous montre un résumé de votre activité : "
        "votre solde de cashback, vos dernières commandes et les offres du moment.",
        features=[
            "Voir votre solde de cashback",
            "Accéder rapidement à vos commandes",
            "Découvrir les offres personnalisées",
            "Consulter vos statistiques",
        ],
        tips="Consultez votre dashboard régulièrement pour ne pas manquer les offres du moment !"
    )
    
    # 3.2 Mon Profil
    section_page(story, styles,
        "3.2 Mon Profil",
        "client_profil",
        "Gérez vos informations personnelles : photo de profil, coordonnées, préférences. "
        "Un profil complet vous permet de recevoir des offres personnalisées.",
        features=[
            "Modifier vos informations personnelles",
            "Ajouter une photo de profil",
            "Définir vos préférences",
            "Gérer vos réseaux sociaux liés",
        ],
        how_to=[
            "Accédez à 'Mon Profil'",
            "Cliquez sur 'Modifier'",
            "Mettez à jour vos informations",
            "Sauvegardez vos changements"
        ]
    )
    
    # 3.3 Mode de vie
    section_page(story, styles,
        "3.3 Mon Mode de Vie",
        "client_mode_vie",
        "Indiquez vos centres d'intérêt et votre mode de vie pour recevoir des "
        "recommandations personnalisées de services et prestataires.",
        features=[
            "Définir vos centres d'intérêt",
            "Indiquer vos préférences",
            "Recevoir des suggestions adaptées",
        ],
        tips="Plus vous renseignez vos préférences, plus les recommandations seront pertinentes."
    )
    
    # ==================== PARTIE 4: AVANTAGES ====================
    print("📄 Partie 4: Avantages...")
    
    story.append(Paragraph("PARTIE 4 - VOS AVANTAGES", styles['SectionTitle']))
    story.append(Paragraph(
        "En tant que client Titelli, vous bénéficiez de nombreux avantages : cashback, "
        "parrainage, offres exclusives et programme Premium.",
        styles['Body']
    ))
    story.append(PageBreak())
    
    # 4.1 Cashback
    section_page(story, styles,
        "4.1 Le Cash-back",
        "client_cashback",
        "Gagnez du cashback sur chaque achat effectué sur Titelli ! L'argent est crédité "
        "sur votre compte et peut être utilisé pour vos prochains achats.",
        features=[
            "Voir votre solde de cashback",
            "Consulter l'historique des gains",
            "Utiliser votre cashback pour payer",
            "Suivre vos économies totales",
        ],
        how_to=[
            "Achetez chez un prestataire Titelli",
            "Le cashback est automatiquement crédité",
            "Utilisez-le lors de votre prochain achat",
        ],
        tips="Le taux de cashback varie selon les prestataires. Consultez les offres du moment pour maximiser vos gains !"
    )
    
    # 4.2 Parrainage
    section_page(story, styles,
        "4.2 Le Parrainage",
        "client_parrainage",
        "Invitez vos amis sur Titelli et gagnez des récompenses ! Chaque ami inscrit "
        "qui effectue un achat vous rapporte du cashback bonus.",
        features=[
            "Générer votre code de parrainage",
            "Partager votre lien par email ou SMS",
            "Suivre vos parrainages",
            "Recevoir vos récompenses automatiquement",
        ],
        how_to=[
            "Accédez à 'Parrainage'",
            "Copiez votre code unique",
            "Partagez-le avec vos amis",
            "Recevez du cashback quand ils s'inscrivent et achètent"
        ],
        tips="Plus vous parrainez, plus vous gagnez ! Partagez sur vos réseaux sociaux pour maximiser vos gains."
    )
    
    # 4.3 Premium
    section_page(story, styles,
        "4.3 Premium Titelli",
        "client_premium",
        "Devenez membre Premium pour bénéficier d'avantages exclusifs : cashback augmenté, "
        "offres réservées, support prioritaire et bien plus.",
        features=[
            "Cashback augmenté sur tous les achats",
            "Accès aux offres exclusives",
            "Support client prioritaire",
            "Invitations aux événements VIP",
        ]
    )
    
    # 4.4 Offres et Invitations
    section_page(story, styles,
        "4.4 Offres et Invitations",
        "client_offres",
        "Découvrez les offres du moment et les invitations spéciales des prestataires. "
        "Des réductions exclusives rien que pour vous !",
        features=[
            "Voir toutes les offres actives",
            "Recevoir des invitations personnalisées",
            "Profiter de réductions exclusives",
            "Ne rien manquer avec les notifications",
        ],
        tips="Activez les notifications pour être alerté dès qu'une offre correspond à vos intérêts."
    )
    
    # ==================== PARTIE 5: COMMANDER ====================
    print("📄 Partie 5: Commander...")
    
    story.append(Paragraph("PARTIE 5 - COMMANDER", styles['SectionTitle']))
    story.append(Paragraph(
        "Réservez des services et achetez des produits en quelques clics. "
        "Suivez vos commandes et gérez votre panier facilement.",
        styles['Body']
    ))
    story.append(PageBreak())
    
    # 5.1 Passer une commande
    story.append(Paragraph("5.1 Passer une commande", styles['SubTitle']))
    story.append(Paragraph(
        "Commander sur Titelli est simple et rapide :",
        styles['Body']
    ))
    story.append(Paragraph("1. ➜ Trouvez le service ou produit souhaité", styles['BulletItem']))
    story.append(Paragraph("2. ➜ Consultez les détails et les avis", styles['BulletItem']))
    story.append(Paragraph("3. ➜ Ajoutez au panier ou réservez directement", styles['BulletItem']))
    story.append(Paragraph("4. ➜ Choisissez votre mode de paiement", styles['BulletItem']))
    story.append(Paragraph("5. ➜ Confirmez votre commande", styles['BulletItem']))
    story.append(Paragraph("6. ➜ Recevez la confirmation par email", styles['BulletItem']))
    
    story.append(PageBreak())
    
    # 5.2 Suivre ses commandes
    section_page(story, styles,
        "5.2 Suivre vos Commandes",
        "client_commandes",
        "Consultez l'historique de toutes vos commandes et suivez leur statut en temps réel.",
        features=[
            "Voir toutes vos commandes passées",
            "Suivre le statut en temps réel",
            "Contacter le prestataire directement",
            "Laisser un avis après le service",
        ]
    )
    
    # 5.3 Panier
    section_page(story, styles,
        "5.3 Votre Panier",
        "client_panier",
        "Gérez votre panier avant de finaliser vos achats. Ajoutez ou retirez des articles, "
        "appliquez des codes promo et utilisez votre cashback.",
        features=[
            "Voir les articles dans votre panier",
            "Modifier les quantités",
            "Appliquer un code promo",
            "Utiliser votre cashback",
        ]
    )
    
    # ==================== PARTIE 6: GESTION ====================
    print("📄 Partie 6: Gestion du compte...")
    
    story.append(Paragraph("PARTIE 6 - GÉRER VOTRE COMPTE", styles['SectionTitle']))
    story.append(Paragraph(
        "Organisez votre vie avec les outils de gestion Titelli : agenda, cartes de paiement, "
        "documents et suivi de vos finances.",
        styles['Body']
    ))
    story.append(PageBreak())
    
    # 6.1 Agenda
    section_page(story, styles,
        "6.1 Mon Agenda",
        "client_agenda",
        "Gardez une trace de tous vos rendez-vous et événements. Synchronisez avec votre "
        "calendrier personnel pour ne rien oublier.",
        features=[
            "Voir tous vos rendez-vous",
            "Ajouter des événements personnels",
            "Recevoir des rappels",
            "Synchroniser avec votre calendrier",
        ],
        how_to=[
            "Accédez à 'Mon agenda'",
            "Consultez vos rendez-vous à venir",
            "Ajoutez des notes ou modifiez si besoin"
        ]
    )
    
    # 6.2 Cartes
    section_page(story, styles,
        "6.2 Mes Cartes de Paiement",
        "client_cartes",
        "Enregistrez vos cartes bancaires pour des paiements plus rapides et sécurisés.",
        features=[
            "Ajouter une carte bancaire",
            "Définir une carte par défaut",
            "Supprimer une carte",
            "Paiements sécurisés",
        ],
        tips="Vos données bancaires sont sécurisées et cryptées. Titelli ne stocke jamais vos numéros complets."
    )
    
    # 6.3 Documents
    section_page(story, styles,
        "6.3 Mes Documents",
        "client_documents",
        "Stockez vos documents importants : factures, CV, attestations. Accédez-y partout, "
        "à tout moment.",
        features=[
            "Télécharger des documents",
            "Organiser par catégories",
            "Partager si nécessaire",
            "Stocker votre CV pour les candidatures",
        ]
    )
    
    # 6.4 Finances
    section_page(story, styles,
        "6.4 Mes Finances",
        "client_finances",
        "Suivez vos dépenses sur Titelli, votre historique de cashback et vos économies totales.",
        features=[
            "Voir l'historique de vos dépenses",
            "Suivre vos gains de cashback",
            "Consulter vos économies totales",
            "Exporter vos données",
        ]
    )
    
    # ==================== PARTIE 7: COMMUNICATION ====================
    print("📄 Partie 7: Communication...")
    
    story.append(Paragraph("PARTIE 7 - COMMUNIQUER", styles['SectionTitle']))
    story.append(Paragraph(
        "Restez en contact avec les prestataires et vos amis sur Titelli.",
        styles['Body']
    ))
    story.append(PageBreak())
    
    # 7.1 Messagerie
    section_page(story, styles,
        "7.1 Messagerie",
        "client_messages",
        "Communiquez directement avec les prestataires pour poser des questions ou "
        "organiser vos rendez-vous.",
        features=[
            "Envoyer des messages aux prestataires",
            "Recevoir des réponses en temps réel",
            "Partager des photos ou fichiers",
            "Historique des conversations",
        ]
    )
    
    # 7.2 Contacts
    section_page(story, styles,
        "7.2 Contacts et Amis",
        "client_contacts",
        "Ajoutez des amis sur Titelli pour partager vos prestataires préférés et "
        "découvrir leurs recommandations.",
        features=[
            "Ajouter des amis",
            "Voir leurs activités",
            "Partager des recommandations",
            "Voir qui est en ligne",
        ]
    )
    
    # ==================== PARTIE 8: AIDE ====================
    print("📄 Partie 8: Aide...")
    
    story.append(Paragraph("PARTIE 8 - AIDE & SUPPORT", styles['SectionTitle']))
    story.append(PageBreak())
    
    # 8.1 Support
    section_page(story, styles,
        "8.1 Service Client",
        "client_support",
        "Besoin d'aide ? Notre équipe support est là pour vous. Contactez-nous par chat, "
        "email ou consultez la FAQ.",
        features=[
            "Chat en direct avec le support",
            "FAQ complète",
            "Email de contact",
            "Aide personnalisée",
        ],
        how_to=[
            "Accédez au support",
            "Consultez d'abord la FAQ",
            "Si besoin, ouvrez un ticket",
            "Décrivez votre problème en détail"
        ],
        tips="La FAQ répond à 80% des questions. Consultez-la d'abord pour une réponse immédiate !"
    )
    
    # 8.2 Paramètres
    section_page(story, styles,
        "8.2 Paramètres",
        "client_parametres",
        "Configurez votre compte selon vos préférences : notifications, langue, "
        "confidentialité et sécurité.",
        features=[
            "Gérer les notifications",
            "Changer de mot de passe",
            "Paramètres de confidentialité",
            "Supprimer le compte",
        ]
    )
    
    # ==================== PAGE FINALE ====================
    print("📄 Page finale...")
    
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("BIENVENUE SUR TITELLI !", styles['SectionTitle']))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Nous espérons que ce guide vous aidera à profiter pleinement de tous les avantages "
        "offerts par Titelli. Notre équipe est à votre disposition pour toute question.",
        styles['Body']
    ))
    story.append(Spacer(1, 1*cm))
    
    story.append(Paragraph("Contact :", styles['SubTitle']))
    story.append(Paragraph("• Site web : www.titelli.com", styles['BulletItem']))
    story.append(Paragraph("• Email : support@titelli.com", styles['BulletItem']))
    story.append(Paragraph("• Téléphone : +41 XX XXX XX XX", styles['BulletItem']))
    
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        "Profitez de vos avantages et découvrez les meilleurs prestataires près de chez vous !",
        styles['Tip']
    ))
    
    # ==================== GÉNÉRATION ====================
    print("\n📄 Génération du PDF...")
    doc.build(story)
    
    size = os.path.getsize(output_path) / (1024 * 1024)
    
    print("\n" + "=" * 70)
    print(f"   ✅ BROCHURE CLIENT GÉNÉRÉE !")
    print(f"   📁 {output_path}")
    print(f"   📦 Taille: {size:.1f} MB")
    print("=" * 70)
    
    return output_path


if __name__ == "__main__":
    generate_client_brochure()
