"""
Gamification System for Titelli
- Points system
- Badges and achievements
- Levels and ranks
- Leaderboards
- Referral system with email notifications
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timezone, timedelta
import logging
import uuid

from .shared import db, get_current_user
from .websocket import ws_manager

# Import email service
try:
    from services.email_service import (
        send_referral_notification,
        send_welcome_bonus_notification,
        send_bonus_milestone_notification
    )
    EMAIL_SERVICE_AVAILABLE = True
except ImportError:
    EMAIL_SERVICE_AVAILABLE = False

router = APIRouter(prefix="/api/gamification", tags=["Gamification"])
logger = logging.getLogger(__name__)


# ============ POINTS CONFIGURATION ============
POINTS_CONFIG = {
    # RDV Actions
    "rdv_offer_created": 10,
    "rdv_invitation_sent": 5,
    "rdv_invitation_accepted": 15,
    "rdv_completed": 25,
    "rdv_first_offer": 50,  # Bonus first offer
    
    # Sports Actions
    "sports_match_created": 10,
    "sports_match_joined": 10,
    "sports_match_won": 30,
    "sports_team_created": 20,
    "sports_competition_won": 100,
    
    # Social Actions
    "chat_message_sent": 1,
    "profile_completed": 25,
    "first_login": 10,
    "daily_login": 5,
    "referral_success": 50,
    
    # Specialist Actions
    "specialist_request_created": 10,
    "specialist_response_accepted": 20,
    
    # Commerce Actions
    "first_purchase": 30,
    "review_written": 15,
    "enterprise_followed": 5
}

# ============ LEVELS CONFIGURATION ============
LEVELS = [
    {"level": 1, "name": "Débutant", "min_points": 0, "icon": "🌱"},
    {"level": 2, "name": "Amateur", "min_points": 100, "icon": "🌿"},
    {"level": 3, "name": "Confirmé", "min_points": 300, "icon": "🌳"},
    {"level": 4, "name": "Expert", "min_points": 600, "icon": "⭐"},
    {"level": 5, "name": "Master", "min_points": 1000, "icon": "🌟"},
    {"level": 6, "name": "Champion", "min_points": 2000, "icon": "🏆"},
    {"level": 7, "name": "Légende", "min_points": 5000, "icon": "👑"},
    {"level": 8, "name": "Titan", "min_points": 10000, "icon": "💎"},
]

# ============ BADGES CONFIGURATION ============
BADGES = {
    # RDV Badges
    "first_rdv": {
        "name": "Premier Rdv",
        "description": "Créer votre premier rendez-vous",
        "icon": "🎯",
        "category": "rdv",
        "condition": {"type": "count", "action": "rdv_offer_created", "count": 1}
    },
    "social_butterfly": {
        "name": "Papillon Social",
        "description": "Créer 10 rendez-vous",
        "icon": "🦋",
        "category": "rdv",
        "condition": {"type": "count", "action": "rdv_offer_created", "count": 10}
    },
    "matchmaker": {
        "name": "Entremetteur",
        "description": "5 invitations acceptées",
        "icon": "💘",
        "category": "rdv",
        "condition": {"type": "count", "action": "rdv_invitation_accepted", "count": 5}
    },
    "romantic_pro": {
        "name": "Pro du Romantique",
        "description": "S'abonner au mode romantique",
        "icon": "❤️",
        "category": "rdv",
        "condition": {"type": "subscription", "subscription": "romantic"}
    },
    
    # Sports Badges
    "first_match": {
        "name": "Premier Match",
        "description": "Participer à votre premier match",
        "icon": "⚽",
        "category": "sports",
        "condition": {"type": "count", "action": "sports_match_joined", "count": 1}
    },
    "team_captain": {
        "name": "Capitaine",
        "description": "Créer une équipe",
        "icon": "🎖️",
        "category": "sports",
        "condition": {"type": "count", "action": "sports_team_created", "count": 1}
    },
    "athlete": {
        "name": "Athlète",
        "description": "Participer à 20 matchs",
        "icon": "🏅",
        "category": "sports",
        "condition": {"type": "count", "action": "sports_match_joined", "count": 20}
    },
    "champion": {
        "name": "Champion",
        "description": "Gagner une compétition",
        "icon": "🏆",
        "category": "sports",
        "condition": {"type": "count", "action": "sports_competition_won", "count": 1}
    },
    
    # Social Badges
    "chatterbox": {
        "name": "Bavard",
        "description": "Envoyer 100 messages",
        "icon": "💬",
        "category": "social",
        "condition": {"type": "count", "action": "chat_message_sent", "count": 100}
    },
    "networker": {
        "name": "Networker",
        "description": "Se connecter 30 jours consécutifs",
        "icon": "🔗",
        "category": "social",
        "condition": {"type": "streak", "action": "daily_login", "days": 30}
    },
    "influencer": {
        "name": "Influenceur",
        "description": "Parrainer 5 personnes",
        "icon": "📣",
        "category": "social",
        "condition": {"type": "count", "action": "referral_success", "count": 5}
    },
    
    # Level Badges
    "level_5": {
        "name": "Master",
        "description": "Atteindre le niveau 5",
        "icon": "🌟",
        "category": "level",
        "condition": {"type": "level", "level": 5}
    },
    "level_7": {
        "name": "Légende",
        "description": "Atteindre le niveau 7",
        "icon": "👑",
        "category": "level",
        "condition": {"type": "level", "level": 7}
    },
    
    # Special Badges
    "early_adopter": {
        "name": "Early Adopter",
        "description": "Parmi les 1000 premiers utilisateurs",
        "icon": "🚀",
        "category": "special",
        "condition": {"type": "special", "special": "early_adopter"}
    },
    "pro_member": {
        "name": "Membre Pro",
        "description": "S'abonner à Titelli Pro++",
        "icon": "💎",
        "category": "special",
        "condition": {"type": "subscription", "subscription": "pro"}
    }
}


# ============ HELPER FUNCTIONS ============

def get_level_for_points(points: int) -> dict:
    """Get the level info for a given point total"""
    current_level = LEVELS[0]
    for level in LEVELS:
        if points >= level["min_points"]:
            current_level = level
        else:
            break
    return current_level


def get_next_level(current_level: int) -> Optional[dict]:
    """Get the next level info"""
    for level in LEVELS:
        if level["level"] > current_level:
            return level
    return None


async def get_user_stats(user_id: str) -> dict:
    """Get user gamification stats from database"""
    stats = await db.user_gamification.find_one({"user_id": user_id}, {"_id": 0})
    
    if not stats:
        # Initialize stats for new user
        stats = {
            "user_id": user_id,
            "total_points": 0,
            "level": 1,
            "badges": [],
            "action_counts": {},
            "login_streak": 0,
            "last_login_date": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        await db.user_gamification.insert_one(stats)
        stats.pop('_id', None)
    
    return stats


async def award_points(user_id: str, action: str, multiplier: float = 1.0) -> dict:
    """Award points for an action"""
    if action not in POINTS_CONFIG:
        return {"points_awarded": 0}
    
    points = int(POINTS_CONFIG[action] * multiplier)
    
    # Get current stats
    stats = await get_user_stats(user_id)
    
    # Update action count
    action_counts = stats.get("action_counts", {})
    action_counts[action] = action_counts.get(action, 0) + 1
    
    # Calculate new total
    new_total = stats.get("total_points", 0) + points
    
    # Check for level up
    old_level = get_level_for_points(stats.get("total_points", 0))
    new_level = get_level_for_points(new_total)
    level_up = new_level["level"] > old_level["level"]
    
    # Update database
    await db.user_gamification.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "total_points": new_total,
                "level": new_level["level"],
                "action_counts": action_counts,
                "updated_at": datetime.now(timezone.utc)
            }
        },
        upsert=True
    )
    
    # Record points history
    await db.points_history.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "action": action,
        "points": points,
        "created_at": datetime.now(timezone.utc)
    })
    
    # Check for new badges
    new_badges = await check_and_award_badges(user_id, action_counts, new_level["level"])
    
    # Send notification if level up
    if level_up:
        await ws_manager.send_personal_message({
            "type": "level_up",
            "level": new_level["level"],
            "level_name": new_level["name"],
            "level_icon": new_level["icon"]
        }, user_id)
    
    return {
        "points_awarded": points,
        "total_points": new_total,
        "level": new_level,
        "level_up": level_up,
        "new_badges": new_badges
    }


async def check_and_award_badges(user_id: str, action_counts: dict, current_level: int) -> List[dict]:
    """Check and award badges based on conditions"""
    stats = await get_user_stats(user_id)
    current_badges = set(stats.get("badges", []))
    new_badges = []
    
    for badge_id, badge_info in BADGES.items():
        if badge_id in current_badges:
            continue
        
        condition = badge_info["condition"]
        earned = False
        
        if condition["type"] == "count":
            action = condition["action"]
            required = condition["count"]
            current = action_counts.get(action, 0)
            earned = current >= required
            
        elif condition["type"] == "level":
            earned = current_level >= condition["level"]
            
        elif condition["type"] == "subscription":
            sub_type = condition["subscription"]
            if sub_type == "romantic":
                sub = await db.romantic_subscriptions.find_one({
                    "user_id": user_id,
                    "status": "active",
                    "expires_at": {"$gt": datetime.now(timezone.utc)}
                })
                earned = sub is not None
            elif sub_type == "pro":
                sub = await db.pro_subscriptions.find_one({
                    "user_id": user_id,
                    "status": "active",
                    "expires_at": {"$gt": datetime.now(timezone.utc)}
                })
                earned = sub is not None
        
        if earned:
            # Award badge
            await db.user_gamification.update_one(
                {"user_id": user_id},
                {"$addToSet": {"badges": badge_id}}
            )
            
            new_badges.append({
                "id": badge_id,
                **badge_info
            })
            
            # Send notification
            await ws_manager.send_personal_message({
                "type": "badge_earned",
                "badge_id": badge_id,
                "badge_name": badge_info["name"],
                "badge_icon": badge_info["icon"]
            }, user_id)
            
            logger.info(f"Badge awarded: {badge_id} to user {user_id}")
    
    return new_badges


async def update_login_streak(user_id: str) -> dict:
    """Update login streak and award daily points"""
    stats = await get_user_stats(user_id)
    today = datetime.now(timezone.utc).date()
    last_login = stats.get("last_login_date")
    
    if last_login:
        if isinstance(last_login, str):
            last_login = datetime.fromisoformat(last_login.replace('Z', '+00:00')).date()
        elif isinstance(last_login, datetime):
            last_login = last_login.date()
    
    streak = stats.get("login_streak", 0)
    
    if last_login:
        days_diff = (today - last_login).days
        if days_diff == 1:
            # Consecutive day
            streak += 1
        elif days_diff > 1:
            # Streak broken
            streak = 1
        # If same day, don't update streak
    else:
        streak = 1
    
    # Update database
    await db.user_gamification.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "login_streak": streak,
                "last_login_date": datetime.now(timezone.utc)
            }
        }
    )
    
    # Award daily login points
    result = await award_points(user_id, "daily_login")
    
    # Bonus for streaks
    bonus_points = 0
    if streak == 7:
        bonus_points = 25
    elif streak == 30:
        bonus_points = 100
    elif streak == 100:
        bonus_points = 500
    
    if bonus_points > 0:
        await db.user_gamification.update_one(
            {"user_id": user_id},
            {"$inc": {"total_points": bonus_points}}
        )
    
    return {
        "streak": streak,
        "points_awarded": result["points_awarded"] + bonus_points,
        "bonus_points": bonus_points
    }


# ============ API ENDPOINTS ============

@router.get("/profile", response_model=dict)
async def get_gamification_profile(current_user: dict = Depends(get_current_user)):
    """Get user's gamification profile"""
    stats = await get_user_stats(current_user["id"])
    
    level_info = get_level_for_points(stats.get("total_points", 0))
    next_level = get_next_level(level_info["level"])
    
    # Calculate progress to next level
    progress = 0
    points_to_next = 0
    if next_level:
        current_points = stats.get("total_points", 0)
        level_start = level_info["min_points"]
        level_end = next_level["min_points"]
        progress = int(((current_points - level_start) / (level_end - level_start)) * 100)
        points_to_next = level_end - current_points
    
    # Get badge details
    badge_details = []
    for badge_id in stats.get("badges", []):
        if badge_id in BADGES:
            badge_details.append({
                "id": badge_id,
                **BADGES[badge_id]
            })
    
    return {
        "user_id": current_user["id"],
        "total_points": stats.get("total_points", 0),
        "level": level_info,
        "next_level": next_level,
        "progress_percent": progress,
        "points_to_next_level": points_to_next,
        "badges": badge_details,
        "badges_count": len(badge_details),
        "login_streak": stats.get("login_streak", 0),
        "action_counts": stats.get("action_counts", {})
    }


@router.get("/badges", response_model=dict)
async def get_all_badges(current_user: dict = Depends(get_current_user)):
    """Get all available badges with earned status"""
    stats = await get_user_stats(current_user["id"])
    earned_badges = set(stats.get("badges", []))
    
    badges_list = []
    for badge_id, badge_info in BADGES.items():
        badges_list.append({
            "id": badge_id,
            "earned": badge_id in earned_badges,
            **badge_info
        })
    
    # Group by category
    by_category = {}
    for badge in badges_list:
        cat = badge["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(badge)
    
    return {
        "badges": badges_list,
        "by_category": by_category,
        "total_badges": len(BADGES),
        "earned_count": len(earned_badges)
    }


@router.get("/levels", response_model=dict)
async def get_levels_info():
    """Get all levels information"""
    return {"levels": LEVELS}


@router.get("/leaderboard", response_model=dict)
async def get_leaderboard(
    period: str = Query("all", pattern="^(all|monthly|weekly)$"),
    limit: int = Query(20, ge=1, le=100)
):
    """Get points leaderboard"""
    # For now, simple all-time leaderboard
    # In production, would filter by period
    
    pipeline = [
        {"$sort": {"total_points": -1}},
        {"$limit": limit},
        {"$project": {"_id": 0, "user_id": 1, "total_points": 1, "level": 1, "badges": 1}}
    ]
    
    leaders = await db.user_gamification.aggregate(pipeline).to_list(limit)
    
    # Enrich with user names
    for i, leader in enumerate(leaders):
        user = await db.users.find_one(
            {"id": leader["user_id"]},
            {"_id": 0, "first_name": 1, "last_name": 1, "profile_image": 1}
        )
        if user:
            leader["rank"] = i + 1
            leader["user_name"] = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or "Utilisateur"
            leader["user_image"] = user.get("profile_image")
            leader["level_info"] = get_level_for_points(leader.get("total_points", 0))
            leader["badges_count"] = len(leader.get("badges", []))
    
    return {"leaderboard": leaders, "period": period}


@router.get("/points-history", response_model=dict)
async def get_points_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get user's points history"""
    history = await db.points_history.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    # Convert datetime and add action labels
    action_labels = {
        "rdv_offer_created": "Offre RDV créée",
        "rdv_invitation_sent": "Invitation envoyée",
        "rdv_invitation_accepted": "Invitation acceptée",
        "sports_match_created": "Match créé",
        "sports_match_joined": "Match rejoint",
        "daily_login": "Connexion quotidienne",
        "chat_message_sent": "Message envoyé",
        "specialist_request_created": "Demande spécialiste"
    }
    
    for h in history:
        if isinstance(h.get("created_at"), datetime):
            h["created_at"] = h["created_at"].isoformat()
        h["action_label"] = action_labels.get(h.get("action"), h.get("action"))
    
    return {"history": history}


@router.post("/daily-login", response_model=dict)
async def record_daily_login(current_user: dict = Depends(get_current_user)):
    """Record daily login and update streak"""
    result = await update_login_streak(current_user["id"])
    return {
        "message": "Connexion enregistrée",
        **result
    }


@router.get("/points-config", response_model=dict)
async def get_points_config():
    """Get points configuration (public)"""
    return {"points_config": POINTS_CONFIG}


# ============ REFERRAL/PARRAINAGE SYSTEM ============

REFERRAL_POINTS = {
    "referrer": 50,  # Points pour le parrain
    "referee": 25,   # Points pour le filleul
    "bonus_5_referrals": 100,  # Bonus à 5 parrainages
    "bonus_10_referrals": 250, # Bonus à 10 parrainages
    "bonus_25_referrals": 500, # Bonus à 25 parrainages
}


def generate_referral_code(user_id: str) -> str:
    """Generate unique referral code from user_id"""
    import hashlib
    # Create a short hash from user_id
    hash_obj = hashlib.sha256(user_id.encode())
    return f"TIT{hash_obj.hexdigest()[:8].upper()}"


class ReferralCodeCreate(BaseModel):
    """Request to get/create referral code"""
    pass


class ReferralUse(BaseModel):
    """Use a referral code during registration"""
    referral_code: str = Field(..., min_length=6, max_length=20)


@router.get("/referral/my-code", response_model=dict)
async def get_my_referral_code(current_user: dict = Depends(get_current_user)):
    """Get or create user's referral code"""
    user_id = current_user["id"]
    
    # Check if user already has a referral record
    referral_data = await db.referral_codes.find_one({"user_id": user_id}, {"_id": 0})
    
    if not referral_data:
        # Create new referral code
        code = generate_referral_code(user_id)
        referral_data = {
            "user_id": user_id,
            "code": code,
            "referrals_count": 0,
            "total_points_earned": 0,
            "referrals": [],
            "created_at": datetime.now(timezone.utc)
        }
        await db.referral_codes.insert_one(referral_data)
        referral_data.pop('_id', None)
    
    # Get user's name for sharing
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "name": 1, "email": 1})
    referrer_name = user.get("name") or user.get("email", "").split("@")[0]
    
    # Generate share URL
    share_url = f"https://image-fix-demo.preview.emergentagent.com/auth?ref={referral_data['code']}"
    
    return {
        "code": referral_data["code"],
        "share_url": share_url,
        "referrals_count": referral_data.get("referrals_count", 0),
        "total_points_earned": referral_data.get("total_points_earned", 0),
        "referrer_name": referrer_name,
        "share_message": f"Rejoins Titelli avec mon code {referral_data['code']} et gagne {REFERRAL_POINTS['referee']} points ! {share_url}"
    }


@router.get("/referral/stats", response_model=dict)
async def get_referral_stats(current_user: dict = Depends(get_current_user)):
    """Get detailed referral statistics"""
    user_id = current_user["id"]
    
    referral_data = await db.referral_codes.find_one({"user_id": user_id}, {"_id": 0})
    
    if not referral_data:
        return {
            "code": None,
            "referrals_count": 0,
            "total_points_earned": 0,
            "referrals": [],
            "next_bonus": {"count": 5, "points": REFERRAL_POINTS["bonus_5_referrals"]}
        }
    
    # Get detailed info about referrals
    referrals = referral_data.get("referrals", [])
    detailed_referrals = []
    
    for ref in referrals[-10:]:  # Last 10 referrals
        ref_user = await db.users.find_one({"id": ref.get("user_id")}, {"_id": 0, "name": 1, "email": 1, "created_at": 1})
        if ref_user:
            detailed_referrals.append({
                "name": ref_user.get("name") or ref_user.get("email", "").split("@")[0],
                "joined_at": ref.get("joined_at"),
                "points_earned": ref.get("points_earned", REFERRAL_POINTS["referrer"])
            })
    
    # Calculate next bonus
    count = referral_data.get("referrals_count", 0)
    next_bonus = None
    if count < 5:
        next_bonus = {"count": 5, "points": REFERRAL_POINTS["bonus_5_referrals"], "remaining": 5 - count}
    elif count < 10:
        next_bonus = {"count": 10, "points": REFERRAL_POINTS["bonus_10_referrals"], "remaining": 10 - count}
    elif count < 25:
        next_bonus = {"count": 25, "points": REFERRAL_POINTS["bonus_25_referrals"], "remaining": 25 - count}
    
    return {
        "code": referral_data["code"],
        "referrals_count": referral_data.get("referrals_count", 0),
        "total_points_earned": referral_data.get("total_points_earned", 0),
        "referrals": detailed_referrals,
        "next_bonus": next_bonus,
        "bonuses_achieved": {
            "5_referrals": count >= 5,
            "10_referrals": count >= 10,
            "25_referrals": count >= 25
        }
    }


@router.get("/referral/validate", response_model=dict)
async def validate_referral_code(code: str = Query(..., min_length=6)):
    """Validate a referral code (public - for registration)"""
    referral = await db.referral_codes.find_one({"code": code.upper()}, {"_id": 0})
    
    if not referral:
        return {"valid": False, "message": "Code de parrainage invalide"}
    
    # Get referrer info
    referrer = await db.users.find_one({"id": referral["user_id"]}, {"_id": 0, "name": 1, "email": 1})
    referrer_name = referrer.get("name") or referrer.get("email", "").split("@")[0] if referrer else "Un ami"
    
    return {
        "valid": True,
        "referrer_name": referrer_name,
        "bonus_points": REFERRAL_POINTS["referee"],
        "message": f"Code valide ! Vous recevrez {REFERRAL_POINTS['referee']} points bonus à l'inscription."
    }


@router.post("/referral/apply", response_model=dict)
async def apply_referral_code(
    data: ReferralUse,
    current_user: dict = Depends(get_current_user)
):
    """Apply a referral code for a new user (called after registration)"""
    user_id = current_user["id"]
    code = data.referral_code.upper()
    
    # Check if user already used a referral code
    existing = await db.referral_uses.find_one({"referee_id": user_id})
    if existing:
        raise HTTPException(status_code=400, detail="Vous avez déjà utilisé un code de parrainage")
    
    # Find referral code
    referral = await db.referral_codes.find_one({"code": code})
    if not referral:
        raise HTTPException(status_code=404, detail="Code de parrainage invalide")
    
    # Can't refer yourself
    if referral["user_id"] == user_id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas utiliser votre propre code")
    
    referrer_id = referral["user_id"]
    now = datetime.now(timezone.utc)
    
    # Record the referral use
    await db.referral_uses.insert_one({
        "id": str(uuid.uuid4()),
        "referrer_id": referrer_id,
        "referee_id": user_id,
        "code": code,
        "created_at": now
    })
    
    # Award points to referee (new user)
    referee_result = await award_points(user_id, "referral_success", multiplier=0.5)  # 25 points
    
    # Award points to referrer
    referrer_result = await award_points(referrer_id, "referral_success")  # 50 points
    
    # Update referral stats for referrer
    new_count = referral.get("referrals_count", 0) + 1
    new_total_points = referral.get("total_points_earned", 0) + REFERRAL_POINTS["referrer"]
    
    await db.referral_codes.update_one(
        {"code": code},
        {
            "$inc": {"referrals_count": 1, "total_points_earned": REFERRAL_POINTS["referrer"]},
            "$push": {
                "referrals": {
                    "user_id": user_id,
                    "joined_at": now.isoformat(),
                    "points_earned": REFERRAL_POINTS["referrer"]
                }
            }
        }
    )
    
    # Check for bonus milestones
    bonus_points = 0
    bonus_message = None
    
    if new_count == 5:
        bonus_points = REFERRAL_POINTS["bonus_5_referrals"]
        bonus_message = "Félicitations ! Bonus 5 parrainages atteint !"
    elif new_count == 10:
        bonus_points = REFERRAL_POINTS["bonus_10_referrals"]
        bonus_message = "Incroyable ! Bonus 10 parrainages atteint !"
    elif new_count == 25:
        bonus_points = REFERRAL_POINTS["bonus_25_referrals"]
        bonus_message = "Légendaire ! Bonus 25 parrainages atteint !"
    
    if bonus_points > 0:
        # Award bonus to referrer
        stats = await get_user_stats(referrer_id)
        new_total = stats.get("total_points", 0) + bonus_points
        new_level = get_level_for_points(new_total)
        
        await db.user_gamification.update_one(
            {"user_id": referrer_id},
            {"$inc": {"total_points": bonus_points}}
        )
        
        await db.points_history.insert_one({
            "id": str(uuid.uuid4()),
            "user_id": referrer_id,
            "action": f"referral_bonus_{new_count}",
            "points": bonus_points,
            "created_at": now
        })
        
        # Notify referrer
        await ws_manager.send_personal_message({
            "type": "referral_bonus",
            "bonus_points": bonus_points,
            "message": bonus_message,
            "total_referrals": new_count
        }, referrer_id)
    
    # Get referrer name and email
    referrer = await db.users.find_one({"id": referrer_id}, {"_id": 0, "name": 1, "email": 1})
    referrer_name = referrer.get("name") or referrer.get("email", "").split("@")[0] if referrer else "Votre parrain"
    referrer_email = referrer.get("email") if referrer else None
    
    # Get current user (referee) info
    referee = await db.users.find_one({"id": user_id}, {"_id": 0, "name": 1, "email": 1})
    referee_name = referee.get("name") or referee.get("email", "").split("@")[0] if referee else "Un nouvel utilisateur"
    referee_email = referee.get("email") if referee else None
    
    # Notify referrer about new referral (WebSocket)
    await ws_manager.send_personal_message({
        "type": "new_referral",
        "message": f"Quelqu'un a utilisé votre code de parrainage ! +{REFERRAL_POINTS['referrer']} points"
    }, referrer_id)
    
    # Send email notifications (non-blocking, in background)
    if EMAIL_SERVICE_AVAILABLE:
        import asyncio
        
        # Email to referrer
        if referrer_email:
            asyncio.create_task(send_referral_notification(
                referrer_email=referrer_email,
                referrer_name=referrer_name,
                referee_name=referee_name,
                points_earned=REFERRAL_POINTS["referrer"],
                total_referrals=new_count
            ))
        
        # Email to new user (referee)
        if referee_email:
            asyncio.create_task(send_welcome_bonus_notification(
                user_email=referee_email,
                user_name=referee_name,
                referrer_name=referrer_name,
                bonus_points=REFERRAL_POINTS["referee"]
            ))
        
        # Email for bonus milestone
        if bonus_points > 0 and referrer_email:
            asyncio.create_task(send_bonus_milestone_notification(
                user_email=referrer_email,
                user_name=referrer_name,
                milestone=new_count,
                bonus_points=bonus_points,
                total_referrals=new_count
            ))
    
    return {
        "success": True,
        "points_earned": REFERRAL_POINTS["referee"],
        "referrer_name": referrer_name,
        "message": f"Code appliqué ! Vous avez gagné {REFERRAL_POINTS['referee']} points grâce à {referrer_name}.",
        "email_sent": EMAIL_SERVICE_AVAILABLE
    }


@router.get("/referral/leaderboard", response_model=dict)
async def get_referral_leaderboard(limit: int = Query(20, ge=5, le=100)):
    """Get top referrers leaderboard"""
    # Get top referrers
    top_referrers = await db.referral_codes.find(
        {"referrals_count": {"$gt": 0}},
        {"_id": 0}
    ).sort("referrals_count", -1).limit(limit).to_list(limit)
    
    leaderboard = []
    for i, ref in enumerate(top_referrers):
        user = await db.users.find_one({"id": ref["user_id"]}, {"_id": 0, "name": 1, "email": 1})
        if user:
            leaderboard.append({
                "rank": i + 1,
                "name": user.get("name") or user.get("email", "").split("@")[0],
                "referrals_count": ref.get("referrals_count", 0),
                "total_points": ref.get("total_points_earned", 0)
            })
    
    return {"leaderboard": leaderboard, "total_count": len(leaderboard)}


# ============ INTERNAL FUNCTIONS FOR OTHER ROUTERS ============

async def award_rdv_points(user_id: str, action: str):
    """Award points for RDV actions (called from rdv_titelli.py)"""
    return await award_points(user_id, action)


async def award_sports_points(user_id: str, action: str):
    """Award points for sports actions (called from titelli_pro.py)"""
    return await award_points(user_id, action)


async def process_referral_on_registration(user_id: str, referral_code: str) -> dict:
    """Process referral code during user registration (called from auth.py)"""
    if not referral_code:
        return {"applied": False}
    
    try:
        # Validate code
        referral = await db.referral_codes.find_one({"code": referral_code.upper()})
        if not referral or referral["user_id"] == user_id:
            return {"applied": False, "reason": "Invalid code"}
        
        # Apply the referral
        from pydantic import BaseModel
        class TempData(BaseModel):
            referral_code: str
        
        # Manually create the referral use record and award points
        referrer_id = referral["user_id"]
        now = datetime.now(timezone.utc)
        code = referral_code.upper()
        
        await db.referral_uses.insert_one({
            "id": str(uuid.uuid4()),
            "referrer_id": referrer_id,
            "referee_id": user_id,
            "code": code,
            "created_at": now
        })
        
        # Award points to both users
        await award_points(user_id, "referral_success", multiplier=0.5)  # 25 points for new user
        await award_points(referrer_id, "referral_success")  # 50 points for referrer
        
        # Update referral stats
        await db.referral_codes.update_one(
            {"code": code},
            {
                "$inc": {"referrals_count": 1, "total_points_earned": REFERRAL_POINTS["referrer"]},
                "$push": {
                    "referrals": {
                        "user_id": user_id,
                        "joined_at": now.isoformat(),
                        "points_earned": REFERRAL_POINTS["referrer"]
                    }
                }
            }
        )
        
        return {"applied": True, "points_earned": REFERRAL_POINTS["referee"]}
        
    except Exception as e:
        logger.error(f"Error processing referral: {e}")
        return {"applied": False, "reason": str(e)}
