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
    """Face arrière avec infos contact - PAS DE DORÉ"""
    if is_white_version:
        c.setFillColor(white)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        text_color_main = black
        text_color_secondary = Color(0.4, 0.4, 0.4)  # Gris foncé
    else:
        c.setFillColor(black)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        text_color_main = white  # BLANC, pas doré
        text_color_secondary = Color(0.7, 0.7, 0.7)  # Gris clair
    
    left_margin = 10 * mm
    right_margin = CARD_WIDTH - 10 * mm
    
    # ===== HAUT =====
    # Nom en police Titelli (Times-Italic) - "Leila Hassini" minuscule avec majuscules
    c.setFillColor(text_color_main)
    c.setFont("Times-Italic", 14)
    nom_y = CARD_HEIGHT - 15 * mm  # Rapproché du haut
    c.drawString(left_margin, nom_y, "Leila Hassini")
    
    # Titre FOUNDER
    c.setFillColor(text_color_secondary)
    c.setFont("Helvetica", 6)
    c.drawString(left_margin, nom_y - 4 * mm, "F O U N D E R")
    
    # ===== BAS (rapproché) =====
    bottom_row1 = 17 * mm  # Remonté
    bottom_row2 = 12 * mm  # Remonté
    
    # Gauche: téléphone et site
    c.drawString(left_margin, bottom_row1, "+41 79 895 03 13")
    c.drawString(left_margin, bottom_row2, "www.titelli.com")
    
    # Droite: email
    c.drawRightString(right_margin, bottom_row1, "info@titelli.com")
    
    # ===== ICONES RESEAUX (en bas à droite) =====
    icon_y = bottom_row2
    icon_size = 3 * mm
    
    # Position des icônes
    icons_start_x = right_margin - 28 * mm
    
    # Icône Instagram (carré arrondi + cercle)
    c.setStrokeColor(text_color_secondary)
    c.setFillColor(text_color_secondary)
    c.setLineWidth(0.4)
    
    insta_x = icons_start_x
    # Carré arrondi
    c.roundRect(insta_x, icon_y - 0.5 * mm, icon_size, icon_size, 0.6 * mm, fill=0, stroke=1)
    # Cercle intérieur (objectif)
    c.circle(insta_x + icon_size/2, icon_y + icon_size/2 - 0.5 * mm, icon_size * 0.28, fill=0, stroke=1)
    # Petit point en haut à droite
    c.circle(insta_x + icon_size * 0.75, icon_y + icon_size * 0.75 - 0.5 * mm, 0.3 * mm, fill=1, stroke=0)
    
    # Texte @titelli.ch
    c.setFont("Helvetica", 6)
    c.drawString(insta_x + icon_size + 1.5 * mm, icon_y, "@titelli.ch")
    
    # Icône Titelli (cercle avec T)
    titelli_x = icons_start_x + 22 * mm
    c.setStrokeColor(text_color_secondary)
    c.circle(titelli_x + icon_size/2, icon_y + icon_size/2 - 0.5 * mm, icon_size/2, fill=0, stroke=1)
    c.setFont("Times-Roman", 5)
    c.setFillColor(text_color_secondary)
    c.drawCentredString(titelli_x + icon_size/2, icon_y, "T")


def create_combined_pdf(output_path):
    """PDF avec toutes les cartes"""
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
    print(f"✅ PDF créé: {output_path}")


if __name__ == "__main__":
    output_dir = "/app/backend/uploads"
    create_combined_pdf(os.path.join(output_dir, "cartes_visite_titelli_final.pdf"))
    
    # Convertir en images pour preview
    from pdf2image import convert_from_path
    images = convert_from_path(os.path.join(output_dir, "cartes_visite_titelli_final.pdf"), dpi=200)
    for i, img in enumerate(images):
        img.save(os.path.join(output_dir, f"carte_page_{i+1}.png"), 'PNG')
        print(f"✅ Page {i+1} convertie en PNG")
