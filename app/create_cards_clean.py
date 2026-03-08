from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, black, white
from reportlab.lib.utils import ImageReader
import qrcode
import os

CARD_WIDTH = 85 * mm
CARD_HEIGHT = 55 * mm

# QR code
qr = qrcode.QRCode(version=1, box_size=10, border=1)
qr.add_data("https://www.titelli.com")
qr.make(fit=True)
qr_white = qr.make_image(fill_color="white", back_color="black").resize((80, 80))
qr_white.save("/app/backend/uploads/qr_white.png")
qr_black = qr.make_image(fill_color="black", back_color="white").resize((80, 80))
qr_black.save("/app/backend/uploads/qr_black.png")


def create_front_card(c, is_white_version=False):
    """Face avant - logo centré"""
    if is_white_version:
        c.setFillColor(white)
    else:
        c.setFillColor(black)
    c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
    
    # Logo centré
    logo = ImageReader("/app/backend/uploads/logo_titelli_new.png")
    logo_size = 32 * mm
    x = (CARD_WIDTH - logo_size) / 2
    y = (CARD_HEIGHT - logo_size) / 2
    c.drawImage(logo, x, y, width=logo_size, height=logo_size, mask='auto')


def create_back_leila(c, is_white_version=False):
    """Carte Leila - PAS de QR, tout centré"""
    if is_white_version:
        c.setFillColor(white)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        main_color = black
        secondary_color = Color(0.4, 0.4, 0.4)
    else:
        c.setFillColor(black)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        main_color = white
        secondary_color = Color(0.65, 0.65, 0.65)
    
    center_x = CARD_WIDTH / 2
    
    # HAUT - Nom centré
    c.setFillColor(main_color)
    c.setFont("Helvetica", 9)
    c.drawCentredString(center_x, CARD_HEIGHT - 18 * mm, "Leila Hassini")
    
    c.setFillColor(secondary_color)
    c.setFont("Helvetica", 5)
    c.drawCentredString(center_x, CARD_HEIGHT - 22 * mm, "F O U N D E R")
    
    # BAS - Infos centrées
    c.setFont("Helvetica", 5)
    
    # Ligne 1: téléphone | email
    c.drawCentredString(center_x, 18 * mm, "+41 79 895 03 13   •   info@titelli.com")
    
    # Ligne 2: site | réseaux
    c.drawCentredString(center_x, 13 * mm, "www.titelli.com   •   @titelli.ch")


def create_back_commercial(c, is_white_version=False):
    """Carte Commercial - AVEC QR, tout centré"""
    if is_white_version:
        c.setFillColor(white)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        main_color = black
        secondary_color = Color(0.4, 0.4, 0.4)
        qr_path = "/app/backend/uploads/qr_black.png"
    else:
        c.setFillColor(black)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        main_color = white
        secondary_color = Color(0.65, 0.65, 0.65)
        qr_path = "/app/backend/uploads/qr_white.png"
    
    center_x = CARD_WIDTH / 2
    
    # HAUT - COMMERCIAL centré
    c.setFillColor(main_color)
    c.setFont("Helvetica", 9)
    c.drawCentredString(center_x, CARD_HEIGHT - 20 * mm, "C O M M E R C I A L")
    
    # MILIEU - QR code centré
    qr = ImageReader(qr_path)
    qr_size = 12 * mm
    c.drawImage(qr, (CARD_WIDTH - qr_size) / 2, (CARD_HEIGHT - qr_size) / 2 - 3 * mm, 
                width=qr_size, height=qr_size, mask='auto')
    
    # BAS - Infos centrées
    c.setFillColor(secondary_color)
    c.setFont("Helvetica", 5)
    
    c.drawCentredString(center_x, 16 * mm, "+41 79 895 03 13   •   info@titelli.com")
    c.drawCentredString(center_x, 11 * mm, "www.titelli.com   •   @titelli.ch")


def create_pdf(output_path):
    c = canvas.Canvas(output_path, pagesize=(CARD_WIDTH, CARD_HEIGHT))
    
    # LEILA - Noire recto
    create_front_card(c, False)
    c.showPage()
    # LEILA - Noire verso
    create_back_leila(c, False)
    c.showPage()
    # LEILA - Blanche recto
    create_front_card(c, True)
    c.showPage()
    # LEILA - Blanche verso
    create_back_leila(c, True)
    c.showPage()
    
    # COMMERCIAL - Noire recto
    create_front_card(c, False)
    c.showPage()
    # COMMERCIAL - Noire verso
    create_back_commercial(c, False)
    c.showPage()
    # COMMERCIAL - Blanche recto
    create_front_card(c, True)
    c.showPage()
    # COMMERCIAL - Blanche verso
    create_back_commercial(c, True)
    
    c.save()
    print(f"✅ {output_path}")


if __name__ == "__main__":
    create_pdf("/app/backend/uploads/cartes_finales.pdf")
    
    # Preview
    from pdf2image import convert_from_path
    imgs = convert_from_path("/app/backend/uploads/cartes_finales.pdf", dpi=200)
    for i, img in enumerate(imgs):
        img.save(f"/app/backend/uploads/preview_{i+1}.png", "PNG")
    print("✅ Previews OK")
