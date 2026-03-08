"""
Cashback Router - Gestion du cashback utilisateur
Routes pour le solde, historique, et retraits
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import uuid
import logging
import os

from .shared import db, get_current_user

router = APIRouter(prefix="/api/cashback", tags=["Cashback"])
logger = logging.getLogger(__name__)

# Configuration
MINIMUM_WITHDRAWAL_CHF = 50.0
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')
STRIPE_CONNECT_ACCOUNT_ID = "acct_1S0gbwGsrEOIn6nv"


# ============ HELPER FUNCTIONS ============

async def create_notification(user_id: str, notification_type: str, title: str, message: str, link: str = None):
    """Helper to create user notifications"""
    notification = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "type": notification_type,
        "title": title,
        "message": message,
        "link": link,
        "is_read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.notifications.insert_one(notification)


# ============ MODELS ============

class WithdrawalRequest(BaseModel):
    amount: Optional[float] = None  # If None, withdraw full balance


# ============ ROUTES ============

@router.get("/balance")
async def get_cashback_balance(current_user: dict = Depends(get_current_user)):
    """Get user's current cashback balance"""
    user = await db.users.find_one({"id": current_user['id']}, {"_id": 0})
    return {"balance": user.get('cashback_balance', 0.0) if user else 0.0}


@router.post("/add")
async def add_cashback(user_id: str, amount: float, current_user: dict = Depends(get_current_user)):
    """Add cashback to a user (admin only)"""
    if current_user.get('email') != 'admin@titelli.com' and current_user.get('user_type') != 'admin':
        raise HTTPException(status_code=403, detail="Non autorisé")
    
    await db.users.update_one(
        {"id": user_id},
        {"$inc": {"cashback_balance": amount}}
    )
    
    transaction = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "amount": amount,
        "type": "credit",
        "description": "Cashback ajouté",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.cashback_transactions.insert_one(transaction)
    
    return {"message": f"Cashback de {amount} CHF ajouté"}


@router.get("/history")
async def get_cashback_history(current_user: dict = Depends(get_current_user)):
    """Get cashback transaction history with statistics"""
    transactions = await db.cashback_transactions.find(
        {"user_id": current_user['id']}, {"_id": 0}
    ).sort("created_at", -1).limit(100).to_list(100)
    
    user = await db.users.find_one({"id": current_user['id']}, {"_id": 0})
    
    total_earned = sum(t['amount'] for t in transactions if t['amount'] > 0)
    total_used = abs(sum(t['amount'] for t in transactions if t['amount'] < 0))
    
    return {
        "balance": user.get('cashback_balance', 0.0) if user else 0.0,
        "transactions": transactions,
        "statistics": {
            "total_earned": round(total_earned, 2),
            "total_used": round(total_used, 2),
            "cashback_rate": "10%",
            "transaction_count": len(transactions)
        }
    }


@router.post("/use")
async def use_cashback(
    amount: float, 
    order_id: Optional[str] = None, 
    current_user: dict = Depends(get_current_user)
):
    """Use cashback for a purchase"""
    user = await db.users.find_one({"id": current_user['id']})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    current_balance = user.get('cashback_balance', 0.0)
    if amount > current_balance:
        raise HTTPException(status_code=400, detail=f"Solde insuffisant ({current_balance} CHF disponible)")
    
    await db.users.update_one(
        {"id": current_user['id']},
        {"$inc": {"cashback_balance": -amount}}
    )
    
    transaction = {
        "id": str(uuid.uuid4()),
        "user_id": current_user['id'],
        "amount": -amount,
        "type": "debit",
        "description": f"Utilisé pour commande {order_id}" if order_id else "Cashback utilisé",
        "order_id": order_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.cashback_transactions.insert_one(transaction)
    
    return {"message": f"Cashback de {amount} CHF utilisé", "new_balance": current_balance - amount}


@router.post("/withdraw")
async def withdraw_cashback(
    request: WithdrawalRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Withdraw cashback to client's bank account.
    Minimum withdrawal: 50 CHF
    Requires: IBAN and bank_account_holder in client profile
    """
    import stripe
    stripe.api_key = STRIPE_API_KEY
    
    user = await db.users.find_one({"id": current_user['id']})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    iban = user.get('iban')
    account_holder = user.get('bank_account_holder')
    
    if not iban or not account_holder:
        raise HTTPException(
            status_code=400, 
            detail="Veuillez d'abord ajouter vos coordonnées bancaires (IBAN et nom du titulaire) dans votre profil"
        )
    
    iban_clean = iban.replace(' ', '').upper()
    if len(iban_clean) < 15 or len(iban_clean) > 34:
        raise HTTPException(status_code=400, detail="Format IBAN invalide")
    
    current_balance = user.get('cashback_balance', 0.0)
    withdrawal_amount = request.amount if request.amount else current_balance
    
    if withdrawal_amount < MINIMUM_WITHDRAWAL_CHF:
        raise HTTPException(
            status_code=400, 
            detail=f"Le montant minimum de retrait est de {MINIMUM_WITHDRAWAL_CHF} CHF. Votre solde: {current_balance:.2f} CHF"
        )
    
    if withdrawal_amount > current_balance:
        raise HTTPException(
            status_code=400, 
            detail=f"Solde insuffisant. Disponible: {current_balance:.2f} CHF"
        )
    
    withdrawal_id = str(uuid.uuid4())
    withdrawal_record = {
        "id": withdrawal_id,
        "user_id": current_user['id'],
        "user_email": user.get('email'),
        "amount": withdrawal_amount,
        "currency": "chf",
        "iban": iban_clean,
        "iban_masked": f"****{iban_clean[-4:]}",
        "account_holder": account_holder,
        "bic_swift": user.get('bic_swift'),
        "status": "pending",
        "stripe_transfer_id": None,
        "stripe_payout_id": None,
        "processing_note": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None
    }
    await db.cashback_withdrawals.insert_one(withdrawal_record)
    
    await db.users.update_one(
        {"id": current_user['id']},
        {"$inc": {"cashback_balance": -withdrawal_amount}}
    )
    
    transaction = {
        "id": str(uuid.uuid4()),
        "user_id": current_user['id'],
        "amount": -withdrawal_amount,
        "type": "withdrawal",
        "description": f"Retrait vers compte bancaire ****{iban_clean[-4:]}",
        "withdrawal_id": withdrawal_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.cashback_transactions.insert_one(transaction)
    
    stripe_success = False
    stripe_error_msg = None
    
    try:
        amount_centimes = int(withdrawal_amount * 100)
        
        transfer = stripe.Transfer.create(
            amount=amount_centimes,
            currency="chf",
            destination=STRIPE_CONNECT_ACCOUNT_ID,
            transfer_group=f"cashback_withdrawal_{withdrawal_id}",
            metadata={
                "withdrawal_id": withdrawal_id,
                "user_id": current_user['id'],
                "user_email": user.get('email', ''),
                "iban_last4": iban_clean[-4:],
                "type": "cashback_withdrawal"
            }
        )
        
        await db.cashback_withdrawals.update_one(
            {"id": withdrawal_id},
            {"$set": {
                "stripe_transfer_id": transfer.id,
                "status": "processing",
                "processing_note": "Transfert Stripe effectué, payout en cours"
            }}
        )
        stripe_success = True
        
    except stripe.error.StripeError as e:
        stripe_error_msg = str(e)
        logger.warning(f"Stripe transfer failed for withdrawal {withdrawal_id}: {e}")
        
        await db.cashback_withdrawals.update_one(
            {"id": withdrawal_id},
            {"$set": {
                "status": "manual_processing",
                "processing_note": f"Traitement manuel requis. Erreur Stripe: {stripe_error_msg[:200]}"
            }}
        )
    
    status_message = "en cours de traitement automatique" if stripe_success else "enregistré et sera traité sous 1-3 jours ouvrables"
    
    await create_notification(
        user_id=current_user['id'],
        notification_type="cashback_withdrawal",
        title="Retrait enregistré",
        message=f"Votre retrait de {withdrawal_amount:.2f} CHF est {status_message}.",
        link="/dashboard/client?tab=cashback"
    )
    
    return {
        "success": True,
        "message": f"Retrait de {withdrawal_amount:.2f} CHF enregistré avec succès",
        "withdrawal_id": withdrawal_id,
        "new_balance": current_balance - withdrawal_amount,
        "status": "processing" if stripe_success else "manual_processing",
        "estimated_arrival": "1-3 jours ouvrables" if stripe_success else "3-5 jours ouvrables",
        "note": None if stripe_success else "Votre demande sera traitée manuellement par notre équipe"
    }


@router.get("/withdrawals")
async def get_withdrawal_history(current_user: dict = Depends(get_current_user)):
    """Get user's withdrawal history"""
    withdrawals = await db.cashback_withdrawals.find(
        {"user_id": current_user['id']},
        {"_id": 0}
    ).sort("created_at", -1).limit(50).to_list(50)
    
    return {"withdrawals": withdrawals}


@router.get("/withdrawal-info")
async def get_withdrawal_info(current_user: dict = Depends(get_current_user)):
    """Get withdrawal eligibility info"""
    user = await db.users.find_one({"id": current_user['id']})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    balance = user.get('cashback_balance', 0.0)
    has_bank_info = bool(user.get('iban') and user.get('bank_account_holder'))
    can_withdraw = balance >= MINIMUM_WITHDRAWAL_CHF and has_bank_info
    
    return {
        "balance": balance,
        "minimum_withdrawal": MINIMUM_WITHDRAWAL_CHF,
        "can_withdraw": can_withdraw,
        "has_bank_info": has_bank_info,
        "iban_masked": f"****{user.get('iban', '')[-4:]}" if user.get('iban') else None,
        "account_holder": user.get('bank_account_holder'),
        "reason_cannot_withdraw": None if can_withdraw else (
            "Ajoutez vos coordonnées bancaires" if not has_bank_info 
            else f"Solde minimum requis: {MINIMUM_WITHDRAWAL_CHF} CHF"
        )
    }
