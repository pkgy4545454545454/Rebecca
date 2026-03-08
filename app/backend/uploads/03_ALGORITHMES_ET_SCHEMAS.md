# 📊 ALGORITHMES ET SCHÉMAS - TITELLI MARKETPLACE

**Version:** 2.0 - Production Ready  
**Date:** 25 Janvier 2026

---

## 📌 TABLE DES MATIÈRES

1. [Algorithme de Publicités & Mise en Avant](#1-algorithme-de-publicités--mise-en-avant)
2. [Algorithme de Paiement & Checkout](#2-algorithme-de-paiement--checkout)
3. [Algorithme du Feed Social](#3-algorithme-du-feed-social)
4. [Algorithme de Cashback](#4-algorithme-de-cashback)
5. [Algorithme de Synchronisation SalonPro](#5-algorithme-de-synchronisation-salonpro)
6. [Algorithme de Notifications](#6-algorithme-de-notifications)

---

## 1. ALGORITHME DE PUBLICITÉS & MISE EN AVANT

### 1.1 Schéma du Système de Mise en Avant

```
┌─────────────────────────────────────────────────────────────────┐
│                    SYSTÈME DE MISE EN AVANT                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   VÉRIFICATION ABONNEMENT                        │
│                                                                  │
│   Entreprise → Récupérer tier abonnement                        │
│                     │                                            │
│        ┌────────────┼────────────┬────────────┐                 │
│        ▼            ▼            ▼            ▼                 │
│    ┌──────┐    ┌──────┐    ┌───────┐    ┌─────────┐            │
│    │ FREE │    │BASIC │    │PREMIUM│    │OPTIMIS. │            │
│    │1 pub │    │2 pubs│    │6 pubs │    │15+ pubs │            │
│    └──────┘    └──────┘    └───────┘    └─────────┘            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CALCUL SCORE AFFICHAGE                         │
│                                                                  │
│   score = (rating × 10) + (reviews × 5) + (tier_bonus × 20)     │
│         + (is_certified × 15) + (is_labeled × 10)               │
│         + (recent_activity × 5)                                  │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ TIER BONUS:                                              │   │
│   │   FREE = 0                                               │   │
│   │   BASIC = 1                                              │   │
│   │   PREMIUM = 3                                            │   │
│   │   OPTIMISATION = 5                                       │   │
│   └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ORDRE D'AFFICHAGE                              │
│                                                                  │
│   1. Entreprises PREMIUM (score décroissant)                    │
│   2. Entreprises CERTIFIÉES (score décroissant)                 │
│   3. Entreprises LABELLISÉES (score décroissant)                │
│   4. Autres entreprises (score décroissant)                     │
│                                                                  │
│   Randomisation légère pour éviter toujours les mêmes en tête   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Algorithme de Ciblage IA Marketing

```
┌─────────────────────────────────────────────────────────────────┐
│                   ALGORITHME CIBLAGE IA                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│   ENTRÉE: Paramètres de campagne                                 │
│   - Budget: 500-50000 CHF                                        │
│   - Cible: âge, genre, localisation, intérêts                   │
│   - Durée: 7-90 jours                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│   ÉTAPE 1: Comptage utilisateurs réels (MongoDB)                 │
│                                                                  │
│   query = {                                                      │
│     "user_type": "client",                                       │
│     "age": {"$gte": min_age, "$lte": max_age},                  │
│     "gender": target_gender,                                     │
│     "city": target_city                                          │
│   }                                                              │
│                                                                  │
│   total_users = db.users.count_documents(query)                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│   ÉTAPE 2: Calcul du reach estimé                                │
│                                                                  │
│   reach_factor = budget / 100  (1 CHF = 1% reach additionnel)   │
│   base_reach = total_users × 0.1  (10% de base)                 │
│   estimated_reach = min(base_reach × reach_factor, total_users) │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ Exemple:                                                 │   │
│   │   Budget: 500 CHF                                        │   │
│   │   Users cibles: 1000                                     │   │
│   │   Base reach: 100 (10%)                                  │   │
│   │   Reach factor: 5                                        │   │
│   │   Estimated reach: 500 users (50%)                       │   │
│   └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│   ÉTAPE 3: Estimations d'engagement                              │
│                                                                  │
│   impressions = reach × 3 (moyenne 3 impressions/user)          │
│   clicks = impressions × 0.02 (CTR 2%)                          │
│   conversions = clicks × 0.05 (taux conversion 5%)              │
│   cost_per_click = budget / clicks                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│   SORTIE: Rapport prédictif                                      │
│                                                                  │
│   {                                                              │
│     "reach": 500,                                                │
│     "impressions": 1500,                                         │
│     "clicks": 30,                                                │
│     "conversions": 2,                                            │
│     "cost_per_click": 16.67,                                     │
│     "recommendations": [...]                                     │
│   }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. ALGORITHME DE PAIEMENT & CHECKOUT

### 2.1 Flux de Paiement Commande

```
┌─────────────────────────────────────────────────────────────────┐
│                   FLUX PAIEMENT COMMANDE                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────┐                                                       
│  CLIENT  │                                                       
│  Panier  │                                                       
└────┬─────┘                                                       
     │ Clic "Payer"                                                
     ▼                                                             
┌─────────────────────────────────────────────────────────────────┐
│   ÉTAPE 1: Calcul des frais                                      │
│                                                                  │
│   subtotal = Σ(item.price × item.quantity)                      │
│   transaction_fee = subtotal × 0.029  (2.9% client)             │
│   management_fee = subtotal × 0.10   (10% entreprise)           │
│   delivery_fee = 5-25 CHF (selon distance)                      │
│   total = subtotal + transaction_fee + delivery_fee             │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ Exemple:                                                 │   │
│   │   Subtotal: 100 CHF                                      │   │
│   │   Transaction fee: 2.90 CHF                              │   │
│   │   Delivery: 10 CHF                                       │   │
│   │   TOTAL CLIENT: 112.90 CHF                               │   │
│   │                                                          │   │
│   │   Management fee: 10 CHF (prélevé sur entreprise)        │   │
│   │   REÇU ENTREPRISE: 90 CHF                                │   │
│   └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
     │                                                             
     ▼                                                             
┌─────────────────────────────────────────────────────────────────┐
│   ÉTAPE 2: Création session Stripe                               │
│                                                                  │
│   stripe.checkout.sessions.create({                             │
│     mode: "payment",                                             │
│     line_items: [...],                                           │
│     success_url: "/payment/success?session={CHECKOUT_SESSION}", │
│     cancel_url: "/payment/cancel"                                │
│   })                                                             │
└─────────────────────────────────────────────────────────────────┘
     │                                                             
     ▼                                                             
┌─────────────────────────────────────────────────────────────────┐
│   ÉTAPE 3: Page Stripe (externe)                                 │
│                                                                  │
│   Client entre ses coordonnées bancaires                        │
│   Stripe valide le paiement                                      │
└─────────────────────────────────────────────────────────────────┘
     │                                                             
     ▼                                                             
┌─────────────────────────────────────────────────────────────────┐
│   ÉTAPE 4: Webhook Stripe → Backend                              │
│                                                                  │
│   Event: checkout.session.completed                              │
│                                                                  │
│   Actions:                                                       │
│   1. Créer commande en BDD (status: "paid")                     │
│   2. Calculer cashback client                                    │
│   3. Ajouter cashback au solde client                           │
│   4. Envoyer notification client "Commande confirmée"           │
│   5. Envoyer notification entreprise "Nouvelle commande"        │
│   6. Vider le panier client                                      │
└─────────────────────────────────────────────────────────────────┘
     │                                                             
     ▼                                                             
┌─────────────────────────────────────────────────────────────────┐
│   ÉTAPE 5: Redirection succès                                    │
│                                                                  │
│   Client → /payment/success                                      │
│   Affichage récapitulatif + cashback gagné                      │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Flux Abonnement Premium

```
┌─────────────────────────────────────────────────────────────────┐
│                   FLUX ABONNEMENT PREMIUM                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────┐                                                       
│  CLIENT  │                                                       
│ Dashboard│                                                       
└────┬─────┘                                                       
     │ Clic "Passer Premium" / "Passer VIP"                       
     ▼                                                             
┌─────────────────────────────────────────────────────────────────┐
│   Backend: /api/client/premium/checkout                          │
│                                                                  │
│   1. Vérifier pas déjà abonné                                   │
│   2. Créer session Stripe (mode: "subscription")                │
│   3. Prix: Premium 9.99 CHF/mois ou VIP 29.99 CHF/mois          │
└─────────────────────────────────────────────────────────────────┘
     │                                                             
     ▼                                                             
┌─────────────────────────────────────────────────────────────────┐
│   Page Stripe: Paiement récurrent                                │
└─────────────────────────────────────────────────────────────────┘
     │                                                             
     ▼                                                             
┌─────────────────────────────────────────────────────────────────┐
│   Webhook: customer.subscription.created                         │
│                                                                  │
│   Actions:                                                       │
│   1. Créer entrée dans "subscriptions"                          │
│   2. Mettre à jour user.premium_tier                            │
│   3. Calculer nouveau taux cashback                             │
│   4. Notification "Bienvenue Premium/VIP!"                      │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ TAUX CASHBACK:                                           │   │
│   │   Gratuit → 1%                                           │   │
│   │   Premium → 10%                                          │   │
│   │   VIP → 15%                                              │   │
│   └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. ALGORITHME DU FEED SOCIAL

### 3.1 Schéma du Feed d'Activité

```
┌─────────────────────────────────────────────────────────────────┐
│                   ALGORITHME FEED SOCIAL                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│   SOURCES DE POSTS                                               │
│                                                                  │
│   ┌────────────┐  ┌────────────┐  ┌────────────┐                │
│   │  WISHLIST  │  │  COMMANDE  │  │   MANUAL   │                │
│   │   Ajout    │  │ Passée     │  │    Post    │                │
│   └─────┬──────┘  └─────┬──────┘  └─────┬──────┘                │
│         │               │               │                        │
│         └───────────────┴───────────────┘                        │
│                         │                                        │
│                         ▼                                        │
│              ┌─────────────────────┐                             │
│              │  CRÉATION POST      │                             │
│              │  activity_feed      │                             │
│              └─────────────────────┘                             │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│   RÉCUPÉRATION FEED                                              │
│                                                                  │
│   1. Récupérer liste d'amis de l'utilisateur                    │
│   2. Query: posts où user_id IN [amis]                          │
│   3. Tri par date décroissante                                   │
│   4. Pagination (limit: 20, offset: x)                          │
│                                                                  │
│   query = {                                                      │
│     "user_id": {"$in": friend_ids},                             │
│     "visibility": "friends"                                      │
│   }                                                              │
│   sort = [("created_at", -1)]                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│   ENRICHISSEMENT                                                 │
│                                                                  │
│   Pour chaque post:                                              │
│   - Joindre infos user (avatar, nom)                            │
│   - Joindre infos entreprise (si applicable)                    │
│   - Compter likes                                                │
│   - Vérifier si user actuel a liké                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│   SORTIE: Liste de posts enrichis                                │
│                                                                  │
│   [                                                              │
│     {                                                            │
│       "id": "uuid",                                              │
│       "user": { "name": "Marie", "avatar": "..." },             │
│       "type": "wishlist",                                        │
│       "content": "Marie a ajouté un service...",                │
│       "enterprise": { "name": "Spa Luxury", ... },              │
│       "likes_count": 5,                                          │
│       "has_liked": false,                                        │
│       "created_at": "2026-01-25T10:00:00"                       │
│     },                                                           │
│     ...                                                          │
│   ]                                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. ALGORITHME DE CASHBACK

### 4.1 Calcul du Cashback

```
┌─────────────────────────────────────────────────────────────────┐
│                   ALGORITHME CASHBACK                            │
└─────────────────────────────────────────────────────────────────┘

┌──────────┐                                                       
│ COMMANDE │                                                       
│ Validée  │                                                       
└────┬─────┘                                                       
     │                                                             
     ▼                                                             
┌─────────────────────────────────────────────────────────────────┐
│   ÉTAPE 1: Déterminer taux cashback                              │
│                                                                  │
│   async def get_user_cashback_rate(user_id):                    │
│       subscription = await db.subscriptions.find_one({           │
│           "user_id": user_id,                                    │
│           "status": "active"                                     │
│       })                                                         │
│                                                                  │
│       if not subscription:                                       │
│           return 0.01  # 1% Gratuit                             │
│                                                                  │
│       plan = subscription.get("plan_id")                        │
│       if plan == "vip":                                          │
│           return 0.15  # 15%                                     │
│       elif plan == "premium":                                    │
│           return 0.10  # 10%                                     │
│       else:                                                      │
│           return 0.01  # 1%                                      │
└─────────────────────────────────────────────────────────────────┘
     │                                                             
     ▼                                                             
┌─────────────────────────────────────────────────────────────────┐
│   ÉTAPE 2: Calculer montant cashback                             │
│                                                                  │
│   cashback_amount = order_subtotal × cashback_rate              │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ Exemple (Client VIP):                                    │   │
│   │   Commande: 100 CHF                                      │   │
│   │   Taux: 15%                                              │   │
│   │   Cashback: 15 CHF                                       │   │
│   └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
     │                                                             
     ▼                                                             
┌─────────────────────────────────────────────────────────────────┐
│   ÉTAPE 3: Créditer le cashback                                  │
│                                                                  │
│   await db.users.update_one(                                    │
│       {"id": user_id},                                           │
│       {"$inc": {"cashback_balance": cashback_amount}}           │
│   )                                                              │
│                                                                  │
│   await db.cashback_history.insert_one({                        │
│       "user_id": user_id,                                        │
│       "amount": cashback_amount,                                 │
│       "order_id": order_id,                                      │
│       "type": "earned"                                           │
│   })                                                             │
└─────────────────────────────────────────────────────────────────┘
     │                                                             
     ▼                                                             
┌─────────────────────────────────────────────────────────────────┐
│   ÉTAPE 4: Notification                                          │
│                                                                  │
│   await create_notification(                                    │
│       user_id,                                                   │
│       "cashback_earned",                                         │
│       f"Vous avez gagné {cashback_amount} CHF de cashback!"     │
│   )                                                              │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Retrait Cashback

```
┌─────────────────────────────────────────────────────────────────┐
│                   ALGORITHME RETRAIT CASHBACK                    │
└─────────────────────────────────────────────────────────────────┘

┌──────────┐                                                       
│  CLIENT  │                                                       
│  Retrait │                                                       
└────┬─────┘                                                       
     │                                                             
     ▼                                                             
┌─────────────────────────────────────────────────────────────────┐
│   VÉRIFICATIONS                                                  │
│                                                                  │
│   ✓ Solde >= 50 CHF (minimum)                                   │
│   ✓ IBAN renseigné                                              │
│   ✓ Pas de retrait en cours                                     │
└─────────────────────────────────────────────────────────────────┘
     │ OK                                                          
     ▼                                                             
┌─────────────────────────────────────────────────────────────────┐
│   CRÉATION DEMANDE                                               │
│                                                                  │
│   withdrawal = {                                                 │
│       "id": uuid,                                                │
│       "user_id": user_id,                                        │
│       "amount": requested_amount,                                │
│       "iban": user.iban,                                         │
│       "status": "pending"                                        │
│   }                                                              │
└─────────────────────────────────────────────────────────────────┘
     │                                                             
     ▼                                                             
┌─────────────────────────────────────────────────────────────────┐
│   TENTATIVE STRIPE CONNECT                                       │
│                                                                  │
│   try:                                                           │
│       stripe.transfers.create(                                   │
│           amount=amount_cents,                                   │
│           currency="chf",                                        │
│           destination=stripe_account_id                          │
│       )                                                          │
│       status = "processing"                                      │
│   except StripeError:                                            │
│       status = "manual_processing"  ← Fallback admin            │
└─────────────────────────────────────────────────────────────────┘
     │                                                             
     ▼                                                             
┌─────────────────────────────────────────────────────────────────┐
│   DÉBIT SOLDE                                                    │
│                                                                  │
│   await db.users.update_one(                                    │
│       {"id": user_id},                                           │
│       {"$inc": {"cashback_balance": -amount}}                   │
│   )                                                              │
└─────────────────────────────────────────────────────────────────┘
     │                                                             
     ▼                                                             
┌─────────────────────────────────────────────────────────────────┐
│   NOTIFICATION                                                   │
│                                                                  │
│   "Votre demande de retrait de X CHF est en cours"              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. ALGORITHME DE SYNCHRONISATION SALONPRO

### 5.1 Webhook Sortant (Titelli → SalonPro)

```
┌─────────────────────────────────────────────────────────────────┐
│                   SYNC TITELLI → SALONPRO                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐                                                
│ Action Titelli  │                                                
│ - Inscription   │                                                
│ - Nouveau RDV   │                                                
│ - Nouveau service│                                               
└───────┬─────────┘                                                
        │                                                          
        ▼                                                          
┌─────────────────────────────────────────────────────────────────┐
│   PRÉPARATION PAYLOAD                                            │
│                                                                  │
│   payload = {                                                    │
│       "event_type": "enterprise_created" | "appointment_created",│
│       "timestamp": datetime.now().isoformat(),                  │
│       "secret": SALONPRO_WEBHOOK_SECRET,                        │
│       "data": {                                                  │
│           "enterprise_id": "...",                                │
│           "client_id": "...",                                    │
│           "service_name": "...",                                 │
│           "start_datetime": "...",                               │
│           ...                                                    │
│       }                                                          │
│   }                                                              │
└─────────────────────────────────────────────────────────────────┘
        │                                                          
        ▼                                                          
┌─────────────────────────────────────────────────────────────────┐
│   ENVOI HTTP ASYNC                                               │
│                                                                  │
│   async with httpx.AsyncClient() as client:                     │
│       response = await client.post(                             │
│           f"{SALONPRO_URL}/api/webhook/titelli",                │
│           json=payload,                                          │
│           timeout=10.0                                           │
│       )                                                          │
└─────────────────────────────────────────────────────────────────┘
        │                                                          
        ▼                                                          
┌─────────────────────────────────────────────────────────────────┐
│   SALONPRO                                                       │
│   - Reçoit webhook                                               │
│   - Valide secret                                                │
│   - Crée/met à jour les données                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Webhook Entrant (SalonPro → Titelli)

```
┌─────────────────────────────────────────────────────────────────┐
│                   SYNC SALONPRO → TITELLI                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐                                                
│ SalonPro envoie │                                                
│ POST /webhook   │                                                
└───────┬─────────┘                                                
        │                                                          
        ▼                                                          
┌─────────────────────────────────────────────────────────────────┐
│   VALIDATION SECRET                                              │
│                                                                  │
│   if payload.secret != SALONPRO_WEBHOOK_SECRET:                 │
│       raise HTTPException(401)                                   │
└─────────────────────────────────────────────────────────────────┘
        │ OK                                                       
        ▼                                                          
┌─────────────────────────────────────────────────────────────────┐
│   TRAITEMENT PAR EVENT TYPE                                      │
│                                                                  │
│   ┌─────────────────────┐                                       │
│   │ appointment_created │ → Créer dans db.agenda                │
│   └─────────────────────┘                                       │
│   ┌─────────────────────┐                                       │
│   │ appointment_updated │ → Update status dans db.agenda        │
│   └─────────────────────┘                                       │
│   ┌─────────────────────┐                                       │
│   │ appointment_cancel  │ → Set status="cancelled"              │
│   └─────────────────────┘                                       │
│   ┌─────────────────────┐                                       │
│   │ service_created     │ → Créer dans db.services_products     │
│   └─────────────────────┘                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. ALGORITHME DE NOTIFICATIONS

### 6.1 Système de Notifications

```
┌─────────────────────────────────────────────────────────────────┐
│                   SYSTÈME NOTIFICATIONS                          │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐                                               
│ Événement déclen-│                                               
│ cheur (commande, │                                               
│ avis, message...)│                                               
└────────┬─────────┘                                               
         │                                                         
         ▼                                                         
┌─────────────────────────────────────────────────────────────────┐
│   FONCTION create_notification()                                 │
│                                                                  │
│   async def create_notification(                                │
│       user_id, notification_type, title, message, data={}       │
│   ):                                                             │
│       notification = {                                           │
│           "id": uuid4(),                                         │
│           "user_id": user_id,                                    │
│           "notification_type": notification_type,               │
│           "title": title,                                        │
│           "message": message,                                    │
│           "data": data,                                          │
│           "is_read": False,                                      │
│           "created_at": datetime.now()                          │
│       }                                                          │
│       await db.notifications.insert_one(notification)           │
│       await send_websocket_notification(user_id, notification)  │
└─────────────────────────────────────────────────────────────────┘
         │                                                         
         ├──────────────────────────────────────┐                  
         │                                      │                  
         ▼                                      ▼                  
┌─────────────────────┐              ┌─────────────────────┐      
│ STOCKAGE MONGODB    │              │ PUSH WEBSOCKET      │      
│                     │              │                     │      
│ Collection:         │              │ Si user connecté:   │      
│ notifications       │              │ Envoi temps réel    │      
└─────────────────────┘              └─────────────────────┘      
```

### 6.2 Types de Notifications

```
┌─────────────────────────────────────────────────────────────────┐
│                   TYPES DE NOTIFICATIONS                         │
└─────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ CLIENT                                                          │
├────────────────────────────────────────────────────────────────┤
│ order_placed        │ "Commande confirmée"                     │
│ order_status        │ "Votre commande a été expédiée"          │
│ cashback_earned     │ "Vous avez gagné X CHF de cashback"      │
│ friend_request      │ "X souhaite vous ajouter comme ami"      │
│ friend_accepted     │ "X a accepté votre demande"              │
│ new_message         │ "Nouveau message de X"                   │
│ withdrawal_update   │ "Votre retrait a été traité"             │
│ premium_activated   │ "Bienvenue dans Premium!"                │
│ booking_confirmed   │ "Votre RDV a été confirmé"               │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ ENTREPRISE                                                      │
├────────────────────────────────────────────────────────────────┤
│ new_order           │ "Nouvelle commande de X"                 │
│ new_review          │ "Nouvel avis ⭐⭐⭐⭐⭐"                 │
│ job_application     │ "Nouvelle candidature pour X"            │
│ training_purchase   │ "X s'est inscrit à votre formation"      │
│ booking_request     │ "Nouvelle demande de RDV"                │
│ subscription_active │ "Votre abonnement est actif"             │
└────────────────────────────────────────────────────────────────┘
```

---

**Document généré le 25 Janvier 2026**  
**Projet Titelli Marketplace - Algorithmes et Schémas**
