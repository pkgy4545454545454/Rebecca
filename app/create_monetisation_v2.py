from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm
import textwrap

# Colors
DARK = HexColor("#1a1a1a")
GOLD = HexColor("#C9A227")
LIGHT_BG = HexColor("#f8f8f8")
TEXT_DARK = HexColor("#333333")
TEXT_GRAY = HexColor("#666666")

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 18 * mm

class BrochureCreator:
    def __init__(self, output_path):
        self.c = canvas.Canvas(output_path, pagesize=A4)
        self.page_num = 0
        
    def new_page(self):
        if self.page_num > 0:
            self.c.showPage()
        self.page_num += 1
        
    def draw_footer(self):
        self.c.setFillColor(DARK)
        self.c.rect(0, 0, PAGE_WIDTH, 10*mm, fill=1, stroke=0)
        self.c.setFillColor(white)
        self.c.setFont("Helvetica", 7)
        self.c.drawCentredString(PAGE_WIDTH/2, 3.5*mm, f"Titelli SA  •  www.titelli.com  •  Page {self.page_num}")
    
    def draw_header_dark(self, title):
        # Header bar
        self.c.setFillColor(DARK)
        self.c.rect(0, PAGE_HEIGHT - 35*mm, PAGE_WIDTH, 35*mm, fill=1, stroke=0)
        
        # Logo
        try:
            logo = ImageReader("/app/backend/uploads/logo_titelli_new.png")
            self.c.drawImage(logo, MARGIN, PAGE_HEIGHT - 22*mm, width=14*mm, height=14*mm, mask='auto')
        except:
            pass
        
        # Titelli
        self.c.setFillColor(white)
        self.c.setFont("Times-Bold", 14)
        self.c.drawString(MARGIN + 18*mm, PAGE_HEIGHT - 16*mm, "Titelli")
        
        self.c.setFont("Helvetica-Oblique", 6)
        self.c.drawString(MARGIN + 18*mm, PAGE_HEIGHT - 21*mm, 
                         "Tous les prestataires préférés de votre région")
        
        # Title
        self.c.setFillColor(GOLD)
        self.c.setFont("Helvetica-Bold", 16)
        self.c.drawRightString(PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 20*mm, title)
        
        return PAGE_HEIGHT - 45*mm
    
    def draw_section_title(self, y, title):
        self.c.setFillColor(DARK)
        self.c.setFont("Helvetica-Bold", 12)
        self.c.drawString(MARGIN, y, title)
        
        # Gold underline
        self.c.setStrokeColor(GOLD)
        self.c.setLineWidth(1.5)
        title_width = self.c.stringWidth(title, "Helvetica-Bold", 12)
        self.c.line(MARGIN, y - 2*mm, MARGIN + title_width + 5*mm, y - 2*mm)
        
        return y - 10*mm
    
    def draw_text(self, y, text, font="Helvetica", size=9, color=TEXT_DARK):
        self.c.setFillColor(color)
        self.c.setFont(font, size)
        lines = textwrap.wrap(text, width=95)
        for line in lines:
            self.c.drawString(MARGIN, y, line)
            y -= 4*mm
        return y - 2*mm
    
    def draw_bullet(self, y, text):
        self.c.setFillColor(GOLD)
        self.c.circle(MARGIN + 2*mm, y + 1*mm, 1.2*mm, fill=1, stroke=0)
        
        self.c.setFillColor(TEXT_DARK)
        self.c.setFont("Helvetica", 9)
        lines = textwrap.wrap(text, width=88)
        for i, line in enumerate(lines):
            self.c.drawString(MARGIN + 6*mm, y - i*4*mm, line)
        return y - len(lines)*4*mm - 3*mm
    
    def draw_price_row(self, y, title, price, desc=""):
        # Title
        self.c.setFillColor(TEXT_DARK)
        self.c.setFont("Helvetica-Bold", 9)
        self.c.drawString(MARGIN, y, title)
        
        # Price
        self.c.setFillColor(GOLD)
        self.c.setFont("Helvetica-Bold", 9)
        self.c.drawRightString(PAGE_WIDTH - MARGIN, y, price)
        
        # Description
        if desc:
            self.c.setFillColor(TEXT_GRAY)
            self.c.setFont("Helvetica", 8)
            self.c.drawString(MARGIN + 3*mm, y - 4*mm, desc)
            return y - 11*mm
        return y - 7*mm
    
    def draw_pack_box(self, x, y, width, height, title, items):
        # Box background
        self.c.setFillColor(DARK)
        self.c.roundRect(x, y - height, width, height, 5, fill=1, stroke=0)
        
        # Title
        self.c.setFillColor(GOLD)
        self.c.setFont("Helvetica-Bold", 11)
        self.c.drawString(x + 8*mm, y - 10*mm, title)
        
        # Items
        self.c.setFillColor(white)
        self.c.setFont("Helvetica", 8)
        item_y = y - 18*mm
        for item in items:
            if item_y > y - height + 5*mm:
                self.c.drawString(x + 8*mm, item_y, "• " + item)
                item_y -= 5*mm
    
    # ==================== PAGES ====================
    
    def page_cover(self):
        self.new_page()
        
        # Full dark top
        self.c.setFillColor(DARK)
        self.c.rect(0, PAGE_HEIGHT - 140*mm, PAGE_WIDTH, 140*mm, fill=1, stroke=0)
        
        # Logo centered
        try:
            logo = ImageReader("/app/backend/uploads/logo_titelli_new.png")
            self.c.drawImage(logo, PAGE_WIDTH/2 - 20*mm, PAGE_HEIGHT - 50*mm, 
                           width=40*mm, height=40*mm, mask='auto')
        except:
            pass
        
        # Title
        self.c.setFillColor(white)
        self.c.setFont("Helvetica-Bold", 28)
        self.c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 70*mm, "Ne cherchez plus")
        self.c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 82*mm, "vos clients")
        
        self.c.setFillColor(GOLD)
        self.c.setFont("Helvetica-Bold", 18)
        self.c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 100*mm, "Laissez-les vous trouver !")
        
        self.c.setFillColor(white)
        self.c.setFont("Helvetica", 10)
        self.c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 115*mm, "Ne manquez plus aucune occasion de vendre.")
        
        # Gold line
        self.c.setStrokeColor(GOLD)
        self.c.setLineWidth(2)
        self.c.line(PAGE_WIDTH/2 - 40*mm, PAGE_HEIGHT - 125*mm, 
                   PAGE_WIDTH/2 + 40*mm, PAGE_HEIGHT - 125*mm)
        
        # Mission section
        y = PAGE_HEIGHT - 155*mm
        y = self.draw_section_title(y, "Notre Mission")
        y = self.draw_text(y, "Connecter les meilleurs prestataires de la région afin de permettre chaque jour à de nouveaux clients de les découvrir.")
        y = self.draw_text(y, "Notre but, Vos intérêts. Notre objectif, vos bénéfices.", "Helvetica-Bold", 10, GOLD)
        
        y -= 8*mm
        y = self.draw_section_title(y, "Notre Vision")
        y = self.draw_text(y, "Rendre le client toujours plus proche de ses prestataires préférés.")
        y = self.draw_text(y, "Titelli voit et croit en le véritable potentiel de votre entreprise ainsi qu'en votre plus-value sur le marché.")
        
        self.draw_footer()
    
    def page_prestations(self):
        self.new_page()
        y = self.draw_header_dark("Nos Prestations")
        
        prestations = [
            ("Inscription annuelle", "250.-", "Obligatoire pour accéder à la plateforme"),
            ("Premium livraison instantanée", "50.-/mois", "Répondez aux demandes clients instantanément"),
            ("Pub Référencement mensuel", "dès 100.-/mois", "Référencé dans votre domaine d'activité"),
            ("Marketing visuel", "100.-/mois", "Accès aux meilleurs outils informatisés"),
            ("Expert marketing visuel", "200.- à 1'000.-/mois", "Expert révise votre publicité"),
            ("Premium dépôt 24/24", "100.-/mois", "Dépôt accessible après 19h"),
            ("Fournisseurs", "200.- à 1'000.-/mois", "Accès fournisseurs optimisation"),
            ("Investissement", "200.- à 500.-/mois", "Trouver un partenaire"),
            ("Formations avancées", "200.- à 2'000.-/mois", "Techniques par spécialistes Suisses"),
            ("Soins entreprise", "500.-/mois", "Soins personnel et entreprise"),
            ("Liquidation de stock", "dès 1'000.-/mois", "Titelli liquide votre stock"),
            ("Gestion d'entreprise", "1'000.- à 30'000.-/an", "Expert marketing et fiscaliste"),
            ("Accès immobilier VIP", "1'000.-/mois", "Réseau immobilier privilégié"),
        ]
        
        for title, price, desc in prestations:
            y = self.draw_price_row(y, title, price, desc)
            if y < 20*mm:
                break
        
        self.draw_footer()
    
    def page_packs(self):
        self.new_page()
        y = self.draw_header_dark("Nos Packs")
        
        # Pack boxes - 2 columns
        box_width = 82*mm
        box_height = 55*mm
        gap = 8*mm
        
        packs = [
            ("Pack 200.-/mois", ["Premium livraison 50.-", "Pub Référencement 100.-", "Marketing visuel 100.-"]),
            ("Pack 500.-/mois", ["Premium livraison 50.-", "Pub Référencement 100.-", "Marketing visuel 100.-", "Premium dépôt 100.-", "Fournisseurs 200.-"]),
            ("Pack 1'000.-/mois", ["Premium livraison 50.-", "Pub Référencement 200.-", "Expert marketing 200.-", "Premium dépôt 100.-", "Fournisseurs 200.-", "Formations 200.-"]),
            ("Pack 3'000.-/mois", ["Tout le pack 1'000.-", "Soins entreprise 500.-", "Liquidation stock 1'000.-"]),
        ]
        
        col = 0
        row_y = y
        for pack_name, items in packs:
            x = MARGIN + col * (box_width + gap)
            self.draw_pack_box(x, row_y, box_width, box_height, pack_name, items)
            col += 1
            if col >= 2:
                col = 0
                row_y -= box_height + gap
        
        # Premium packs
        y = row_y - 15*mm
        self.c.setFillColor(GOLD)
        self.c.setFont("Helvetica-Bold", 11)
        self.c.drawString(MARGIN, y, "Packs Premium")
        y -= 10*mm
        
        premium = [
            ("Pack 5'000.-/mois", "Gestion d'entreprise starter incluse"),
            ("Pack 10'000.-/mois", "Gestion smarter + Formations 1'000.-"),
            ("Pack 20'000.-/mois", "Gestion Guest + Immobilier VIP"),
        ]
        
        for name, desc in premium:
            self.c.setFillColor(TEXT_DARK)
            self.c.setFont("Helvetica-Bold", 9)
            self.c.drawString(MARGIN, y, name)
            self.c.setFillColor(TEXT_GRAY)
            self.c.setFont("Helvetica", 8)
            self.c.drawString(MARGIN + 45*mm, y, desc)
            y -= 7*mm
        
        self.draw_footer()
    
    def page_avantages_gratuits(self):
        self.new_page()
        y = self.draw_header_dark("Avantages Gratuits")
        
        avantages = [
            "Une exposition sur Titelli auprès d'un nouveau public",
            "Un spécialiste marketing reprend votre communication",
            "Profil entreprise - book attrayant pour vos prestations",
            "Référencement préférentiel pour renforcer votre présence",
            "Publication d'offres illimitées pour fidéliser vos clients",
            "Mention \"Certifié\" pour valoriser votre savoir-faire",
            "Mention \"Labellisé\" pour les prestations prestigieuses",
            "Accès aux Offres du moment et Guests du moment",
            "Système de Cash-Back (10% retour sur achat)",
            "Gestion du personnel et cahiers des charges",
            "Gestion des stocks avec alertes et automatisation",
            "Espace finance et cartes centralisé",
            "Messagerie professionnelle intégrée",
            "Business News et Feed entreprises",
        ]
        
        for av in avantages:
            y = self.draw_bullet(y, av)
            if y < 20*mm:
                break
        
        self.draw_footer()
    
    def page_services(self):
        self.new_page()
        y = self.draw_header_dark("Services Complémentaires")
        
        services = [
            ("Service Premium", "Accessibilité renforcée pour clients exigeants"),
            ("Optimisation fiscale", "Expert comptable et juridique"),
            ("Livraison instantanée", "Service à domicile en 1-2h"),
            ("Premium dépôt 24/24", "Services disponibles après 19h"),
            ("Liquidez votre stock", "Livraison quotidienne clients réguliers"),
            ("Fournisseurs élite", "Meilleurs fournisseurs internationaux"),
            ("Healthy lifestyle pass", "Exigences de santé respectées"),
            ("Expert Marketing", "Meilleurs experts marketing Suisse"),
            ("Soins entreprise", "Make-up, sport, formation, traiteur..."),
            ("Gestion d'entreprise", "Les experts s'occupent de tout"),
            ("Accès immobilier VIP", "Espaces exclusifs"),
        ]
        
        for title, desc in services:
            self.c.setFillColor(TEXT_DARK)
            self.c.setFont("Helvetica-Bold", 9)
            self.c.drawString(MARGIN, y, title)
            self.c.setFillColor(TEXT_GRAY)
            self.c.setFont("Helvetica", 8)
            self.c.drawString(MARGIN + 50*mm, y, desc)
            y -= 8*mm
            if y < 20*mm:
                break
        
        self.draw_footer()
    
    def page_avantages_clients(self):
        self.new_page()
        y = self.draw_header_dark("Avantages Clients")
        
        avantages = [
            "Profil avec photos et vidéos souvenirs",
            "Cash-back de 10% réutilisable partout",
            "Mode de vie avec objectifs et suggestions",
            "Steward 24/24 pour demandes spontanées",
            "Livraison instantanée 24/24",
            "Formations et opportunités professionnelles",
            "Investissements accessibles en un click",
            "Offres toute l'année aux meilleurs prix",
            "Prestataires Labellisés ou Certifiés garantis",
            "Fiche d'exigences personnalisée",
            "Organisation de sorties avec amis",
            "Fil d'actualité et business news",
            "Devenir influenceur rémunéré",
            "Page publicité personnelle 24/24",
        ]
        
        for av in avantages:
            y = self.draw_bullet(y, av)
            if y < 20*mm:
                break
        
        self.draw_footer()
    
    def page_contact(self):
        self.new_page()
        
        # Full dark page
        self.c.setFillColor(DARK)
        self.c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
        
        # Logo
        try:
            logo = ImageReader("/app/backend/uploads/logo_titelli_new.png")
            self.c.drawImage(logo, PAGE_WIDTH/2 - 25*mm, PAGE_HEIGHT - 90*mm, 
                           width=50*mm, height=50*mm, mask='auto')
        except:
            pass
        
        self.c.setFillColor(white)
        self.c.setFont("Times-Bold", 32)
        self.c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 115*mm, "Titelli")
        
        # Gold line
        self.c.setStrokeColor(GOLD)
        self.c.setLineWidth(2)
        self.c.line(PAGE_WIDTH/2 - 30*mm, PAGE_HEIGHT - 125*mm, 
                   PAGE_WIDTH/2 + 30*mm, PAGE_HEIGHT - 125*mm)
        
        self.c.setFillColor(GOLD)
        self.c.setFont("Helvetica-Bold", 14)
        self.c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 145*mm, "Contactez-nous")
        
        self.c.setFillColor(white)
        self.c.setFont("Helvetica", 11)
        self.c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 165*mm, "www.titelli.com")
        self.c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 177*mm, "info@titelli.com")
        self.c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 189*mm, "+41 79 895 03 13")
        
        # Slogan
        self.c.setFillColor(GOLD)
        self.c.setFont("Helvetica-Oblique", 9)
        self.c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 215*mm, 
                                "\"Tous les prestataires préférés de votre région")
        self.c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 225*mm, 
                                "se trouvent sur Titelli\"")
        
        # Copyright
        self.c.setFillColor(TEXT_GRAY)
        self.c.setFont("Helvetica", 8)
        self.c.drawCentredString(PAGE_WIDTH/2, 15*mm, "© Titelli SA - Tous droits réservés")
    
    def create(self):
        self.page_cover()
        self.page_prestations()
        self.page_packs()
        self.page_avantages_gratuits()
        self.page_services()
        self.page_avantages_clients()
        self.page_contact()
        self.c.save()
        print(f"✅ Brochure créée: {self.page_num} pages")


if __name__ == "__main__":
    brochure = BrochureCreator("/app/backend/uploads/monetisation_titelli_v2.pdf")
    brochure.create()
