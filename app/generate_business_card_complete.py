from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, black, white
import os

# Business card dimensions (standard: 85mm x 55mm)
CARD_WIDTH = 85 * mm
CARD_HEIGHT = 55 * mm

# Colors
GOLD_TEXT = Color(0.75, 0.72, 0.55)
LIGHT_TEXT = Color(0.6, 0.6, 0.6)


def create_front_card(output_path, is_white_version=False):
    """Create the FRONT of the business card with Titelli logo"""
    c = canvas.Canvas(output_path, pagesize=(CARD_WIDTH, CARD_HEIGHT))
    
    # Background
    if is_white_version:
        c.setFillColor(white)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        logo_color = black
    else:
        c.setFillColor(black)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        logo_color = white
    
    # Center position
    center_x = CARD_WIDTH / 2
    center_y = CARD_HEIGHT / 2 + 5 * mm
    
    # Draw circle for logo
    circle_radius = 12 * mm
    c.setStrokeColor(logo_color)
    c.setLineWidth(1.5)
    c.circle(center_x, center_y, circle_radius, fill=0, stroke=1)
    
    # Draw "T" letter inside circle
    c.setFillColor(logo_color)
    c.setFont("Times-Roman", 28)
    c.drawCentredString(center_x, center_y - 8, "T")
    
    # Draw "Titelli" text below circle
    c.setFont("Times-Italic", 18)
    c.drawCentredString(center_x, center_y - circle_radius - 10 * mm, "Titelli")
    
    c.save()
    print(f"Front card created: {output_path}")


def create_back_card(output_path, is_white_version=False):
    """Create the BACK of the business card with contact info"""
    c = canvas.Canvas(output_path, pagesize=(CARD_WIDTH, CARD_HEIGHT))
    
    # Background and colors
    if is_white_version:
        c.setFillColor(white)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        text_color_main = black
        text_color_secondary = Color(0.3, 0.3, 0.3)
    else:
        c.setFillColor(black)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        text_color_main = GOLD_TEXT
        text_color_secondary = LIGHT_TEXT
    
    # Margins
    left_margin = 10 * mm
    right_margin = CARD_WIDTH - 10 * mm
    
    # Name - Leila Hassini
    c.setFillColor(text_color_main)
    c.setFont("Helvetica", 12)
    nom_y = CARD_HEIGHT - 18 * mm
    c.drawString(left_margin, nom_y, "L E I L A   H A S S I N I")
    
    # Function - Founder
    c.setFillColor(text_color_secondary)
    c.setFont("Helvetica", 6)
    titre_y = nom_y - 4 * mm
    c.drawString(left_margin, titre_y, "F O U N D E R")
    
    # Bottom row
    bottom_row1 = 14 * mm
    bottom_row2 = 10 * mm
    
    # LEFT COLUMN - téléphone / site web
    c.drawString(left_margin, bottom_row1, "téléphone / autre")
    c.drawString(left_margin, bottom_row2, "www.titelli.com")
    
    # RIGHT COLUMN - email / @reseauxsociaux
    c.drawRightString(right_margin, bottom_row1, "info@titelli.com")
    c.drawRightString(right_margin, bottom_row2, "@reseauxsociaux")
    
    c.save()
    print(f"Back card created: {output_path}")


if __name__ == "__main__":
    output_dir = "/app/backend/uploads"
    os.makedirs(output_dir, exist_ok=True)
    
    # FRONT cards (logo Titelli)
    create_front_card(os.path.join(output_dir, "carte_front_noire.pdf"), is_white_version=False)
    create_front_card(os.path.join(output_dir, "carte_front_blanche.pdf"), is_white_version=True)
    
    # BACK cards (contact info)
    create_back_card(os.path.join(output_dir, "carte_back_noire.pdf"), is_white_version=False)
    create_back_card(os.path.join(output_dir, "carte_back_blanche.pdf"), is_white_version=True)
    
    print("\n✅ Toutes les cartes ont été générées!")
