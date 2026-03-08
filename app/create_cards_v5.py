from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, black, white
from reportlab.lib.utils import ImageReader
import qrcode
import os

CARD_WIDTH = 85 * mm
CARD_HEIGHT = 55 * mm

# QR codes petits
qr = qrcode.QRCode(version=1, box_size=6, border=1)
qr.add_data("https://www.titelli.com")
qr.make(fit=True)
qr_white = qr.make_image(fill_color="white", back_color="black").resize((50, 50))
qr_white.save("/app/backend/uploads/qr_mini_white.png")
qr_black = qr.make_image(fill_color="black", back_color="white").resize((50, 50))
qr_black.save("/app/backend/uploads/qr_mini_black.png")


def create_front_card(c, is_white_version=False):
    """Face avant - logo centré, taille réelle"""
    if is_white_version:
        c.setFillColor(white)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        # Logo noir pour fond blanc
        logo = ImageReader("/app/backend/uploads/logo_titelli_noir_v2.png")
    else:
        c.setFillColor(black)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        # Logo blanc/clair pour fond noir
        logo = ImageReader("/app/backend/uploads/logo_titelli_new.png")
    
    # Logo plus grand - taille réelle
    logo_size = 45 * mm
    x = (CARD_WIDTH - logo_size) / 2
    y = (CARD_HEIGHT - logo_size) / 2
    c.drawImage(logo, x, y, width=logo_size, height=logo_size, mask='auto')


def create_back_leila(c, is_white_version=False):
    """Carte Leila Hassini"""
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
    
    # Nom centré
    c.setFillColor(main_color)
    c.setFont("Helvetica", 9)
    c.drawCentredString(center_x, CARD_HEIGHT - 18 * mm, "Leila Hassini")
    
    c.setFillColor(secondary_color)
    c.setFont("Helvetica", 5)
    c.drawCentredString(center_x, CARD_HEIGHT - 22 * mm, "F O U N D E R")
    
    # Infos centrées
    c.drawCentredString(center_x, 18 * mm, "+41 79 895 03 13   •   info@titelli.com")
    c.drawCentredString(center_x, 13 * mm, "www.titelli.com   •   @titelli.ch")


def create_back_commercial(c, is_white_version=False):
    """Carte Commercial - MEME FORMAT que Founder, QR petit comme icône"""
    if is_white_version:
        c.setFillColor(white)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        main_color = black
        secondary_color = Color(0.4, 0.4, 0.4)
        qr_path = "/app/backend/uploads/qr_mini_black.png"
    else:
        c.setFillColor(black)
        c.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
        main_color = white
        secondary_color = Color(0.65, 0.65, 0.65)
        qr_path = "/app/backend/uploads/qr_mini_white.png"
    
    center_x = CARD_WIDTH / 2
    
    # COMMERCIAL centré (même position que le nom sur carte Founder)
    c.setFillColor(main_color)
    c.setFont("Helvetica", 9)
    c.drawCentredString(center_x, CARD_HEIGHT - 18 * mm, "C O M M E R C I A L")
    
    # Infos - même format que Founder
    c.setFillColor(secondary_color)
    c.setFont("Helvetica", 5)
    c.drawCentredString(center_x, 18 * mm, "+41 79 895 03 13   •   info@titelli.com")
    
    # Ligne site avec petit QR comme icône - mieux centré
    # Format: [QR] www.titelli.com • @titelli.ch
    text_site = "www.titelli.com   •   @titelli.ch"
    text_width = c.stringWidth(text_site, "Helvetica", 5)
    qr_size = 2.8 * mm  # Encore plus petit pour être vraiment comme une icône
    spacing = 1 * mm  # Espace entre QR et texte
    total_width = qr_size + spacing + text_width
    start_x = (CARD_WIDTH - total_width) / 2
    
    # QR mini comme icône
    qr = ImageReader(qr_path)
    qr_y = 13 * mm - (qr_size / 2) + 0.5 * mm  # Centré verticalement avec le texte
    c.drawImage(qr, start_x, qr_y, width=qr_size, height=qr_size, mask='auto')
    
    # Texte après QR
    c.drawString(start_x + qr_size + spacing, 13 * mm, text_site)


def create_pdf(output_path):
    c = canvas.Canvas(output_path, pagesize=(CARD_WIDTH, CARD_HEIGHT))
    
    # LEILA
    create_front_card(c, False)
    c.showPage()
    create_back_leila(c, False)
    c.showPage()
    create_front_card(c, True)
    c.showPage()
    create_back_leila(c, True)
    c.showPage()
    
    # COMMERCIAL
    create_front_card(c, False)
    c.showPage()
    create_back_commercial(c, False)
    c.showPage()
    create_front_card(c, True)
    c.showPage()
    create_back_commercial(c, True)
    
    c.save()
    print(f"✅ {output_path}")


if __name__ == "__main__":
    create_pdf("/app/backend/uploads/cartes_finales.pdf")
    
    from pdf2image import convert_from_path
    imgs = convert_from_path("/app/backend/uploads/cartes_finales.pdf", dpi=200)
    for i, img in enumerate(imgs):
        img.save(f"/app/backend/uploads/preview_{i+1}.png", "PNG")
    print("✅ Done")
