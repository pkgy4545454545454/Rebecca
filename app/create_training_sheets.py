from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import textwrap

# Colors
PRIMARY_BLACK = HexColor("#1a1a1a")
ACCENT_GRAY = HexColor("#666666")
LIGHT_GRAY = HexColor("#f5f5f5")
BORDER_GRAY = HexColor("#e0e0e0")
WHITE = HexColor("#ffffff")

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 20 * mm
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN

def draw_header(c, title):
    """Draw professional header with logo and slogan"""
    # Header background - subtle gradient effect with line
    c.setStrokeColor(BORDER_GRAY)
    c.setLineWidth(0.5)
    c.line(MARGIN, PAGE_HEIGHT - 45 * mm, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 45 * mm)
    
    # Logo (small, top left)
    logo = ImageReader("/app/backend/uploads/logo_titelli_noir_v2.png")
    logo_height = 12 * mm
    logo_width = 12 * mm
    c.drawImage(logo, MARGIN, PAGE_HEIGHT - 20 * mm, width=logo_width, height=logo_height, mask='auto')
    
    # "TITELLI" text next to logo
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(MARGIN + logo_width + 3 * mm, PAGE_HEIGHT - 14 * mm, "TITELLI")
    
    # Slogan (small, italic)
    c.setFillColor(ACCENT_GRAY)
    c.setFont("Helvetica-Oblique", 7)
    c.drawString(MARGIN + logo_width + 3 * mm, PAGE_HEIGHT - 19 * mm, 
                 "Tous les prestataires préférés de votre région se trouvent sur Titelli")
    
    # Document type badge (top right)
    badge_text = "FORMATION INTERNE"
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Helvetica", 7)
    badge_width = c.stringWidth(badge_text, "Helvetica", 7) + 8 * mm
    badge_x = PAGE_WIDTH - MARGIN - badge_width
    c.roundRect(badge_x, PAGE_HEIGHT - 17 * mm, badge_width, 6 * mm, 2, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.drawCentredString(badge_x + badge_width/2, PAGE_HEIGHT - 15.5 * mm, badge_text)
    
    # Main title
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(MARGIN, PAGE_HEIGHT - 38 * mm, title)


def draw_footer(c, page_num, total_pages):
    """Draw footer with page number"""
    c.setStrokeColor(BORDER_GRAY)
    c.setLineWidth(0.5)
    c.line(MARGIN, 15 * mm, PAGE_WIDTH - MARGIN, 15 * mm)
    
    c.setFillColor(ACCENT_GRAY)
    c.setFont("Helvetica", 8)
    c.drawString(MARGIN, 10 * mm, "Document de formation interne - Titelli SA")
    c.drawRightString(PAGE_WIDTH - MARGIN, 10 * mm, f"Page {page_num}/{total_pages}")


def draw_section_title(c, y, title, icon_char=""):
    """Draw a section title with accent"""
    # Accent bar
    c.setFillColor(PRIMARY_BLACK)
    c.rect(MARGIN, y - 1 * mm, 3 * mm, 5 * mm, fill=1, stroke=0)
    
    # Title
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN + 5 * mm, y, title.upper())
    
    return y - 8 * mm


def draw_bullet_point(c, y, text, indent=0, is_sub=False):
    """Draw a bullet point"""
    x = MARGIN + 5 * mm + indent * 5 * mm
    
    if is_sub:
        c.setFillColor(ACCENT_GRAY)
        c.setFont("Helvetica", 8)
        bullet = "○"
    else:
        c.setFillColor(PRIMARY_BLACK)
        c.setFont("Helvetica", 9)
        bullet = "●"
    
    # Bullet
    c.drawString(x, y, bullet)
    
    # Text (wrap if too long)
    text_x = x + 4 * mm
    max_width = CONTENT_WIDTH - indent * 5 * mm - 10 * mm
    
    # Simple text wrapping
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if c.stringWidth(test_line, "Helvetica", 9 if not is_sub else 8) < max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    for i, line in enumerate(lines):
        c.drawString(text_x, y - i * 4 * mm, line)
    
    return y - (len(lines) * 4 * mm + 2 * mm)


def draw_highlight_box(c, y, text, height=12*mm):
    """Draw a highlighted info box"""
    c.setFillColor(LIGHT_GRAY)
    c.roundRect(MARGIN, y - height + 3*mm, CONTENT_WIDTH, height, 3, fill=1, stroke=0)
    
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Helvetica-Oblique", 9)
    
    # Wrap text
    lines = textwrap.wrap(text, width=90)
    text_y = y - 2*mm
    for line in lines[:3]:
        c.drawString(MARGIN + 4*mm, text_y, line)
        text_y -= 4*mm
    
    return y - height - 3*mm


def create_prospect_rdv_pdf():
    """Create the Prospect Rendez-vous client PDF"""
    output_path = "/app/backend/uploads/fiche_prospect_rdv_client.pdf"
    c = canvas.Canvas(output_path, pagesize=A4)
    
    # PAGE 1
    draw_header(c, "Prospect Rendez-vous Client")
    y = PAGE_HEIGHT - 55 * mm
    
    # Procédé de vente
    y = draw_section_title(c, y, "Procédé de vente en rendez-vous")
    
    items_page1 = [
        ("Prendre connaissance du prestataire", []),
        ("Préparer ses arguments correspondants", [
            "Identifier le public cible (si exigeants : labellisés ! Si accessibles : nos offres !)",
            "La qualité du produit ou service",
            "La disponibilité du produit ou service",
            "Le marché et son terrain d'action"
        ]),
        ("Émotion d'arrivée et présentation", ["Bonne poignée de main, souriant, regard droit"]),
        ("Créer une accroche avec questions ouvertes", []),
        ("Présentation du site et concept Titelli", ["Sur tablette ou ordinateur"]),
        ("Vidéos prestataires divertissantes", []),
        ("Présentation de nos offres", [
            "Avantages directs, indirects et long terme",
            "Termes contractuels et monétisation"
        ]),
        ("Émotion d'achat", ["Le client se sent privilégié"]),
        ("Réception facture par mail", []),
        ("Mail gift : optimisation + publicité offerte", [
            "100.- de publicité offerte",
            "Optimisation entreprise starter"
        ]),
    ]
    
    for item, subitems in items_page1:
        y = draw_bullet_point(c, y, item)
        for subitem in subitems:
            y = draw_bullet_point(c, y, subitem, indent=1, is_sub=True)
        if y < 40 * mm:
            break
    
    draw_footer(c, 1, 3)
    c.showPage()
    
    # PAGE 2
    draw_header(c, "Prospect Rendez-vous Client")
    y = PAGE_HEIGHT - 55 * mm
    
    y = draw_section_title(c, y, "Suite du procédé")
    
    items_page2 = [
        ("Accompagner création profil prestataire", []),
        ("Vidéos formation prestataires", []),
        ("Expliquer comment faire des revenus avec Titelli", []),
        ("Gift Titelli partenaire", []),
        ("Autocollant sur la porte + caisse", []),
        ("Flyers en caisse", []),
        ("Demander des recommandations", []),
        ("Proposer un geste commercial", []),
        ("Remettre carte de visite", []),
        ("Émotion de départ positive", []),
        ("Rappeler : activation compte dans 30-50 jours", []),
    ]
    
    for item, subitems in items_page2:
        y = draw_bullet_point(c, y, item)
        for subitem in subitems:
            y = draw_bullet_point(c, y, subitem, indent=1, is_sub=True)
    
    y -= 5*mm
    y = draw_section_title(c, y, "En cas de refus")
    y = draw_highlight_box(c, y, 
        "\"Nos partenaires sont convaincus de représenter leur corps de métier en tant que meilleur prestataire de la région. "
        "Prenez le temps de découvrir Titelli, je vous laisse ma carte. Vous pouvez vous inscrire par vous-même si vous le souhaitez.\"",
        height=16*mm)
    
    draw_footer(c, 2, 3)
    c.showPage()
    
    # PAGE 3 - Objectif et Émotions
    draw_header(c, "Prospect Rendez-vous Client")
    y = PAGE_HEIGHT - 55 * mm
    
    y = draw_section_title(c, y, "Objectif")
    y = draw_highlight_box(c, y,
        "Susciter un véritable intérêt et partager notre enchantement pour Titelli ! "
        "Le client doit éprouver une véritable satisfaction. Ce ressenti établit un lien direct avec la plateforme.",
        height=14*mm)
    
    y -= 5*mm
    y = draw_section_title(c, y, "Créer une émotion")
    
    emotions = [
        ("L'émotion d'arrivée", "Regard droit, sourire, bonne poignée de main, prestance et énergie communicative."),
        ("L'émotion à la vente", "Comme un nouvel achat qu'on s'empresse d'utiliser. \"Vivement que l'aventure commence!\""),
        ("L'émotion de départ", "Votre énergie doit encore être présente une fois parti. \"J'ai saisi là une occasion!\""),
    ]
    
    for title, desc in emotions:
        c.setFillColor(PRIMARY_BLACK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN + 5*mm, y, title)
        y -= 5*mm
        c.setFillColor(ACCENT_GRAY)
        c.setFont("Helvetica", 9)
        lines = textwrap.wrap(desc, width=80)
        for line in lines:
            c.drawString(MARGIN + 10*mm, y, line)
            y -= 4*mm
        y -= 3*mm
    
    y -= 5*mm
    y = draw_section_title(c, y, "Points clés")
    
    key_points = [
        "S'adapter à son interlocuteur, le mettre à l'aise",
        "Employer un vocabulaire significatif et positif",
        "Adapter les RDV selon les contextes (fermetures, fatigues, charges)",
        "Ne pas prendre un rejet personnellement",
        "Le client doit se sentir spécial"
    ]
    
    for point in key_points:
        y = draw_bullet_point(c, y, point)
    
    draw_footer(c, 3, 3)
    c.save()
    print(f"✅ {output_path}")
    return output_path


def create_prospect_tel_pdf():
    """Create the Prospect Téléphonique PDF"""
    output_path = "/app/backend/uploads/fiche_prospect_telephonique.pdf"
    c = canvas.Canvas(output_path, pagesize=A4)
    
    # PAGE 1
    draw_header(c, "Prospect Téléphonique")
    y = PAGE_HEIGHT - 55 * mm
    
    # Matériel
    y = draw_section_title(c, y, "Matériel nécessaire")
    for item in ["Téléphone", "Brochure", "App interne de gestion des rendez-vous"]:
        y = draw_bullet_point(c, y, item)
    
    y -= 5*mm
    y = draw_section_title(c, y, "Clients cibles")
    for item in ["Petits prestataires et commerçants", "Site web mal élaboré ou absent", "Nouveaux commerces / reprises"]:
        y = draw_bullet_point(c, y, item)
    
    y -= 5*mm
    y = draw_section_title(c, y, "Objectif")
    y = draw_highlight_box(c, y, "Fixer des rendez-vous clients", height=10*mm)
    
    y -= 5*mm
    y = draw_section_title(c, y, "Script d'appel - Présentation")
    
    c.setFillColor(LIGHT_GRAY)
    c.roundRect(MARGIN, y - 35*mm, CONTENT_WIDTH, 38*mm, 3, fill=1, stroke=0)
    
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Helvetica-Oblique", 9)
    script1 = [
        "\"Bonjour, je suis [nom/prénom] chargé de communication pour l'application",
        "Titelli. Serait-ce possible de parler à un responsable ?",
        "",
        "Nous représentons une application Suisse spécialisée dans la gestion des",
        "prestataires régionaux.\"",
        "",
        "\"Je me permets de vous appeler rapidement — vous êtes bien responsable de",
        "l'entreprise [Nom] basée à [Ville] ? Parfait !\""
    ]
    text_y = y - 2*mm
    for line in script1:
        c.drawString(MARGIN + 4*mm, text_y, line)
        text_y -= 4*mm
    y -= 42*mm
    
    y = draw_section_title(c, y, "Script d'appel - Créer l'intérêt")
    
    c.setFillColor(LIGHT_GRAY)
    c.roundRect(MARGIN, y - 30*mm, CONTENT_WIDTH, 33*mm, 3, fill=1, stroke=0)
    
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Helvetica-Oblique", 9)
    script2 = [
        "\"Titelli est une application 100% Suisse qui permet de mettre en avant les",
        "meilleurs prestataires de la région auprès d'un nouveau public — habitants,",
        "touristes et nouveaux arrivants.",
        "",
        "Le but est simple : rendre les prestataires plus visibles, leur générer de",
        "nouveaux revenus significatifs et des contacts qualifiés.\""
    ]
    text_y = y - 2*mm
    for line in script2:
        c.drawString(MARGIN + 4*mm, text_y, line)
        text_y -= 4*mm
    
    draw_footer(c, 1, 2)
    c.showPage()
    
    # PAGE 2
    draw_header(c, "Prospect Téléphonique")
    y = PAGE_HEIGHT - 55 * mm
    
    y = draw_section_title(c, y, "Script d'appel - Proposer le RDV")
    
    c.setFillColor(LIGHT_GRAY)
    c.roundRect(MARGIN, y - 28*mm, CONTENT_WIDTH, 31*mm, 3, fill=1, stroke=0)
    
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Helvetica-Oblique", 9)
    script3 = [
        "\"Auriez-vous 5 minutes à accorder à un chargé de communication cette",
        "semaine ? C'est sans engagement et votre profil amène du monde dès activation.",
        "",
        "Cette semaine je n'ai de disponibilité qu'à partir de [proposer 2 créneaux :",
        "jeudi matin ou vendredi après-midi] ? Par exemple !\""
    ]
    text_y = y - 2*mm
    for line in script3:
        c.drawString(MARGIN + 4*mm, text_y, line)
        text_y -= 4*mm
    y -= 35*mm
    
    c.setFillColor(ACCENT_GRAY)
    c.setFont("Helvetica", 8)
    c.drawString(MARGIN, y, "→ Réunir les RDV sur les mêmes journées pour éviter les déplacements inutiles")
    y -= 5*mm
    c.drawString(MARGIN, y, "→ Si refus : demander une adresse mail pour envoyer une mini vidéo")
    
    y -= 10*mm
    y = draw_section_title(c, y, "Arguments clés")
    
    arguments = [
        "Investir régulièrement permet de ne pas se laisser dépasser par les tendances",
        "Être exposé uniquement sur son site limite l'accès à ceux qui vous connaissent",
        "Système de Cash-Back inclus - très attrayant pour les clients",
        "Système de gestion des stocks avec suggestions par algorithmes",
        "Publier une offre permet de contrôler l'écoulement du stock",
        "Notre objectif : regrouper les meilleurs prestataires chez Titelli !"
    ]
    
    for arg in arguments:
        y = draw_bullet_point(c, y, arg)
    
    y -= 8*mm
    y = draw_section_title(c, y, "Conseils pratiques")
    
    conseils = [
        "Personnalisez au maximum l'intro (nom, secteur, ville)",
        "Ayez une tonalité dynamique mais respectueuse",
        "Soyez prêt à envoyer une présentation après l'appel"
    ]
    
    for conseil in conseils:
        y = draw_bullet_point(c, y, conseil)
    
    draw_footer(c, 2, 2)
    c.save()
    print(f"✅ {output_path}")
    return output_path


if __name__ == "__main__":
    create_prospect_rdv_pdf()
    create_prospect_tel_pdf()
    print("✅ Fiches de formation créées!")
