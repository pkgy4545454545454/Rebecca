"""
Online Status Router - Gestion du statut en ligne des utilisateurs
"""
from fastapi import APIRouter, Depends
from datetime import datetime, timezone

# Import from main server (will be circular imports fixed later)
# For now this is a placeholder showing the structure

router = APIRouter(prefix="/user", tags=["online_status"])

# Note: Ces endpoints sont actuellement dans server.py
# Ce fichier montre la structure cible du refactoring

"""
Endpoints à migrer depuis server.py:
- POST /user/heartbeat - Update user's last seen timestamp
- POST /user/offline - Mark user as offline
- GET /client/friends/online - Get online status for all friends
"""
