"""
Système de Factures PDF et Export Comptable
Génération de factures professionnelles et exports financiers
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import io
import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

router = APIRouter(prefix="/api/invoices", tags=["invoices"])

# Couleurs Titelli
TITELLI_BLUE = colors.Color(0/255, 71/255, 171/255)


def generate_invoice_pdf(order_data: dict, user_data: dict, enterprise_data: dict) -> io.BytesIO:
    """Génère une facture PDF professionnelle"""
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    
    # Styles personnalisés
    styles.add(ParagraphStyle(
        name='InvoiceTitle',
        fontSize=24,
        textColor=TITELLI_BLUE,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=20
    ))
    
    styles.add(ParagraphStyle(
        name='CompanyName',
        fontSize=14,
        fontName='Helvetica-Bold',
        spaceAfter=5
    ))
    
    styles.add(ParagraphStyle(
        name='SmallText',
        fontSize=9,
        textColor=colors.gray,
        fontName='Helvetica'
    ))
    
    story = []
    
    # En-tête TITELLI
    story.append(Paragraph("TITELLI", styles['InvoiceTitle']))
    story.append(Paragraph("Facture", styles['Heading2']))
    story.append(Spacer(1, 1*cm))
    
    # Informations facture
    invoice_info = [
        ['Numéro de facture:', f"FAC-{order_data.get('id', 'N/A')[:8].upper()}"],
        ['Date:', datetime.now().strftime('%d/%m/%Y')],
        ['Référence commande:', order_data.get('id', 'N/A')[:8].upper()],
    ]
    
    info_table = Table(invoice_info, colWidths=[5*cm, 8*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 1*cm))
    
    # Adresses
    address_data = [
        [
            Paragraph("<b>Vendeur</b><br/>" + 
                     f"{enterprise_data.get('name', 'Entreprise')}<br/>" +
                     f"{enterprise_data.get('address', 'Adresse')}<br/>" +
                     f"{enterprise_data.get('city', 'Ville')}", styles['Normal']),
            Paragraph("<b>Client</b><br/>" +
                     f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}<br/>" +
                     f"{user_data.get('email', '')}<br/>" +
                     f"{user_data.get('address', '')}", styles['Normal'])
        ]
    ]
    
    address_table = Table(address_data, colWidths=[8*cm, 8*cm])
    address_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
    ]))
    story.append(address_table)
    story.append(Spacer(1, 1*cm))
    
    # Détails commande
    items = order_data.get('items', [])
    
    table_data = [['Description', 'Qté', 'Prix unitaire', 'Total']]
    
    subtotal = 0
    for item in items:
        qty = item.get('quantity', 1)
        price = item.get('price', 0)
        total = qty * price
        subtotal += total
        
        table_data.append([
            item.get('name', 'Article'),
            str(qty),
            f"{price:.2f} CHF",
            f"{total:.2f} CHF"
        ])
    
    # Commission Titelli
    commission_rate = order_data.get('commission_rate', 0.10)
    commission = subtotal * commission_rate
    
    # Totaux
    table_data.append(['', '', 'Sous-total:', f"{subtotal:.2f} CHF"])
    table_data.append(['', '', 'TVA (7.7%):', f"{subtotal * 0.077:.2f} CHF"])
    table_data.append(['', '', 'TOTAL:', f"{subtotal * 1.077:.2f} CHF"])
    
    items_table = Table(table_data, colWidths=[8*cm, 2*cm, 3*cm, 3*cm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TITELLI_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, len(items)), 0.5, colors.gray),
        ('FONTNAME', (2, -3), (2, -1), 'Helvetica-Bold'),
        ('FONTNAME', (3, -1), (3, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 11),
        ('LINEABOVE', (2, -3), (-1, -3), 1, colors.gray),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 1.5*cm))
    
    # Informations de paiement
    story.append(Paragraph("<b>Informations de paiement</b>", styles['Normal']))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(f"Statut: {order_data.get('status', 'payé').upper()}", styles['Normal']))
    story.append(Paragraph(f"Mode de paiement: Carte bancaire via Stripe", styles['Normal']))
    story.append(Paragraph(f"Date de paiement: {order_data.get('paid_at', datetime.now().strftime('%d/%m/%Y'))}", styles['Normal']))
    
    story.append(Spacer(1, 1.5*cm))
    
    # Footer
    story.append(Paragraph(
        "Merci pour votre confiance !",
        ParagraphStyle(name='Thanks', fontSize=12, alignment=TA_CENTER, textColor=TITELLI_BLUE)
    ))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Titelli SA • Lausanne, Suisse • www.titelli.com • support@titelli.com",
        styles['SmallText']
    ))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


@router.get("/order/{order_id}/pdf")
async def download_order_invoice(order_id: str):
    """Télécharge la facture PDF d'une commande"""
    from server import db
    
    # Récupérer la commande
    order = db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    # Récupérer l'utilisateur
    user = db.users.find_one({"id": order.get("user_id")}) or {}
    
    # Récupérer l'entreprise
    enterprise = db.enterprises.find_one({"id": order.get("enterprise_id")}) or db.users.find_one({"id": order.get("enterprise_id")}) or {}
    
    # Générer le PDF
    pdf_buffer = generate_invoice_pdf(order, user, enterprise)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=facture_{order_id[:8]}.pdf"
        }
    )


@router.get("/export/csv")
async def export_accounting_csv(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user_id: Optional[str] = None
):
    """Exporte les données comptables en CSV"""
    from server import db
    
    # Construire le filtre
    query = {}
    
    if start_date:
        query["created_at"] = {"$gte": start_date}
    if end_date:
        if "created_at" in query:
            query["created_at"]["$lte"] = end_date
        else:
            query["created_at"] = {"$lte": end_date}
    
    if user_id:
        query["$or"] = [
            {"user_id": user_id},
            {"enterprise_id": user_id}
        ]
    
    # Récupérer les commandes
    orders = list(db.orders.find(query, {"_id": 0}))
    
    # Créer le CSV
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    
    # En-tête
    writer.writerow([
        'Date',
        'N° Commande',
        'Client',
        'Entreprise',
        'Montant HT',
        'TVA',
        'Montant TTC',
        'Commission',
        'Net Entreprise',
        'Statut',
        'Mode Paiement'
    ])
    
    # Données
    for order in orders:
        total = order.get('total', 0)
        tva = total * 0.077
        ttc = total + tva
        commission = total * order.get('commission_rate', 0.10)
        net = total - commission
        
        writer.writerow([
            order.get('created_at', '')[:10] if order.get('created_at') else '',
            order.get('id', '')[:8].upper(),
            order.get('user_id', '')[:8],
            order.get('enterprise_id', '')[:8],
            f"{total:.2f}",
            f"{tva:.2f}",
            f"{ttc:.2f}",
            f"{commission:.2f}",
            f"{net:.2f}",
            order.get('status', 'inconnu'),
            'Stripe'
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=export_comptable_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )


@router.get("/stats/{user_id}")
async def get_financial_stats(user_id: str, period: str = "month"):
    """Récupère les statistiques financières d'un utilisateur"""
    from server import db
    from datetime import timedelta
    
    now = datetime.now(timezone.utc)
    
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    elif period == "year":
        start_date = now - timedelta(days=365)
    else:
        start_date = now - timedelta(days=30)
    
    start_str = start_date.isoformat()
    
    # Récupérer les commandes
    orders = list(db.orders.find({
        "$or": [
            {"user_id": user_id},
            {"enterprise_id": user_id}
        ],
        "created_at": {"$gte": start_str}
    }, {"_id": 0}))
    
    # Calculer les stats
    total_revenue = sum(o.get('total', 0) for o in orders if o.get('enterprise_id') == user_id)
    total_spent = sum(o.get('total', 0) for o in orders if o.get('user_id') == user_id)
    total_commission = sum(o.get('total', 0) * o.get('commission_rate', 0.10) for o in orders if o.get('enterprise_id') == user_id)
    total_orders = len(orders)
    
    # Calculer les revenus par jour
    daily_revenue = {}
    for order in orders:
        if order.get('enterprise_id') == user_id:
            date = order.get('created_at', '')[:10]
            if date:
                daily_revenue[date] = daily_revenue.get(date, 0) + order.get('total', 0)
    
    return {
        "period": period,
        "total_revenue": round(total_revenue, 2),
        "total_spent": round(total_spent, 2),
        "total_commission": round(total_commission, 2),
        "net_revenue": round(total_revenue - total_commission, 2),
        "total_orders": total_orders,
        "average_order": round(total_revenue / total_orders, 2) if total_orders > 0 else 0,
        "daily_revenue": daily_revenue
    }
