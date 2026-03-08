#!/usr/bin/env python3
"""
Génération de la Brochure Titelli V2 - Version Ultra-Détaillée
Une page par section du menu avec screenshots réels
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
    Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

SCREENSHOTS_DIR = '/app/backend/uploads/brochure_screenshots_v2'
OUTPUT_DIR = '/app/backend/uploads'

# Couleurs Titelli
TITELLI_BLUE = colors.Color(0, 71/255, 171/255)
TITELLI_DARK = colors.Color(15/255, 15/255, 20/255)
TITELLI_GOLD = colors.Color(255/255, 193/255, 7/255)
TITELLI_GREEN = colors.Color(34/255, 197/255, 94/255)
TITELLI_PURPLE = colors.Color(147/255, 51/255, 234/255)

def create_styles():
    """Crée les styles personnalisés"""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='CoverTitle',
        fontSize=42,
        textColor=TITELLI_BLUE,
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
        textColor=TITELLI_BLUE,
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
        textColor=TITELLI_BLUE,
        leftIndent=10,
        rightIndent=10,
        spaceBefore=10,
        spaceAfter=10,
        fontName='Helvetica-Oblique',
        backColor=colors.Color(0.95, 0.97, 1.0),
        borderWidth=1,
        borderColor=TITELLI_BLUE,
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
        textColor=TITELLI_BLUE,
        spaceBefore=15,
        spaceAfter=5,
        fontName='Helvetica-Bold'
    ))
    
    return styles


def add_image(story, image_path, caption="", width=15*cm, max_height=14*cm, styles=None):
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


def create_cover(story, styles):
    """Page de couverture"""
    story.append(Spacer(1, 4*cm))
    story.append(Paragraph("TITELLI", styles['CoverTitle']))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("BROCHURE DE PRÉSENTATION", styles['CoverSubtitle']))
    story.append(Paragraph("Guide Complet pour les Prestataires", styles['CoverSubtitle']))
    story.append(Spacer(1, 1*cm))
    
    add_image(story, f'{SCREENSHOTS_DIR}/accueil_hero.png', "", width=14*cm, max_height=10*cm, styles=styles)
    
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"Version {datetime.now().strftime('%B %Y')}", styles['CoverSubtitle']))
    story.append(Paragraph("La plateforme suisse de mise en relation", styles['Body']))
    story.append(PageBreak())


def create_toc(story, styles):
    """Table des matières détaillée"""
    story.append(Paragraph("TABLE DES MATIÈRES", styles['SectionTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    toc_sections = [
        ("PARTIE 1 - PRÉSENTATION GÉNÉRALE", [
            "1.1 Qu'est-ce que Titelli ?",
            "1.2 La page d'accueil",
            "1.3 Les avantages pour les prestataires",
        ]),
        ("PARTIE 2 - INSCRIPTION & CONNEXION", [
            "2.1 Créer un compte entreprise",
            "2.2 Se connecter",
            "2.3 Compléter son profil",
        ]),
        ("PARTIE 3 - LE DASHBOARD ENTREPRISE", [
            "3.1 Accueil du dashboard",
            "3.2 Profil entreprise",
            "3.3 Galerie média",
        ]),
        ("PARTIE 4 - GESTION COMMERCIALE", [
            "4.1 Services & Produits",
            "4.2 Mes commandes",
            "4.3 Mes livraisons",
            "4.4 Gestion des stocks",
        ]),
        ("PARTIE 5 - MARKETING & PUBLICITÉ", [
            "5.1 Offres & Promotions",
            "5.2 Mes publicités",
            "5.3 IA Ciblage clients",
            "5.4 Influenceurs",
        ]),
        ("PARTIE 6 - RESSOURCES HUMAINES", [
            "6.1 Mon personnel",
            "6.2 Emplois & Stages",
            "6.3 Formations",
        ]),
        ("PARTIE 7 - FINANCES", [
            "7.1 Mes finances",
            "7.2 Mes cartes",
            "7.3 Abonnements",
        ]),
        ("PARTIE 8 - COMMUNICATION", [
            "8.1 Messagerie",
            "8.2 Documents",
            "8.3 Support",
        ]),
    ]
    
    for section_title, items in toc_sections:
        story.append(Paragraph(section_title, styles['TOCSection']))
        for item in items:
            story.append(Paragraph(f"    {item}", styles['TOCItem']))
    
    story.append(PageBreak())


def section_page(story, styles, title, image_name, description, features=None, tips=None, how_to=None):
    """Crée une page de section standardisée"""
    story.append(Paragraph(title, styles['SectionTitle']))
    story.append(Spacer(1, 0.3*cm))
    
    # Description
    story.append(Paragraph(description, styles['Body']))
    story.append(Spacer(1, 0.3*cm))
    
    # Screenshot
    img_path = f'{SCREENSHOTS_DIR}/{image_name}.png'
    add_image(story, img_path, f"Capture d'écran : {title}", width=14*cm, max_height=10*cm, styles=styles)
    
    # Fonctionnalités
    if features:
        story.append(Paragraph("Fonctionnalités disponibles :", styles['SubTitle']))
        for feat in features:
            story.append(Paragraph(f"✓ {feat}", styles['BulletItem']))
    
    # Comment utiliser
    if how_to:
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("Comment utiliser cette section :", styles['SubTitle']))
        for i, step in enumerate(how_to, 1):
            story.append(Paragraph(f"{i}. {step}", styles['BulletItem']))
    
    # Conseils
    if tips:
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(f"💡 Conseil : {tips}", styles['Tip']))
    
    story.append(PageBreak())


def generate_brochure():
    """Génère la brochure complète"""
    print("=" * 70)
    print("   GÉNÉRATION BROCHURE TITELLI V2 - ULTRA-DÉTAILLÉE")
    print("=" * 70)
    
    output_path = f'{OUTPUT_DIR}/TITELLI_BROCHURE_V2_COMPLETE.pdf'
    
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
    create_cover(story, styles)
    
    # ==================== TABLE DES MATIÈRES ====================
    print("📄 Table des matières...")
    create_toc(story, styles)
    
    # ==================== PARTIE 1: PRÉSENTATION ====================
    print("📄 Partie 1: Présentation générale...")
    
    story.append(Paragraph("PARTIE 1 - PRÉSENTATION GÉNÉRALE", styles['SectionTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    # 1.1 Qu'est-ce que Titelli
    story.append(Paragraph("1.1 Qu'est-ce que Titelli ?", styles['SubTitle']))
    story.append(Paragraph(
        "Titelli est une plateforme suisse innovante de mise en relation entre prestataires de services "
        "et clients. Notre mission est de simplifier la découverte et la réservation de services de qualité "
        "en Suisse romande et au-delà. Que vous soyez coiffeur, restaurateur, artisan ou consultant, "
        "Titelli vous offre tous les outils nécessaires pour développer votre activité en ligne.",
        styles['Body']
    ))
    story.append(Spacer(1, 0.5*cm))
    
    # 1.2 Page d'accueil
    story.append(Paragraph("1.2 La page d'accueil", styles['SubTitle']))
    story.append(Paragraph(
        "La page d'accueil est le point d'entrée principal de Titelli. Elle présente les services populaires, "
        "les prestataires mis en avant et les offres du moment. C'est ici que vos futurs clients vous découvriront.",
        styles['Body']
    ))
    add_image(story, f'{SCREENSHOTS_DIR}/accueil_part1_hero.png', 
              "Page d'accueil - Section Hero avec barre de recherche", width=14*cm, max_height=9*cm, styles=styles)
    
    story.append(Paragraph("Le menu de navigation propose :", styles['Body']))
    story.append(Paragraph("• Services : Accès à tous les services disponibles", styles['BulletItem']))
    story.append(Paragraph("• Produits : Catalogue des produits en vente", styles['BulletItem']))
    story.append(Paragraph("• Entreprises : Liste des prestataires", styles['BulletItem']))
    story.append(Paragraph("• Rdv : Système de prise de rendez-vous", styles['BulletItem']))
    story.append(Paragraph("• Sports : Section dédiée aux activités sportives", styles['BulletItem']))
    story.append(Paragraph("• Pub IA : Création de publicités avec l'IA", styles['BulletItem']))
    
    story.append(PageBreak())
    
    # Section services de la page d'accueil
    story.append(Paragraph("La section Services populaires :", styles['SubTitle']))
    add_image(story, f'{SCREENSHOTS_DIR}/accueil_part2_services.png',
              "Section des services populaires", width=14*cm, max_height=9*cm, styles=styles)
    
    story.append(Paragraph(
        "Cette section affiche les services les plus demandés. En tant que prestataire, vos services "
        "peuvent apparaître ici si vous avez de bonnes évaluations et une activité régulière.",
        styles['Body']
    ))
    
    story.append(PageBreak())
    
    # ==================== PARTIE 2: INSCRIPTION ====================
    print("📄 Partie 2: Inscription & Connexion...")
    
    story.append(Paragraph("PARTIE 2 - INSCRIPTION & CONNEXION", styles['SectionTitle']))
    story.append(Spacer(1, 0.5*cm))
    
    # 2.1 Créer un compte
    story.append(Paragraph("2.1 Créer un compte entreprise", styles['SubTitle']))
    story.append(Paragraph(
        "Pour commencer à utiliser Titelli en tant que prestataire, vous devez créer un compte entreprise. "
        "Le processus est simple et rapide.",
        styles['Body']
    ))
    
    add_image(story, f'{SCREENSHOTS_DIR}/connexion.png',
              "Page d'authentification - Connexion et inscription", width=12*cm, max_height=9*cm, styles=styles)
    
    story.append(Paragraph("Étapes d'inscription :", styles['SubTitle']))
    story.append(Paragraph("1. ➜ Cliquez sur 'Connexion' en haut à droite de la page", styles['BulletItem']))
    story.append(Paragraph("2. ➜ Sélectionnez l'onglet 'Inscription'", styles['BulletItem']))
    story.append(Paragraph("3. ➜ Choisissez 'Entreprise' comme type de compte", styles['BulletItem']))
    story.append(Paragraph("4. ➜ Remplissez votre email professionnel", styles['BulletItem']))
    story.append(Paragraph("5. ➜ Créez un mot de passe sécurisé (min. 8 caractères)", styles['BulletItem']))
    story.append(Paragraph("6. ➜ Renseignez vos informations personnelles", styles['BulletItem']))
    story.append(Paragraph("7. ➜ Validez les conditions d'utilisation", styles['BulletItem']))
    story.append(Paragraph("8. ➜ Cliquez sur 'S'inscrire'", styles['BulletItem']))
    
    story.append(Paragraph(
        "💡 Conseil : Utilisez une adresse email professionnelle (ex: contact@votreentreprise.ch) "
        "pour renforcer votre crédibilité auprès des clients.",
        styles['Tip']
    ))
    
    story.append(PageBreak())
    
    # Page inscription entreprise détaillée
    story.append(Paragraph("2.2 Formulaire d'inscription détaillé", styles['SubTitle']))
    add_image(story, f'{SCREENSHOTS_DIR}/inscription_entreprise.png',
              "Formulaire d'inscription entreprise", width=13*cm, max_height=10*cm, styles=styles)
    
    story.append(Paragraph("Informations requises :", styles['Body']))
    story.append(Paragraph("• Nom de l'entreprise : Le nom commercial visible par les clients", styles['BulletItem']))
    story.append(Paragraph("• Email : Votre adresse email de contact", styles['BulletItem']))
    story.append(Paragraph("• Téléphone : Numéro de contact professionnel", styles['BulletItem']))
    story.append(Paragraph("• Adresse : Localisation de votre établissement", styles['BulletItem']))
    story.append(Paragraph("• Catégorie : Secteur d'activité principal", styles['BulletItem']))
    story.append(Paragraph("• Description : Présentation de votre activité", styles['BulletItem']))
    
    story.append(PageBreak())
    
    # ==================== PARTIE 3: DASHBOARD ====================
    print("📄 Partie 3: Dashboard entreprise...")
    
    story.append(Paragraph("PARTIE 3 - LE DASHBOARD ENTREPRISE", styles['SectionTitle']))
    story.append(Paragraph(
        "Le Dashboard est votre centre de contrôle pour gérer toute votre activité sur Titelli. "
        "Toutes les fonctionnalités sont accessibles depuis le menu latéral à gauche.",
        styles['Body']
    ))
    story.append(Spacer(1, 0.5*cm))
    
    # 3.1 Accueil Dashboard
    section_page(story, styles,
        "3.1 Accueil du Dashboard",
        "dashboard_accueil",
        "L'accueil du dashboard vous donne une vue d'ensemble de votre activité : statistiques, "
        "commandes récentes, notifications et accès rapides aux fonctionnalités principales.",
        features=[
            "Vue des statistiques du mois (vues, commandes, revenus)",
            "Graphiques de performance",
            "Notifications importantes",
            "Raccourcis vers les actions fréquentes",
            "Résumé des commandes en attente"
        ],
        tips="Consultez votre dashboard chaque jour pour ne manquer aucune commande ou message important."
    )
    
    # 3.2 Profil entreprise
    section_page(story, styles,
        "3.2 Profil Entreprise",
        "dashboard_profil",
        "La section Profil vous permet de gérer toutes les informations de votre entreprise visibles "
        "par les clients : nom, description, coordonnées, horaires d'ouverture, etc.",
        features=[
            "Modifier le nom et la description",
            "Ajouter/modifier le logo",
            "Définir les horaires d'ouverture",
            "Ajouter l'adresse et les coordonnées",
            "Configurer les réseaux sociaux",
            "Gérer les certifications et labels"
        ],
        how_to=[
            "Cliquez sur 'Profil entreprise' dans le menu",
            "Remplissez tous les champs disponibles",
            "Ajoutez une photo de profil attrayante",
            "Rédigez une description détaillée de vos services",
            "Cliquez sur 'Enregistrer' pour sauvegarder"
        ],
        tips="Un profil complet avec photos et description détaillée génère 3x plus de contacts que les profils incomplets."
    )
    
    # 3.3 Galerie média
    section_page(story, styles,
        "3.3 Galerie Média",
        "dashboard_media",
        "La galerie média vous permet d'ajouter des photos et vidéos de vos réalisations, "
        "de votre établissement et de votre équipe. Ces visuels sont essentiels pour attirer des clients.",
        features=[
            "Télécharger des photos haute qualité",
            "Ajouter des vidéos de présentation",
            "Organiser les médias par catégories",
            "Définir une photo principale",
            "Ajouter des descriptions aux images"
        ],
        how_to=[
            "Accédez à 'Galerie média'",
            "Cliquez sur '+ Ajouter'",
            "Sélectionnez vos fichiers (JPG, PNG, MP4)",
            "Ajoutez une description pour chaque média",
            "Réorganisez l'ordre d'affichage si nécessaire"
        ],
        tips="Utilisez des photos professionnelles avec un bon éclairage. Les images de qualité augmentent significativement les conversions."
    )
    
    # ==================== PARTIE 4: COMMERCIAL ====================
    print("📄 Partie 4: Gestion commerciale...")
    
    story.append(Paragraph("PARTIE 4 - GESTION COMMERCIALE", styles['SectionTitle']))
    story.append(Paragraph(
        "Cette partie couvre toutes les fonctionnalités liées à la vente de vos services et produits : "
        "création d'offres, gestion des commandes, livraisons et stocks.",
        styles['Body']
    ))
    story.append(PageBreak())
    
    # 4.1 Services & Produits
    section_page(story, styles,
        "4.1 Services & Produits",
        "dashboard_services",
        "C'est ici que vous créez et gérez tous vos services et produits en vente. "
        "Chaque élément aura sa propre fiche visible par les clients.",
        features=[
            "Créer des services avec prix et durée",
            "Ajouter des produits avec stock",
            "Définir des catégories",
            "Gérer les disponibilités",
            "Activer/désactiver des offres",
            "Configurer les options de réservation"
        ],
        how_to=[
            "Cliquez sur '+ Ajouter un service' ou '+ Ajouter un produit'",
            "Renseignez le nom et la description détaillée",
            "Définissez le prix en CHF",
            "Ajoutez des photos de qualité",
            "Sélectionnez la catégorie appropriée",
            "Publiez votre offre"
        ],
        tips="Des descriptions détaillées et des photos de qualité augmentent vos chances de vente de 80%."
    )
    
    # 4.2 Commandes
    section_page(story, styles,
        "4.2 Mes Commandes",
        "dashboard_commandes",
        "Suivez toutes les commandes de vos clients en temps réel. Validez, annulez ou marquez "
        "comme terminées vos commandes depuis cette interface.",
        features=[
            "Voir toutes les commandes (en attente, validées, terminées)",
            "Filtrer par statut ou date",
            "Accepter ou refuser une commande",
            "Contacter le client directement",
            "Imprimer les détails de commande",
            "Générer des factures"
        ],
        how_to=[
            "Accédez à 'Mes commandes'",
            "Consultez les commandes en attente (badge rouge)",
            "Cliquez sur une commande pour voir les détails",
            "Validez ou refusez selon votre disponibilité",
            "Marquez comme terminée une fois le service rendu"
        ],
        tips="Répondez aux commandes dans les 24h pour maintenir un bon taux de satisfaction client."
    )
    
    # 4.3 Livraisons
    section_page(story, styles,
        "4.3 Mes Livraisons",
        "dashboard_livraisons",
        "Si vous vendez des produits physiques, cette section vous permet de gérer toutes vos "
        "livraisons : préparation, expédition, suivi et confirmation.",
        features=[
            "Voir les livraisons en cours",
            "Générer des étiquettes d'expédition",
            "Suivre les colis",
            "Confirmer les livraisons",
            "Gérer les retours"
        ],
        how_to=[
            "Consultez les commandes en attente de livraison",
            "Préparez le colis",
            "Renseignez le numéro de suivi",
            "Le client sera notifié automatiquement"
        ]
    )
    
    # 4.4 Stocks
    section_page(story, styles,
        "4.4 Gestion des Stocks",
        "dashboard_stocks",
        "Gérez votre inventaire en temps réel. Soyez alerté quand un produit atteint un niveau "
        "de stock critique pour éviter les ruptures.",
        features=[
            "Vue d'ensemble de l'inventaire",
            "Alertes de stock bas",
            "Historique des mouvements",
            "Import/Export de données",
            "Prévisions de réapprovisionnement"
        ],
        how_to=[
            "Ajoutez vos produits avec leur quantité initiale",
            "Définissez le seuil d'alerte pour chaque produit",
            "Les stocks se mettent à jour automatiquement après chaque vente",
            "Réapprovisionnez quand vous recevez une alerte"
        ],
        tips="Configurez des alertes de stock à 20% de votre stock moyen pour ne jamais être en rupture."
    )
    
    # ==================== PARTIE 5: MARKETING ====================
    print("📄 Partie 5: Marketing & Publicité...")
    
    story.append(Paragraph("PARTIE 5 - MARKETING & PUBLICITÉ", styles['SectionTitle']))
    story.append(Paragraph(
        "Boostez votre visibilité avec les outils marketing intégrés : promotions, publicités, "
        "ciblage IA et collaboration avec des influenceurs.",
        styles['Body']
    ))
    story.append(PageBreak())
    
    # 5.1 Offres & Promotions
    section_page(story, styles,
        "5.1 Offres & Promotions",
        "dashboard_offres",
        "Créez des offres spéciales pour attirer de nouveaux clients et fidéliser les existants. "
        "Les promotions apparaissent en priorité dans les résultats de recherche.",
        features=[
            "Créer des réductions en pourcentage",
            "Offres à durée limitée",
            "Codes promo personnalisés",
            "Offres de bienvenue",
            "Ventes flash",
            "Packs promotionnels"
        ],
        how_to=[
            "Cliquez sur '+ Nouvelle offre'",
            "Sélectionnez le type de promotion",
            "Définissez le montant de la réduction",
            "Choisissez les produits/services concernés",
            "Définissez la période de validité",
            "Publiez l'offre"
        ],
        tips="Les offres de bienvenue (-10% sur la première commande) convertissent 40% de nouveaux clients."
    )
    
    # 5.2 Publicités
    section_page(story, styles,
        "5.2 Mes Publicités",
        "dashboard_publicites",
        "Lancez des campagnes publicitaires pour augmenter votre visibilité sur Titelli. "
        "Ciblez précisément votre audience et suivez vos performances en temps réel.",
        features=[
            "Créer des campagnes pub",
            "Cibler par zone géographique",
            "Définir un budget quotidien",
            "Suivre les statistiques (impressions, clics)",
            "Générer des visuels avec l'IA",
            "A/B testing"
        ],
        how_to=[
            "Accédez à 'Mes publicités'",
            "Cliquez sur 'Créer une campagne'",
            "Définissez votre budget et durée",
            "Créez ou téléchargez votre visuel",
            "Ciblez votre audience",
            "Lancez la campagne"
        ],
        tips="Un budget de 10 CHF/jour pendant 7 jours peut générer plus de 1000 impressions ciblées."
    )
    
    # 5.3 IA Ciblage
    section_page(story, styles,
        "5.3 IA Ciblage Clients",
        "dashboard_ia_ciblage",
        "Utilisez l'intelligence artificielle pour identifier et cibler automatiquement les clients "
        "les plus susceptibles d'être intéressés par vos services.",
        features=[
            "Analyse automatique de votre clientèle",
            "Segmentation intelligente",
            "Suggestions de ciblage",
            "Prédiction des comportements",
            "Optimisation des campagnes"
        ],
        how_to=[
            "Activez le ciblage IA",
            "L'IA analyse vos clients existants",
            "Recevez des recommandations personnalisées",
            "Appliquez les suggestions à vos campagnes"
        ],
        tips="Le ciblage IA peut augmenter le taux de conversion de vos publicités de 50%."
    )
    
    # 5.4 Influenceurs
    section_page(story, styles,
        "5.4 Influenceurs",
        "dashboard_influenceurs",
        "Collaborez avec des influenceurs Titelli pour promouvoir votre activité auprès de leur audience. "
        "Une façon efficace d'atteindre de nouveaux clients.",
        features=[
            "Trouver des influenceurs par niche",
            "Proposer des collaborations",
            "Suivre les résultats des partenariats",
            "Gérer les commissions",
            "Évaluer les performances"
        ],
        how_to=[
            "Parcourez la liste des influenceurs",
            "Filtrez par catégorie et audience",
            "Envoyez une proposition de collaboration",
            "Définissez les termes du partenariat",
            "Suivez les performances"
        ]
    )
    
    # ==================== PARTIE 6: RH ====================
    print("📄 Partie 6: Ressources Humaines...")
    
    story.append(Paragraph("PARTIE 6 - RESSOURCES HUMAINES", styles['SectionTitle']))
    story.append(Paragraph(
        "Gérez votre équipe, publiez des offres d'emploi et formez votre personnel directement "
        "depuis votre dashboard Titelli.",
        styles['Body']
    ))
    story.append(PageBreak())
    
    # 6.1 Personnel
    section_page(story, styles,
        "6.1 Mon Personnel",
        "dashboard_personnel",
        "Gérez votre équipe : ajoutez des collaborateurs, attribuez des rôles et suivez "
        "leur activité sur Titelli.",
        features=[
            "Ajouter des membres d'équipe",
            "Attribuer des permissions",
            "Planifier les horaires",
            "Suivre les performances",
            "Gérer les accès"
        ],
        how_to=[
            "Cliquez sur '+ Ajouter un collaborateur'",
            "Renseignez ses informations",
            "Définissez son rôle et ses permissions",
            "Envoyez-lui une invitation par email"
        ]
    )
    
    # 6.2 Emplois
    section_page(story, styles,
        "6.2 Emplois & Stages",
        "dashboard_emplois",
        "Publiez des offres d'emploi ou de stage pour recruter de nouveaux talents. "
        "Les annonces sont visibles dans la section Emplois de Titelli.",
        features=[
            "Créer des offres d'emploi",
            "Publier des stages",
            "Recevoir des candidatures",
            "Filtrer les profils",
            "Contacter les candidats"
        ],
        how_to=[
            "Cliquez sur '+ Nouvelle offre'",
            "Décrivez le poste en détail",
            "Définissez les critères requis",
            "Publiez l'annonce",
            "Recevez les candidatures dans 'Postulations'"
        ]
    )
    
    # 6.3 Formations
    section_page(story, styles,
        "6.3 Formations",
        "dashboard_formations",
        "Proposez ou suivez des formations pour développer les compétences de votre équipe "
        "ou proposer des formations à vos clients.",
        features=[
            "Créer des formations",
            "Inscrire des participants",
            "Suivre les progressions",
            "Délivrer des certificats"
        ]
    )
    
    # ==================== PARTIE 7: FINANCES ====================
    print("📄 Partie 7: Finances...")
    
    story.append(Paragraph("PARTIE 7 - FINANCES", styles['SectionTitle']))
    story.append(Paragraph(
        "Suivez vos revenus, gérez vos paiements et choisissez l'abonnement adapté à vos besoins.",
        styles['Body']
    ))
    story.append(PageBreak())
    
    # 7.1 Finances
    section_page(story, styles,
        "7.1 Mes Finances",
        "dashboard_finances",
        "Vue complète de vos revenus, dépenses et historique des transactions. "
        "Exportez vos données pour votre comptabilité.",
        features=[
            "Tableau de bord financier",
            "Historique des paiements",
            "Revenus par période",
            "Export comptable (CSV, PDF)",
            "Prévisions de revenus"
        ],
        how_to=[
            "Consultez le résumé mensuel",
            "Filtrez par période ou type",
            "Exportez vos données pour votre comptable",
            "Analysez vos performances"
        ]
    )
    
    # 7.2 Cartes
    section_page(story, styles,
        "7.2 Mes Cartes",
        "dashboard_cartes",
        "Gérez vos moyens de paiement pour les services Titelli : publicité, abonnements "
        "et autres services premium.",
        features=[
            "Ajouter une carte bancaire",
            "Gérer les cartes enregistrées",
            "Configurer le paiement par défaut",
            "Historique des paiements"
        ]
    )
    
    # 7.3 Abonnements
    section_page(story, styles,
        "7.3 Abonnements",
        "dashboard_abonnements",
        "Choisissez la formule d'abonnement adaptée à vos besoins. Plus votre abonnement est élevé, "
        "plus vous bénéficiez d'avantages et de réductions sur les commissions.",
        features=[
            "Voir l'abonnement actuel",
            "Comparer les formules",
            "Changer d'abonnement",
            "Historique des factures"
        ]
    )
    
    # Tableau des abonnements
    story.append(Paragraph("Comparatif des Abonnements :", styles['SubTitle']))
    story.append(Spacer(1, 0.3*cm))
    
    abo_data = [
        ['Formule', 'Prix', 'Commission', 'Avantages'],
        ['Guest', 'Gratuit', '15%', 'Profil basique, 3 services max'],
        ['Certifié', '29 CHF/mois', '12%', 'Services illimités, Badge, Stats'],
        ['Labellisé', '79 CHF/mois', '10%', 'Pub gratuite, Support prioritaire'],
        ['Exclusif', '149 CHF/mois', '8%', 'Account manager, Formation'],
    ]
    
    table = Table(abo_data, colWidths=[3*cm, 3*cm, 2.5*cm, 7*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TITELLI_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.Color(0.97, 0.97, 0.97)),
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(table)
    
    story.append(PageBreak())
    
    # ==================== PARTIE 8: COMMUNICATION ====================
    print("📄 Partie 8: Communication...")
    
    story.append(Paragraph("PARTIE 8 - COMMUNICATION & DOCUMENTS", styles['SectionTitle']))
    story.append(Paragraph(
        "Communiquez avec vos clients, stockez vos documents importants et obtenez de l'aide "
        "de l'équipe support Titelli.",
        styles['Body']
    ))
    story.append(PageBreak())
    
    # 8.1 Messagerie
    section_page(story, styles,
        "8.1 Messagerie",
        "dashboard_messagerie",
        "Communiquez directement avec vos clients depuis la messagerie intégrée. "
        "Répondez rapidement aux questions et finalisez les réservations.",
        features=[
            "Chat en temps réel",
            "Historique des conversations",
            "Notifications de nouveaux messages",
            "Envoi de fichiers et images",
            "Réponses rapides prédéfinies"
        ],
        how_to=[
            "Accédez à la messagerie",
            "Consultez les conversations non lues",
            "Répondez aux questions des clients",
            "Utilisez les réponses rapides pour gagner du temps"
        ],
        tips="Un temps de réponse inférieur à 1 heure augmente vos chances de conversion de 70%."
    )
    
    # 8.2 Documents
    section_page(story, styles,
        "8.2 Documents",
        "dashboard_documents",
        "Stockez tous vos documents importants : factures, contrats, attestations, etc. "
        "Accédez-y à tout moment depuis votre dashboard.",
        features=[
            "Télécharger des documents",
            "Organiser par catégories",
            "Partager avec des collaborateurs",
            "Recherche rapide"
        ]
    )
    
    # 8.3 Support
    section_page(story, styles,
        "8.3 Service Client",
        "dashboard_support",
        "Besoin d'aide ? Le service client Titelli est là pour vous accompagner. "
        "Contactez-nous par chat, email ou téléphone.",
        features=[
            "Chat en direct avec le support",
            "FAQ et guides d'aide",
            "Tickets de support",
            "Formation personnalisée"
        ],
        how_to=[
            "Accédez au support",
            "Consultez d'abord la FAQ",
            "Si nécessaire, ouvrez un ticket",
            "Décrivez votre problème en détail",
            "Attendez la réponse de notre équipe"
        ],
        tips="Consultez la FAQ avant d'ouvrir un ticket - 80% des questions y trouvent une réponse immédiate."
    )
    
    # ==================== PAGE FINALE ====================
    print("📄 Page finale...")
    
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("MERCI DE VOTRE CONFIANCE", styles['SectionTitle']))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Nous espérons que cette brochure vous a permis de découvrir toutes les possibilités "
        "offertes par Titelli. Notre équipe est à votre disposition pour vous accompagner "
        "dans le développement de votre activité.",
        styles['Body']
    ))
    story.append(Spacer(1, 1*cm))
    
    story.append(Paragraph("Contact :", styles['SubTitle']))
    story.append(Paragraph("• Site web : www.titelli.com", styles['BulletItem']))
    story.append(Paragraph("• Email : support@titelli.com", styles['BulletItem']))
    story.append(Paragraph("• Téléphone : +41 XX XXX XX XX", styles['BulletItem']))
    
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        "Rejoignez la communauté Titelli et développez votre activité dès aujourd'hui !",
        styles['Tip']
    ))
    
    # ==================== GÉNÉRATION ====================
    print("\n📄 Génération du PDF...")
    doc.build(story)
    
    size = os.path.getsize(output_path) / (1024 * 1024)
    
    print("\n" + "=" * 70)
    print(f"   ✅ BROCHURE V2 GÉNÉRÉE !")
    print(f"   📁 {output_path}")
    print(f"   📦 Taille: {size:.1f} MB")
    print("=" * 70)
    
    return output_path


if __name__ == "__main__":
    generate_brochure()
