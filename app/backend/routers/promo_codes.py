"""
Système de Codes Promo Titelli
Gestion des codes promotionnels et crédits publicitaires
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/api/promo", tags=["promo"])

# Base de données simulée pour les codes promo (à remplacer par MongoDB)
PROMO_CODES = {
    "BIENVENUE100": {
        "id": "promo_bienvenue100",
        "code": "BIENVENUE100",
        "description": "Code de bienvenue - 100 CHF de crédit publicitaire",
        "credit_amount": 100.0,
        "type": "pub_credit",  # pub_credit, discount_percent, discount_amount
        "valid_for": ["entreprise"],  # Types d'utilisateurs éligibles
        "max_uses": None,  # Illimité
        "uses_per_user": 1,
        "active": True,
        "expires_at": None,  # Pas d'expiration
        "created_at": "2026-01-01T00:00:00Z"
    },
    "TITELLI50": {
        "id": "promo_titelli50",
        "code": "TITELLI50",
        "description": "50% de réduction sur la première pub IA",
        "discount_percent": 50,
        "type": "discount_percent",
        "valid_for": ["entreprise"],
        "max_uses": 100,
        "uses_per_user": 1,
        "active": True,
        "expires_at": "2026-12-31T23:59:59Z",
        "created_at": "2026-01-01T00:00:00Z"
    },
    "ESSAI30": {
        "id": "promo_essai30",
        "code": "ESSAI30",
        "description": "30 CHF de crédit pub pour essayer",
        "credit_amount": 30.0,
        "type": "pub_credit",
        "valid_for": ["entreprise", "client"],
        "max_uses": 500,
        "uses_per_user": 1,
        "active": True,
        "expires_at": None,
        "created_at": "2026-01-01T00:00:00Z"
    }
}


class PromoCodeValidation(BaseModel):
    code: str


class PromoCodeApply(BaseModel):
    code: str
    user_id: str
    user_type: str


class PromoCodeResponse(BaseModel):
    valid: bool
    code: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    credit_amount: Optional[float] = None
    discount_percent: Optional[float] = None
    message: str


@router.post("/validate", response_model=PromoCodeResponse)
async def validate_promo_code(data: PromoCodeValidation):
    """Valide un code promo sans l'appliquer"""
    code = data.code.upper().strip()
    
    if code not in PROMO_CODES:
        return PromoCodeResponse(
            valid=False,
            message="Code promo invalide ou expiré"
        )
    
    promo = PROMO_CODES[code]
    
    if not promo["active"]:
        return PromoCodeResponse(
            valid=False,
            message="Ce code promo n'est plus actif"
        )
    
    if promo.get("expires_at"):
        expires = datetime.fromisoformat(promo["expires_at"].replace("Z", "+00:00"))
        if datetime.now(timezone.utc) > expires:
            return PromoCodeResponse(
                valid=False,
                message="Ce code promo a expiré"
            )
    
    return PromoCodeResponse(
        valid=True,
        code=promo["code"],
        description=promo["description"],
        type=promo["type"],
        credit_amount=promo.get("credit_amount"),
        discount_percent=promo.get("discount_percent"),
        message="Code promo valide !"
    )


@router.post("/apply")
async def apply_promo_code(data: PromoCodeApply):
    """Applique un code promo au compte utilisateur"""
    from server import db  # Import dynamique pour éviter les imports circulaires
    
    code = data.code.upper().strip()
    
    if code not in PROMO_CODES:
        raise HTTPException(status_code=400, detail="Code promo invalide")
    
    promo = PROMO_CODES[code]
    
    if not promo["active"]:
        raise HTTPException(status_code=400, detail="Ce code promo n'est plus actif")
    
    # Vérifier si l'utilisateur peut utiliser ce code
    if data.user_type not in promo["valid_for"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Ce code est réservé aux comptes: {', '.join(promo['valid_for'])}"
        )
    
    # Vérifier si l'utilisateur a déjà utilisé ce code
    existing_use = db.promo_uses.find_one({
        "user_id": data.user_id,
        "promo_code": code
    })
    
    if existing_use:
        raise HTTPException(
            status_code=400, 
            detail="Vous avez déjà utilisé ce code promo"
        )
    
    # Appliquer le code promo
    if promo["type"] == "pub_credit":
        # Ajouter du crédit pub à l'utilisateur
        db.users.update_one(
            {"id": data.user_id},
            {
                "$inc": {"pub_credit": promo["credit_amount"]},
                "$set": {"pub_credit_updated_at": datetime.now(timezone.utc).isoformat()}
            }
        )
        
        # Créer une entrée dans les transactions de crédit
        db.pub_credit_transactions.insert_one({
            "id": str(uuid.uuid4()),
            "user_id": data.user_id,
            "amount": promo["credit_amount"],
            "type": "promo_credit",
            "promo_code": code,
            "description": promo["description"],
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    
    # Enregistrer l'utilisation du code
    db.promo_uses.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": data.user_id,
        "user_type": data.user_type,
        "promo_code": code,
        "promo_id": promo["id"],
        "benefit_type": promo["type"],
        "benefit_value": promo.get("credit_amount") or promo.get("discount_percent"),
        "applied_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {
        "success": True,
        "message": f"Code promo appliqué ! {promo['description']}",
        "benefit": {
            "type": promo["type"],
            "credit_amount": promo.get("credit_amount"),
            "discount_percent": promo.get("discount_percent")
        }
    }


@router.get("/my-credit/{user_id}")
async def get_user_pub_credit(user_id: str):
    """Récupère le crédit pub d'un utilisateur"""
    from server import db
    
    user = db.users.find_one({"id": user_id}, {"pub_credit": 1, "email": 1})
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Récupérer l'historique des transactions
    transactions = list(db.pub_credit_transactions.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(10))
    
    return {
        "pub_credit": user.get("pub_credit", 0),
        "transactions": transactions
    }


@router.get("/codes")
async def list_available_codes():
    """Liste les codes promo disponibles (pour info publique)"""
    public_codes = []
    
    for code, promo in PROMO_CODES.items():
        if promo["active"]:
            public_codes.append({
                "code": promo["code"],
                "description": promo["description"],
                "type": promo["type"],
                "valid_for": promo["valid_for"]
            })
    
    return {"codes": public_codes}
