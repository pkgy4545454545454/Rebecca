# 🔧 DOCUMENTATION TECHNIQUE - TITELLI MARKETPLACE

**Version:** 2.0 - Production Ready  
**Date:** 25 Janvier 2026

---

## 📌 TABLE DES MATIÈRES

1. [Stack Technologique](#1-stack-technologique)
2. [Architecture Système](#2-architecture-système)
3. [Configuration Environnement](#3-configuration-environnement)
4. [API Endpoints](#4-api-endpoints)
5. [Base de Données](#5-base-de-données)
6. [WebSocket](#6-websocket)
7. [Intégration Stripe](#7-intégration-stripe)

---

## 1. STACK TECHNOLOGIQUE

### 1.1 Frontend

| Technologie | Version | Usage |
|-------------|---------|-------|
| **React** | 18.x | Framework UI |
| **React Router DOM** | 6.x | Routing SPA |
| **Axios** | Latest | HTTP Client |
| **Lucide React** | Latest | Icônes |
| **Shadcn/UI** | Latest | Composants UI |
| **Tailwind CSS** | 3.x | Styling |
| **Sonner** | Latest | Toasts/Notifications |

### 1.2 Backend

| Technologie | Version | Usage |
|-------------|---------|-------|
| **Python** | 3.11+ | Langage |
| **FastAPI** | 0.104+ | Framework API |
| **Uvicorn** | Latest | ASGI Server |
| **Motor** | Latest | MongoDB Async Driver |
| **Pydantic** | 2.x | Validation |
| **bcrypt** | Latest | Hash passwords |
| **PyJWT** | Latest | Tokens JWT |
| **httpx** | Latest | HTTP Client async |
| **openpyxl** | Latest | Export Excel |
| **reportlab** | Latest | Export PDF |

### 1.3 Base de Données

| Technologie | Version | Usage |
|-------------|---------|-------|
| **MongoDB** | 6.x | Base de données principale |
| **Motor** | Latest | Driver async Python |

### 1.4 Services Externes

| Service | Usage |
|---------|-------|
| **Stripe** | Paiements, Abonnements, Transferts |
| **SalonPro** | Synchronisation agenda (Webhook) |

---

## 2. ARCHITECTURE SYSTÈME

### 2.1 Schéma d'Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│                     React 18 (Port 3000)                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │HomePage │  │Client   │  │Enterprise│  │Admin    │        │
│  │         │  │Dashboard│  │Dashboard │  │Dashboard│        │
│  └────┬────┘  └────┬────┘  └────┬─────┘  └────┬────┘        │
│       │            │            │              │             │
│       └────────────┴────────────┴──────────────┘             │
│                          │                                   │
│                    api.js (Axios)                            │
└──────────────────────────┼───────────────────────────────────┘
                           │ HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   KUBERNETES INGRESS                         │
│              /api/* → Backend (8001)                         │
│              /*     → Frontend (3000)                        │
└──────────────────────────┼───────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                               │
│                  FastAPI (Port 8001)                         │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│  │   Auth     │  │   CRUD     │  │  Business  │             │
│  │  Routes    │  │  Routes    │  │   Logic    │             │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘             │
│        │               │               │                     │
│        └───────────────┴───────────────┘                     │
│                        │                                     │
│               ┌────────┴────────┐                            │
│               │    MongoDB      │                            │
│               │    (Motor)      │                            │
│               └────────┬────────┘                            │
└────────────────────────┼─────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      MONGODB                                 │
│                                                              │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │ users   │ │enterprises│ │ orders  │ │bookings │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │subscript│ │ reviews │ │messages │ │notificat│           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Flux de Données

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │────▶│ Frontend │────▶│ Backend  │────▶│ MongoDB  │
│ Browser  │◀────│  React   │◀────│ FastAPI  │◀────│          │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                                        │
                                        ▼
                                 ┌──────────┐
                                 │  Stripe  │
                                 │   API    │
                                 └──────────┘
                                        │
                                        ▼
                                 ┌──────────┐
                                 │ SalonPro │
                                 │ Webhook  │
                                 └──────────┘
```

---

## 3. CONFIGURATION ENVIRONNEMENT

### 3.1 Variables Backend (.env)

```bash
# MongoDB
MONGO_URL=mongodb://localhost:27017
DB_NAME=titelli_db

# JWT
JWT_SECRET=titelli_jwt_secret_key_2024

# Stripe
STRIPE_API_KEY=sk_live_xxx

# SalonPro Integration
SALONPRO_WEBHOOK_URL=https://salonpro.example.com
SALONPRO_WEBHOOK_SECRET=titelli_salonpro_sync_secret

# CORS
CORS_ORIGINS=*
```

### 3.2 Variables Frontend (.env)

```bash
REACT_APP_BACKEND_URL=https://image-fix-demo.preview.emergentagent.com
```

### 3.3 Ports

| Service | Port | Usage |
|---------|------|-------|
| Frontend | 3000 | React Dev Server |
| Backend | 8001 | FastAPI |
| MongoDB | 27017 | Base de données |

---

## 4. API ENDPOINTS

### 4.1 Authentification

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/auth/register` | Inscription |
| POST | `/api/auth/login` | Connexion |
| GET | `/api/auth/me` | Profil utilisateur |
| PUT | `/api/auth/profile` | Mise à jour profil |

### 4.2 Entreprises

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/enterprises` | Liste entreprises |
| GET | `/api/enterprises/{id}` | Détail entreprise |
| POST | `/api/enterprises` | Créer entreprise |
| PUT | `/api/enterprises/{id}` | Modifier entreprise |
| GET | `/api/enterprise/dashboard` | Stats dashboard |
| GET | `/api/enterprise/orders` | Commandes reçues |

### 4.3 Services & Produits

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/services-products` | Liste services/produits |
| POST | `/api/services-products` | Créer service/produit |
| PUT | `/api/services-products/{id}` | Modifier |
| DELETE | `/api/services-products/{id}` | Supprimer |

### 4.4 Commandes

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/orders` | Créer commande |
| GET | `/api/orders` | Mes commandes |
| GET | `/api/orders/{id}` | Détail commande |
| PUT | `/api/orders/{id}/status` | Modifier statut |

### 4.5 Cashback

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/cashback/balance` | Solde cashback |
| GET | `/api/cashback/history` | Historique |
| POST | `/api/cashback/withdraw` | Demande retrait |
| GET | `/api/cashback/withdrawal-info` | Info éligibilité |
| POST | `/api/cashback/save-bank-info` | Sauver IBAN |

### 4.6 Abonnements

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/client/premium/checkout` | Checkout Premium client |
| POST | `/api/enterprise/subscription/checkout` | Checkout Entreprise |
| POST | `/api/subscription/cancel` | Annuler abonnement |
| GET | `/api/subscription/status` | Statut abonnement |

### 4.7 Messages

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/messages/conversations` | Liste conversations |
| GET | `/api/messages/{partner_id}` | Messages avec partenaire |
| POST | `/api/messages` | Envoyer message |

### 4.8 Notifications

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/notifications` | Liste notifications |
| PUT | `/api/notifications/{id}/read` | Marquer lue |
| PUT | `/api/notifications/read-all` | Marquer toutes lues |

### 4.9 Booking / RDV

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/booking/appointment` | Créer RDV |
| GET | `/api/booking/my-appointments` | Mes RDV |
| GET | `/api/booking/enterprise/{id}/availability` | Disponibilités |
| PUT | `/api/booking/{id}/status` | Modifier statut RDV |

### 4.10 Admin

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/admin/stats` | Statistiques plateforme |
| GET | `/api/admin/users` | Liste utilisateurs |
| GET | `/api/admin/accounting/summary` | Résumé comptable |
| GET | `/api/admin/accounting/export/excel` | Export Excel |
| GET | `/api/admin/accounting/export/pdf` | Export PDF |
| GET | `/api/admin/withdrawals` | Demandes retrait |
| PUT | `/api/admin/withdrawals/{id}` | Modifier retrait |

### 4.11 Webhooks

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/webhook/stripe` | Webhook Stripe |
| POST | `/api/webhook/salonpro` | Webhook SalonPro |

---

## 5. BASE DE DONNÉES

### 5.1 Collections MongoDB

| Collection | Description | Taille estimée |
|------------|-------------|----------------|
| `users` | Utilisateurs | ~41 docs |
| `enterprises` | Entreprises | ~12 docs |
| `services_products` | Catalogue | ~100+ docs |
| `orders` | Commandes | ~20 docs |
| `reviews` | Avis | ~17 docs |
| `subscriptions` | Abonnements | ~10 docs |
| `messages` | Messages | ~50+ docs |
| `notifications` | Notifications | ~200+ docs |
| `cashback_withdrawals` | Retraits | ~3 docs |
| `bookings` | RDV | ~10+ docs |
| `agenda` | Événements agenda | ~10+ docs |
| `enterprise_contacts` | Contacts entreprise | ~5 docs |
| `friends` | Relations amis | ~20+ docs |
| `activity_feed` | Posts activité | ~30+ docs |

### 5.2 Index Recommandés

```javascript
// users
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "id": 1 }, { unique: true })

// enterprises
db.enterprises.createIndex({ "user_id": 1 }, { unique: true })
db.enterprises.createIndex({ "city": 1 })
db.enterprises.createIndex({ "category": 1 })

// orders
db.orders.createIndex({ "client_id": 1 })
db.orders.createIndex({ "enterprise_id": 1 })
db.orders.createIndex({ "created_at": -1 })

// notifications
db.notifications.createIndex({ "user_id": 1, "is_read": 1 })
db.notifications.createIndex({ "created_at": -1 })

// bookings
db.bookings.createIndex({ "enterprise_id": 1, "start_datetime": 1 })
db.bookings.createIndex({ "client_id": 1 })
```

---

## 6. WEBSOCKET

### 6.1 Endpoints WebSocket

| Endpoint | Description |
|----------|-------------|
| `/ws/notifications?token=xxx` | Notifications temps réel |
| `/ws/presence?token=xxx` | Statut en ligne amis |

### 6.2 Messages WebSocket

**Client → Serveur:**
```json
{
  "type": "mark_read",
  "notification_id": "uuid"
}
```

**Serveur → Client:**
```json
{
  "type": "notification",
  "data": {
    "id": "uuid",
    "title": "Nouvelle commande",
    "message": "...",
    "notification_type": "new_order"
  }
}
```

### 6.3 Heartbeat

```json
// Client envoie ping
{ "type": "ping" }

// Serveur répond pong
{ "type": "pong" }
```

---

## 7. INTÉGRATION STRIPE

### 7.1 Flux Checkout

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Frontend │────▶│ Backend  │────▶│  Stripe  │
│  Click   │     │ Create   │     │ Checkout │
│ "Payer"  │     │ Session  │     │ Session  │
└──────────┘     └──────────┘     └──────────┘
                                       │
                                       ▼
                              ┌──────────────┐
                              │ Stripe Page  │
                              │  (Paiement)  │
                              └──────────────┘
                                       │
                                       ▼
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Frontend │◀────│ Backend  │◀────│  Stripe  │
│ Success  │     │ Webhook  │     │ Webhook  │
│  Page    │     │ Handler  │     │  Event   │
└──────────┘     └──────────┘     └──────────┘
```

### 7.2 Events Webhook Stripe

| Event | Action |
|-------|--------|
| `checkout.session.completed` | Valider commande/abonnement |
| `customer.subscription.created` | Activer abonnement |
| `customer.subscription.deleted` | Désactiver abonnement |
| `transfer.paid` | Marquer retrait complété |
| `transfer.failed` | Marquer retrait échoué |

### 7.3 Prix Stripe

**Client Premium:**
- Premium: 9.99 CHF/mois
- VIP: 29.99 CHF/mois

**Entreprise:**
- Standard: 200 CHF/mois
- Guest: 250 CHF/mois
- Premium: 500 CHF/mois
- Optimisation: 2000-15000 CHF/mois

---

## 📊 MÉTRIQUES CODE

| Fichier | Lignes | Description |
|---------|--------|-------------|
| `server.py` | 9,353 | API Backend principale |
| `ClientDashboard.js` | 4,536 | Dashboard client |
| `EnterpriseDashboard.js` | 4,231 | Dashboard entreprise |
| `AdminDashboard.js` | 1,117 | Dashboard admin |
| `api.js` | ~600 | Service API frontend |
| **TOTAL** | ~19,000+ | Lignes de code |

---

**Document généré le 25 Janvier 2026**  
**Projet Titelli Marketplace - Documentation Technique**
