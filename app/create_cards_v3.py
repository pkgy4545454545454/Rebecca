from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, black, white
import os

CARD_WIDTH = 85 * mm
CARD_HEIGHT = 55 * mm


def create_front_card(c, is_white_version=False):
    """Face avant avec logo Titelli"""
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
    
    # Cercle logo
    c.setStrokeColor(logo_color)
    c.setLineWidth(1.5)
    c.circle(center_x, center_y, 12 * mm, fill=0, stroke=1)
    
    # Lettre T
    c.setFillColor(logo_color)
    c.setFont("Times-Roman", 28)
    c.drawCentredString(center_x, center_y - 8, "T")
    
    # Texte Titelli
    c.setFont("Times-Italic", 18)
    c.drawCentredString(center_x, center_y - 22 * mm, "Titelli")


def create_back_card(c, is_white_version=False):
    """Face arrière avec infos contact"""
    if is_white_version:
        c.setFillColor(white)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        text_color_main = black
        text_color_secondary = Color(0.4, 0.4, 0.4)
    else:
        c.setFillColor(black)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        text_color_main = white
        text_color_secondary = Color(0.7, 0.7, 0.7)
    
    left_margin = 12 * mm  # Plus vers le centre
    right_margin = CARD_WIDTH - 12 * mm  # Plus vers le centre
    
    # ===== HAUT (rapproché vers le centre) =====
    # Nom - PAS italique, PAS gras, plus petit
    c.setFillColor(text_color_main)
    c.setFont("Helvetica", 11)  # Police normale, plus petite
    nom_y = CARD_HEIGHT - 18 * mm  # Plus vers le centre
    c.drawString(left_margin, nom_y, "Leila Hassini")
    
    # Titre FOUNDER
    c.setFillColor(text_color_secondary)
    c.setFont("Helvetica", 5.5)
    c.drawString(left_margin, nom_y - 4 * mm, "F O U N D E R")
    
    # ===== BAS (rapproché vers le centre) =====
    bottom_row1 = 19 * mm  # Plus vers le centre
    bottom_row2 = 14 * mm  # Plus vers le centre
    
    # Gauche: téléphone et site
    c.setFont("Helvetica", 5.5)
    c.drawString(left_margin, bottom_row1, "+41 79 895 03 13")
    c.drawString(left_margin, bottom_row2, "www.titelli.com")
    
    # Droite: email
    c.drawRightString(right_margin, bottom_row1, "info@titelli.com")
    
    # ===== ICONES RESEAUX =====
    icon_y = bottom_row2
    icon_size = 2.8 * mm
    
    icons_start_x = right_margin - 26 * mm
    
    # Icône Instagram
    c.setStrokeColor(text_color_secondary)
    c.setFillColor(text_color_secondary)
    c.setLineWidth(0.4)
    
    insta_x = icons_start_x
    c.roundRect(insta_x, icon_y - 0.5 * mm, icon_size, icon_size, 0.5 * mm, fill=0, stroke=1)
    c.circle(insta_x + icon_size/2, icon_y + icon_size/2 - 0.5 * mm, icon_size * 0.28, fill=0, stroke=1)
    c.circle(insta_x + icon_size * 0.75, icon_y + icon_size * 0.72 - 0.5 * mm, 0.25 * mm, fill=1, stroke=0)
    
    # @titelli.ch
    c.setFont("Helvetica", 5.5)
    c.drawString(insta_x + icon_size + 1.2 * mm, icon_y, "@titelli.ch")
    
    # Icône Titelli
    titelli_x = icons_start_x + 20 * mm
    c.setStrokeColor(text_color_secondary)
    c.circle(titelli_x + icon_size/2, icon_y + icon_size/2 - 0.5 * mm, icon_size/2, fill=0, stroke=1)
    c.setFont("Times-Roman", 4.5)
    c.setFillColor(text_color_secondary)
    c.drawCentredString(titelli_x + icon_size/2, icon_y - 0.2 * mm, "T")


def create_combined_pdf(output_path):
    """PDF avec toutes les cartes recto-verso"""
    c = canvas.Canvas(output_path, pagesize=(CARD_WIDTH, CARD_HEIGHT))
    
    # Carte noire recto (front)
    create_front_card(c, is_white_version=False)
    c.showPage()
    
    # Carte noire verso (back)
    create_back_card(c, is_white_version=False)
    c.showPage()
    
    # Carte blanche recto (front)
    create_front_card(c, is_white_version=True)
    c.showPage()
    
    # Carte blanche verso (back)
    create_back_card(c, is_white_version=True)
    
    c.save()
    print(f"✅ PDF créé: {output_path}")


if __name__ == "__main__":
    output_dir = "/app/backend/uploads"
    create_combined_pdf(os.path.join(output_dir, "cartes_visite_complete.pdf"))
    
    # Preview
    from pdf2image import convert_from_path
    images = convert_from_path(os.path.join(output_dir, "cartes_visite_complete.pdf"), dpi=200)
    for i, img in enumerate(images):
        img.save(os.path.join(output_dir, f"carte_preview_{i+1}.png"), 'PNG')
    print("✅ Previews créés")
