from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, black, white
from reportlab.lib.utils import ImageReader
import os

# Business card dimensions (standard: 85mm x 55mm)
CARD_WIDTH = 85 * mm
CARD_HEIGHT = 55 * mm

# Colors
GOLD_TEXT = Color(0.83, 0.69, 0.22)  # Gold #D4AF37
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
    
    # Draw "Titelli" text below circle - using Times-Italic for elegant look
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
        text_color_secondary = white  # White text on black card
    
    # Margins
    left_margin = 10 * mm
    right_margin = CARD_WIDTH - 10 * mm
    
    # ========== TOP SECTION ==========
    # Name - "Leila Hassini" in Titelli-style font (Times-Italic, elegant)
    c.setFillColor(text_color_main)
    c.setFont("Times-Italic", 14)  # Elegant italic font like Titelli
    nom_y = CARD_HEIGHT - 16 * mm  # Slightly closer to top
    c.drawString(left_margin, nom_y, "Leila Hassini")
    
    # Function - Founder (spaced letters)
    c.setFillColor(text_color_secondary)
    c.setFont("Helvetica", 6)
    titre_y = nom_y - 4 * mm
    c.drawString(left_margin, titre_y, "F O U N D E R")
    
    # ========== BOTTOM SECTION (moved up a bit) ==========
    bottom_row1 = 16 * mm  # Was 14, now 16 (closer to middle)
    bottom_row2 = 11 * mm  # Was 10, now 11
    
    # LEFT COLUMN
    c.setFont("Helvetica", 6)
    c.setFillColor(text_color_secondary)
    c.drawString(left_margin, bottom_row1, "+41 79 895 03 13")
    c.drawString(left_margin, bottom_row2, "www.titelli.com")
    
    # RIGHT COLUMN
    c.drawRightString(right_margin, bottom_row1, "info@titelli.com")
    
    # Social icons row - Instagram icon + "titelli.ch" + Titelli icon
    icon_y = bottom_row2
    
    # Draw mini Instagram icon (simplified square with rounded corners + camera)
    insta_x = right_margin - 35 * mm
    icon_size = 3 * mm
    
    c.setStrokeColor(text_color_secondary)
    c.setLineWidth(0.5)
    c.roundRect(insta_x, icon_y - 0.5 * mm, icon_size, icon_size, 0.5 * mm, fill=0, stroke=1)
    c.circle(insta_x + icon_size/2, icon_y + icon_size/2 - 0.5 * mm, icon_size * 0.25, fill=0, stroke=1)
    
    # Text "@titelli.ch"
    c.setFillColor(text_color_secondary)
    c.drawString(insta_x + icon_size + 1.5 * mm, icon_y, "@titelli.ch")
    
    # Draw mini Titelli icon (circle with T)
    titelli_x = right_margin - 8 * mm
    c.circle(titelli_x + icon_size/2, icon_y + icon_size/2 - 0.5 * mm, icon_size/2, fill=0, stroke=1)
    c.setFont("Times-Roman", 5)
    c.drawCentredString(titelli_x + icon_size/2, icon_y, "T")
    
    c.save()
    print(f"Back card created: {output_path}")


def create_combined_pdf(output_path):
    """Create a combined PDF with all card versions"""
    from reportlab.lib.pagesizes import A4
    from PyPDF2 import PdfMerger, PdfReader
    import io
    
    # Create individual cards first
    cards = []
    
    # Black front
    buf1 = io.BytesIO()
    c1 = canvas.Canvas(buf1, pagesize=(CARD_WIDTH, CARD_HEIGHT))
    # ... copy front black logic
    c1.setFillColor(black)
    c1.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
    center_x, center_y = CARD_WIDTH/2, CARD_HEIGHT/2 + 5*mm
    c1.setStrokeColor(white)
    c1.setLineWidth(1.5)
    c1.circle(center_x, center_y, 12*mm, fill=0, stroke=1)
    c1.setFillColor(white)
    c1.setFont("Times-Roman", 28)
    c1.drawCentredString(center_x, center_y - 8, "T")
    c1.setFont("Times-Italic", 18)
    c1.drawCentredString(center_x, center_y - 22*mm, "Titelli")
    c1.save()
    cards.append(buf1)
    
    print("Combined PDF would require PyPDF2 - generating individual cards instead")


if __name__ == "__main__":
    output_dir = "/app/backend/uploads"
    os.makedirs(output_dir, exist_ok=True)
    
    # FRONT cards (logo Titelli)
    create_front_card(os.path.join(output_dir, "carte_front_noire_v2.pdf"), is_white_version=False)
    create_front_card(os.path.join(output_dir, "carte_front_blanche_v2.pdf"), is_white_version=True)
    
    # BACK cards (contact info)
    create_back_card(os.path.join(output_dir, "carte_back_noire_v2.pdf"), is_white_version=False)
    create_back_card(os.path.join(output_dir, "carte_back_blanche_v2.pdf"), is_white_version=True)
    
    print("\n✅ Toutes les cartes V2 ont été générées!")
