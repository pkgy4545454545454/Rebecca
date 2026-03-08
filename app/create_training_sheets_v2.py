from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm
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
    c.setStrokeColor(BORDER_GRAY)
    c.setLineWidth(0.5)
    c.line(MARGIN, PAGE_HEIGHT - 45 * mm, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 45 * mm)
    
    logo = ImageReader("/app/backend/uploads/logo_titelli_noir_v2.png")
    logo_height = 12 * mm
    logo_width = 12 * mm
    c.drawImage(logo, MARGIN, PAGE_HEIGHT - 20 * mm, width=logo_width, height=logo_height, mask='auto')
    
    # Titelli - même style que logo (serif, élégant)
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Times-Roman", 14)
    c.drawString(MARGIN + logo_width + 3 * mm, PAGE_HEIGHT - 14 * mm, "Titelli")
    
    c.setFillColor(ACCENT_GRAY)
    c.setFont("Helvetica-Oblique", 7)
    c.drawString(MARGIN + logo_width + 3 * mm, PAGE_HEIGHT - 19 * mm, 
                 "Tous les prestataires préférés de votre région se trouvent sur Titelli")
    
    # Titre avec bonne casse
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(MARGIN, PAGE_HEIGHT - 38 * mm, title)


def draw_footer(c, page_num, total_pages):
    c.setStrokeColor(BORDER_GRAY)
    c.setLineWidth(0.5)
    c.line(MARGIN, 15 * mm, PAGE_WIDTH - MARGIN, 15 * mm)
    
    c.setFillColor(ACCENT_GRAY)
    c.setFont("Helvetica", 8)
    c.drawString(MARGIN, 10 * mm, "Document de formation interne - Titelli SA")
    c.drawRightString(PAGE_WIDTH - MARGIN, 10 * mm, f"Page {page_num}/{total_pages}")


def draw_section_title(c, y, title):
    # Titre de section simple sans bloc noir
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, title)
    return y - 8 * mm


def draw_bullet_point(c, y, text, indent=0, is_sub=False):
    x = MARGIN + 5 * mm + indent * 5 * mm
    
    if is_sub:
        c.setFillColor(ACCENT_GRAY)
        c.setFont("Helvetica", 8)
        bullet = "○"
    else:
        c.setFillColor(PRIMARY_BLACK)
        c.setFont("Helvetica", 9)
        bullet = "●"
    
    c.drawString(x, y, bullet)
    text_x = x + 4 * mm
    max_width = CONTENT_WIDTH - indent * 5 * mm - 10 * mm
    
    words = text.split()
    lines = []
    current_line = ""
    font_size = 8 if is_sub else 9
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if c.stringWidth(test_line, "Helvetica", font_size) < max_width:
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
    c.setFillColor(LIGHT_GRAY)
    c.roundRect(MARGIN, y - height + 3*mm, CONTENT_WIDTH, height, 3, fill=1, stroke=0)
    
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Helvetica-Oblique", 9)
    
    lines = textwrap.wrap(text, width=90)
    text_y = y - 2*mm
    for line in lines[:4]:
        c.drawString(MARGIN + 4*mm, text_y, line)
        text_y -= 4*mm
    
    return y - height - 3*mm


def create_prospect_rdv_v2_pdf():
    """Create the Prospect Rendez-vous client V2 PDF"""
    output_path = "/app/backend/uploads/fiche_prospect_rdv_client_v2.pdf"
    c = canvas.Canvas(output_path, pagesize=A4)
    
    # PAGE 1
    draw_header(c, "Prospect Rendez-vous Client")
    y = PAGE_HEIGHT - 55 * mm
    
    y = draw_section_title(c, y, "Procédé de vente en rendez-vous")
    
    items_page1 = [
        ("Prendre connaissance du prestataire", []),
        ("Préparer ses arguments correspondants", [
            "Identifier le public cible (si exigeants : labellisés ! Si accessibles : nos offres !)",
            "La qualité du produit ou service - Soyez reconnu pour votre savoir-faire !",
            "La disponibilité - Livraison à domicile en tout temps ?",
            "Le marché - Connaissez-vous tous les clients de votre domaine ?"
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
            "Optimisation entreprise starter + critères labellisation"
        ]),
    ]
    
    for item, subitems in items_page1:
        y = draw_bullet_point(c, y, item)
        for subitem in subitems:
            y = draw_bullet_point(c, y, subitem, indent=1, is_sub=True)
        if y < 40 * mm:
            break
    
    draw_footer(c, 1, 4)
    c.showPage()
    
    # PAGE 2
    draw_header(c, "Prospect Rendez-vous Client")
    y = PAGE_HEIGHT - 55 * mm
    
    y = draw_section_title(c, y, "Suite du procédé")
    
    items_page2 = [
        ("Accompagner création profil prestataire", ["Montrer comment compléter son profil"]),
        ("Vidéos formation prestataires", []),
        ("Expliquer comment faire des revenus avec Titelli", ["Rentabilité instantanée + page publicité"]),
        ("Gift Titelli partenaire", []),
        ("Autocollant sur la porte + caisse", ["Optimiser visibilité et faire plus de ventes"]),
        ("Flyers en caisse", []),
        ("Demander des recommandations", ["Collègues de métier à qui nous recommander ?"]),
        ("Proposer un geste commercial", ["Les nouveaux clients Titelli apprécient !"]),
        ("Remettre carte de visite", ["Je me tiens à votre entière disposition"]),
        ("Émotion de départ positive", ["Merci de votre confiance, c'est un honneur de collaborer"]),
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
        "Prenez le temps de découvrir Titelli, je vous laisse ma carte. Ce fût agréable de partager la vision Titelli avec vous.\"",
        height=16*mm)
    
    draw_footer(c, 2, 4)
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
        ("L'émotion d'arrivée", "Regard droit, sourire, bonne poignée de main, prestance et énergie communicative. S'adapter à son interlocuteur."),
        ("L'émotion à la vente", "Comme un nouvel achat qu'on s'empresse d'utiliser. \"Vivement que l'aventure commence!\" Accompagner la création de son profil."),
        ("L'émotion de départ", "Votre énergie doit encore être présente une fois parti. \"J'ai saisi là une occasion!\" ou \"J'ai peut-être manqué une occasion\"."),
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
        "Ne pas prendre un rejet personnellement - hauteur d'esprit",
        "Le client doit se sentir spécial"
    ]
    
    for point in key_points:
        y = draw_bullet_point(c, y, point)
    
    draw_footer(c, 3, 4)
    c.showPage()
    
    # PAGE 4 - Arguments et éléments d'influence
    draw_header(c, "Prospect Rendez-vous Client")
    y = PAGE_HEIGHT - 55 * mm
    
    y = draw_section_title(c, y, "Argument brochure")
    y = draw_highlight_box(c, y,
        "\"Rendez-vous compte que le tout est accessible pour seulement 250.- et est valable une année !\"",
        height=10*mm)
    
    y -= 5*mm
    y = draw_section_title(c, y, "Éléments d'influence et force de Titelli")
    
    elements = [
        "Titelli regroupe les meilleurs prestataires de la région, Faites-en partie !",
        "Titelli accompagne ses clients tout au long de leur journée de consommation",
        "Devenez la recommandation préférée de Titelli !"
    ]
    
    for elem in elements:
        y = draw_bullet_point(c, y, elem)
    
    y -= 8*mm
    y = draw_section_title(c, y, "Question de clôture")
    y = draw_highlight_box(c, y,
        "\"Qu'avez-vous fait pour vous investir sur votre entreprise cette année ? "
        "Savez-vous qu'avec Titelli, vous faites un retour sur investissement le premier mois ? "
        "Et votre compte est valable sur une durée d'une année !\"",
        height=18*mm)
    
    draw_footer(c, 4, 4)
    c.save()
    print(f"✅ {output_path}")
    return output_path


def create_prospect_tel_v2_pdf():
    """Create the Prospect Téléphonique V2 PDF"""
    output_path = "/app/backend/uploads/fiche_prospect_telephonique_v2.pdf"
    c = canvas.Canvas(output_path, pagesize=A4)
    
    # PAGE 1
    draw_header(c, "Prospect Téléphonique")
    y = PAGE_HEIGHT - 55 * mm
    
    y = draw_section_title(c, y, "Matériel nécessaire")
    for item in ["Téléphone", "Brochure", "App interne de gestion des rendez-vous clients"]:
        y = draw_bullet_point(c, y, item)
    
    y -= 3*mm
    y = draw_section_title(c, y, "Procédé")
    for item in ["Repérer les petits commerçants/prestataires et en apprendre sur eux", 
                 "Contacter l'entreprise et demander un responsable",
                 "Fixer le rendez-vous client"]:
        y = draw_bullet_point(c, y, item)
    
    y -= 3*mm
    y = draw_section_title(c, y, "Clients cibles")
    for item in ["Petits prestataires et commerçants", "Site web mal élaboré ou absent", "Nouveaux commerces / reprises"]:
        y = draw_bullet_point(c, y, item)
    
    y -= 3*mm
    y = draw_section_title(c, y, "Objectif")
    y = draw_highlight_box(c, y, "Fixer des rendez-vous clients", height=10*mm)
    
    y -= 3*mm
    y = draw_section_title(c, y, "Script - Présentation et capter l'attention")
    
    c.setFillColor(LIGHT_GRAY)
    c.roundRect(MARGIN, y - 38*mm, CONTENT_WIDTH, 41*mm, 3, fill=1, stroke=0)
    
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
        "l'entreprise [Nom] basée à [Ville/Région] ? Parfait !\""
    ]
    text_y = y - 2*mm
    for line in script1:
        c.drawString(MARGIN + 4*mm, text_y, line)
        text_y -= 4*mm
    
    draw_footer(c, 1, 2)
    c.showPage()
    
    # PAGE 2
    draw_header(c, "Prospect Téléphonique")
    y = PAGE_HEIGHT - 55 * mm
    
    y = draw_section_title(c, y, "Script - Créer l'intérêt")
    
    c.setFillColor(LIGHT_GRAY)
    c.roundRect(MARGIN, y - 38*mm, CONTENT_WIDTH, 41*mm, 3, fill=1, stroke=0)
    
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Helvetica-Oblique", 9)
    script2 = [
        "\"Titelli est une application 100% Suisse qui permet de mettre en avant les",
        "meilleurs prestataires de la région auprès d'un nouveau public — habitants,",
        "touristes et nouveaux arrivants.",
        "",
        "Le but est simple : rendre les prestataires plus visibles, leur générer de",
        "nouveaux revenus significatifs et des contacts qualifiés.",
        "",
        "Nos clients bénéficient aussi gratuitement de multiples outils de gestion.\""
    ]
    text_y = y - 2*mm
    for line in script2:
        c.drawString(MARGIN + 4*mm, text_y, line)
        text_y -= 4*mm
    y -= 45*mm
    
    y = draw_section_title(c, y, "Script - Proposer le RDV")
    
    c.setFillColor(LIGHT_GRAY)
    c.roundRect(MARGIN, y - 32*mm, CONTENT_WIDTH, 35*mm, 3, fill=1, stroke=0)
    
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Helvetica-Oblique", 9)
    script3 = [
        "\"Auriez-vous 5 minutes à accorder à un chargé de communication cette",
        "semaine ? C'est sans engagement et votre profil amène du monde dès activation.",
        "",
        "Cette semaine je n'ai de disponibilité qu'à partir de [proposer 2 créneaux :",
        "jeudi matin ou vendredi après-midi] ? Par exemple !\"",
    ]
    text_y = y - 2*mm
    for line in script3:
        c.drawString(MARGIN + 4*mm, text_y, line)
        text_y -= 4*mm
    y -= 38*mm
    
    c.setFillColor(ACCENT_GRAY)
    c.setFont("Helvetica", 8)
    c.drawString(MARGIN, y, "→ Réunir les RDV sur les mêmes journées pour éviter les déplacements inutiles")
    y -= 5*mm
    c.drawString(MARGIN, y, "→ Si refus : demander une adresse mail pour envoyer une mini vidéo divertissante")
    
    y -= 8*mm
    y = draw_section_title(c, y, "Arguments clés")
    
    arguments = [
        "Investir régulièrement permet de ne pas se laisser dépasser par les tendances",
        "Être exposé uniquement sur son site limite l'accès à ceux qui vous connaissent",
        "Système de Cash-Back inclus - très attrayant pour les clients",
        "Système de gestion des stocks avec suggestions par algorithmes et experts",
        "Se rendre accessible impacte directement l'économie ET l'image",
        "Publier une offre permet de contrôler l'écoulement du stock"
    ]
    
    for arg in arguments:
        y = draw_bullet_point(c, y, arg)
        if y < 25*mm:
            break
    
    draw_footer(c, 2, 2)
    c.save()
    print(f"✅ {output_path}")
    return output_path


if __name__ == "__main__":
    create_prospect_rdv_v2_pdf()
    create_prospect_tel_v2_pdf()
    print("✅ Fiches V2 créées!")
