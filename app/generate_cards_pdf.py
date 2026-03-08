from reportlab.lib.pagesizes import A4, mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, black, white
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageOps
import os

# Business card dimensions (standard: 85mm x 55mm)
CARD_WIDTH = 85 * mm
CARD_HEIGHT = 55 * mm

# Colors
GOLD_TEXT = Color(0.75, 0.72, 0.55)
LIGHT_TEXT = Color(0.6, 0.6, 0.6)

# Image paths
LOGO_NOIR_PATH = "/app/backend/uploads/logo_titelli_noir.png"
LOGO_BLANC_PATH = "/app/backend/uploads/logo_titelli_blanc.png"


def create_inverted_logo():
    """Create white version of the logo (inverted colors)"""
    img = Image.open(LOGO_NOIR_PATH).convert("RGBA")
    
    # Split into channels
    r, g, b, a = img.split()
    
    # Invert RGB channels
    r = ImageOps.invert(r)
    g = ImageOps.invert(g)
    b = ImageOps.invert(b)
    
    # Merge back
    inverted = Image.merge("RGBA", (r, g, b, a))
    inverted.save(LOGO_BLANC_PATH)
    print(f"Inverted logo created: {LOGO_BLANC_PATH}")


def draw_front_card(c, x, y, is_white_version=False):
    """Draw front card - just the image, nothing else"""
    if is_white_version:
        logo_path = LOGO_BLANC_PATH
    else:
        logo_path = LOGO_NOIR_PATH
    
    # Draw image directly at card dimensions - PURE image
    img = ImageReader(logo_path)
    c.drawImage(img, x, y, width=CARD_WIDTH, height=CARD_HEIGHT)


def draw_back_card(c, x, y, is_white_version=False):
    """Draw back card with contact info"""
    # Background and colors
    if is_white_version:
        c.setFillColor(white)
        c.rect(x, y, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        text_color_main = black
        text_color_secondary = Color(0.3, 0.3, 0.3)
    else:
        c.setFillColor(black)
        c.rect(x, y, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        text_color_main = white  # Changed to WHITE instead of gold
        text_color_secondary = Color(0.85, 0.85, 0.85)  # Light white/gray
    
    # Margins
    left_margin = x + 10 * mm
    right_margin = x + CARD_WIDTH - 10 * mm
    
    # Name - Leila Hassini
    c.setFillColor(text_color_main)
    c.setFont("Helvetica", 12)
    nom_y = y + CARD_HEIGHT - 18 * mm
    c.drawString(left_margin, nom_y, "L E I L A   H A S S I N I")
    
    # Function - Founder
    c.setFillColor(text_color_secondary)
    c.setFont("Helvetica", 6)
    titre_y = nom_y - 4 * mm
    c.drawString(left_margin, titre_y, "F O U N D E R")
    
    # Bottom row
    bottom_row1 = y + 14 * mm
    bottom_row2 = y + 10 * mm
    
    # LEFT COLUMN
    c.drawString(left_margin, bottom_row1, "téléphone / autre")
    c.drawString(left_margin, bottom_row2, "www.titelli.com")
    
    # RIGHT COLUMN
    c.drawRightString(right_margin, bottom_row1, "info@titelli.com")
    c.drawRightString(right_margin, bottom_row2, "@reseauxsociaux")


def create_complete_pdf(output_path):
    """Create PDF with all business card versions"""
    c = canvas.Canvas(output_path, pagesize=A4)
    page_width, page_height = A4
    
    # Spacing
    margin = 20 * mm
    spacing = 15 * mm
    
    # === VERSION NOIRE (Avant noir + Arrière noir) ===
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(black)
    c.drawString(margin, page_height - 30 * mm, "VERSION NOIRE")
    
    c.setFont("Helvetica", 10)
    c.drawString(margin, page_height - 40 * mm, "Face avant")
    draw_front_card(c, margin, page_height - 45 * mm - CARD_HEIGHT, is_white_version=False)
    
    c.drawString(margin + CARD_WIDTH + spacing, page_height - 40 * mm, "Face arrière")
    draw_back_card(c, margin + CARD_WIDTH + spacing, page_height - 45 * mm - CARD_HEIGHT, is_white_version=False)
    
    # === VERSION BLANCHE (Avant blanc + Arrière blanc) ===
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, page_height - 120 * mm, "VERSION BLANCHE")
    
    c.setFont("Helvetica", 10)
    c.drawString(margin, page_height - 130 * mm, "Face avant")
    draw_front_card(c, margin, page_height - 135 * mm - CARD_HEIGHT, is_white_version=True)
    
    c.drawString(margin + CARD_WIDTH + spacing, page_height - 130 * mm, "Face arrière")
    # Border for visibility
    c.setStrokeColor(Color(0.8, 0.8, 0.8))
    c.rect(margin + CARD_WIDTH + spacing, page_height - 135 * mm - CARD_HEIGHT, CARD_WIDTH, CARD_HEIGHT, fill=0, stroke=1)
    draw_back_card(c, margin + CARD_WIDTH + spacing, page_height - 135 * mm - CARD_HEIGHT, is_white_version=True)
    
    # === VERSION MIXTE (Avant noir + Arrière blanc) ===
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(black)
    c.drawString(margin, page_height - 210 * mm, "VERSION MIXTE (Avant noir / Arrière blanc)")
    
    c.setFont("Helvetica", 10)
    c.drawString(margin, page_height - 220 * mm, "Face avant")
    draw_front_card(c, margin, page_height - 225 * mm - CARD_HEIGHT, is_white_version=False)
    
    c.drawString(margin + CARD_WIDTH + spacing, page_height - 220 * mm, "Face arrière")
    c.setStrokeColor(Color(0.8, 0.8, 0.8))
    c.rect(margin + CARD_WIDTH + spacing, page_height - 225 * mm - CARD_HEIGHT, CARD_WIDTH, CARD_HEIGHT, fill=0, stroke=1)
    draw_back_card(c, margin + CARD_WIDTH + spacing, page_height - 225 * mm - CARD_HEIGHT, is_white_version=True)
    
    c.save()
    print(f"✅ PDF complet créé: {output_path}")


if __name__ == "__main__":
    output_dir = "/app/backend/uploads"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create inverted (white) logo
    create_inverted_logo()
    
    # Create complete PDF
    create_complete_pdf(os.path.join(output_dir, "cartes_visite_titelli_complete.pdf"))
