#!/usr/bin/env python3
"""
TITELLI - CDC MONETISATION ULTRA-COMPLET
========================================
Document exhaustif de tous les modeles de revenus,
abonnements, options a la carte et algorithmes
"""

from fpdf import FPDF
from datetime import datetime
import os

class TitelliMonetisationCDC(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.chapter_num = 0
        self.section_num = 0
        
    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, f'TITELLI - CDC Monetisation Complete | Page {self.page_no()}', align='C')
            self.ln(15)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Document confidentiel - {datetime.now().strftime("%d/%m/%Y")}', align='C')
    
    def add_cover(self):
        self.add_page()
        self.set_fill_color(16, 185, 129)  # Vert emerald
        self.rect(0, 0, 210, 297, 'F')
        
        self.set_font('Helvetica', 'B', 48)
        self.set_text_color(255, 255, 255)
        self.set_y(60)
        self.cell(0, 20, 'TITELLI', align='C')
        
        self.set_font('Helvetica', 'B', 28)
        self.ln(30)
        self.cell(0, 15, 'CAHIER DES CHARGES', align='C')
        self.ln(15)
        self.cell(0, 15, 'MONETISATION', align='C')
        
        self.set_font('Helvetica', '', 18)
        self.ln(25)
        self.cell(0, 10, 'EDITION ULTRA-COMPLETE', align='C')
        
        self.set_font('Helvetica', '', 14)
        self.ln(40)
        self.cell(0, 8, 'Tous les abonnements detailles', align='C')
        self.ln(8)
        self.cell(0, 8, 'Options a la carte', align='C')
        self.ln(8)
        self.cell(0, 8, 'Algorithmes de tarification', align='C')
        self.ln(8)
        self.cell(0, 8, 'Scenarios et flux de paiement', align='C')
        
        self.set_font('Helvetica', 'B', 14)
        self.ln(40)
        self.cell(0, 10, f'Version 5.0 - {datetime.now().strftime("%d %B %Y")}', align='C')
    
    def add_toc(self):
        self.add_page()
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(16, 185, 129)
        self.cell(0, 15, 'TABLE DES MATIERES', align='C')
        self.ln(20)
        
        toc = [
            ("1. RESUME EXECUTIF MONETISATION", 4),
            ("2. ABONNEMENTS ENTREPRISES", 6),
            ("   2.1 Standard (200 CHF/mois)", 7),
            ("   2.2 Guest (250 CHF/mois)", 8),
            ("   2.3 Premium (500 CHF/mois)", 9),
            ("   2.4 Premium MVP (1000 CHF/mois)", 10),
            ("   2.5 Optimisation Starter 2K", 12),
            ("   2.6 Optimisation Starter+ 3K", 14),
            ("   2.7 Optimisation 5K", 16),
            ("   2.8 Optimisation 10K", 18),
            ("   2.9 Optimisation 20K", 20),
            ("   2.10 Optimisation 50K", 22),
            ("3. ABONNEMENTS CLIENTS", 25),
            ("   3.1 Free (Gratuit)", 26),
            ("   3.2 Premium Client (9.99 CHF/mois)", 27),
            ("   3.3 VIP Client (29.99 CHF/mois)", 28),
            ("4. OPTIONS A LA CARTE", 30),
            ("   4.1 Options mensuelles", 31),
            ("   4.2 Options ponctuelles", 34),
            ("5. PUBLICITES ET VISIBILITE", 37),
            ("   5.1 Pub Flash (Encheres)", 38),
            ("   5.2 Pub Expert (Forfaits)", 42),
            ("   5.3 Pub Media IA (Images)", 45),
            ("   5.4 Video Pub IA (Sora 2)", 50),
            ("6. COMMISSIONS ET TRANSACTIONS", 55),
            ("   6.1 Commission sur ventes", 56),
            ("   6.2 Systeme de Cashback", 58),
            ("7. ALGORITHMES DE TARIFICATION", 62),
            ("   7.1 Algorithme de boost publicitaire", 63),
            ("   7.2 Calcul du cashback", 66),
            ("   7.3 Algorithme de visibilite", 68),
            ("8. SCENARIOS DE MONETISATION", 72),
            ("   8.1 Parcours entreprise Standard", 73),
            ("   8.2 Parcours entreprise Premium", 76),
            ("   8.3 Parcours client Premium", 80),
            ("9. FLUX DE PAIEMENT STRIPE", 84),
            ("10. PROJECTIONS FINANCIERES", 90),
            ("11. ANNEXES - TARIFS COMPLETS", 98),
        ]
        
        self.set_font('Helvetica', '', 10)
        self.set_text_color(60, 60, 60)
        for item, page in toc:
            if item.startswith("   "):
                self.set_font('Helvetica', '', 9)
            else:
                self.set_font('Helvetica', 'B', 10)
                self.ln(2)
            dots = '.' * (65 - len(item))
            self.cell(0, 5, f"{item} {dots} {page}")
            self.ln(5)
    
    def add_chapter(self, title):
        self.chapter_num += 1
        self.section_num = 0
        self.add_page()
        self.set_fill_color(16, 185, 129)
        self.rect(0, 0, 210, 50, 'F')
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(255, 255, 255)
        self.set_y(20)
        self.cell(0, 15, f'{self.chapter_num}. {title.upper()}', align='C')
        self.ln(35)
        self.set_text_color(60, 60, 60)
    
    def add_section(self, title):
        self.section_num += 1
        self.ln(8)
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(16, 185, 129)
        self.cell(0, 10, f'{self.chapter_num}.{self.section_num} {title}')
        self.ln(10)
        self.set_text_color(60, 60, 60)
    
    def add_subsection(self, title):
        self.ln(5)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(80, 80, 80)
        self.cell(0, 7, title)
        self.ln(8)
        self.set_text_color(60, 60, 60)
    
    def add_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(60, 60, 60)
        self.multi_cell(185, 5, text)
        self.ln(3)
    
    def add_bullet(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(60, 60, 60)
        self.multi_cell(185, 5, f"  * {text}")
    
    def add_price_box(self, title, price, period="mois"):
        self.set_fill_color(16, 185, 129)
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(255, 255, 255)
        self.cell(90, 10, title, fill=True, align='C')
        self.set_fill_color(245, 245, 245)
        self.set_text_color(16, 185, 129)
        self.set_font('Helvetica', 'B', 14)
        self.cell(90, 10, f"{price} CHF/{period}", fill=True, align='C')
        self.ln(12)
    
    def add_feature_list(self, features, included=True):
        self.set_font('Helvetica', '', 9)
        for f in features:
            if included:
                self.set_text_color(16, 185, 129)
                prefix = "[OK] "
            else:
                self.set_text_color(200, 200, 200)
                prefix = "[  ] "
            self.multi_cell(185, 4, f"{prefix}{f}")
        self.ln(3)
        self.set_text_color(60, 60, 60)
    
    def add_table(self, headers, rows, col_widths=None):
        if col_widths is None:
            col_widths = [180 / len(headers)] * len(headers)
        
        self.set_font('Helvetica', 'B', 8)
        self.set_fill_color(16, 185, 129)
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, str(h)[:25], border=1, fill=True, align='C')
        self.ln(7)
        
        self.set_font('Helvetica', '', 8)
        self.set_text_color(60, 60, 60)
        fill = False
        for row in rows:
            if fill:
                self.set_fill_color(245, 245, 245)
            else:
                self.set_fill_color(255, 255, 255)
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 6, str(cell)[:25], border=1, fill=True, align='C')
            self.ln(6)
            fill = not fill
        self.ln(5)
    
    def add_algorithm_box(self, title, code):
        self.set_fill_color(40, 40, 50)
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(16, 185, 129)
        self.cell(180, 8, f"ALGORITHME: {title}", fill=True)
        self.ln(10)
        self.set_font('Courier', '', 8)
        self.set_text_color(200, 200, 200)
        lines = code.strip().split('\n')
        for line in lines:
            line = line.replace('\t', '    ')[:80]
            self.set_fill_color(40, 40, 50)
            self.multi_cell(180, 4, line, fill=True)
        self.ln(5)
        self.set_text_color(60, 60, 60)
    
    def add_scenario_box(self, num, title, steps, result, revenue):
        self.set_fill_color(16, 185, 129)
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(255, 255, 255)
        self.cell(140, 8, f"SCENARIO {num}: {title}", fill=True)
        self.set_fill_color(245, 158, 11)
        self.cell(40, 8, f"{revenue} CHF", fill=True, align='C')
        self.ln(10)
        
        self.set_font('Helvetica', '', 9)
        self.set_text_color(60, 60, 60)
        for i, step in enumerate(steps, 1):
            self.multi_cell(180, 4, f"  {i}. {step}")
        
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(16, 185, 129)
        self.multi_cell(180, 5, f"  => RESULTAT: {result}")
        self.ln(5)


def generate_monetisation_cdc():
    pdf = TitelliMonetisationCDC()
    
    # ========== COVER ==========
    pdf.add_cover()
    
    # ========== TOC ==========
    pdf.add_toc()
    
    # ========== CHAPITRE 1: RESUME EXECUTIF ==========
    pdf.add_chapter("RESUME EXECUTIF MONETISATION")
    
    pdf.add_text("""
TITELLI genere des revenus a travers 6 canaux principaux de monetisation, offrant une diversification optimale des sources de revenus et un modele scalable.

SYNTHESE DES SOURCES DE REVENUS:
    """)
    
    pdf.add_table(
        ["Source de revenus", "Type", "Fourchette", "% CA estime"],
        [
            ["Abonnements Entreprises", "Recurrent", "200-50'000 CHF/mois", "45%"],
            ["Abonnements Clients", "Recurrent", "0-29.99 CHF/mois", "8%"],
            ["Options a la carte", "Ponctuel/Recurrent", "200-4'000 CHF", "12%"],
            ["Publicites (Encheres)", "Variable", "10-2'000 CHF", "15%"],
            ["Pub Media IA (Images)", "Ponctuel", "19.90-69.90 CHF", "10%"],
            ["Video Pub IA (Sora 2)", "Ponctuel", "129.90-399.90 CHF", "7%"],
            ["Commissions ventes", "% transaction", "5-10%", "3%"],
        ],
        [50, 35, 50, 45]
    )
    
    pdf.add_text("""
CHIFFRES CLES:
- 10 plans d'abonnement entreprises (200 a 50'000 CHF)
- 3 plans d'abonnement clients (Gratuit, Premium, VIP)
- 13 options a la carte disponibles
- 9 types de publicites (encheres et forfaits)
- 34 templates Pub Media IA
- 13 templates Video Pub IA
- Taux de cashback: 1% (free) a 15% (VIP)
    """)
    
    # ========== CHAPITRE 2: ABONNEMENTS ENTREPRISES ==========
    pdf.add_chapter("ABONNEMENTS ENTREPRISES")
    
    pdf.add_text("""
Les abonnements entreprises constituent le coeur du modele de revenus de Titelli. 
10 plans sont disponibles, du Standard (200 CHF) jusqu'a l'Optimisation 50K.
Chaque plan offre des fonctionnalites progressives et un accompagnement croissant.
    """)
    
    # Plan Standard
    pdf.add_section("Standard")
    pdf.add_price_box("STANDARD", "200", "mois")
    pdf.add_text("Le plan d'entree pour les petites entreprises souhaitant rejoindre la plateforme.")
    pdf.add_subsection("Fonctionnalites incluses")
    pdf.add_feature_list([
        "Exposition standard dans les resultats de recherche",
        "Une publication mensuelle sur le fil d'actualites",
        "Systeme de Cash-Back (taux standard)",
        "Systeme de gestion des stocks basique",
        "Acces a la messagerie clients",
        "Fiches exigences clients",
        "Calendrier client",
        "Agenda interne"
    ])
    pdf.add_subsection("Fonctionnalites NON incluses")
    pdf.add_feature_list([
        "Publicites supplementaires",
        "Referencement preferentiel",
        "Acces investisseurs",
        "Livraison 24/24",
        "Acces fournisseurs",
        "Formations premium"
    ], included=False)
    
    pdf.add_subsection("Cas d'usage type")
    pdf.add_text("""
- Coiffeur independant souhaitant tester la plateforme
- Petit commerce de quartier
- Artisan debutant
- Auto-entrepreneur
    """)
    
    # Plan Guest
    pdf.add_section("Guest")
    pdf.add_price_box("GUEST", "250", "mois")
    pdf.add_text("Plan intermediaire avec profil professionnel et referencement ameliore.")
    pdf.add_subsection("Fonctionnalites incluses")
    pdf.add_feature_list([
        "Profil prestataire professionnel complet",
        "Referencement preferentiel dans les recherches",
        "Publication d'offres illimitees",
        "Systeme de Cash-Back",
        "Systeme de gestion des stocks",
        "Badge 'Guest' sur le profil",
        "Statistiques de base"
    ])
    
    # Plan Premium
    pdf.add_section("Premium")
    pdf.add_price_box("PREMIUM", "500", "mois")
    pdf.add_text("Plan complet pour les entreprises etablies cherchant plus de visibilite.")
    pdf.add_subsection("Fonctionnalites incluses")
    pdf.add_feature_list([
        "Profil prestataire professionnel",
        "4 Publicites par mois (valeur 120 CHF)",
        "Accessible aux investisseurs",
        "Accessible aux livraisons 24/24",
        "Referencement preferentiel",
        "Publication d'offres illimitees",
        "Systeme de Cash-Back ameliore",
        "Systeme de gestion des stocks avance",
        "Systeme gestion du personnel",
        "Badge 'Premium' dore"
    ])
    
    pdf.add_subsection("Calcul de rentabilite")
    pdf.add_table(
        ["Element", "Valeur incluse", "Si achete separement"],
        [
            ["4 Publicites/mois", "Inclus", "120 CHF"],
            ["Acces investisseurs", "Inclus", "300 CHF"],
            ["Livraison 24/24", "Inclus", "300 CHF"],
            ["Gestion personnel", "Inclus", "200 CHF"],
            ["TOTAL", "500 CHF", "920 CHF"],
        ]
    )
    pdf.add_text("Economie: 420 CHF/mois soit 84% de reduction")
    
    # Plan Premium MVP
    pdf.add_section("Premium MVP")
    pdf.add_price_box("PREMIUM MVP", "1'000", "mois")
    pdf.add_text("Plan avance avec publicites medias et video incluses.")
    pdf.add_subsection("Fonctionnalites incluses")
    pdf.add_feature_list([
        "Tout le plan Premium +",
        "5 Publicites media par mois (generation IA)",
        "1 Publicite video par mois (Sora 2)",
        "Acces aux fournisseurs partenaires",
        "Acces au local 24/24",
        "Support prioritaire",
        "Badge 'MVP' exclusif"
    ])
    
    pdf.add_subsection("Valeur des services inclus")
    pdf.add_table(
        ["Service", "Quantite", "Prix unitaire", "Valeur totale"],
        [
            ["Pub Media IA", "5/mois", "29.90 CHF", "149.50 CHF"],
            ["Video Pub IA", "1/mois", "199.90 CHF", "199.90 CHF"],
            ["Acces fournisseurs", "Illimite", "500 CHF", "500 CHF"],
            ["Acces local 24/24", "Illimite", "300 CHF", "300 CHF"],
            ["SOUS-TOTAL", "-", "-", "1'149.40 CHF"],
            ["+ Plan Premium", "-", "-", "500 CHF"],
            ["TOTAL VALEUR", "-", "-", "1'649.40 CHF"],
        ]
    )
    pdf.add_text("Economie: 649.40 CHF/mois soit 39% de reduction")
    
    # Plans Optimisation
    pdf.add_section("Optimisation Starter 2K")
    pdf.add_price_box("OPTI STARTER", "2'000", "mois")
    pdf.add_text("Premier niveau du programme d'optimisation d'entreprise avec accompagnement expert.")
    pdf.add_subsection("Fonctionnalites exclusives")
    pdf.add_feature_list([
        "8 Publicites media par mois",
        "1 Publicite video par mois",
        "Acces aux formations premium",
        "Acces aux recrutements",
        "Acces a l'espace immobilier",
        "Un expert offre des conseils d'optimisation",
        "Un expert vous labellise (certification)",
        "Accompagnement personnalise"
    ])
    
    pdf.add_section("Optimisation Starter+ 3K")
    pdf.add_price_box("OPTI STARTER+", "3'000", "mois")
    pdf.add_subsection("Fonctionnalites additionnelles vs 2K")
    pdf.add_feature_list([
        "15 Publicites a choix par mois (vs 8)",
        "2 Publicites videos par mois (vs 1)",
        "5h Prestation service entreprise OU",
        "2 dejeuners d'equipe (10 personnes)"
    ])
    
    pdf.add_section("Optimisation 5K")
    pdf.add_price_box("OPTI 5K", "5'000", "mois")
    pdf.add_subsection("Fonctionnalites additionnelles vs 3K")
    pdf.add_feature_list([
        "10h Prestation service entreprise OU 5 dejeuners equipe",
        "3'000 CHF de prestations liquidees par nos equipes",
        "Accompagnement commercial renforce"
    ])
    
    pdf.add_section("Optimisation 10K")
    pdf.add_price_box("OPTI 10K", "10'000", "mois")
    pdf.add_subsection("Fonctionnalites additionnelles vs 5K")
    pdf.add_feature_list([
        "20h Prestation service entreprise OU 8 dejeuners equipe",
        "7'000 CHF de prestations liquidees par nos equipes",
        "Fiscaliste inclus (valeur 4'000 CHF/mois)",
        "Conseil fiscal et optimisation"
    ])
    
    pdf.add_section("Optimisation 20K")
    pdf.add_price_box("OPTI 20K", "20'000", "mois")
    pdf.add_subsection("Fonctionnalites additionnelles vs 10K")
    pdf.add_feature_list([
        "25 Publicites a choix par mois (vs 15)",
        "4 Publicites videos par mois (vs 2)",
        "40h Prestation service entreprise OU 20 dejeuners equipe",
        "15'000 CHF de prestations liquidees par nos equipes",
        "Fiscaliste inclus",
        "Account manager dedie"
    ])
    
    pdf.add_section("Optimisation 50K")
    pdf.add_price_box("OPTI 50K", "50'000", "mois")
    pdf.add_text("Le plan ultime pour les grandes entreprises avec accompagnement complet.")
    pdf.add_subsection("Fonctionnalites completes")
    pdf.add_feature_list([
        "25 Publicites a choix par mois",
        "4 Publicites videos par mois",
        "80h Prestation service entreprise OU 40 dejeuners equipe",
        "40'000 CHF de prestations liquidees par nos equipes",
        "Fiscaliste inclus",
        "Account manager VIP dedie",
        "Reporting personnalise mensuel",
        "Acces a tous les evenements Titelli",
        "Mise en avant homepage permanente"
    ])
    
    # Tableau comparatif complet
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(16, 185, 129)
    pdf.cell(0, 10, "TABLEAU COMPARATIF ABONNEMENTS ENTREPRISES")
    pdf.ln(15)
    
    pdf.add_table(
        ["Plan", "Prix", "Pubs/mois", "Videos/mois", "Prestations"],
        [
            ["Standard", "200 CHF", "1", "0", "-"],
            ["Guest", "250 CHF", "Illimite", "0", "-"],
            ["Premium", "500 CHF", "4", "0", "-"],
            ["Premium MVP", "1'000 CHF", "5", "1", "-"],
            ["Opti 2K", "2'000 CHF", "8", "1", "Expert conseil"],
            ["Opti 3K", "3'000 CHF", "15", "2", "5h service"],
            ["Opti 5K", "5'000 CHF", "15", "2", "10h + 3K liquide"],
            ["Opti 10K", "10'000 CHF", "15", "2", "20h + 7K + fiscal"],
            ["Opti 20K", "20'000 CHF", "25", "4", "40h + 15K + fiscal"],
            ["Opti 50K", "50'000 CHF", "25", "4", "80h + 40K + VIP"],
        ],
        [35, 30, 30, 30, 55]
    )
    
    # ========== CHAPITRE 3: ABONNEMENTS CLIENTS ==========
    pdf.add_chapter("ABONNEMENTS CLIENTS")
    
    pdf.add_text("""
Les clients particuliers peuvent souscrire a des abonnements premium pour beneficier d'avantages exclusifs, notamment un taux de cashback ameliore.
    """)
    
    pdf.add_section("Free (Gratuit)")
    pdf.add_price_box("FREE", "0", "mois")
    pdf.add_subsection("Fonctionnalites incluses")
    pdf.add_feature_list([
        "Acces complet a la plateforme",
        "Achat aupres de tous les prestataires",
        "Messagerie avec les entreprises",
        "Cashback 1% sur tous les achats",
        "Systeme de gamification (XP, badges)",
        "Fil d'actualites"
    ])
    
    pdf.add_section("Premium Client")
    pdf.add_price_box("PREMIUM", "9.99", "mois")
    pdf.add_subsection("Fonctionnalites incluses")
    pdf.add_feature_list([
        "Acces illimite aux prestataires",
        "Messagerie illimitee",
        "10% cashback (vs 1% free)",
        "Offres exclusives Premium",
        "Support prioritaire",
        "Badge Premium visible",
        "Acces aux ventes privees"
    ])
    
    pdf.add_subsection("Calcul de rentabilite client")
    pdf.add_text("""
Pour rentabiliser l'abonnement Premium a 9.99 CHF/mois avec 10% de cashback:
- Depenses necessaires: 9.99 / (10% - 1%) = 111 CHF/mois
- Soit environ 28 CHF/semaine d'achats sur la plateforme
    """)
    
    pdf.add_section("VIP Client")
    pdf.add_price_box("VIP", "29.99", "mois")
    pdf.add_subsection("Fonctionnalites incluses")
    pdf.add_feature_list([
        "Tout Premium +",
        "15% cashback (le meilleur taux)",
        "Concierge personnel dedie",
        "Acces aux evenements VIP Titelli",
        "Reductions partenaires exclusives",
        "Badge VIP dore exclusif",
        "Livraison prioritaire",
        "Acces anticipe aux nouveautes"
    ])
    
    pdf.add_subsection("Calcul de rentabilite VIP")
    pdf.add_text("""
Pour rentabiliser l'abonnement VIP a 29.99 CHF/mois avec 15% de cashback:
- Depenses necessaires: 29.99 / (15% - 1%) = 214 CHF/mois
- Soit environ 54 CHF/semaine d'achats sur la plateforme
    """)
    
    # Tableau comparatif clients
    pdf.add_table(
        ["Plan", "Prix/mois", "Cashback", "Support", "Badge"],
        [
            ["Free", "0 CHF", "1%", "Standard", "-"],
            ["Premium", "9.99 CHF", "10%", "Prioritaire", "Premium"],
            ["VIP", "29.99 CHF", "15%", "Concierge", "VIP dore"],
        ]
    )
    
    # ========== CHAPITRE 4: OPTIONS A LA CARTE ==========
    pdf.add_chapter("OPTIONS A LA CARTE")
    
    pdf.add_text("""
Les entreprises peuvent enrichir leur abonnement avec des options a la carte, 
soit de maniere mensuelle recurrente, soit en achat ponctuel unique.
    """)
    
    pdf.add_section("Options mensuelles")
    
    pdf.add_table(
        ["Option", "Prix/mois", "Description"],
        [
            ["2 Pubs + 1 video", "200 CHF", "Pack publicitaire supplementaire"],
            ["Acces investisseurs", "300 CHF", "Visibilite aupres des investisseurs"],
            ["Livraison 24/24", "300 CHF", "Service livraison permanente"],
            ["Acces local 24/24", "300 CHF", "Cle virtuelle pour clients"],
            ["Acces fournisseurs", "500 CHF", "Reseau fournisseurs Titelli"],
            ["Formations premium", "200 CHF", "Catalogue formations business"],
            ["Recrutement instantane", "200 CHF", "Acces candidats qualifies"],
            ["Espace immobilier", "200 CHF", "Annonces locaux commerciaux"],
            ["Expert conseil", "1'000 CHF", "Accompagnement mensuel expert"],
            ["Fiscaliste", "4'000 CHF", "Conseil fiscal professionnel"],
            ["Prestations liquidees", "1'000 CHF", "800 CHF de services offerts"],
        ],
        [50, 35, 95]
    )
    
    pdf.add_section("Options ponctuelles")
    
    pdf.add_table(
        ["Option", "Prix unique", "Description"],
        [
            ["Expert labellisation", "400 CHF", "Certification par expert Titelli"],
            ["20h Prestation service", "1'000 CHF", "Pack heures de service"],
            ["20 dejeuners equipe", "2'000 CHF", "Team building (10 pers/dejeuner)"],
        ],
        [50, 35, 95]
    )
    
    pdf.add_subsection("Combinaisons recommandees")
    pdf.add_text("""
PACK VISIBILITE (600 CHF/mois):
- 2 Pubs + 1 video (200 CHF)
- Acces investisseurs (300 CHF)
- Economies: ideal pour levee de fonds

PACK CROISSANCE (1'400 CHF/mois):
- Acces fournisseurs (500 CHF)
- Formations premium (200 CHF)
- Recrutement instantane (200 CHF)
- Acces espace immobilier (200 CHF)
- Expert conseil (300 CHF - remise pack)
- Economies: 300 CHF vs achat separe

PACK PREMIUM COMPLET (5'200 CHF/mois):
- Expert conseil (1'000 CHF)
- Fiscaliste (4'000 CHF)
- Prestations liquidees (1'000 CHF)
- Remise pack: -800 CHF
- Economies: ideal pour PME en croissance
    """)
    
    # ========== CHAPITRE 5: PUBLICITES ==========
    pdf.add_chapter("PUBLICITES ET VISIBILITE")
    
    pdf.add_section("Pub Flash (Systeme d'encheres)")
    
    pdf.add_text("""
Le systeme Pub Flash permet aux entreprises de booster leur visibilite via un systeme d'encheres. 
Plus le budget est eleve, plus la visibilite est importante.
    """)
    
    pdf.add_table(
        ["Type Pub Flash", "Budget Min", "Budget Max", "Placement"],
        [
            ["Offres du moment", "10 CHF", "1'000 CHF", "Homepage carousel"],
            ["Certifies", "20 CHF", "1'000 CHF", "Section certifies"],
            ["Labellises", "30 CHF", "2'000 CHF", "Section premium"],
            ["Son domaine", "10 CHF", "1'000 CHF", "Par categorie"],
            ["Guests", "10 CHF", "1'000 CHF", "Section guests"],
            ["Tendances", "20 CHF", "1'000 CHF", "Trending section"],
        ],
        [50, 35, 35, 60]
    )
    
    pdf.add_subsection("Algorithme de positionnement")
    pdf.add_algorithm_box("BOOST_POSITION", """
def calculate_ad_position(budget, base_position):
    # Score de boost base sur le budget
    if budget >= 500:
        boost_multiplier = 3.0  # Top priority
    elif budget >= 200:
        boost_multiplier = 2.0  # High priority
    elif budget >= 100:
        boost_multiplier = 1.5  # Medium priority
    else:
        boost_multiplier = 1.0  # Standard
    
    # Score final = budget * multiplicateur
    score = budget * boost_multiplier
    
    # Tri par score decroissant
    return sorted(ads, key=lambda x: x.score, reverse=True)
    """)
    
    pdf.add_section("Pub Expert (Forfaits annuels)")
    
    pdf.add_table(
        ["Forfait", "Prix/an", "Avantages"],
        [
            ["Pub Expert Standard", "300 CHF", "Visibilite section experts"],
            ["Pub Expert Premium", "1'000 CHF", "Top placement + badge"],
        ],
        [60, 40, 80]
    )
    
    pdf.add_section("Pub Media IA (Generation d'images)")
    
    pdf.add_text("""
Service de generation d'images publicitaires par intelligence artificielle (DALL-E).
34 templates disponibles dans 7 categories.
    """)
    
    pdf.add_table(
        ["Categorie", "Templates", "Prix moyen", "Formats"],
        [
            ["Reseaux Sociaux", "7", "29.90 CHF", "1080x1080, 1080x1920"],
            ["Bannieres Web", "5", "39.90 CHF", "1920x600, 300x600"],
            ["Restauration", "6", "39.90 CHF", "A4, A5"],
            ["Flyers & Affiches", "5", "44.90 CHF", "A5, A3"],
            ["Email Marketing", "4", "34.90 CHF", "600x200, 600x900"],
            ["Video (miniatures)", "3", "24.90 CHF", "1280x720"],
            ["Print", "4", "39.90 CHF", "85x55mm, A4"],
        ],
        [45, 25, 35, 75]
    )
    
    pdf.add_subsection("Tarifs detailles par template")
    pdf.add_table(
        ["Template", "Prix"],
        [
            ["Instagram Post (Promo Flash)", "29.90 CHF"],
            ["Instagram Story", "24.90 CHF"],
            ["Carousel Produit", "39.90 CHF"],
            ["Hero Banner", "49.90 CHF"],
            ["Menu Restaurant", "39.90-44.90 CHF"],
            ["Flyer Evenement", "34.90 CHF"],
            ["Affiche A3", "54.90 CHF"],
            ["Newsletter", "49.90 CHF"],
            ["Miniature YouTube", "24.90 CHF"],
            ["Carte de visite", "34.90-39.90 CHF"],
            ["Brochure corporate", "69.90 CHF"],
        ],
        [100, 80]
    )
    
    pdf.add_section("Video Pub IA (Sora 2)")
    
    pdf.add_text("""
Service de generation de videos publicitaires par Sora 2 (OpenAI).
13 templates disponibles dans 6 categories.
    """)
    
    pdf.add_table(
        ["Categorie", "Templates", "Duree", "Prix"],
        [
            ["Reseaux Sociaux", "3", "8-15s", "129.90-199.90 CHF"],
            ["Publicites", "3", "8-15s", "179.90-299.90 CHF"],
            ["Restauration", "2", "12-15s", "199.90-219.90 CHF"],
            ["Corporate", "2", "12-15s", "199.90-249.90 CHF"],
            ["Evenements", "2", "8-15s", "149.90-219.90 CHF"],
            ["Sur Mesure", "1", "15s", "399.90 CHF"],
        ],
        [50, 25, 30, 75]
    )
    
    pdf.add_subsection("Tarifs video detailles")
    pdf.add_table(
        ["Template Video", "Duree", "Taille", "Prix"],
        [
            ["Instagram Reel - Produit", "15s", "1024x1792", "199.90 CHF"],
            ["TikTok - Tendance", "8s", "1024x1792", "149.90 CHF"],
            ["Story Animee", "8s", "1024x1792", "129.90 CHF"],
            ["Pub Hero - Premium", "15s", "1792x1024", "249.90 CHF"],
            ["Spot Produit 30s", "12s", "1792x1024", "299.90 CHF"],
            ["Teaser Lancement", "8s", "1280x720", "179.90 CHF"],
            ["Menu Video", "15s", "1280x720", "199.90 CHF"],
            ["Ambiance Restaurant", "12s", "1792x1024", "219.90 CHF"],
            ["Presentation Entreprise", "15s", "1792x1024", "249.90 CHF"],
            ["Vitrine Services", "12s", "1280x720", "199.90 CHF"],
            ["Promo Evenement", "15s", "1280x720", "219.90 CHF"],
            ["Compte a Rebours", "8s", "1024x1024", "149.90 CHF"],
            ["Creation Sur Mesure", "15s", "Custom", "399.90 CHF"],
        ],
        [55, 20, 35, 40]
    )
    
    # ========== CHAPITRE 6: COMMISSIONS ==========
    pdf.add_chapter("COMMISSIONS ET TRANSACTIONS")
    
    pdf.add_section("Commission sur ventes")
    
    pdf.add_text("""
Titelli preleve une commission sur chaque transaction realisee sur la plateforme.
Le taux varie selon le type d'abonnement de l'entreprise.
    """)
    
    pdf.add_table(
        ["Type abonnement", "Commission", "Description"],
        [
            ["Standard/Guest", "10%", "Taux de base"],
            ["Premium", "8%", "Taux reduit premium"],
            ["Premium MVP", "7%", "Taux preferentiel"],
            ["Optimisation 2K-5K", "6%", "Taux optimise"],
            ["Optimisation 10K+", "5%", "Meilleur taux"],
        ],
        [60, 35, 85]
    )
    
    pdf.add_section("Systeme de Cashback")
    
    pdf.add_text("""
Le cashback est credite automatiquement sur le compte du client apres chaque achat confirme.
Le taux depend de l'abonnement client.
    """)
    
    pdf.add_table(
        ["Abonnement client", "Taux cashback", "Exemple 100 CHF"],
        [
            ["Free", "1%", "1 CHF credite"],
            ["Premium (9.99 CHF)", "10%", "10 CHF credites"],
            ["VIP (29.99 CHF)", "15%", "15 CHF credites"],
        ],
        [60, 50, 70]
    )
    
    pdf.add_subsection("Algorithme de calcul cashback")
    pdf.add_algorithm_box("CASHBACK_CALCULATION", """
async def calculate_cashback(user_id, order_total):
    # Recuperer le plan utilisateur
    subscription = await db.subscriptions.find_one({
        "user_id": user_id,
        "status": "active"
    })
    
    # Determiner le taux
    CASHBACK_RATES = {
        "free": 0.01,    # 1%
        "premium": 0.10,  # 10%
        "vip": 0.15       # 15%
    }
    
    plan = subscription.get('plan', 'free') if subscription else 'free'
    rate = CASHBACK_RATES.get(plan, 0.01)
    
    # Calculer le montant
    cashback_amount = order_total * rate
    
    # Crediter le compte
    await db.users.update_one(
        {"id": user_id},
        {"$inc": {"cashback_balance": cashback_amount}}
    )
    
    return cashback_amount
    """)
    
    # ========== CHAPITRE 7: ALGORITHMES ==========
    pdf.add_chapter("ALGORITHMES DE TARIFICATION")
    
    pdf.add_section("Algorithme de boost publicitaire")
    
    pdf.add_text("""
L'algorithme de boost determine l'ordre d'affichage des publicites payantes.
Les entreprises avec un budget plus eleve apparaissent en premier.
    """)
    
    pdf.add_algorithm_box("ADVERTISING_BOOST", """
async def get_boosted_advertising(placement, category, limit):
    # Recuperer les pubs actives et payees
    query = {
        "status": "active",
        "payment_status": "paid",
        "expires_at": {"$gt": datetime.now()}
    }
    
    if placement:
        query["placement"] = placement
    if category:
        query["category"] = category
    
    # Trier par budget decroissant (plus de budget = plus visible)
    ads = await db.advertising.find(query)
        .sort("budget", -1)
        .limit(limit)
        .to_list(length=limit)
    
    # Calculer le score de visibilite
    for ad in ads:
        ad['visibility_score'] = calculate_visibility_score(ad)
    
    return sorted(ads, key=lambda x: x['visibility_score'], reverse=True)

def calculate_visibility_score(ad):
    base_score = ad.get('budget', 0)
    
    # Bonus pour abonnement premium
    if ad.get('enterprise_tier') in ['premium', 'optimisation']:
        base_score *= 1.2
    
    # Bonus pour certification
    if ad.get('is_certified'):
        base_score *= 1.1
    
    # Malus pour anciennete (pubs recentes prioritaires)
    days_old = (datetime.now() - ad.get('created_at')).days
    freshness_factor = max(0.5, 1 - (days_old * 0.02))
    
    return base_score * freshness_factor
    """)
    
    pdf.add_section("Calcul du cashback (detaille)")
    
    pdf.add_algorithm_box("CASHBACK_COMPLETE", """
# Configuration des taux par plan
PREMIUM_PLANS = {
    "free": {
        "name": "Gratuit",
        "price": 0.0,
        "cashback_rate": 0.01,  # 1%
        "features": ["Acces de base"]
    },
    "premium": {
        "name": "Premium", 
        "price": 9.99,
        "cashback_rate": 0.10,  # 10%
        "features": ["Support prioritaire", "Offres exclusives"]
    },
    "vip": {
        "name": "VIP",
        "price": 29.99,
        "cashback_rate": 0.15,  # 15%
        "features": ["Concierge", "Evenements VIP"]
    }
}

async def process_order_cashback(order):
    user = await db.users.find_one({"id": order['user_id']})
    rate = await get_cashback_rate(order['user_id'])
    
    cashback = order['total'] * rate
    
    # Enregistrer la transaction
    await db.cashback_transactions.insert_one({
        "user_id": order['user_id'],
        "order_id": order['id'],
        "amount": cashback,
        "rate": rate,
        "type": "earned",
        "created_at": datetime.now()
    })
    
    # Crediter le solde
    await db.users.update_one(
        {"id": order['user_id']},
        {"$inc": {"cashback_balance": cashback}}
    )
    
    return cashback
    """)
    
    pdf.add_section("Algorithme de visibilite entreprises")
    
    pdf.add_algorithm_box("ENTERPRISE_VISIBILITY", """
def calculate_enterprise_ranking(enterprise):
    score = 0
    
    # 1. Score abonnement (poids: 40%)
    PLAN_SCORES = {
        "standard": 10,
        "guest": 20,
        "premium": 40,
        "premium_mvp": 60,
        "opti_2k": 80,
        "opti_3k": 90,
        "opti_5k": 100,
        "opti_10k": 120,
        "opti_20k": 150,
        "opti_50k": 200
    }
    score += PLAN_SCORES.get(enterprise['plan'], 10) * 0.4
    
    # 2. Score avis (poids: 25%)
    avg_rating = enterprise.get('avg_rating', 0)
    review_count = enterprise.get('review_count', 0)
    rating_score = avg_rating * min(review_count, 100) / 100
    score += rating_score * 25
    
    # 3. Score activite (poids: 20%)
    products_count = enterprise.get('products_count', 0)
    orders_count = enterprise.get('orders_count', 0)
    activity_score = min(100, products_count * 2 + orders_count)
    score += activity_score * 0.2
    
    # 4. Score certifications (poids: 15%)
    if enterprise.get('is_certified'):
        score += 10
    if enterprise.get('is_labellise'):
        score += 5
    
    return score
    """)
    
    # ========== CHAPITRE 8: SCENARIOS ==========
    pdf.add_chapter("SCENARIOS DE MONETISATION")
    
    pdf.add_section("Parcours entreprise Standard")
    
    pdf.add_scenario_box(
        "M01", "Salon de coiffure - Abonnement Standard",
        [
            "Le salon s'inscrit sur Titelli (gratuit)",
            "Souscrit a l'abonnement Standard (200 CHF/mois)",
            "Publie ses services et tarifs",
            "Recoit des commandes via la plateforme",
            "Commission 10% prelevee sur chaque vente"
        ],
        "Visibilite locale + gestion simplifiee",
        "200/mois + 10% ventes"
    )
    
    pdf.add_scenario_box(
        "M02", "Restaurant - Upgrade vers Premium",
        [
            "Restaurant avec abonnement Standard depuis 3 mois",
            "Decide d'upgrader vers Premium (500 CHF/mois)",
            "Beneficie de 4 publicites/mois incluses",
            "Commission reduite a 8%",
            "Utilise les pubs pour promouvoir le menu du jour"
        ],
        "Augmentation visibilite + reduction commission",
        "500/mois + 8% ventes"
    )
    
    pdf.add_scenario_box(
        "M03", "Boutique - Pub Media IA",
        [
            "Boutique mode avec Premium MVP (1000 CHF/mois)",
            "Utilise les 5 Pub Media IA incluses",
            "Commande 3 templates supplementaires (89.70 CHF)",
            "Genere des visuels pour Instagram et site web"
        ],
        "Contenu marketing professionnel sans graphiste",
        "1000/mois + 89.70 ponctuels"
    )
    
    pdf.add_section("Parcours entreprise Premium")
    
    pdf.add_scenario_box(
        "M04", "Agence immobiliere - Optimisation 5K",
        [
            "Agence souscrit a Opti 5K (5000 CHF/mois)",
            "Beneficie de 15 pubs + 2 videos/mois",
            "Utilise les 10h de prestation service",
            "3000 CHF de prestations liquidees par Titelli",
            "Commission reduite a 6%"
        ],
        "Accompagnement complet + visibilite maximale",
        "5000/mois + 6% ventes"
    )
    
    pdf.add_scenario_box(
        "M05", "Groupe hotelier - Optimisation 50K",
        [
            "Groupe souscrit au plan ultime (50000 CHF/mois)",
            "40000 CHF de prestations liquidees",
            "Fiscaliste inclus (valeur 4000 CHF)",
            "Account manager VIP dedie",
            "80h de prestations ou 40 dejeuners equipe",
            "Commission minimale de 5%"
        ],
        "Service VIP complet + ROI maximise",
        "50000/mois + 5% ventes"
    )
    
    pdf.add_section("Parcours client Premium")
    
    pdf.add_scenario_box(
        "M06", "Client regulier - Upgrade Premium",
        [
            "Client avec compte gratuit (1% cashback)",
            "Depense 300 CHF/mois sur la plateforme",
            "Cashback actuel: 3 CHF/mois",
            "Souscrit a Premium (9.99 CHF/mois)",
            "Nouveau cashback: 30 CHF/mois (10%)"
        ],
        "Gain net: 30 - 9.99 - 3 = 17.01 CHF/mois",
        "9.99/mois client"
    )
    
    pdf.add_scenario_box(
        "M07", "Client VIP - Gros acheteur",
        [
            "Client Premium souhaitant maximiser ses gains",
            "Depense 500 CHF/mois sur la plateforme",
            "Upgrade vers VIP (29.99 CHF/mois)",
            "Cashback: 75 CHF/mois (15%)",
            "Acces concierge + evenements VIP"
        ],
        "Gain net: 75 - 29.99 = 45.01 CHF/mois + avantages",
        "29.99/mois client"
    )
    
    # ========== CHAPITRE 9: FLUX STRIPE ==========
    pdf.add_chapter("FLUX DE PAIEMENT STRIPE")
    
    pdf.add_section("Architecture paiement")
    
    pdf.add_text("""
Tous les paiements Titelli transitent par Stripe Checkout, garantissant:
- Securite PCI-DSS niveau 1
- Support cartes internationales
- Integration TWINT (Suisse)
- Gestion automatique des remboursements
    """)
    
    pdf.add_subsection("Flux abonnement entreprise")
    pdf.add_algorithm_box("STRIPE_SUBSCRIPTION_FLOW", """
# 1. Creation session Stripe
async def create_subscription_checkout(plan_id, user_id):
    plan = SUBSCRIPTION_PLANS[plan_id]
    
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'chf',
                'product_data': {
                    'name': f'Titelli {plan["name"]}',
                    'description': plan['description']
                },
                'unit_amount': int(plan["price"] * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=f'{FRONTEND_URL}/dashboard?success=true',
        cancel_url=f'{FRONTEND_URL}/dashboard?cancelled=true',
        metadata={
            'type': 'subscription',
            'plan_id': plan_id,
            'user_id': user_id
        }
    )
    
    return session.url

# 2. Webhook confirmation
@app.post("/api/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get('stripe-signature')
    
    event = stripe.Webhook.construct_event(payload, sig, WEBHOOK_SECRET)
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        metadata = session.get('metadata', {})
        
        if metadata.get('type') == 'subscription':
            await activate_subscription(
                metadata['user_id'],
                metadata['plan_id']
            )
    
    return {"status": "success"}
    """)
    
    pdf.add_subsection("Flux paiement Pub Media IA")
    pdf.add_algorithm_box("STRIPE_MEDIA_PUB_FLOW", """
# Creation checkout pour commande pub
async def create_media_pub_checkout(order_id, enterprise_id):
    order = await db.pub_orders.find_one({"id": order_id})
    
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'chf',
                'product_data': {
                    'name': f'Pub Media IA - {order["template_name"]}',
                },
                'unit_amount': int(order["price"] * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=f'{FRONTEND_URL}/media-pub/success?session_id={{CHECKOUT_SESSION_ID}}',
        cancel_url=f'{FRONTEND_URL}/media-pub?cancelled=true',
        metadata={
            'type': 'media_pub',
            'order_id': order_id,
            'enterprise_id': enterprise_id
        }
    )
    
    # Sauvegarder session ID
    await db.pub_orders.update_one(
        {"id": order_id},
        {"$set": {"stripe_session_id": session.id}}
    )
    
    return session.url
    """)
    
    # ========== CHAPITRE 10: PROJECTIONS ==========
    pdf.add_chapter("PROJECTIONS FINANCIERES")
    
    pdf.add_section("Hypotheses de base")
    
    pdf.add_text("""
MARCHE CIBLE:
- Region lausannoise: 420'000 habitants
- Entreprises locales: 12'500
- Penetration annee 1: 5% entreprises, 0.5% clients

PANIER MOYEN:
- Client: 85 CHF/commande, 4x/an
- Entreprise abonnement moyen: 800 CHF/mois
- Pub Media IA moyenne: 35 CHF/commande
- Video Pub IA moyenne: 200 CHF/commande
    """)
    
    pdf.add_section("Projections revenus par source")
    
    pdf.add_table(
        ["Source", "An 1", "An 2", "An 3", "An 5"],
        [
            ["Abonnements Entreprises", "450K CHF", "810K CHF", "1.3M CHF", "2.3M CHF"],
            ["Abonnements Clients", "80K CHF", "144K CHF", "230K CHF", "400K CHF"],
            ["Options a la carte", "120K CHF", "216K CHF", "345K CHF", "600K CHF"],
            ["Pub Flash (encheres)", "150K CHF", "270K CHF", "430K CHF", "750K CHF"],
            ["Pub Media IA", "100K CHF", "180K CHF", "290K CHF", "500K CHF"],
            ["Video Pub IA", "70K CHF", "126K CHF", "200K CHF", "350K CHF"],
            ["Commissions ventes", "30K CHF", "54K CHF", "87K CHF", "150K CHF"],
            ["TOTAL", "1.0M CHF", "1.8M CHF", "2.9M CHF", "5.05M CHF"],
        ],
        [50, 30, 30, 30, 40]
    )
    
    pdf.add_section("Repartition CA par canal")
    
    pdf.add_text("""
ANNEE 1:
- Abonnements: 53% (530K CHF)
- Publicites: 32% (320K CHF)
- Services IA: 17% (170K CHF)
- Commissions: 3% (30K CHF)

ANNEE 5 (projection):
- Abonnements: 57% (2.9M CHF)
- Publicites: 26% (1.3M CHF)
- Services IA: 17% (850K CHF)
- Commissions: 3% (150K CHF)
    """)
    
    pdf.add_section("Break-even analysis")
    
    pdf.add_table(
        ["Indicateur", "Seuil", "Projete An 1"],
        [
            ["Entreprises abonnees", "400", "625"],
            ["Clients premium", "2'000", "2'100"],
            ["CA mensuel min", "70K CHF", "83K CHF"],
            ["Marge brute cible", "60%", "65%"],
            ["Break-even", "Mois 8", "Mois 7"],
        ],
        [70, 55, 55]
    )
    
    # ========== CHAPITRE 11: ANNEXES ==========
    pdf.add_chapter("ANNEXES - TARIFS COMPLETS")
    
    pdf.add_section("Grille tarifaire complete entreprises")
    
    pdf.add_table(
        ["Plan", "Mensuel", "Annuel (-15%)", "Engagement"],
        [
            ["Standard", "200 CHF", "2'040 CHF", "1 mois"],
            ["Guest", "250 CHF", "2'550 CHF", "1 mois"],
            ["Premium", "500 CHF", "5'100 CHF", "1 mois"],
            ["Premium MVP", "1'000 CHF", "10'200 CHF", "3 mois"],
            ["Opti 2K", "2'000 CHF", "20'400 CHF", "6 mois"],
            ["Opti 3K", "3'000 CHF", "30'600 CHF", "6 mois"],
            ["Opti 5K", "5'000 CHF", "51'000 CHF", "12 mois"],
            ["Opti 10K", "10'000 CHF", "102'000 CHF", "12 mois"],
            ["Opti 20K", "20'000 CHF", "204'000 CHF", "12 mois"],
            ["Opti 50K", "50'000 CHF", "510'000 CHF", "12 mois"],
        ],
        [40, 40, 50, 50]
    )
    
    pdf.add_section("Grille tarifaire Pub Media IA")
    
    templates_prices = [
        ("social_promo_1", "Promo Flash Moderne", "1080x1080", "29.90"),
        ("social_promo_2", "Vente Flash Neon", "1080x1080", "29.90"),
        ("social_promo_3", "Minimaliste Chic", "1080x1080", "29.90"),
        ("social_promo_4", "Gradient Tendance", "1080x1080", "29.90"),
        ("social_story_1", "Story Elegante", "1080x1920", "24.90"),
        ("social_story_2", "Story Dynamique", "1080x1920", "24.90"),
        ("social_carousel_1", "Carousel Produit", "1080x1080", "39.90"),
        ("banner_hero_1", "Hero Banner Corporate", "1920x600", "49.90"),
        ("banner_hero_2", "Hero Creatif", "1920x600", "49.90"),
        ("banner_hero_3", "Hero Minimaliste", "1920x600", "49.90"),
        ("banner_sidebar_1", "Sidebar Vertical", "300x600", "34.90"),
        ("banner_leaderboard_1", "Leaderboard Classic", "728x90", "29.90"),
        ("menu_elegant_1", "Menu Gastronomique", "A4", "44.90"),
        ("menu_bistro_1", "Menu Bistro Ardoise", "A4", "39.90"),
        ("menu_modern_1", "Menu Moderne Epure", "A4", "39.90"),
        ("menu_italian_1", "Menu Italien", "A4", "39.90"),
        ("menu_sushi_1", "Menu Sushi Japonais", "A4", "44.90"),
        ("menu_cafe_1", "Carte Cafe & Desserts", "A5", "34.90"),
        ("flyer_event_1", "Flyer Evenement", "A5", "34.90"),
        ("flyer_promo_1", "Flyer Promotion Vente", "A5", "34.90"),
        ("flyer_opening_1", "Flyer Ouverture", "A5", "34.90"),
        ("poster_vitrine_1", "Affiche Vitrine A3", "A3", "54.90"),
        ("poster_concert_1", "Affiche Concert", "A3", "54.90"),
        ("email_header_1", "Header Email", "600x200", "19.90"),
        ("email_header_2", "Header Newsletter", "600x200", "19.90"),
        ("newsletter_promo_1", "Newsletter Promo", "600x900", "49.90"),
        ("newsletter_product_1", "Newsletter Produit", "600x900", "49.90"),
        ("youtube_thumb_1", "Miniature YouTube Gaming", "1280x720", "24.90"),
        ("youtube_thumb_2", "Miniature YouTube Business", "1280x720", "24.90"),
        ("youtube_thumb_3", "Miniature Tutoriel", "1280x720", "24.90"),
        ("business_card_modern", "Carte Visite Moderne", "85x55mm", "34.90"),
        ("business_card_minimal", "Carte Visite Minimaliste", "85x55mm", "34.90"),
        ("business_card_creative", "Carte Visite Creative", "85x55mm", "39.90"),
        ("brochure_corporate", "Brochure Corporate", "A4 Tri-fold", "69.90"),
    ]
    
    pdf.add_table(
        ["ID", "Nom", "Format", "Prix"],
        [(t[0][:15], t[1][:20], t[2], t[3] + " CHF") for t in templates_prices[:17]],
        [35, 55, 40, 30]
    )
    
    pdf.add_page()
    pdf.add_table(
        ["ID", "Nom", "Format", "Prix"],
        [(t[0][:15], t[1][:20], t[2], t[3] + " CHF") for t in templates_prices[17:]],
        [35, 55, 40, 30]
    )
    
    pdf.add_section("Grille tarifaire Video Pub IA")
    
    video_prices = [
        ("social_reel_1", "Instagram Reel - Produit", "15s", "1024x1792", "199.90"),
        ("social_reel_2", "TikTok - Tendance", "8s", "1024x1792", "149.90"),
        ("social_story", "Story Animee", "8s", "1024x1792", "129.90"),
        ("ad_hero", "Pub Hero - Premium", "15s", "1792x1024", "249.90"),
        ("ad_product", "Spot Produit 30s", "12s", "1792x1024", "299.90"),
        ("ad_teaser", "Teaser Lancement", "8s", "1280x720", "179.90"),
        ("resto_menu", "Menu Video", "15s", "1280x720", "199.90"),
        ("resto_ambiance", "Ambiance Restaurant", "12s", "1792x1024", "219.90"),
        ("corp_intro", "Presentation Entreprise", "15s", "1792x1024", "249.90"),
        ("service_showcase", "Vitrine Services", "12s", "1280x720", "199.90"),
        ("event_promo", "Promo Evenement", "15s", "1280x720", "219.90"),
        ("event_countdown", "Compte a Rebours", "8s", "1024x1024", "149.90"),
        ("sur_mesure", "Creation Sur Mesure", "15s", "Custom", "399.90"),
    ]
    
    pdf.add_table(
        ["ID", "Nom", "Duree", "Taille", "Prix"],
        [(v[0][:12], v[1][:18], v[2], v[3], v[4] + " CHF") for v in video_prices],
        [30, 50, 20, 35, 35]
    )
    
    # Page finale
    pdf.add_page()
    pdf.set_fill_color(16, 185, 129)
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_font('Helvetica', 'B', 32)
    pdf.set_text_color(255, 255, 255)
    pdf.set_y(100)
    pdf.cell(0, 15, 'CDC MONETISATION', align='C')
    pdf.ln(15)
    pdf.cell(0, 15, 'COMPLET', align='C')
    
    pdf.set_font('Helvetica', '', 16)
    pdf.ln(40)
    pdf.multi_cell(180, 10, """
10 Plans Abonnements Entreprises
3 Plans Abonnements Clients
13 Options a la carte
9 Types de Publicites
34 Templates Pub Media IA
13 Templates Video Pub IA

Tous les algorithmes documentes
Tous les scenarios detailles
Toutes les projections financieres
    """, align='C')
    
    pdf.set_font('Helvetica', 'B', 14)
    pdf.ln(30)
    pdf.cell(0, 10, f'Document genere le {datetime.now().strftime("%d/%m/%Y")}', align='C')
    
    # Save
    output_dir = "/app/backend/uploads/documents"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/CDC_MONETISATION_ULTRA_COMPLET.pdf"
    pdf.output(output_path)
    
    print(f"CDC Monetisation Ultra-Complet genere: {output_path}")
    print(f"Nombre de pages: {pdf.page_no()}")
    return output_path


if __name__ == "__main__":
    generate_monetisation_cdc()
