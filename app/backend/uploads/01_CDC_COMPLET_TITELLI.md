# 📋 CAHIER DES CHARGES COMPLET - TITELLI MARKETPLACE

**Version:** 2.0 - Production Ready  
**Date:** 25 Janvier 2026  
**Statut:** ✅ COMPLÉTÉ + SUPPLÉMENTS

---

## 📌 TABLE DES MATIÈRES

1. [Présentation du Projet](#1-présentation-du-projet)
2. [Fonctionnalités Demandées (CDC Original)](#2-fonctionnalités-demandées-cdc-original)
3. [🔴 SUPPLÉMENTS IMPLÉMENTÉS](#3-suppléments-implémentés)
4. [Architecture Technique](#4-architecture-technique)
5. [Modèles de Données](#5-modèles-de-données)
6. [Sécurité et Authentification](#6-sécurité-et-authentification)
7. [Intégrations Tierces](#7-intégrations-tierces)

---

## 1. PRÉSENTATION DU PROJET

### 1.1 Vision
Titelli est une **marketplace premium** connectant les entreprises, clients et influenceurs de la région lausannoise. La plateforme offre une expérience utilisateur haut de gamme avec système de fidélité, cashback et réseau social intégré.

### 1.2 Objectifs Business
- Créer un écosystème commercial local premium
- Fidéliser les clients via un système de cashback innovant
- Offrir aux entreprises des outils de gestion et marketing avancés
- Connecter influenceurs et marques locales

### 1.3 Cibles Utilisateurs
| Type | Description |
|------|-------------|
| **Client** | Consommateurs cherchant des services/produits premium |
| **Entreprise** | Prestataires de services et commerces locaux |
| **Influenceur** | Créateurs de contenu pour partenariats |
| **Admin** | Gestionnaires de la plateforme |

---

## 2. FONCTIONNALITÉS DEMANDÉES (CDC ORIGINAL)

### 2.1 Système d'Authentification
- ✅ Inscription Client / Entreprise / Influenceur
- ✅ Connexion sécurisée JWT
- ✅ Gestion des rôles et permissions
- ✅ Profils utilisateurs complets

### 2.2 Marketplace - Entreprises
- ✅ Catalogue de services et produits
- ✅ Pages entreprise avec photos/vidéos
- ✅ Système de notation et avis
- ✅ Filtres par catégorie, ville, certification
- ✅ Badges : Certifié, Labellisé, Premium, Guest

### 2.3 Système de Commandes
- ✅ Panier multi-entreprises
- ✅ Checkout sécurisé Stripe
- ✅ Suivi de commande en temps réel
- ✅ Historique des achats

### 2.4 Système de Cashback Client
- ✅ Cashback sur chaque achat
- ✅ 3 niveaux : Gratuit (1%), Premium (10%), VIP (15%)
- ✅ Solde visible dans le dashboard
- ✅ Utilisation du cashback pour les achats

### 2.5 Abonnements Premium Client
- ✅ Plan Gratuit : Cashback 1%
- ✅ Plan Premium (9.99 CHF/mois) : Cashback 10%
- ✅ Plan VIP (29.99 CHF/mois) : Cashback 15%
- ✅ Paiement récurrent Stripe

### 2.6 Abonnements Entreprise
- ✅ Plan Standard (200 CHF/mois)
- ✅ Plan Guest (250 CHF/mois)
- ✅ Plan Premium (500 CHF/mois)
- ✅ Plans Optimisation (2000-15000 CHF/mois)
- ✅ Add-ons à la carte

### 2.7 Dashboard Client
- ✅ Vue d'ensemble (stats, cashback, commandes)
- ✅ Mes commandes
- ✅ Mon cashback
- ✅ Mes prestataires favoris
- ✅ Mes amis
- ✅ Messages
- ✅ Notifications

### 2.8 Dashboard Entreprise
- ✅ Vue d'ensemble (stats, revenus, avis)
- ✅ Catalogue (services/produits)
- ✅ Commandes clients
- ✅ Avis et notations
- ✅ Équipe et personnel
- ✅ Stock et inventaire
- ✅ Offres promotionnelles
- ✅ Formations proposées
- ✅ Offres d'emploi
- ✅ Immobilier
- ✅ Investissements

### 2.9 Messagerie
- ✅ Conversations Client ↔ Entreprise
- ✅ Messages temps réel
- ✅ Historique des échanges

### 2.10 Système d'Amis (Réseau Social)
- ✅ Demandes d'amis
- ✅ Liste d'amis
- ✅ Profils cliquables
- ✅ Feed d'activité

### 2.11 Notifications
- ✅ Notifications push in-app
- ✅ Badge compteur temps réel
- ✅ Catégorisation par type

### 2.12 Page d'Accueil
- ✅ Présentation de la plateforme
- ✅ Entreprises mises en avant
- ✅ Catégories de services
- ✅ Avis défilants

---

## 3. 🔴 SUPPLÉMENTS IMPLÉMENTÉS

> Les fonctionnalités suivantes ont été ajoutées **AU-DELÀ** du CDC original

### 🔴 3.1 SYSTÈME DE RETRAIT CASHBACK
**Non prévu initialement - Ajouté à la demande**
- Interface de saisie IBAN dans le profil
- Bouton "Retirer vers mon compte bancaire"
- Minimum de retrait : 50 CHF
- Intégration Stripe Connect pour les transferts
- Fallback manuel si API restreinte
- Historique des retraits avec statuts

### 🔴 3.2 DASHBOARD ADMIN COMPLET
**Non prévu initialement - Ajouté à la demande**
- Accès sécurisé `/admin` pour utilisateurs admin
- **Section Comptabilité** :
  - KPIs financiers (CA, Commissions, Passif cashback)
  - Détail des revenus par source
  - Historique des transactions
  - Export Excel et PDF
- **Section Retraits** :
  - Liste des demandes de retrait
  - Actions approuver/rejeter
  - Export CSV
  - Vue IBAN complet
- **Section Utilisateurs** :
  - Liste de tous les utilisateurs
  - Filtres par type et statut
- **Section Entreprises** :
  - Gestion des entreprises
  - Statistiques par entreprise
- **Section Commandes** :
  - Toutes les commandes de la plateforme
- **Section Paiements** :
  - Résumé des paiements

### 🔴 3.3 SYSTÈME DE WEBHOOKS SALONPRO
**Non prévu initialement - Ajouté à la demande**
- Synchronisation bidirectionnelle Titelli ↔ SalonPro
- Webhook sortant : sync entreprise à l'inscription
- Webhook sortant : sync RDV à la création
- Webhook entrant : réception d'événements SalonPro
- Configuration via variables d'environnement

### 🔴 3.4 SYSTÈME DE PRISE DE RDV
**Non prévu initialement - Ajouté à la demande**
- Modal de réservation sur page entreprise
- Sélection service + date + heure
- Message optionnel
- Notification automatique à l'entreprise
- Sync vers SalonPro
- Statuts : pending → confirmed → completed

### 🔴 3.5 SECTION CONTACTS ENTREPRISE
**Non prévu initialement - Ajouté à la demande**
- CRUD complet pour contacts (clients, fournisseurs, partenaires)
- Filtres par type de contact
- Système de tags personnalisés
- Recherche et statistiques

### 🔴 3.6 MESSAGERIE ENTREPRISE AMÉLIORÉE
**Amélioration du CDC - Interface complète**
- Interface de chat avec liste de conversations
- Compteur de messages non lus
- Responsive mobile (vue liste/conversation)

### 🔴 3.7 WEBSOCKET TEMPS RÉEL
**Non prévu initialement - Ajouté pour UX**
- Notifications push instantanées
- Statut en ligne des amis
- Reconnexion automatique
- Fallback polling si WebSocket indisponible

### 🔴 3.8 VIDÉO PANORAMIQUE HOMEPAGE
**Amélioration UX non prévue**
- Vidéo background HD automatique
- Contrôles play/pause et mute/unmute
- Overlay gradient pour lisibilité

### 🔴 3.9 COMMENTAIRES DÉFILANTS
**Amélioration UX non prévue**
- Animation CSS infinite scroll
- Pause au survol
- Affichage sur Homepage et pages Entreprise

### 🔴 3.10 ALGORITHME IA TARGETING
**Non prévu initialement - Ajouté à la demande**
- Calcul de reach basé sur vrais utilisateurs DB
- Segmentation par âge, genre, localisation
- Suggestions d'optimisation budget

### 🔴 3.11 FRAIS ET COMMISSIONS PRODUCTION
**Paramétrage business non initialement spécifié**
- Frais de gestion : 10% (entreprise)
- Frais de transaction : 2.9% (client)
- Commission investissements : 12%
- Frais de livraison : 5-25 CHF

### 🔴 3.12 FEED SOCIAL / MODE DE VIE
**Extension non prévue du réseau social**
- Posts d'activité automatiques (wishlist)
- Likes et compteurs
- Publication manuelle de posts

---

## 4. ARCHITECTURE TECHNIQUE

### 4.1 Stack Technologique

| Couche | Technologie | Version |
|--------|-------------|---------|
| Frontend | React | 18.x |
| UI Components | Shadcn/UI | Latest |
| Backend | FastAPI | 0.104+ |
| Base de données | MongoDB | 6.x |
| Paiements | Stripe | Latest API |
| Auth | JWT | HS256 |
| WebSocket | FastAPI WebSocket | Native |

### 4.2 Structure des Fichiers

```
/app/
├── backend/
│   ├── server.py              # API principale (9353 lignes)
│   ├── stripe_helper.py       # Intégration Stripe native
│   ├── requirements.txt       # Dépendances Python
│   ├── uploads/               # Fichiers uploadés
│   └── .env                   # Variables d'environnement
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── HomePage.js
│   │   │   ├── ClientDashboard.js     # 4536 lignes
│   │   │   ├── EnterpriseDashboard.js # 4231 lignes
│   │   │   ├── AdminDashboard.js      # 1117 lignes
│   │   │   ├── EnterprisePage.js
│   │   │   └── ...
│   │   ├── components/
│   │   │   ├── ui/            # Shadcn components
│   │   │   ├── dashboard/
│   │   │   └── ...
│   │   ├── services/
│   │   │   └── api.js         # Appels API centralisés
│   │   ├── context/
│   │   │   ├── AuthContext.js
│   │   │   └── CartContext.js
│   │   └── hooks/
│   │       └── useWebSocket.js
│   └── package.json
│
├── memory/
│   └── PRD.md                 # Documentation projet
│
└── test_reports/
    └── iteration_*.json       # 35 rapports de tests
```

---

## 5. MODÈLES DE DONNÉES

### 5.1 Collection `users`
```json
{
  "id": "uuid",
  "email": "string",
  "password": "hashed",
  "user_type": "client | entreprise | influenceur",
  "first_name": "string",
  "last_name": "string",
  "phone": "string",
  "avatar": "url",
  "cover_image": "url",
  "is_admin": "boolean",
  "iban": "string",
  "bank_account_holder": "string",
  "created_at": "datetime"
}
```

### 5.2 Collection `enterprises`
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "business_name": "string",
  "category": "string",
  "description": "string",
  "address": "string",
  "city": "string",
  "phone": "string",
  "logo": "url",
  "cover_image": "url",
  "opening_hours": "object",
  "is_certified": "boolean",
  "is_labeled": "boolean",
  "is_premium": "boolean",
  "average_rating": "number",
  "total_reviews": "number"
}
```

### 5.3 Collection `orders`
```json
{
  "id": "uuid",
  "client_id": "uuid",
  "enterprise_id": "uuid",
  "items": "array",
  "subtotal": "number",
  "transaction_fee": "number",
  "total": "number",
  "status": "pending | confirmed | shipped | delivered | cancelled",
  "payment_intent_id": "string",
  "created_at": "datetime"
}
```

### 5.4 Collection `subscriptions`
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "plan_id": "string",
  "plan_type": "client | enterprise",
  "status": "active | cancelled | expired",
  "stripe_subscription_id": "string",
  "created_at": "datetime",
  "expires_at": "datetime"
}
```

### 5.5 Collection `cashback_withdrawals` 🔴 SUPPLÉMENT
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "amount": "number",
  "status": "pending | processing | manual_processing | completed | failed",
  "iban": "string",
  "bank_account_holder": "string",
  "created_at": "datetime",
  "completed_at": "datetime"
}
```

### 5.6 Collection `bookings` 🔴 SUPPLÉMENT
```json
{
  "id": "uuid",
  "enterprise_id": "uuid",
  "client_id": "uuid",
  "service_id": "uuid",
  "service_name": "string",
  "start_datetime": "datetime",
  "end_datetime": "datetime",
  "notes": "string",
  "status": "pending | confirmed | cancelled | completed",
  "source": "titelli_booking | salonpro"
}
```

---

## 6. SÉCURITÉ ET AUTHENTIFICATION

### 6.1 Authentification JWT
- Token JWT signé avec clé secrète
- Expiration : 7 jours
- Stockage : localStorage (`titelli_token`)
- Header : `Authorization: Bearer <token>`

### 6.2 Protection des Routes
- Middleware `get_current_user` sur routes protégées
- Vérification du rôle utilisateur
- Routes admin protégées par flag `is_admin`

### 6.3 Sécurité Webhook
- Secret partagé pour webhooks SalonPro
- Validation du secret à chaque requête
- Logging des erreurs

### 6.4 Protection des Données
- Mots de passe hashés (bcrypt)
- IBAN masqué dans l'affichage (****XXXX)
- CORS configuré

---

## 7. INTÉGRATIONS TIERCES

### 7.1 Stripe
- **Checkout Sessions** : Paiements one-time et abonnements
- **Subscriptions** : Gestion des abonnements récurrents
- **Connect** : Transferts vers comptes bancaires
- **Webhooks** : Événements de paiement

### 7.2 SalonPro (Webhook) 🔴 SUPPLÉMENT
- **Sync entreprise** : À l'inscription
- **Sync RDV** : À la création de booking
- **Réception events** : Endpoint webhook entrant

### 7.3 Exports
- **Excel** : openpyxl (multi-feuilles)
- **PDF** : reportlab (tableaux formatés)
- **CSV** : Natif Python

---

## 📊 RÉSUMÉ DES MÉTRIQUES

| Métrique | Valeur |
|----------|--------|
| Lignes de code backend | 9,353 |
| Lignes de code frontend | ~15,000 |
| Endpoints API | 150+ |
| Collections MongoDB | 20+ |
| Tests exécutés | 35 itérations |
| Taux de réussite tests | 100% |
| Fonctionnalités CDC | 100% complétées |
| Suppléments ajoutés | 12 |

---

**Document généré le 25 Janvier 2026**  
**Projet Titelli Marketplace - Version Production**
