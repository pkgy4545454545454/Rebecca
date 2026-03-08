from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Colors
PRIMARY_BLACK = HexColor("#1a1a1a")
ACCENT_GRAY = HexColor("#666666")
BORDER_GRAY = HexColor("#e0e0e0")
GOLD = HexColor("#D4AF37")
BLUE = HexColor("#0047AB")

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 20 * mm

def draw_header(c, title, subtitle=""):
    """En-tête avec logo et slogan"""
    # Ligne séparatrice
    c.setStrokeColor(BORDER_GRAY)
    c.setLineWidth(0.5)
    c.line(MARGIN, PAGE_HEIGHT - 50 * mm, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 50 * mm)
    
    # Logo
    try:
        logo = ImageReader("/app/backend/uploads/logo_titelli_noir_v2.png")
        c.drawImage(logo, MARGIN, PAGE_HEIGHT - 22 * mm, width=14 * mm, height=14 * mm, mask='auto')
    except:
        pass
    
    # Titelli
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Times-Roman", 16)
    c.drawString(MARGIN + 17 * mm, PAGE_HEIGHT - 14 * mm, "Titelli")
    
    # Slogan
    c.setFillColor(ACCENT_GRAY)
    c.setFont("Helvetica-Oblique", 7)
    c.drawString(MARGIN + 17 * mm, PAGE_HEIGHT - 20 * mm, 
                 "Tous les prestataires préférés de votre région se trouvent sur Titelli")
    
    # Titre du document
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(MARGIN, PAGE_HEIGHT - 38 * mm)
    
    # Draw title with potential line break
    title_lines = title.split('\n')
    y_pos = PAGE_HEIGHT - 36 * mm
    for line in title_lines:
        c.drawString(MARGIN, y_pos, line)
        y_pos -= 8 * mm
    
    # Subtitle
    if subtitle:
        c.setFillColor(ACCENT_GRAY)
        c.setFont("Helvetica-Oblique", 11)
        c.drawString(MARGIN, PAGE_HEIGHT - 46 * mm, subtitle)


def draw_footer(c, page_num=1, total_pages=1):
    """Pied de page"""
    c.setStrokeColor(BORDER_GRAY)
    c.setLineWidth(0.5)
    c.line(MARGIN, 15 * mm, PAGE_WIDTH - MARGIN, 15 * mm)
    
    c.setFillColor(ACCENT_GRAY)
    c.setFont("Helvetica", 8)
    c.drawString(MARGIN, 10 * mm, "Document de formation interne - Titelli SA")
    c.drawRightString(PAGE_WIDTH - MARGIN, 10 * mm, f"Page {page_num}/{total_pages}")


def draw_section_title(c, y, title):
    """Titre de section avec ligne décorative"""
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(MARGIN, y, title)
    
    # Ligne sous le titre
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.line(MARGIN, y - 3 * mm, MARGIN + 50 * mm, y - 3 * mm)
    
    return y - 10 * mm


def draw_bullet_point(c, y, text, indent=0):
    """Point avec bullet"""
    bullet_x = MARGIN + indent * mm
    c.setFillColor(GOLD)
    c.circle(bullet_x + 2 * mm, y + 1.5 * mm, 1.5 * mm, fill=1)
    
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Helvetica", 10)
    c.drawString(bullet_x + 7 * mm, y, text)
    
    return y - 6 * mm


def draw_text(c, y, text, bold=False):
    """Texte simple"""
    c.setFillColor(PRIMARY_BLACK)
    if bold:
        c.setFont("Helvetica-Bold", 10)
    else:
        c.setFont("Helvetica", 10)
    c.drawString(MARGIN, y, text)
    return y - 5 * mm


# ============================================
# PDF 1: Guide de Prospection Téléphonique
# ============================================
def create_prospection_pdf():
    output_path = "/app/backend/uploads/01_Prospection_Telephonique_Titelli.pdf"
    c = canvas.Canvas(output_path, pagesize=A4)
    
    # Page 1 - Titre
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Times-Roman", 16)
    c.drawString(MARGIN + 17 * mm, PAGE_HEIGHT - 14 * mm, "Titelli")
    
    try:
        logo = ImageReader("/app/backend/uploads/logo_titelli_noir_v2.png")
        c.drawImage(logo, MARGIN, PAGE_HEIGHT - 22 * mm, width=14 * mm, height=14 * mm, mask='auto')
    except:
        pass
    
    c.setFillColor(ACCENT_GRAY)
    c.setFont("Helvetica-Oblique", 7)
    c.drawString(MARGIN + 17 * mm, PAGE_HEIGHT - 20 * mm, 
                 "Tous les prestataires préférés de votre région se trouvent sur Titelli")
    
    # Main title centered
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 + 20 * mm, "Guide de Prospection")
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 + 8 * mm, "Téléphonique")
    
    c.setFillColor(ACCENT_GRAY)
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 5 * mm, "Méthodologie commerciale structurée")
    
    # Decorative line
    c.setStrokeColor(GOLD)
    c.setLineWidth(3)
    c.line(PAGE_WIDTH / 2 - 40 * mm, PAGE_HEIGHT / 2 - 15 * mm, PAGE_WIDTH / 2 + 40 * mm, PAGE_HEIGHT / 2 - 15 * mm)
    
    draw_footer(c, 1, 2)
    c.showPage()
    
    # Page 2 - Contenu
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Times-Roman", 16)
    c.drawString(MARGIN + 17 * mm, PAGE_HEIGHT - 14 * mm, "Titelli")
    
    try:
        logo = ImageReader("/app/backend/uploads/logo_titelli_noir_v2.png")
        c.drawImage(logo, MARGIN, PAGE_HEIGHT - 22 * mm, width=14 * mm, height=14 * mm, mask='auto')
    except:
        pass
    
    c.setStrokeColor(BORDER_GRAY)
    c.setLineWidth(0.5)
    c.line(MARGIN, PAGE_HEIGHT - 28 * mm, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 28 * mm)
    
    y = PAGE_HEIGHT - 40 * mm
    
    # Section 1
    y = draw_section_title(c, y, "Objectif stratégique")
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Helvetica", 10)
    text = "Créer un intérêt immédiat et fixer des rendez-vous qualifiés en valorisant"
    c.drawString(MARGIN, y, text)
    y -= 5 * mm
    text = "la visibilité et la rentabilité apportées par Titelli."
    c.drawString(MARGIN, y, text)
    y -= 12 * mm
    
    # Section 2
    y = draw_section_title(c, y, "Cibles prioritaires")
    y = draw_bullet_point(c, y, "Petits commerçants et prestataires régionaux")
    y = draw_bullet_point(c, y, "Entreprises avec faible visibilité digitale")
    y = draw_bullet_point(c, y, "Nouveaux commerces ou reprises")
    y -= 8 * mm
    
    # Section 3
    y = draw_section_title(c, y, "Arguments différenciants")
    y = draw_bullet_point(c, y, "Visibilité auprès d'un public qualifié")
    y = draw_bullet_point(c, y, "Revenus supplémentaires")
    y = draw_bullet_point(c, y, "Outils de gestion intégrés")
    y = draw_bullet_point(c, y, "Optimisation marketing et stocks")
    
    draw_footer(c, 2, 2)
    c.save()
    print(f"✅ {output_path}")
    return output_path


# ============================================
# PDF 2: Questionnaire de Formation
# ============================================
def create_questionnaire_pdf():
    output_path = "/app/backend/uploads/02_Questionnaire_Formation_Titelli.pdf"
    c = canvas.Canvas(output_path, pagesize=A4)
    
    # Page 1 - Titre
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Times-Roman", 16)
    c.drawString(MARGIN + 17 * mm, PAGE_HEIGHT - 14 * mm, "Titelli")
    
    try:
        logo = ImageReader("/app/backend/uploads/logo_titelli_noir_v2.png")
        c.drawImage(logo, MARGIN, PAGE_HEIGHT - 22 * mm, width=14 * mm, height=14 * mm, mask='auto')
    except:
        pass
    
    c.setFillColor(ACCENT_GRAY)
    c.setFont("Helvetica-Oblique", 7)
    c.drawString(MARGIN + 17 * mm, PAGE_HEIGHT - 20 * mm, 
                 "Tous les prestataires préférés de votre région se trouvent sur Titelli")
    
    # Main title
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 + 20 * mm, "Questionnaire de")
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 + 8 * mm, "Formation")
    
    c.setFillColor(ACCENT_GRAY)
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 5 * mm, "Évaluation des compétences commerciales")
    
    c.setStrokeColor(GOLD)
    c.setLineWidth(3)
    c.line(PAGE_WIDTH / 2 - 40 * mm, PAGE_HEIGHT / 2 - 15 * mm, PAGE_WIDTH / 2 + 40 * mm, PAGE_HEIGHT / 2 - 15 * mm)
    
    draw_footer(c, 1, 2)
    c.showPage()
    
    # Page 2 - Contenu
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Times-Roman", 16)
    c.drawString(MARGIN + 17 * mm, PAGE_HEIGHT - 14 * mm, "Titelli")
    
    try:
        logo = ImageReader("/app/backend/uploads/logo_titelli_noir_v2.png")
        c.drawImage(logo, MARGIN, PAGE_HEIGHT - 22 * mm, width=14 * mm, height=14 * mm, mask='auto')
    except:
        pass
    
    c.setStrokeColor(BORDER_GRAY)
    c.setLineWidth(0.5)
    c.line(MARGIN, PAGE_HEIGHT - 28 * mm, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 28 * mm)
    
    y = PAGE_HEIGHT - 40 * mm
    
    # Section 1
    y = draw_section_title(c, y, "Maîtrise commerciale")
    y = draw_bullet_point(c, y, "Analyse préalable du client")
    y = draw_bullet_point(c, y, "Adaptation stratégique des arguments")
    y = draw_bullet_point(c, y, "Moments clés d'une vente réussie")
    y -= 12 * mm
    
    # Section 2
    y = draw_section_title(c, y, "Conclusion & suivi")
    y = draw_bullet_point(c, y, "Gestion des objections")
    y = draw_bullet_point(c, y, "Clôture engageante")
    y = draw_bullet_point(c, y, "Suivi post rendez-vous structuré")
    
    draw_footer(c, 2, 2)
    c.save()
    print(f"✅ {output_path}")
    return output_path


# ============================================
# PDF 3: Guide de Vente en Rendez-Vous Client
# ============================================
def create_guide_rdv_pdf():
    output_path = "/app/backend/uploads/03_Guide_RendezVous_Client_Titelli.pdf"
    c = canvas.Canvas(output_path, pagesize=A4)
    
    # Page 1 - Titre
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Times-Roman", 16)
    c.drawString(MARGIN + 17 * mm, PAGE_HEIGHT - 14 * mm, "Titelli")
    
    try:
        logo = ImageReader("/app/backend/uploads/logo_titelli_noir_v2.png")
        c.drawImage(logo, MARGIN, PAGE_HEIGHT - 22 * mm, width=14 * mm, height=14 * mm, mask='auto')
    except:
        pass
    
    c.setFillColor(ACCENT_GRAY)
    c.setFont("Helvetica-Oblique", 7)
    c.drawString(MARGIN + 17 * mm, PAGE_HEIGHT - 20 * mm, 
                 "Tous les prestataires préférés de votre région se trouvent sur Titelli")
    
    # Main title
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 + 25 * mm, "Guide de Vente en")
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 + 13 * mm, "Rendez-Vous Client")
    
    c.setFillColor(ACCENT_GRAY)
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2, "Processus premium & expérience émotionnelle")
    
    c.setStrokeColor(GOLD)
    c.setLineWidth(3)
    c.line(PAGE_WIDTH / 2 - 40 * mm, PAGE_HEIGHT / 2 - 12 * mm, PAGE_WIDTH / 2 + 40 * mm, PAGE_HEIGHT / 2 - 12 * mm)
    
    draw_footer(c, 1, 2)
    c.showPage()
    
    # Page 2 - Contenu
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Times-Roman", 16)
    c.drawString(MARGIN + 17 * mm, PAGE_HEIGHT - 14 * mm, "Titelli")
    
    try:
        logo = ImageReader("/app/backend/uploads/logo_titelli_noir_v2.png")
        c.drawImage(logo, MARGIN, PAGE_HEIGHT - 22 * mm, width=14 * mm, height=14 * mm, mask='auto')
    except:
        pass
    
    c.setStrokeColor(BORDER_GRAY)
    c.setLineWidth(0.5)
    c.line(MARGIN, PAGE_HEIGHT - 28 * mm, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 28 * mm)
    
    y = PAGE_HEIGHT - 40 * mm
    
    # Section 1
    y = draw_section_title(c, y, "Préparation stratégique")
    y = draw_bullet_point(c, y, "Analyse du positionnement")
    y = draw_bullet_point(c, y, "Identification du public cible")
    y = draw_bullet_point(c, y, "Évaluation qualité et disponibilité")
    y -= 12 * mm
    
    # Section 2
    y = draw_section_title(c, y, "Déroulement du rendez-vous")
    y = draw_bullet_point(c, y, "Créer une émotion positive")
    y = draw_bullet_point(c, y, "Présentation du concept")
    y = draw_bullet_point(c, y, "Démonstration et accompagnement")
    y = draw_bullet_point(c, y, "Explication des bénéfices")
    
    draw_footer(c, 2, 2)
    c.save()
    print(f"✅ {output_path}")
    return output_path


if __name__ == "__main__":
    create_prospection_pdf()
    create_questionnaire_pdf()
    create_guide_rdv_pdf()
    print("\n✅ Les 3 PDFs ont été générés avec succès!")
