#!/usr/bin/env python3
"""
Script pour générer les 3 PDFs Titelli propres
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# Couleurs Titelli
TITELLI_BLUE = HexColor('#0047AB')
TITELLI_GOLD = HexColor('#D4AF37')
DARK_BG = HexColor('#0a0a0a')
LIGHT_TEXT = HexColor('#f5f5f5')
GRAY_TEXT = HexColor('#888888')

def draw_header(c, width, height, title, subtitle=""):
    """Dessine l'en-tête Titelli"""
    # Fond noir en haut
    c.setFillColor(DARK_BG)
    c.rect(0, height - 4*cm, width, 4*cm, fill=True, stroke=False)
    
    # Logo T
    c.setFillColor(TITELLI_GOLD)
    c.setFont("Helvetica-Bold", 36)
    c.drawString(2*cm, height - 2.5*cm, "T")
    
    # Titre
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(4*cm, height - 2.2*cm, title)
    
    if subtitle:
        c.setFillColor(GRAY_TEXT)
        c.setFont("Helvetica", 12)
        c.drawString(4*cm, height - 3*cm, subtitle)
    
    # Ligne dorée
    c.setStrokeColor(TITELLI_GOLD)
    c.setLineWidth(2)
    c.line(2*cm, height - 4*cm, width - 2*cm, height - 4*cm)

def draw_footer(c, width, height):
    """Dessine le pied de page"""
    c.setFillColor(DARK_BG)
    c.rect(0, 0, width, 1.5*cm, fill=True, stroke=False)
    
    c.setFillColor(TITELLI_GOLD)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2*cm, 0.6*cm, "Titelli")
    
    c.setFillColor(GRAY_TEXT)
    c.setFont("Helvetica", 8)
    c.drawString(width - 5*cm, 0.6*cm, "www.titelli.ch")

def draw_section_title(c, y, title, width):
    """Dessine un titre de section"""
    c.setFillColor(TITELLI_BLUE)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, y, title)
    
    c.setStrokeColor(TITELLI_GOLD)
    c.setLineWidth(1)
    c.line(2*cm, y - 3*mm, width - 2*cm, y - 3*mm)
    
    return y - 1*cm

def draw_question(c, y, number, question, width):
    """Dessine une question avec numéro"""
    # Numéro
    c.setFillColor(TITELLI_GOLD)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, f"{number}.")
    
    # Question
    c.setFillColor(black)
    c.setFont("Helvetica", 11)
    
    # Wrap text
    text = question
    max_width = width - 5*cm
    lines = []
    words = text.split()
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if c.stringWidth(test_line, "Helvetica", 11) < max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    for i, line in enumerate(lines):
        c.drawString(3*cm, y - i * 0.5*cm, line)
    
    return y - (len(lines) + 1) * 0.5*cm - 0.3*cm

def draw_checkbox_item(c, y, text, width, checked=False):
    """Dessine un élément avec checkbox"""
    # Checkbox
    c.setStrokeColor(TITELLI_BLUE)
    c.setLineWidth(1)
    c.rect(2*cm, y - 3*mm, 4*mm, 4*mm, fill=False, stroke=True)
    
    if checked:
        c.setFillColor(TITELLI_GOLD)
        c.rect(2*cm + 0.5*mm, y - 2.5*mm, 3*mm, 3*mm, fill=True, stroke=False)
    
    # Texte
    c.setFillColor(black)
    c.setFont("Helvetica", 10)
    c.drawString(2.8*cm, y, text)
    
    return y - 0.7*cm


# ============ PDF 1: Questions Formations ============
def create_questions_formations_pdf():
    filename = "/app/backend/uploads/Questions_Formations_Titelli.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    draw_header(c, width, height, "Questions Formations", "Formulaire d'évaluation")
    
    y = height - 5.5*cm
    
    # Section 1
    y = draw_section_title(c, y, "Informations sur le participant", width)
    
    questions_section1 = [
        "Quelle est la principale raison qui vous a poussé à suivre cette formation ?",
        "Quelles étaient vos attentes avant de commencer cette formation ?",
        "Avez-vous trouvé le contenu de la formation conforme à vos attentes ? Pourquoi ?",
        "Qu'avez-vous appris de plus important lors de cette formation ?",
        "Les méthodes pédagogiques utilisées vous ont-elles aidé à mieux comprendre le sujet ?"
    ]
    
    for i, q in enumerate(questions_section1, 1):
        y = draw_question(c, y, i, q, width)
        if y < 4*cm:
            draw_footer(c, width, height)
            c.showPage()
            draw_header(c, width, height, "Questions Formations", "Formulaire d'évaluation")
            y = height - 5.5*cm
    
    y -= 0.5*cm
    y = draw_section_title(c, y, "Évaluation de la formation", width)
    
    questions_section2 = [
        "Comment évalueriez-vous la qualité du formateur ? (clarté, compétence, disponibilité)",
        "Le rythme de la formation vous a-t-il convenu ?",
        "Les supports de formation (documents, présentations) étaient-ils adaptés ?",
        "Recommanderiez-vous cette formation à d'autres personnes ? Pourquoi ?",
        "Quelles améliorations suggéreriez-vous pour les prochaines sessions ?"
    ]
    
    for i, q in enumerate(questions_section2, 6):
        y = draw_question(c, y, i, q, width)
        if y < 4*cm:
            draw_footer(c, width, height)
            c.showPage()
            draw_header(c, width, height, "Questions Formations", "Formulaire d'évaluation")
            y = height - 5.5*cm
    
    draw_footer(c, width, height)
    c.save()
    print(f"✓ PDF créé: {filename}")
    return filename


# ============ PDF 2: Prospect Rendez-vous Client ============
def create_prospect_rdv_pdf():
    filename = "/app/backend/uploads/Prospect_RDV_Client_Titelli.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    draw_header(c, width, height, "Prospect Rendez-vous", "Guide de qualification client")
    
    y = height - 5.5*cm
    
    # Section Coordonnées
    y = draw_section_title(c, y, "Coordonnées du prospect", width)
    
    fields = ["Nom de l'entreprise:", "Nom du contact:", "Téléphone:", "Email:", "Adresse:"]
    for field in fields:
        c.setFillColor(GRAY_TEXT)
        c.setFont("Helvetica", 10)
        c.drawString(2*cm, y, field)
        c.setStrokeColor(GRAY_TEXT)
        c.setLineWidth(0.5)
        c.line(5*cm, y - 1*mm, width - 2*cm, y - 1*mm)
        y -= 0.8*cm
    
    y -= 0.5*cm
    y = draw_section_title(c, y, "Questions de qualification", width)
    
    questions = [
        "Quel est votre secteur d'activité principal ?",
        "Depuis combien de temps exercez-vous cette activité ?",
        "Quel est votre chiffre d'affaires annuel approximatif ?",
        "Combien d'employés avez-vous ?",
        "Quels sont vos principaux défis actuels ?",
        "Avez-vous déjà utilisé des services similaires à Titelli ?",
        "Qu'est-ce qui vous a attiré vers notre plateforme ?",
        "Quel budget mensuel envisagez-vous pour ce type de service ?",
        "Quand souhaitez-vous démarrer ?",
        "Qui prend les décisions dans votre entreprise ?"
    ]
    
    for i, q in enumerate(questions, 1):
        y = draw_question(c, y, i, q, width)
        if y < 4*cm:
            draw_footer(c, width, height)
            c.showPage()
            draw_header(c, width, height, "Prospect Rendez-vous", "Guide de qualification client")
            y = height - 5.5*cm
    
    y -= 0.5*cm
    y = draw_section_title(c, y, "Actions à entreprendre", width)
    
    actions = [
        "Envoyer documentation complète",
        "Planifier démonstration",
        "Établir devis personnalisé",
        "Relancer dans 1 semaine",
        "Transférer au service commercial"
    ]
    
    for action in actions:
        y = draw_checkbox_item(c, y, action, width)
        if y < 3*cm:
            break
    
    draw_footer(c, width, height)
    c.save()
    print(f"✓ PDF créé: {filename}")
    return filename


# ============ PDF 3: Prospect Téléphonique ============
def create_prospect_telephonique_pdf():
    filename = "/app/backend/uploads/Prospect_Telephonique_Titelli.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    draw_header(c, width, height, "Prospect Téléphonique", "Script et guide d'appel")
    
    y = height - 5.5*cm
    
    # Introduction
    y = draw_section_title(c, y, "Script d'introduction", width)
    
    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica-Oblique", 10)
    intro_text = [
        "« Bonjour [Nom du prospect], je suis [Votre nom] de Titelli.",
        "Je vous appelle suite à votre intérêt pour nos services.",
        "Avez-vous quelques minutes pour en discuter ? »"
    ]
    for line in intro_text:
        c.drawString(2*cm, y, line)
        y -= 0.5*cm
    
    y -= 0.5*cm
    y = draw_section_title(c, y, "Questions de découverte", width)
    
    questions = [
        "Comment avez-vous entendu parler de Titelli ?",
        "Quelle est votre activité principale ?",
        "Quels sont vos besoins actuels en termes de visibilité ?",
        "Utilisez-vous actuellement d'autres plateformes similaires ?",
        "Qu'est-ce qui vous a motivé à nous contacter ?",
        "Quel est votre objectif principal pour les 6 prochains mois ?",
        "Avez-vous un budget défini pour ce type de service ?",
        "Qui d'autre dans votre entreprise serait concerné par cette décision ?"
    ]
    
    for i, q in enumerate(questions, 1):
        y = draw_question(c, y, i, q, width)
        if y < 5*cm:
            draw_footer(c, width, height)
            c.showPage()
            draw_header(c, width, height, "Prospect Téléphonique", "Script et guide d'appel")
            y = height - 5.5*cm
    
    y -= 0.5*cm
    y = draw_section_title(c, y, "Objections courantes", width)
    
    objections = [
        ("« C'est trop cher »", "→ Expliquer le ROI et les avantages exclusifs"),
        ("« Je n'ai pas le temps »", "→ Proposer un RDV de 15 min à leur convenance"),
        ("« Je dois réfléchir »", "→ Identifier les freins et proposer des garanties")
    ]
    
    for obj, response in objections:
        c.setFillColor(TITELLI_BLUE)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2*cm, y, obj)
        y -= 0.5*cm
        c.setFillColor(HexColor('#555555'))
        c.setFont("Helvetica", 9)
        c.drawString(2.5*cm, y, response)
        y -= 0.7*cm
    
    y -= 0.3*cm
    y = draw_section_title(c, y, "Clôture", width)
    
    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica-Oblique", 10)
    closing = [
        "« Parfait ! Je vous propose de fixer un rendez-vous pour",
        "vous présenter en détail nos solutions adaptées à vos besoins.",
        "Quelle date vous conviendrait le mieux ? »"
    ]
    for line in closing:
        c.drawString(2*cm, y, line)
        y -= 0.5*cm
    
    draw_footer(c, width, height)
    c.save()
    print(f"✓ PDF créé: {filename}")
    return filename


if __name__ == "__main__":
    print("Génération des PDFs Titelli...")
    print()
    
    pdf1 = create_questions_formations_pdf()
    pdf2 = create_prospect_rdv_pdf()
    pdf3 = create_prospect_telephonique_pdf()
    
    print()
    print("✓ Tous les PDFs ont été créés avec succès!")
    print()
    print("URLs des fichiers:")
    print(f"  1. /api/uploads/Questions_Formations_Titelli.pdf")
    print(f"  2. /api/uploads/Prospect_RDV_Client_Titelli.pdf")
    print(f"  3. /api/uploads/Prospect_Telephonique_Titelli.pdf")
