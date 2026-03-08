"""
WebSocket routes for Titelli (Real-time notifications and presence).
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List, Optional
import asyncio
import logging
import jwt
from datetime import datetime, timezone

from .shared import db, get_current_user, JWT_SECRET, JWT_ALGORITHM

router = APIRouter(tags=["WebSocket"])
logger = logging.getLogger(__name__)


# ============ CONNECTION MANAGER ============

class ConnectionManager:
    """
    WebSocket connection manager for real-time notifications.
    Maintains a dictionary of connections per user_id.
    """
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept a new WebSocket connection for a user."""
        await websocket.accept()
        async with self.lock:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected for user {user_id}")
    
    async def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection."""
        async with self.lock:
            if user_id in self.active_connections:
                if websocket in self.active_connections[user_id]:
                    self.active_connections[user_id].remove(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send a message to all connections of a user."""
        if user_id in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
                    dead_connections.append(connection)
            
            for conn in dead_connections:
                await self.disconnect(conn, user_id)
    
    async def broadcast_to_users(self, message: dict, user_ids: List[str]):
        """Send a message to multiple users."""
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)
    
    def get_online_users(self) -> List[str]:
        """Return the list of connected user_ids."""
        return list(self.active_connections.keys())
    
    def is_user_online(self, user_id: str) -> bool:
        """Check if a user is online."""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0


# Global connection manager instance
ws_manager = ConnectionManager()


# ============ HELPER FUNCTIONS ============

async def get_user_from_token(token: str) -> Optional[dict]:
    """Validate JWT token and return user."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get('user_id')
        if not user_id:
            return None
        user = await db.users.find_one({"id": user_id}, {"_id": 0, "password": 0})
        return user
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# ============ API ROUTES ============

@router.get("/api/ws/status")
async def get_websocket_status():
    """Return WebSocket statistics."""
    online_users = ws_manager.get_online_users()
    return {
        "online_users_count": len(online_users),
        "status": "active"
    }


@router.get("/api/ws/online-friends")
async def get_online_friends(current_user: dict = Depends(get_current_user)):
    """Return the list of online friends."""
    user_id = current_user['id']
    
    friendships = await db.friendships.find({
        "$or": [{"user_id": user_id}, {"friend_id": user_id}],
        "status": "accepted"
    }).to_list(100)
    
    online_friends = []
    for f in friendships:
        friend_id = f['friend_id'] if f['user_id'] == user_id else f['user_id']
        if ws_manager.is_user_online(friend_id):
            friend_user = await db.users.find_one(
                {"id": friend_id}, 
                {"_id": 0, "id": 1, "first_name": 1, "last_name": 1, "profile_image": 1}
            )
            if friend_user:
                online_friends.append(friend_user)
    
    return {"online_friends": online_friends, "count": len(online_friends)}


# Export manager for use in other modules
def get_ws_manager():
    return ws_manager
