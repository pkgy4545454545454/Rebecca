from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm
import textwrap

# Colors from template
DARK_CHARCOAL = HexColor("#1E1E1E")
GOLD_ACCENT = HexColor("#D4A84B")
LIGHT_GRAY = HexColor("#F5F5F5")
WHITE = white
TEXT_GRAY = HexColor("#666666")

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 15 * mm

def draw_header_bar(c, y_pos, height=25*mm):
    """Dark header bar with diagonal cut"""
    c.setFillColor(DARK_CHARCOAL)
    path = c.beginPath()
    path.moveTo(0, y_pos)
    path.lineTo(PAGE_WIDTH, y_pos)
    path.lineTo(PAGE_WIDTH, y_pos - height)
    path.lineTo(PAGE_WIDTH * 0.7, y_pos - height)
    path.lineTo(PAGE_WIDTH * 0.6, y_pos - height - 10*mm)
    path.lineTo(0, y_pos - height - 10*mm)
    path.close()
    c.drawPath(path, fill=1, stroke=0)
    return y_pos - height - 10*mm

def draw_logo_header(c):
    """Logo + Titelli en haut"""
    # Logo
    try:
        logo = ImageReader("/app/backend/uploads/logo_titelli_new.png")
        c.drawImage(logo, MARGIN, PAGE_HEIGHT - 18*mm, width=12*mm, height=12*mm, mask='auto')
    except:
        pass
    
    # Titelli text
    c.setFillColor(WHITE)
    c.setFont("Times-Bold", 16)
    c.drawString(MARGIN + 15*mm, PAGE_HEIGHT - 14*mm, "Titelli")
    
    # Slogan
    c.setFont("Helvetica-Oblique", 7)
    c.drawString(MARGIN + 15*mm, PAGE_HEIGHT - 19*mm, 
                 "Tous les prestataires préférés de votre région se trouvent sur Titelli")

def draw_gold_line(c, y):
    """Gold accent line"""
    c.setStrokeColor(GOLD_ACCENT)
    c.setLineWidth(2)
    c.line(MARGIN, y, MARGIN + 40*mm, y)

def draw_section_title(c, y, title, color=DARK_CHARCOAL):
    """Section title with gold underline"""
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(MARGIN, y, title)
    draw_gold_line(c, y - 3*mm)
    return y - 12*mm

def draw_dark_section(c, y, height, title, content_lines):
    """Dark background section"""
    c.setFillColor(DARK_CHARCOAL)
    c.rect(0, y - height, PAGE_WIDTH, height, fill=1, stroke=0)
    
    # Title in gold
    c.setFillColor(GOLD_ACCENT)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN, y - 8*mm, title)
    
    # Content in white
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 9)
    text_y = y - 16*mm
    for line in content_lines[:6]:
        if text_y > y - height + 5*mm:
            c.drawString(MARGIN, text_y, line)
            text_y -= 5*mm
    
    return y - height

def draw_bullet(c, y, text, indent=0):
    """Draw bullet point"""
    x = MARGIN + indent*5*mm
    c.setFillColor(GOLD_ACCENT)
    c.circle(x + 1.5*mm, y + 1*mm, 1.2*mm, fill=1, stroke=0)
    c.setFillColor(DARK_CHARCOAL)
    c.setFont("Helvetica", 9)
    
    # Wrap text
    max_chars = 85 - indent*5
    lines = textwrap.wrap(text, width=max_chars)
    for i, line in enumerate(lines):
        c.drawString(x + 5*mm, y - i*4*mm, line)
    return y - len(lines)*4*mm - 2*mm

def draw_price_item(c, y, title, price, description=""):
    """Draw pricing item"""
    c.setFillColor(DARK_CHARCOAL)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, y, title)
    
    c.setFillColor(GOLD_ACCENT)
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(PAGE_WIDTH - MARGIN, y, price)
    
    if description:
        c.setFillColor(TEXT_GRAY)
        c.setFont("Helvetica", 8)
        lines = textwrap.wrap(description, width=90)
        text_y = y - 4*mm
        for line in lines[:2]:
            c.drawString(MARGIN + 5*mm, text_y, line)
            text_y -= 3.5*mm
        return text_y - 2*mm
    return y - 6*mm

def draw_footer(c, page_num):
    """Footer with page number"""
    c.setFillColor(DARK_CHARCOAL)
    c.rect(0, 0, PAGE_WIDTH, 12*mm, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 8)
    c.drawCentredString(PAGE_WIDTH/2, 4*mm, f"Titelli SA  •  Document de monétisation  •  Page {page_num}")

def create_monetisation_brochure():
    output_path = "/app/backend/uploads/monetisation_titelli_pro.pdf"
    c = canvas.Canvas(output_path, pagesize=A4)
    
    # ========== PAGE 1 - COVER ==========
    # Dark header
    c.setFillColor(DARK_CHARCOAL)
    c.rect(0, PAGE_HEIGHT - 120*mm, PAGE_WIDTH, 120*mm, fill=1, stroke=0)
    
    draw_logo_header(c)
    
    # Main title
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 32)
    c.drawString(MARGIN, PAGE_HEIGHT - 55*mm, "Ne cherchez plus")
    c.drawString(MARGIN, PAGE_HEIGHT - 70*mm, "vos clients")
    
    c.setFillColor(GOLD_ACCENT)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(MARGIN, PAGE_HEIGHT - 90*mm, "Laissez-les vous trouver !")
    
    # Tagline
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 11)
    c.drawString(MARGIN, PAGE_HEIGHT - 105*mm, "Ne manquez plus aucune occasion de vendre.")
    
    # Mission section
    y = PAGE_HEIGHT - 140*mm
    y = draw_section_title(c, y, "Notre Mission")
    
    c.setFillColor(DARK_CHARCOAL)
    c.setFont("Helvetica", 10)
    mission_text = [
        "Connecter les meilleurs prestataires de la région afin de permettre",
        "chaque jour à de nouveaux clients de les découvrir.",
        "",
        "Notre but, Vos intérêts. Notre objectif, vos bénéfices.",
    ]
    for line in mission_text:
        c.drawString(MARGIN, y, line)
        y -= 5*mm
    
    # Vision section
    y -= 10*mm
    y = draw_section_title(c, y, "Notre Vision")
    
    vision_text = [
        "Rendre le client toujours plus proche de ses prestataires préférés.",
        "",
        "Titelli voit et croit en le véritable potentiel de votre entreprise",
        "ainsi qu'en votre plus-value sur le marché.",
    ]
    for line in vision_text:
        c.drawString(MARGIN, y, line)
        y -= 5*mm
    
    draw_footer(c, 1)
    c.showPage()
    
    # ========== PAGE 2 - NOS PRESTATIONS ==========
    c.setFillColor(DARK_CHARCOAL)
    c.rect(0, PAGE_HEIGHT - 30*mm, PAGE_WIDTH, 30*mm, fill=1, stroke=0)
    draw_logo_header(c)
    
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(MARGIN, PAGE_HEIGHT - 22*mm, "Nos Prestations")
    
    y = PAGE_HEIGHT - 45*mm
    
    prestations = [
        ("Inscription annuelle", "250.-", "Obligatoire pour accéder à la plateforme"),
        ("Premium livraison instantanée", "50.-/mois ou 500.-/an", "Répondez aux demandes clients instantanément"),
        ("Pub Référencement mensuel", "dès 100.- ou 1'000.-/an", "Référencé dans votre domaine d'activité toute l'année"),
        ("Marketing visuel", "100.- ou 1'000.-/an", "Accès aux meilleurs outils informatisés"),
        ("Expert marketing visuel", "200.- à 1'000.-/mois", "Un expert révise votre publicité tous les mois"),
        ("Premium dépôt 24/24", "100.- ou 1'000.-/an", "Dépôt accessible après 19h pour liquider votre stock"),
        ("Fournisseurs", "200.- à 1'000.-/an", "Accès à des fournisseurs pour optimiser votre entreprise"),
        ("Investissement", "200.- à 500.-/an", "Trouver un partenaire, proposer des parts"),
        ("Formations avancées", "200.- à 2'000.-/mois", "Les meilleures techniques par des spécialistes Suisses"),
        ("Soins entreprise", "500.- ou 5'000.-/an", "Soins pour votre personnel et entreprise"),
        ("Liquidation de stock", "dès 1'000.- ou 10'000.-/an", "Titelli liquide votre stock pour vous"),
        ("Gestion d'entreprise", "1'000.- à 30'000.-/an", "Expert marketing et fiscaliste à votre service"),
    ]
    
    for title, price, desc in prestations:
        y = draw_price_item(c, y, title, price, desc)
        if y < 25*mm:
            break
    
    draw_footer(c, 2)
    c.showPage()
    
    # ========== PAGE 3 - PACKS ==========
    c.setFillColor(DARK_CHARCOAL)
    c.rect(0, PAGE_HEIGHT - 30*mm, PAGE_WIDTH, 30*mm, fill=1, stroke=0)
    draw_logo_header(c)
    
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(MARGIN, PAGE_HEIGHT - 22*mm, "Nos Packs")
    
    y = PAGE_HEIGHT - 45*mm
    
    # Pack boxes
    packs = [
        ("Pack 200.-/mois", ["Premium livraison 50.-", "Pub Référencement 100.-", "Marketing visuel 100.-"]),
        ("Pack 500.-/mois", ["Premium livraison 50.-", "Pub Référencement 100.-", "Marketing visuel 100.-", "Premium dépôt 24/24 100.-", "Fournisseurs 200.-"]),
        ("Pack 1'000.-/mois", ["Premium livraison 50.-", "Pub Référencement 200.-", "Expert marketing 200.-", "Premium dépôt 100.-", "Fournisseurs 200.-", "Formations 200.-"]),
        ("Pack 3'000.-/mois", ["Tout le pack 1'000.-", "+ Soins entreprise 500.-", "+ Liquidation stock 1'000.-"]),
    ]
    
    col_width = (PAGE_WIDTH - 3*MARGIN) / 2
    col = 0
    start_y = y
    
    for pack_name, items in packs:
        x = MARGIN + col * (col_width + MARGIN/2)
        
        # Pack header
        c.setFillColor(DARK_CHARCOAL)
        c.roundRect(x, y - 45*mm, col_width, 45*mm, 3, fill=1, stroke=0)
        
        c.setFillColor(GOLD_ACCENT)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x + 5*mm, y - 8*mm, pack_name)
        
        c.setFillColor(WHITE)
        c.setFont("Helvetica", 8)
        item_y = y - 15*mm
        for item in items[:5]:
            c.drawString(x + 5*mm, item_y, "• " + item)
            item_y -= 5*mm
        
        col += 1
        if col >= 2:
            col = 0
            y -= 52*mm
    
    # Big packs
    y -= 15*mm
    c.setFillColor(GOLD_ACCENT)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN, y, "Packs Premium")
    y -= 10*mm
    
    big_packs = [
        ("Pack 5'000.-/mois", "Gestion d'entreprise starter incluse"),
        ("Pack 10'000.-/mois", "Gestion d'entreprise smarter + Formations avancées 1'000.-"),
        ("Pack 20'000.-/mois", "Gestion Guest + Accès immobilier VIP + Fournisseurs VIP"),
    ]
    
    for name, desc in big_packs:
        c.setFillColor(DARK_CHARCOAL)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, y, name)
        c.setFillColor(TEXT_GRAY)
        c.setFont("Helvetica", 9)
        c.drawString(MARGIN + 50*mm, y, desc)
        y -= 8*mm
    
    draw_footer(c, 3)
    c.showPage()
    
    # ========== PAGE 4 - AVANTAGES GRATUITS ==========
    c.setFillColor(DARK_CHARCOAL)
    c.rect(0, PAGE_HEIGHT - 30*mm, PAGE_WIDTH, 30*mm, fill=1, stroke=0)
    draw_logo_header(c)
    
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(MARGIN, PAGE_HEIGHT - 22*mm, "Avantages gratuits avec votre compte")
    
    y = PAGE_HEIGHT - 45*mm
    
    avantages = [
        "Une exposition sur Titelli auprès d'un nouveau public",
        "Un spécialiste marketing reprend votre communication",
        "Profil entreprise - book attrayant pour vos prestations",
        "Référencement préférentiel pour renforcer votre présence",
        "Publication d'offres illimitées pour fidéliser vos clients",
        "Mention \"Certifié\" pour valoriser votre savoir-faire",
        "Mention \"Labellisé\" pour les prestations prestigieuses",
        "Accès aux Offres du moment et Guests du moment",
        "Système de Cash-Back (10% retour sur achat)",
        "Gestion du personnel et cahiers des charges",
        "Gestion des stocks avec alertes et automatisation",
        "Espace finance et cartes centralisé",
        "Messagerie professionnelle intégrée",
    ]
    
    for av in avantages:
        y = draw_bullet(c, y, av)
        if y < 25*mm:
            break
    
    draw_footer(c, 4)
    c.showPage()
    
    # ========== PAGE 5 - SERVICES COMPLEMENTAIRES ==========
    c.setFillColor(DARK_CHARCOAL)
    c.rect(0, PAGE_HEIGHT - 30*mm, PAGE_WIDTH, 30*mm, fill=1, stroke=0)
    draw_logo_header(c)
    
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(MARGIN, PAGE_HEIGHT - 22*mm, "Services Complémentaires")
    
    y = PAGE_HEIGHT - 45*mm
    
    services = [
        ("Service Premium", "Accessibilité renforcée, répondre aux clients les plus exigeants"),
        ("Optimisation fiscale", "Expert comptable et juridique pour optimiser vos bénéfices"),
        ("Livraison standard ou instantanée", "Service à domicile en 1-2h avec nos chauffeurs"),
        ("Premium dépôt 24/24", "Vos services disponibles même après 19h"),
        ("Liquidez votre stock", "Titelli livre quotidiennement à vos clients réguliers"),
        ("Fournisseurs élite", "Accès aux meilleurs fournisseurs internationaux"),
        ("Healthy lifestyle pass", "Prestataires respectant les exigences de santé"),
        ("Lifestyle pass", "Nouveau mode de vie pour vos clients"),
        ("Expert Marketing", "Les meilleurs experts marketing de Suisse"),
        ("Soins entreprise", "Make-up, sport, formation, traiteur, nettoyage..."),
        ("Gestion d'entreprise", "Les meilleurs experts s'occupent de tout"),
        ("Accès immobilier VIP", "Espaces exclusifs introuvables sur le marché"),
    ]
    
    for title, desc in services:
        c.setFillColor(DARK_CHARCOAL)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, y, title)
        y -= 5*mm
        c.setFillColor(TEXT_GRAY)
        c.setFont("Helvetica", 9)
        lines = textwrap.wrap(desc, width=85)
        for line in lines:
            c.drawString(MARGIN + 5*mm, y, line)
            y -= 4*mm
        y -= 3*mm
        if y < 25*mm:
            break
    
    draw_footer(c, 5)
    c.showPage()
    
    # ========== PAGE 6 - AVANTAGES CLIENTS ==========
    c.setFillColor(DARK_CHARCOAL)
    c.rect(0, PAGE_HEIGHT - 30*mm, PAGE_WIDTH, 30*mm, fill=1, stroke=0)
    draw_logo_header(c)
    
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(MARGIN, PAGE_HEIGHT - 22*mm, "Avantages pour vos Clients")
    
    y = PAGE_HEIGHT - 45*mm
    
    client_avantages = [
        "Profil avec photos et vidéos souvenirs",
        "Cash-back de 10% réutilisable partout",
        "Mode de vie avec objectifs et suggestions",
        "Steward 24/24 pour demandes spontanées",
        "Livraison instantanée 24/24",
        "Formations et opportunités professionnelles",
        "Investissements accessibles en un click",
        "Offres toute l'année aux meilleurs prix",
        "Prestataires Labellisés ou Certifiés garantis",
        "Fiche d'exigences personnalisée",
        "Organisation de sorties avec amis",
        "Fil d'actualité et business news",
        "Devenir influenceur rémunéré",
        "Page publicité personnelle 24/24",
        "Agenda et calendrier centralisés",
    ]
    
    for av in client_avantages:
        y = draw_bullet(c, y, av)
        if y < 25*mm:
            break
    
    draw_footer(c, 6)
    c.showPage()
    
    # ========== PAGE 7 - CONTACT ==========
    # Full dark page
    c.setFillColor(DARK_CHARCOAL)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    
    # Logo centered
    try:
        logo = ImageReader("/app/backend/uploads/logo_titelli_new.png")
        c.drawImage(logo, PAGE_WIDTH/2 - 25*mm, PAGE_HEIGHT - 80*mm, width=50*mm, height=50*mm, mask='auto')
    except:
        pass
    
    c.setFillColor(WHITE)
    c.setFont("Times-Bold", 28)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 100*mm, "Titelli")
    
    c.setFillColor(GOLD_ACCENT)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 130*mm, "Contactez-nous")
    
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 12)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 150*mm, "www.titelli.com")
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 162*mm, "info@titelli.com")
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 174*mm, "+41 79 895 03 13")
    
    c.setFillColor(GOLD_ACCENT)
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 200*mm, 
                        "\"Tous les prestataires préférés de votre région")
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 212*mm, 
                        "se trouvent sur Titelli\"")
    
    # Gold line
    c.setStrokeColor(GOLD_ACCENT)
    c.setLineWidth(2)
    c.line(PAGE_WIDTH/2 - 50*mm, PAGE_HEIGHT - 220*mm, PAGE_WIDTH/2 + 50*mm, PAGE_HEIGHT - 220*mm)
    
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 9)
    c.drawCentredString(PAGE_WIDTH/2, 20*mm, "© Titelli SA - Tous droits réservés")
    
    c.save()
    print(f"✅ {output_path}")
    return output_path


if __name__ == "__main__":
    create_monetisation_brochure()
