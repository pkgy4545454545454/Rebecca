"""
Admin Router - Gestion administrative Titelli
Routes pour les statistiques, utilisateurs, validations
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import logging
import csv
import io

from .shared import db, get_current_user

router = APIRouter(prefix="/api/admin", tags=["Administration"])
logger = logging.getLogger(__name__)


def is_admin(user: dict) -> bool:
    """Check if user is admin"""
    return user.get("user_type") == "admin" or user.get("email") == "admin@titelli.com"


# ============ STATS ROUTES ============

@router.get("/stats")
async def get_admin_stats(current_user: dict = Depends(get_current_user)):
    """Get platform statistics"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Accès admin requis")
    
    # Counts
    total_users = await db.users.count_documents({})
    total_enterprises = await db.enterprises.count_documents({})
    total_orders = await db.orders.count_documents({})
    active_enterprises = await db.enterprises.count_documents({"activation_status": "active"})
    
    # Revenue
    pipeline = [
        {"$match": {"payment_status": "paid"}},
        {"$group": {"_id": None, "total": {"$sum": "$total"}, "fees": {"$sum": "$platform_fee"}}}
    ]
    revenue_result = await db.orders.aggregate(pipeline).to_list(1)
    total_revenue = revenue_result[0]["total"] if revenue_result else 0
    total_fees = revenue_result[0]["fees"] if revenue_result else 0
    
    # Recent activity
    recent_orders = await db.orders.count_documents({
        "created_at": {"$gte": datetime.now(timezone.utc) - timedelta(days=7)}
    })
    recent_users = await db.users.count_documents({
        "created_at": {"$gte": datetime.now(timezone.utc) - timedelta(days=7)}
    })
    
    return {
        "users": {
            "total": total_users,
            "recent": recent_users
        },
        "enterprises": {
            "total": total_enterprises,
            "active": active_enterprises
        },
        "orders": {
            "total": total_orders,
            "recent": recent_orders
        },
        "revenue": {
            "total": total_revenue,
            "platform_fees": total_fees
        }
    }


# ============ USERS ROUTES ============

@router.get("/users")
async def get_all_users(
    current_user: dict = Depends(get_current_user),
    user_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    skip: int = 0
):
    """Get all users"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Accès admin requis")
    
    query = {}
    if user_type:
        query["user_type"] = user_type
    if search:
        query["$or"] = [
            {"email": {"$regex": search, "$options": "i"}},
            {"name": {"$regex": search, "$options": "i"}}
        ]
    
    users = await db.users.find(query, {"_id": 0, "password": 0}).skip(skip).limit(limit).to_list(limit)
    total = await db.users.count_documents(query)
    
    return {"users": users, "total": total}


@router.get("/users/{user_id}")
async def get_user_detail(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get user detail"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Accès admin requis")
    
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return user


@router.put("/users/{user_id}/verify")
async def verify_user(
    user_id: str,
    is_certified: bool = False,
    is_labeled: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Verify/certify a user"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Accès admin requis")
    
    update_data = {
        "is_certified": is_certified,
        "is_labeled": is_labeled,
        "verified_at": datetime.now(timezone.utc) if is_certified else None
    }
    
    await db.users.update_one({"id": user_id}, {"$set": update_data})
    
    # Also update enterprise if linked
    user = await db.users.find_one({"id": user_id})
    if user and user.get("enterprise_id"):
        await db.enterprises.update_one(
            {"id": user["enterprise_id"]},
            {"$set": {"is_certified": is_certified, "is_labeled": is_labeled}}
        )
    
    return {"message": "Utilisateur vérifié"}


@router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a user"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Accès admin requis")
    
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Don't allow deleting admins
    if user.get("user_type") == "admin":
        raise HTTPException(status_code=403, detail="Impossible de supprimer un admin")
    
    await db.users.delete_one({"id": user_id})
    
    return {"message": "Utilisateur supprimé"}


# ============ REGISTRATION REQUESTS ============

@router.get("/registration-requests")
async def get_registration_requests(
    current_user: dict = Depends(get_current_user),
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """Get enterprise registration requests"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Accès admin requis")
    
    query = {}
    if status:
        query["status"] = status
    
    requests = await db.registration_requests.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.registration_requests.count_documents(query)
    
    return {"requests": requests, "total": total}


@router.post("/registration-requests/{request_id}/approve")
async def approve_registration(request_id: str, current_user: dict = Depends(get_current_user)):
    """Approve enterprise registration"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Accès admin requis")
    
    request = await db.registration_requests.find_one({"id": request_id})
    if not request:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    
    # Update request status
    await db.registration_requests.update_one(
        {"id": request_id},
        {"$set": {
            "status": "approved",
            "approved_at": datetime.now(timezone.utc),
            "approved_by": current_user["id"]
        }}
    )
    
    # Update enterprise status
    if request.get("enterprise_id"):
        await db.enterprises.update_one(
            {"id": request["enterprise_id"]},
            {"$set": {"activation_status": "active"}}
        )
    
    return {"message": "Demande approuvée"}


@router.post("/registration-requests/{request_id}/reject")
async def reject_registration(
    request_id: str,
    reason: str = "Non conforme",
    current_user: dict = Depends(get_current_user)
):
    """Reject enterprise registration"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Accès admin requis")
    
    request = await db.registration_requests.find_one({"id": request_id})
    if not request:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    
    await db.registration_requests.update_one(
        {"id": request_id},
        {"$set": {
            "status": "rejected",
            "rejected_at": datetime.now(timezone.utc),
            "rejected_by": current_user["id"],
            "rejection_reason": reason
        }}
    )
    
    return {"message": "Demande rejetée"}


# ============ WITHDRAWALS ============

@router.get("/withdrawals")
async def get_all_withdrawals(
    current_user: dict = Depends(get_current_user),
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """Get all withdrawal requests"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Accès admin requis")
    
    query = {}
    if status:
        query["status"] = status
    
    withdrawals = await db.cashback_withdrawals.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.cashback_withdrawals.count_documents(query)
    
    return {"withdrawals": withdrawals, "total": total}


@router.put("/withdrawals/{withdrawal_id}/status")
async def update_withdrawal_status(
    withdrawal_id: str,
    status: str,
    current_user: dict = Depends(get_current_user)
):
    """Update withdrawal status"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Accès admin requis")
    
    valid_statuses = ["pending", "processing", "completed", "rejected"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Statut invalide. Valides: {valid_statuses}")
    
    withdrawal = await db.cashback_withdrawals.find_one({"id": withdrawal_id})
    if not withdrawal:
        raise HTTPException(status_code=404, detail="Retrait non trouvé")
    
    await db.cashback_withdrawals.update_one(
        {"id": withdrawal_id},
        {"$set": {
            "status": status,
            "processed_at": datetime.now(timezone.utc) if status in ["completed", "rejected"] else None,
            "processed_by": current_user["id"]
        }}
    )
    
    # If rejected, refund the amount
    if status == "rejected":
        await db.users.update_one(
            {"id": withdrawal["user_id"]},
            {"$inc": {"cashback_balance": withdrawal["amount"]}}
        )
    
    return {"message": f"Statut mis à jour: {status}"}


# ============ ACCOUNTING ============

@router.get("/accounting/summary")
async def get_accounting_summary(
    current_user: dict = Depends(get_current_user),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get accounting summary"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Accès admin requis")
    
    # Build date filter
    date_filter = {}
    if start_date:
        date_filter["$gte"] = datetime.fromisoformat(start_date)
    if end_date:
        date_filter["$lte"] = datetime.fromisoformat(end_date)
    
    match_query = {"payment_status": "paid"}
    if date_filter:
        match_query["created_at"] = date_filter
    
    # Revenue summary
    pipeline = [
        {"$match": match_query},
        {"$group": {
            "_id": None,
            "total_revenue": {"$sum": "$total"},
            "platform_fees": {"$sum": "$platform_fee"},
            "order_count": {"$sum": 1}
        }}
    ]
    
    result = await db.orders.aggregate(pipeline).to_list(1)
    summary = result[0] if result else {"total_revenue": 0, "platform_fees": 0, "order_count": 0}
    
    # Subscription revenue
    sub_pipeline = [
        {"$match": {"status": "active"}},
        {"$group": {"_id": None, "count": {"$sum": 1}, "mrr": {"$sum": "$price"}}}
    ]
    sub_result = await db.subscriptions.aggregate(sub_pipeline).to_list(1)
    subscription_data = sub_result[0] if sub_result else {"count": 0, "mrr": 0}
    
    return {
        "orders": {
            "total_revenue": summary.get("total_revenue", 0),
            "platform_fees": summary.get("platform_fees", 0),
            "count": summary.get("order_count", 0)
        },
        "subscriptions": {
            "active_count": subscription_data.get("count", 0),
            "mrr": subscription_data.get("mrr", 0)
        }
    }


@router.get("/accounting/transactions")
async def get_accounting_transactions(
    current_user: dict = Depends(get_current_user),
    type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """Get accounting transactions"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Accès admin requis")
    
    query = {}
    if type:
        query["type"] = type
    
    transactions = await db.finance_transactions.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.finance_transactions.count_documents(query)
    
    return {"transactions": transactions, "total": total}
