from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm

# Colors
PRIMARY_BLACK = HexColor("#1a1a1a")
ACCENT_GRAY = HexColor("#666666")
BORDER_GRAY = HexColor("#e0e0e0")

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 20 * mm

def draw_header(c, title):
    """En-tête avec logo et slogan"""
    # Ligne séparatrice
    c.setStrokeColor(BORDER_GRAY)
    c.setLineWidth(0.5)
    c.line(MARGIN, PAGE_HEIGHT - 45 * mm, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 45 * mm)
    
    # Logo
    logo = ImageReader("/app/backend/uploads/logo_titelli_noir_v2.png")
    c.drawImage(logo, MARGIN, PAGE_HEIGHT - 20 * mm, width=12 * mm, height=12 * mm, mask='auto')
    
    # Titelli
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Times-Roman", 14)
    c.drawString(MARGIN + 15 * mm, PAGE_HEIGHT - 14 * mm, "Titelli")
    
    # Slogan
    c.setFillColor(ACCENT_GRAY)
    c.setFont("Helvetica-Oblique", 7)
    c.drawString(MARGIN + 15 * mm, PAGE_HEIGHT - 19 * mm, 
                 "Tous les prestataires préférés de votre région se trouvent sur Titelli")
    
    # Titre du document
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(MARGIN, PAGE_HEIGHT - 38 * mm, title)


def draw_footer(c, page_num=1, total_pages=1):
    """Pied de page"""
    c.setStrokeColor(BORDER_GRAY)
    c.setLineWidth(0.5)
    c.line(MARGIN, 15 * mm, PAGE_WIDTH - MARGIN, 15 * mm)
    
    c.setFillColor(ACCENT_GRAY)
    c.setFont("Helvetica", 8)
    c.drawString(MARGIN, 10 * mm, "Document de formation interne - Titelli SA")
    c.drawRightString(PAGE_WIDTH - MARGIN, 10 * mm, f"Page {page_num}/{total_pages}")


def create_template(output_path="/app/backend/uploads/modele_titelli.pdf", title="Titre du document"):
    """Créer un modèle vide avec en-tête et pied de page"""
    c = canvas.Canvas(output_path, pagesize=A4)
    
    draw_header(c, title)
    draw_footer(c, 1, 1)
    
    c.save()
    print(f"✅ {output_path}")
    return output_path


if __name__ == "__main__":
    create_template()
