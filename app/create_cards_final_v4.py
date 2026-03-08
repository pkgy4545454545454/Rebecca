from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, black, white
from reportlab.lib.utils import ImageReader
import qrcode
from PIL import Image
import os
import io

CARD_WIDTH = 85 * mm
CARD_HEIGHT = 55 * mm

# Générer QR code pour titelli.com
def generate_qr_code(url, size=100):
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="white", back_color="black")
    img = img.resize((size, size))
    return img

# Créer QR code
qr_img = generate_qr_code("https://www.titelli.com", 80)
qr_path = "/app/backend/uploads/qr_titelli.png"
qr_img.save(qr_path)

# Créer version blanche du QR
qr_img_white = generate_qr_code("https://www.titelli.com", 80)
# Inverser pour fond blanc
qr_black = qrcode.QRCode(version=1, box_size=10, border=1)
qr_black.add_data("https://www.titelli.com")
qr_black.make(fit=True)
qr_img_black = qr_black.make_image(fill_color="black", back_color="white")
qr_img_black = qr_img_black.resize((80, 80))
qr_path_black = "/app/backend/uploads/qr_titelli_black.png"
qr_img_black.save(qr_path_black)


def create_front_card(c, is_white_version=False):
    """Face avant avec le nouveau logo"""
    if is_white_version:
        c.setFillColor(white)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
    else:
        c.setFillColor(black)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
    
    # Charger et placer le logo
    logo_path = "/app/backend/uploads/logo_titelli_new.png"
    try:
        logo = ImageReader(logo_path)
        logo_width = 35 * mm
        logo_height = 35 * mm
        x = (CARD_WIDTH - logo_width) / 2
        y = (CARD_HEIGHT - logo_height) / 2 + 2 * mm
        c.drawImage(logo, x, y, width=logo_width, height=logo_height, mask='auto')
    except Exception as e:
        print(f"Logo error: {e}")
        # Fallback: dessiner le logo manuellement
        center_x = CARD_WIDTH / 2
        center_y = CARD_HEIGHT / 2 + 5 * mm
        logo_color = black if is_white_version else white
        c.setStrokeColor(logo_color)
        c.setLineWidth(1.5)
        c.circle(center_x, center_y, 12 * mm, fill=0, stroke=1)
        c.setFillColor(logo_color)
        c.setFont("Times-Roman", 28)
        c.drawCentredString(center_x, center_y - 8, "T")
        c.setFont("Times-Italic", 18)
        c.drawCentredString(center_x, center_y - 22 * mm, "Titelli")


def create_back_card(c, is_white_version=False, is_commercial=False):
    """Face arrière avec infos contact"""
    if is_white_version:
        c.setFillColor(white)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        text_color_main = black
        text_color_secondary = Color(0.4, 0.4, 0.4)
        qr_to_use = qr_path_black
    else:
        c.setFillColor(black)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        text_color_main = white
        text_color_secondary = Color(0.7, 0.7, 0.7)
        qr_to_use = qr_path
    
    left_margin = 14 * mm  # Plus vers le centre
    right_margin = CARD_WIDTH - 14 * mm
    
    # ===== HAUT (encore plus rapproché) =====
    c.setFillColor(text_color_main)
    nom_y = CARD_HEIGHT - 20 * mm  # Plus vers le centre
    
    if is_commercial:
        # Version Commercial - juste "COMMERCIAL"
        c.setFont("Helvetica", 8)  # Encore plus petit
        c.drawString(left_margin, nom_y, "COMMERCIAL")
    else:
        # Version Leila Hassini - nom plus petit
        c.setFont("Helvetica", 9)  # Encore plus petit
        c.drawString(left_margin, nom_y, "Leila Hassini")
        # Titre FOUNDER
        c.setFillColor(text_color_secondary)
        c.setFont("Helvetica", 5)
        c.drawString(left_margin, nom_y - 3.5 * mm, "F O U N D E R")
    
    # ===== BAS (encore plus rapproché) =====
    bottom_row1 = 20 * mm  # Plus vers le centre
    bottom_row2 = 15.5 * mm
    
    c.setFillColor(text_color_secondary)
    c.setFont("Helvetica", 5)
    
    # Gauche: téléphone
    c.drawString(left_margin, bottom_row1, "+41 79 895 03 13")
    
    # Site web avec QR code à côté
    c.drawString(left_margin, bottom_row2, "www.titelli.com")
    
    # QR Code mini à côté du site
    qr_size = 6 * mm
    try:
        qr = ImageReader(qr_to_use)
        c.drawImage(qr, left_margin + 20 * mm, bottom_row2 - 1.5 * mm, width=qr_size, height=qr_size, mask='auto')
    except Exception as e:
        print(f"QR error: {e}")
    
    # Droite: email
    c.drawRightString(right_margin, bottom_row1, "info@titelli.com")
    
    # Icônes réseaux
    icon_y = bottom_row2
    icon_size = 2.5 * mm
    icons_start_x = right_margin - 24 * mm
    
    # Icône Instagram
    c.setStrokeColor(text_color_secondary)
    c.setFillColor(text_color_secondary)
    c.setLineWidth(0.35)
    
    insta_x = icons_start_x
    c.roundRect(insta_x, icon_y - 0.5 * mm, icon_size, icon_size, 0.4 * mm, fill=0, stroke=1)
    c.circle(insta_x + icon_size/2, icon_y + icon_size/2 - 0.5 * mm, icon_size * 0.25, fill=0, stroke=1)
    c.circle(insta_x + icon_size * 0.75, icon_y + icon_size * 0.7 - 0.5 * mm, 0.2 * mm, fill=1, stroke=0)
    
    # @titelli.ch
    c.setFont("Helvetica", 5)
    c.drawString(insta_x + icon_size + 1 * mm, icon_y, "@titelli.ch")
    
    # Icône Titelli
    titelli_x = icons_start_x + 18 * mm
    c.circle(titelli_x + icon_size/2, icon_y + icon_size/2 - 0.5 * mm, icon_size/2, fill=0, stroke=1)
    c.setFont("Times-Roman", 4)
    c.drawCentredString(titelli_x + icon_size/2, icon_y - 0.1 * mm, "T")


def create_combined_pdf(output_path):
    """PDF avec toutes les cartes"""
    c = canvas.Canvas(output_path, pagesize=(CARD_WIDTH, CARD_HEIGHT))
    
    # ===== CARTE LEILA HASSINI =====
    # Recto noire
    create_front_card(c, is_white_version=False)
    c.showPage()
    # Verso noire
    create_back_card(c, is_white_version=False, is_commercial=False)
    c.showPage()
    # Recto blanche
    create_front_card(c, is_white_version=True)
    c.showPage()
    # Verso blanche
    create_back_card(c, is_white_version=True, is_commercial=False)
    c.showPage()
    
    # ===== CARTE COMMERCIAL =====
    # Recto noire
    create_front_card(c, is_white_version=False)
    c.showPage()
    # Verso noire
    create_back_card(c, is_white_version=False, is_commercial=True)
    c.showPage()
    # Recto blanche
    create_front_card(c, is_white_version=True)
    c.showPage()
    # Verso blanche
    create_back_card(c, is_white_version=True, is_commercial=True)
    
    c.save()
    print(f"✅ PDF créé: {output_path}")


if __name__ == "__main__":
    output_dir = "/app/backend/uploads"
    create_combined_pdf(os.path.join(output_dir, "cartes_visite_all.pdf"))
    
    # Preview
    from pdf2image import convert_from_path
    images = convert_from_path(os.path.join(output_dir, "cartes_visite_all.pdf"), dpi=200)
    for i, img in enumerate(images):
        img.save(os.path.join(output_dir, f"carte_all_{i+1}.png"), 'PNG')
    print("✅ Previews créés")
