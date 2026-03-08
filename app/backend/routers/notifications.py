"""
Notifications System for Titelli
- Push notifications via WebSocket
- Notification preferences
- Notification history
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import logging
import uuid

from .shared import db, get_current_user
from .websocket import ws_manager

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])
logger = logging.getLogger(__name__)


# ============ PYDANTIC MODELS ============

class NotificationPreferences(BaseModel):
    """User notification preferences"""
    rdv_invitations: bool = True
    rdv_messages: bool = True
    specialist_responses: bool = True
    sports_matches: bool = True
    promotions: bool = True
    email_notifications: bool = False
    push_notifications: bool = True


class NotificationCreate(BaseModel):
    """Create a notification (internal use)"""
    user_id: str
    type: str
    title: str
    message: str
    data: Optional[dict] = None
    action_url: Optional[str] = None


# ============ NOTIFICATION TYPES ============
NOTIFICATION_TYPES = {
    "rdv_invitation": {"icon": "💌", "color": "pink"},
    "rdv_accepted": {"icon": "✅", "color": "green"},
    "rdv_declined": {"icon": "❌", "color": "red"},
    "rdv_message": {"icon": "💬", "color": "blue"},
    "specialist_response": {"icon": "🔔", "color": "amber"},
    "sports_match": {"icon": "⚽", "color": "green"},
    "sports_joined": {"icon": "🏆", "color": "amber"},
    "payment_success": {"icon": "💳", "color": "green"},
    "subscription_expiring": {"icon": "⏰", "color": "amber"},
    "promotion": {"icon": "🎁", "color": "purple"},
    "system": {"icon": "ℹ️", "color": "gray"}
}


# ============ HELPER FUNCTIONS ============

async def create_notification(
    user_id: str,
    notification_type: str,
    title: str,
    message: str,
    data: dict = None,
    action_url: str = None
):
    """Create and send a notification"""
    notification_id = str(uuid.uuid4())
    
    type_info = NOTIFICATION_TYPES.get(notification_type, NOTIFICATION_TYPES["system"])
    
    notification = {
        "id": notification_id,
        "user_id": user_id,
        "type": notification_type,
        "title": title,
        "message": message,
        "icon": type_info["icon"],
        "color": type_info["color"],
        "data": data or {},
        "action_url": action_url,
        "is_read": False,
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.notifications.insert_one(notification)
    notification.pop('_id', None)
    
    # Send via WebSocket
    await ws_manager.send_personal_message({
        "type": "notification",
        "notification": {
            "id": notification_id,
            "type": notification_type,
            "title": title,
            "message": message,
            "icon": type_info["icon"],
            "color": type_info["color"],
            "action_url": action_url,
            "created_at": notification["created_at"].isoformat()
        }
    }, user_id)
    
    logger.info(f"Notification sent to {user_id}: {title}")
    return notification


async def send_rdv_invitation_notification(inviter_name: str, offer_title: str, invitee_id: str, invitation_id: str):
    """Send notification for new RDV invitation"""
    await create_notification(
        user_id=invitee_id,
        notification_type="rdv_invitation",
        title="Nouvelle invitation !",
        message=f"{inviter_name} vous invite à '{offer_title}'",
        data={"invitation_id": invitation_id},
        action_url="/rdv"
    )


async def send_rdv_accepted_notification(participant_name: str, offer_title: str, creator_id: str, chat_room_id: str):
    """Send notification when invitation is accepted"""
    await create_notification(
        user_id=creator_id,
        notification_type="rdv_accepted",
        title="Invitation acceptée !",
        message=f"{participant_name} a accepté votre invitation pour '{offer_title}'",
        data={"chat_room_id": chat_room_id},
        action_url=f"/rdv/chat/{chat_room_id}"
    )


async def send_chat_notification(sender_name: str, preview: str, recipient_id: str, room_id: str):
    """Send notification for new chat message"""
    await create_notification(
        user_id=recipient_id,
        notification_type="rdv_message",
        title=f"Message de {sender_name}",
        message=preview,
        data={"room_id": room_id},
        action_url=f"/rdv/chat/{room_id}"
    )


async def send_specialist_response_notification(specialist_name: str, request_title: str, client_id: str, request_id: str):
    """Send notification for specialist response"""
    await create_notification(
        user_id=client_id,
        notification_type="specialist_response",
        title="Nouvelle réponse !",
        message=f"{specialist_name} a répondu à votre demande '{request_title}'",
        data={"request_id": request_id},
        action_url="/specialists"
    )


async def send_sports_match_notification(match_title: str, sport: str, participant_ids: List[str], match_id: str):
    """Send notification for sports match update"""
    for user_id in participant_ids:
        await create_notification(
            user_id=user_id,
            notification_type="sports_match",
            title="Match mis à jour !",
            message=f"Le match '{match_title}' a été mis à jour",
            data={"match_id": match_id, "sport": sport},
            action_url="/sports"
        )


# ============ API ENDPOINTS ============

@router.get("", response_model=dict)
async def get_notifications(
    is_read: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get user's notifications"""
    query = {"user_id": current_user["id"]}
    
    if is_read is not None:
        query["is_read"] = is_read
    
    notifications = await db.notifications.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    # Convert datetime to ISO string
    for n in notifications:
        if isinstance(n.get("created_at"), datetime):
            n["created_at"] = n["created_at"].isoformat()
    
    total = await db.notifications.count_documents(query)
    unread_count = await db.notifications.count_documents({"user_id": current_user["id"], "is_read": False})
    
    return {
        "notifications": notifications,
        "total": total,
        "unread_count": unread_count
    }


@router.get("/unread-count", response_model=dict)
async def get_unread_count(current_user: dict = Depends(get_current_user)):
    """Get unread notifications count"""
    count = await db.notifications.count_documents({
        "user_id": current_user["id"],
        "is_read": False
    })
    return {"unread_count": count}


@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark a notification as read"""
    result = await db.notifications.update_one(
        {"id": notification_id, "user_id": current_user["id"]},
        {"$set": {"is_read": True, "read_at": datetime.now(timezone.utc)}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notification non trouvée")
    
    return {"message": "Notification marquée comme lue"}


@router.post("/read-all")
async def mark_all_as_read(current_user: dict = Depends(get_current_user)):
    """Mark all notifications as read"""
    result = await db.notifications.update_many(
        {"user_id": current_user["id"], "is_read": False},
        {"$set": {"is_read": True, "read_at": datetime.now(timezone.utc)}}
    )
    
    return {"message": f"{result.modified_count} notifications marquées comme lues"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a notification"""
    result = await db.notifications.delete_one({
        "id": notification_id,
        "user_id": current_user["id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notification non trouvée")
    
    return {"message": "Notification supprimée"}


@router.delete("")
async def clear_all_notifications(current_user: dict = Depends(get_current_user)):
    """Clear all notifications"""
    result = await db.notifications.delete_many({"user_id": current_user["id"]})
    return {"message": f"{result.deleted_count} notifications supprimées"}


# ============ PREFERENCES ============

@router.get("/preferences", response_model=dict)
async def get_preferences(current_user: dict = Depends(get_current_user)):
    """Get notification preferences"""
    prefs = await db.notification_preferences.find_one(
        {"user_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not prefs:
        # Default preferences
        prefs = NotificationPreferences().dict()
        prefs["user_id"] = current_user["id"]
    
    return {"preferences": prefs}


@router.put("/preferences", response_model=dict)
async def update_preferences(
    prefs: NotificationPreferences,
    current_user: dict = Depends(get_current_user)
):
    """Update notification preferences"""
    prefs_dict = prefs.dict()
    prefs_dict["user_id"] = current_user["id"]
    prefs_dict["updated_at"] = datetime.now(timezone.utc)
    
    await db.notification_preferences.update_one(
        {"user_id": current_user["id"]},
        {"$set": prefs_dict},
        upsert=True
    )
    
    return {"message": "Préférences mises à jour", "preferences": prefs_dict}


# ============ EMAIL PREFERENCES ============

class EmailPreferencesUpdate(BaseModel):
    """Email notification preferences"""
    email_enabled: bool = True
    preferences: dict = {}


@router.get("/email-preferences", response_model=dict)
async def get_email_preferences(current_user: dict = Depends(get_current_user)):
    """Get email notification preferences"""
    prefs = await db.email_preferences.find_one(
        {"user_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not prefs:
        # Default preferences
        prefs = {
            "user_id": current_user["id"],
            "email_enabled": True,
            "preferences": {
                "referral": True,
                "payments": True,
                "orders": True,
                "rdv": True,
                "sports": True,
                "promotions": True,
                "newsletter": True,
                "community": True
            }
        }
    
    return prefs


@router.put("/email-preferences", response_model=dict)
async def update_email_preferences(
    data: EmailPreferencesUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update email notification preferences"""
    prefs_dict = {
        "user_id": current_user["id"],
        "email_enabled": data.email_enabled,
        "preferences": data.preferences,
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db.email_preferences.update_one(
        {"user_id": current_user["id"]},
        {"$set": prefs_dict},
        upsert=True
    )
    
    return {"message": "Préférences email mises à jour", "preferences": prefs_dict}


# ============ SEND TEST NOTIFICATION ============

@router.post("/test")
async def send_test_notification(current_user: dict = Depends(get_current_user)):
    """Send a test notification"""
    await create_notification(
        user_id=current_user["id"],
        notification_type="system",
        title="Test notification",
        message="Ceci est une notification de test. Si vous voyez ce message, les notifications fonctionnent ! 🎉",
        action_url="/"
    )
    
    return {"message": "Notification de test envoyée"}
