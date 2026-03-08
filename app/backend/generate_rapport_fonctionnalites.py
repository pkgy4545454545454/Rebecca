#!/usr/bin/env python3
"""
Rapport PDF - Nouvelles Fonctionnalités Titelli (Aujourd'hui à partir de 12h)
"""

from fpdf import FPDF
from datetime import datetime

BASE_URL = "https://image-fix-demo.preview.emergentagent.com"

class TitelliPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
        self.add_font('DejaVu', 'B', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
        
    def header(self):
        self.set_font('DejaVu', 'B', 11)
        self.set_text_color(212, 175, 55)
        self.cell(0, 8, 'TITELLI - Nouvelles Fonctionnalités', new_x='LMARGIN', new_y='NEXT', align='C')
        self.set_draw_color(212, 175, 55)
        self.line(10, 18, 200, 18)
        self.ln(3)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', '', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} - {datetime.now().strftime("%d/%m/%Y")}', align='C')

    def titre(self, txt, emoji=""):
        self.set_font('DejaVu', 'B', 13)
        self.set_text_color(30, 30, 30)
        self.set_fill_color(245, 245, 245)
        self.cell(0, 9, f'{emoji} {txt}', new_x='LMARGIN', new_y='NEXT', fill=True)
        self.ln(2)
        
    def sous_titre(self, txt):
        self.set_font('DejaVu', 'B', 10)
        self.set_text_color(80, 80, 80)
        self.cell(0, 7, txt, new_x='LMARGIN', new_y='NEXT')
        self.ln(1)
        
    def texte(self, txt):
        self.set_font('DejaVu', '', 9)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, txt)
        self.ln(1)

    def bullet(self, txt):
        self.set_font('DejaVu', '', 9)
        self.set_text_color(50, 50, 50)
        self.cell(5)
        self.cell(0, 5, f'• {txt}', new_x='LMARGIN', new_y='NEXT')

    def table(self, headers, data, widths):
        self.set_font('DejaVu', 'B', 8)
        self.set_fill_color(212, 175, 55)
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.cell(widths[i], 7, h, border=1, align='C', fill=True)
        self.ln()
        self.set_font('DejaVu', '', 8)
        self.set_text_color(50, 50, 50)
        for row in data:
            for i, cell in enumerate(row):
                self.cell(widths[i], 6, str(cell), border=1, align='C')
            self.ln()
        self.ln(2)


def generate():
    pdf = TitelliPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # PAGE 1
    pdf.add_page()
    pdf.ln(5)
    pdf.set_font('DejaVu', 'B', 20)
    pdf.set_text_color(212, 175, 55)
    pdf.cell(0, 12, 'TITELLI', new_x='LMARGIN', new_y='NEXT', align='C')
    pdf.set_font('DejaVu', '', 12)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, 'Nouvelles Fonctionnalités', new_x='LMARGIN', new_y='NEXT', align='C')
    pdf.set_font('DejaVu', 'B', 10)
    pdf.cell(0, 8, f'Session du {datetime.now().strftime("%d/%m/%Y")} - à partir de 12h00', new_x='LMARGIN', new_y='NEXT', align='C')
    pdf.ln(10)
    
    # RÉSUMÉ
    pdf.titre('RÉSUMÉ DES AJOUTS', '📊')
    pdf.table(
        ['Fonctionnalité', 'Status'],
        [
            ['RDV chez Titelli (Social Booking)', 'Terminé'],
            ['Demandes Spécialistes', 'Terminé'],
            ['Lifestyle Passes (3 niveaux)', 'Terminé'],
            ['Titelli Pro++ (B2B)', 'Terminé'],
            ['Sports & Compétitions', 'Terminé'],
            ['Notifications Push', 'Terminé'],
            ['Système Gamification', 'Terminé'],
        ],
        [120, 70]
    )
    
    # FONCTIONNALITÉ 1
    pdf.ln(3)
    pdf.titre('1. RDV CHEZ TITELLI', '💕')
    pdf.texte('Fonctionnalité de social booking permettant de partager des activités à deux.')
    pdf.sous_titre('Caractéristiques:')
    pdf.bullet('Mode Amical (gratuit) et Romantique (payant)')
    pdf.bullet('Chat temps réel entre participants')
    pdf.bullet('8 catégories: restaurant, sport, wellness, culture, nature, party, creative, autre')
    pdf.ln(2)
    pdf.sous_titre('Tarification:')
    pdf.table(
        ['Service', 'Prix'],
        [
            ['Abonnement Romantique', '200 CHF/mois'],
            ['Acceptation invitation', '2 CHF'],
        ],
        [100, 90]
    )
    pdf.sous_titre('Fichiers créés:')
    pdf.bullet('/app/backend/routers/rdv_titelli.py (1,135 lignes)')
    pdf.bullet('/app/frontend/src/pages/RdvTitelliPage.js')
    pdf.bullet('/app/frontend/src/pages/RdvChatPage.js')
    
    # FONCTIONNALITÉ 2
    pdf.add_page()
    pdf.titre('2. DEMANDES SPÉCIALISTES', '👨‍⚕️')
    pdf.texte('Système de recherche et demandes de spécialistes avec IA.')
    pdf.sous_titre('Caractéristiques:')
    pdf.bullet('Recherche intelligente de spécialistes')
    pdf.bullet('Création de demandes urgentes/spécifiques')
    pdf.bullet('Système de réponses des prestataires')
    pdf.bullet('Acceptation de réponses par le client')
    pdf.ln(2)
    pdf.sous_titre('Fichiers créés:')
    pdf.bullet('/app/backend/routers/specialists.py (585 lignes)')
    pdf.bullet('/app/frontend/src/pages/SpecialistsPage.js')
    
    # FONCTIONNALITÉ 3
    pdf.ln(5)
    pdf.titre('3. LIFESTYLE PASSES', '🎫')
    pdf.texte('Abonnements mensuels premium avec différents niveaux.')
    pdf.ln(2)
    pdf.table(
        ['Pass', 'Prix/mois', 'Inclus'],
        [
            ['Healthy Lifestyle', '99 CHF', 'Bien-être, santé'],
            ['Better You', '149 CHF', 'Développement personnel'],
            ['Special MVP', '299 CHF', 'Accès VIP exclusif'],
        ],
        [55, 40, 95]
    )
    
    # FONCTIONNALITÉ 4
    pdf.ln(3)
    pdf.titre('4. TITELLI PRO++ (B2B)', '🏢')
    pdf.texte('Services B2B pour les entreprises.')
    pdf.sous_titre('Caractéristiques:')
    pdf.bullet('Livraisons B2B récurrentes (quotidien/hebdo/mensuel)')
    pdf.bullet('Liquidation de stock (surstock, fin saison, expiration)')
    pdf.bullet('Analytics B2B')
    pdf.bullet('Abonnement Pro++: 199 CHF/mois')
    pdf.ln(2)
    pdf.sous_titre('Fichiers créés:')
    pdf.bullet('/app/backend/routers/titelli_pro.py (720 lignes)')
    pdf.bullet('/app/frontend/src/pages/TitelliProPage.js')
    
    # FONCTIONNALITÉ 5
    pdf.add_page()
    pdf.titre('5. SPORTS & COMPÉTITIONS', '⚽')
    pdf.texte('Fonctionnalité pour organiser des matchs et compétitions sportives.')
    pdf.sous_titre('Types de matchs:')
    pdf.bullet('Cherche adversaire - Match 1v1')
    pdf.bullet('Cherche joueurs - Besoin de participants')
    pdf.bullet('Cherche équipe - Rejoindre une équipe')
    pdf.ln(2)
    pdf.sous_titre('11 Catégories sportives:')
    pdf.texte('Football, Tennis, Basketball, Volleyball, Badminton, Padel, Squash, Running, Cycling, Swimming, Fitness')
    pdf.ln(2)
    pdf.sous_titre('Fichiers créés:')
    pdf.bullet('/app/frontend/src/pages/SportsPage.js')
    
    # FONCTIONNALITÉ 6
    pdf.ln(5)
    pdf.titre('6. NOTIFICATIONS PUSH', '🔔')
    pdf.texte('Système de notifications temps réel.')
    pdf.sous_titre('Types de notifications:')
    pdf.bullet('Invitations RDV')
    pdf.bullet('Messages chat')
    pdf.bullet('Réponses spécialistes')
    pdf.bullet('Matchs sports')
    pdf.ln(2)
    pdf.sous_titre('Fichiers créés:')
    pdf.bullet('/app/backend/routers/notifications.py (316 lignes)')
    pdf.bullet('/app/frontend/src/components/NotificationsDropdown.js')
    
    # FONCTIONNALITÉ 7
    pdf.ln(5)
    pdf.titre('7. SYSTÈME GAMIFICATION', '🎮')
    pdf.texte('Points et badges pour récompenser l\'activité des utilisateurs.')
    pdf.ln(2)
    pdf.table(
        ['Action', 'Points'],
        [
            ['Créer offre RDV', '+10'],
            ['Envoyer invitation', '+5'],
            ['Accepter invitation', '+15'],
            ['Créer match sport', '+10'],
            ['Rejoindre match', '+5'],
        ],
        [100, 90]
    )
    pdf.sous_titre('Fichiers créés:')
    pdf.bullet('/app/backend/routers/gamification.py (591 lignes)')
    
    # PAGE NAVIGATION
    pdf.add_page()
    pdf.titre('MISE À JOUR NAVIGATION', '🔗')
    pdf.texte('Nouveaux liens ajoutés dans le header de navigation:')
    pdf.ln(2)
    pdf.table(
        ['Lien', 'Couleur', 'URL'],
        [
            ['Rdv', 'Rose (#EC4899)', '/rdv-titelli'],
            ['Sports', 'Vert (#10B981)', '/sports'],
        ],
        [50, 50, 90]
    )
    
    # INTÉGRATIONS STRIPE
    pdf.ln(5)
    pdf.titre('INTÉGRATIONS STRIPE AJOUTÉES', '💳')
    pdf.table(
        ['Service', 'Type', 'Prix'],
        [
            ['Abonnement Romantique', 'Récurrent', '200 CHF/mois'],
            ['Acceptation invitation', 'One-time', '2 CHF'],
            ['Abonnement Pro++', 'Récurrent', '199 CHF/mois'],
            ['Healthy Pass', 'Récurrent', '99 CHF/mois'],
            ['Better You Pass', 'Récurrent', '149 CHF/mois'],
            ['MVP Pass', 'Récurrent', '299 CHF/mois'],
        ],
        [70, 40, 80]
    )
    
    # COLLECTIONS DB
    pdf.ln(3)
    pdf.titre('NOUVELLES COLLECTIONS MONGODB', '🗄️')
    pdf.table(
        ['Collection', 'Description'],
        [
            ['shared_offers', 'Offres RDV Titelli'],
            ['offer_invitations', 'Invitations RDV'],
            ['chat_rooms', 'Salons de chat'],
            ['chat_messages', 'Messages chat'],
            ['specialist_requests', 'Demandes spécialistes'],
            ['lifestyle_subscriptions', 'Abonnements passes'],
            ['gamification_points', 'Points utilisateurs'],
            ['gamification_actions_log', 'Log actions'],
            ['sports_matches', 'Matchs sportifs'],
            ['notifications', 'Notifications push'],
        ],
        [70, 120]
    )
    
    # RÉSUMÉ FINAL
    pdf.add_page()
    pdf.titre('RÉSUMÉ TECHNIQUE', '📋')
    pdf.table(
        ['Métrique', 'Valeur'],
        [
            ['Nouvelles pages Frontend', '5'],
            ['Nouveaux routers Backend', '4'],
            ['Lignes de code ajoutées', '~3,500'],
            ['Collections MongoDB créées', '10'],
            ['Endpoints API ajoutés', '~40'],
            ['Intégrations Stripe', '6'],
        ],
        [100, 90]
    )
    
    pdf.ln(10)
    pdf.set_font('DejaVu', 'B', 11)
    pdf.set_text_color(212, 175, 55)
    pdf.cell(0, 8, 'Fin du Rapport', new_x='LMARGIN', new_y='NEXT', align='C')
    pdf.set_font('DejaVu', '', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f'URL: {BASE_URL}', new_x='LMARGIN', new_y='NEXT', align='C')
    pdf.cell(0, 6, f'Généré le {datetime.now().strftime("%d/%m/%Y à %H:%M")}', new_x='LMARGIN', new_y='NEXT', align='C')
    
    # Save
    output = '/app/backend/uploads/RAPPORT_NOUVELLES_FONCTIONNALITES.pdf'
    pdf.output(output)
    print(f"PDF: {output}")
    return output

if __name__ == "__main__":
    generate()
