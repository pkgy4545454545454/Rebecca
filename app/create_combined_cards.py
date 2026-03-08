from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, black, white
from PyPDF2 import PdfMerger
import os

# Business card dimensions
CARD_WIDTH = 85 * mm
CARD_HEIGHT = 55 * mm

# Colors
GOLD_TEXT = Color(0.83, 0.69, 0.22)
LIGHT_TEXT = Color(0.6, 0.6, 0.6)


def create_front_card(c, is_white_version=False):
    """Draw front of card on canvas"""
    if is_white_version:
        c.setFillColor(white)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        logo_color = black
    else:
        c.setFillColor(black)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        logo_color = white
    
    center_x = CARD_WIDTH / 2
    center_y = CARD_HEIGHT / 2 + 5 * mm
    
    # Circle logo
    c.setStrokeColor(logo_color)
    c.setLineWidth(1.5)
    c.circle(center_x, center_y, 12 * mm, fill=0, stroke=1)
    
    # T letter
    c.setFillColor(logo_color)
    c.setFont("Times-Roman", 28)
    c.drawCentredString(center_x, center_y - 8, "T")
    
    # Titelli text
    c.setFont("Times-Italic", 18)
    c.drawCentredString(center_x, center_y - 22 * mm, "Titelli")


def create_back_card(c, is_white_version=False):
    """Draw back of card on canvas"""
    if is_white_version:
        c.setFillColor(white)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        text_color_main = black
        text_color_secondary = Color(0.3, 0.3, 0.3)
    else:
        c.setFillColor(black)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        text_color_main = GOLD_TEXT
        text_color_secondary = white
    
    left_margin = 10 * mm
    right_margin = CARD_WIDTH - 10 * mm
    
    # Name
    c.setFillColor(text_color_main)
    c.setFont("Times-Italic", 14)
    nom_y = CARD_HEIGHT - 16 * mm
    c.drawString(left_margin, nom_y, "Leila Hassini")
    
    # Title
    c.setFillColor(text_color_secondary)
    c.setFont("Helvetica", 6)
    c.drawString(left_margin, nom_y - 4 * mm, "F O U N D E R")
    
    # Bottom section
    bottom_row1 = 16 * mm
    bottom_row2 = 11 * mm
    
    c.drawString(left_margin, bottom_row1, "+41 79 895 03 13")
    c.drawString(left_margin, bottom_row2, "www.titelli.com")
    c.drawRightString(right_margin, bottom_row1, "info@titelli.com")
    
    # Social icons
    icon_y = bottom_row2
    icon_size = 3 * mm
    
    # Instagram icon
    insta_x = right_margin - 35 * mm
    c.setStrokeColor(text_color_secondary)
    c.setLineWidth(0.5)
    c.roundRect(insta_x, icon_y - 0.5 * mm, icon_size, icon_size, 0.5 * mm, fill=0, stroke=1)
    c.circle(insta_x + icon_size/2, icon_y + icon_size/2 - 0.5 * mm, icon_size * 0.25, fill=0, stroke=1)
    
    # @titelli.ch
    c.setFillColor(text_color_secondary)
    c.drawString(insta_x + icon_size + 1.5 * mm, icon_y, "@titelli.ch")
    
    # Titelli icon
    titelli_x = right_margin - 8 * mm
    c.circle(titelli_x + icon_size/2, icon_y + icon_size/2 - 0.5 * mm, icon_size/2, fill=0, stroke=1)
    c.setFont("Times-Roman", 5)
    c.drawCentredString(titelli_x + icon_size/2, icon_y, "T")


def create_combined_pdf(output_path):
    """Create a single PDF with all card versions"""
    c = canvas.Canvas(output_path, pagesize=(CARD_WIDTH, CARD_HEIGHT))
    
    # Page 1: Front Noire
    create_front_card(c, is_white_version=False)
    c.showPage()
    
    # Page 2: Back Noire
    create_back_card(c, is_white_version=False)
    c.showPage()
    
    # Page 3: Front Blanche
    create_front_card(c, is_white_version=True)
    c.showPage()
    
    # Page 4: Back Blanche
    create_back_card(c, is_white_version=True)
    
    c.save()
    print(f"✅ PDF combiné créé: {output_path}")


if __name__ == "__main__":
    output_dir = "/app/backend/uploads"
    create_combined_pdf(os.path.join(output_dir, "cartes_visite_titelli_v2.pdf"))
