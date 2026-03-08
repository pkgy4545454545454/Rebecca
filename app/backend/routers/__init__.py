"""
Routers package for Titelli API.

This package contains modular routers for different API sections:
- auth: Authentication (login, register, profile)
- payments: Stripe payments and subscriptions
- websocket: Real-time notifications and presence
- client: Client-specific endpoints
- enterprise: Enterprise profiles, services, products, reviews
- admin: Administration, stats, user management
- orders: Order management and checkout
- rdv_titelli: Social booking feature
- specialists: Specialist search and lifestyle passes
- titelli_pro: B2B services and sports
- notifications: Push notifications
- gamification: Points and badges system
- trainings: Training courses endpoints
"""

from .auth import router as auth_router
from .payments import router as payments_router
from .websocket import router as websocket_router, ws_manager, get_ws_manager
from .enterprise import router as enterprise_router
from .admin import router as admin_router
from .orders import router as orders_router
from .shared import (
    db, 
    get_current_user, 
    get_user_cashback_rate,
    get_user_plan,
    TITELLI_FEES,
    PREMIUM_PLANS,
    verify_password,
    create_token
)

__all__ = [
    'auth_router',
    'payments_router', 
    'websocket_router',
    'enterprise_router',
    'admin_router',
    'orders_router',
    'ws_manager',
    'get_ws_manager',
    'db',
    'get_current_user',
    'get_user_cashback_rate',
    'get_user_plan',
    'TITELLI_FEES',
    'PREMIUM_PLANS',
    'hash_password',
    'verify_password',
    'create_token'
]
