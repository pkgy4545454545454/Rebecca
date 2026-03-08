#!/usr/bin/env python3
"""
Génère le QR Code Titelli avec message de bienvenue et code promo
"""
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = '/app/backend/uploads'

def generate_qr_code():
    """Génère le QR code vers www.titelli.com"""
    print("🔲 Génération du QR Code...")
    
    # Créer le QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data('https://www.titelli.com')
    qr.make(fit=True)
    
    # Créer l'image QR avec couleurs Titelli
    qr_img = qr.make_image(fill_color="#0047AB", back_color="white")
    
    # Sauvegarder le QR simple
    qr_simple_path = f'{OUTPUT_DIR}/TITELLI_QR_CODE.png'
    qr_img.save(qr_simple_path)
    print(f"   ✅ QR Code simple: {qr_simple_path}")
    
    return qr_simple_path


def generate_welcome_card():
    """Génère la carte de bienvenue avec QR code et code promo"""
    print("🎁 Génération de la carte de bienvenue...")
    
    # Dimensions de la carte (format A6 paysage)
    width, height = 1400, 1000
    
    # Créer l'image
    card = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(card)
    
    # Couleurs Titelli
    blue = "#0047AB"
    gold = "#FFC107"
    dark = "#1a1a1a"
    gray = "#666666"
    
    # Fond dégradé en haut
    for i in range(200):
        color_val = int(0 + (71 * i / 200))
        color = f"#{0:02x}{color_val:02x}{int(171 * i / 200):02x}"
        draw.line([(0, i), (width, i)], fill=color)
    
    # Titre TITELLI
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        code_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = title_font
        body_font = title_font
        code_font = title_font
        small_font = title_font
    
    # Titre
    draw.text((width//2, 80), "TITELLI", font=title_font, fill="white", anchor="mm")
    
    # Sous-titre
    draw.text((width//2, 140), "vous souhaite la bienvenue !", font=subtitle_font, fill=gold, anchor="mm")
    
    # Message principal
    y_pos = 250
    messages = [
        "Merci de votre confiance.",
        "",
        "Profitez de votre cadeau de bienvenue et commencez",
        "d'ores et déjà à rentabiliser votre business !",
    ]
    
    for msg in messages:
        if msg:
            draw.text((width//2, y_pos), msg, font=body_font, fill=dark, anchor="mm")
        y_pos += 35
    
    # Encadré code promo
    promo_box_y = 400
    promo_box_height = 150
    
    # Rectangle doré
    draw.rectangle(
        [(100, promo_box_y), (width - 400, promo_box_y + promo_box_height)],
        fill="#FFF8E1",
        outline=gold,
        width=3
    )
    
    # Texte code promo
    draw.text((100 + (width - 500)//2, promo_box_y + 30), 
              "VOTRE CODE PROMO DE BIENVENUE", font=small_font, fill=gray, anchor="mm")
    
    # Le code
    draw.text((100 + (width - 500)//2, promo_box_y + 80), 
              "BIENVENUE100", font=code_font, fill=blue, anchor="mm")
    
    draw.text((100 + (width - 500)//2, promo_box_y + 125), 
              "100 CHF de crédit publicitaire offert", font=small_font, fill=dark, anchor="mm")
    
    # QR Code à droite
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=6,
        border=1,
    )
    qr.add_data('https://www.titelli.com')
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color=blue, back_color="white")
    qr_img = qr_img.resize((180, 180))
    
    # Coller le QR code
    card.paste(qr_img, (width - 280, promo_box_y - 10))
    draw.text((width - 190, promo_box_y + 180), "www.titelli.com", font=small_font, fill=blue, anchor="mm")
    
    # Section suggestions
    y_suggestions = 600
    draw.text((width//2, y_suggestions), 
              "Découvrez nos prestations IA", font=subtitle_font, fill=blue, anchor="mm")
    
    # Suggestions
    suggestions = [
        "🎨 Images publicitaires IA - Testez gratuitement !",
        "🎬 Vidéos promotionnelles IA - Aperçu avant paiement",
        "📊 Ciblage intelligent - Optimisez votre audience",
    ]
    
    y_pos = y_suggestions + 50
    for suggestion in suggestions:
        draw.text((width//2, y_pos), suggestion, font=body_font, fill=dark, anchor="mm")
        y_pos += 40
    
    # Footer
    draw.rectangle([(0, height - 80), (width, height)], fill=blue)
    draw.text((width//2, height - 40), 
              "Essayez sans engagement • Rentrez votre photo ou descriptif • Validez et payez si satisfait !",
              font=small_font, fill="white", anchor="mm")
    
    # Sauvegarder
    card_path = f'{OUTPUT_DIR}/TITELLI_CARTE_BIENVENUE.png'
    card.save(card_path, quality=95)
    print(f"   ✅ Carte de bienvenue: {card_path}")
    
    return card_path


def main():
    print("=" * 70)
    print("   GÉNÉRATION QR CODE & CARTE BIENVENUE TITELLI")
    print("=" * 70)
    
    qr_path = generate_qr_code()
    card_path = generate_welcome_card()
    
    print("\n" + "=" * 70)
    print("   ✅ FICHIERS GÉNÉRÉS !")
    print(f"   📁 QR Code: {qr_path}")
    print(f"   📁 Carte: {card_path}")
    print("=" * 70)
    
    return qr_path, card_path


if __name__ == "__main__":
    main()
