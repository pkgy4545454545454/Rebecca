# Plan de Refactoring - server.py → modules

## Objectif
Diviser le fichier monolithique `server.py` (7300+ lignes) en modules spécialisés pour améliorer la maintenabilité et la lisibilité du code.

## Architecture Cible

```
/app/backend/
├── server.py              # Point d'entrée principal (configuration CORS, montage routers)
├── routers/
│   ├── __init__.py        # ✅ FAIT - Exports des routers
│   ├── shared.py          # ✅ FAIT - DB, auth helpers, config partagée
│   ├── auth.py            # ✅ FAIT - register, login, profile
│   ├── payments.py        # ✅ FAIT - Stripe checkout, webhooks
│   ├── websocket.py       # ✅ FAIT - Notifications temps réel
│   ├── client.py          # 🔄 EN COURS - Endpoints client
│   ├── client_premium.py  # ⏳ À FAIRE - Premium client features
│   ├── enterprise.py      # ⏳ À FAIRE - Endpoints entreprise
│   ├── trainings.py       # ⏳ À FAIRE - Formations
│   ├── jobs.py            # ⏳ À FAIRE - Offres d'emploi
│   ├── influencers.py     # ⏳ À FAIRE - Influenceurs
│   └── admin.py           # ⏳ À FAIRE - Administration
└── models/
    ├── __init__.py
    ├── user.py            # User, UserCreate, UserResponse
    ├── enterprise.py      # Enterprise models
    ├── order.py           # Order, OrderItem, OrderCreate
    └── ...
```

## Modules Complétés

### 1. shared.py ✅
- Configuration MongoDB
- Configuration JWT
- Configuration Stripe
- Constantes TITELLI_FEES et PREMIUM_PLANS
- Fonctions: hash_password, verify_password, create_token
- Dépendances: get_current_user, get_user_cashback_rate, get_user_plan

### 2. auth.py ✅
- POST /auth/register
- POST /auth/login
- GET /auth/me
- PUT /auth/profile
- PUT /auth/password
- POST /auth/validate-token

### 3. payments.py ✅
- POST /payments/checkout
- GET /payments/status/{session_id}
- POST /payments/webhook

### 4. websocket.py ✅
- ConnectionManager class
- GET /ws/status
- GET /ws/online-friends
- Export ws_manager pour create_notification

## Prochaines Étapes

1. **client.py** - Endpoints client:
   - Wishlist, providers, orders, cashback
   - Activity feed, lifestyle
   - Friends, messages

2. **enterprise.py** - Endpoints entreprise:
   - Profile, services/products
   - Orders, finances, invoices
   - IA campaigns, advertising

3. **trainings.py** - Formations:
   - CRUD trainings
   - Enrollments, certificates

4. **jobs.py** - Emplois:
   - CRUD jobs
   - Applications

5. **Mise à jour server.py**:
   - Supprimer le code migré
   - Inclure les nouveaux routers
   - Garder les endpoints WebSocket au niveau app

## Notes Importantes

- Les endpoints WebSocket doivent rester dans server.py car ils utilisent @app.websocket()
- ws_manager doit être importé dans server.py pour les fonctions create_notification
- Garder la compatibilité avec le frontend (mêmes URLs)
- Tester après chaque migration

## Estimation
- Total: ~7300 lignes
- Migré: ~500 lignes (7%)
- Restant: ~6800 lignes
