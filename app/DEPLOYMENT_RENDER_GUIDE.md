# Guide de Déploiement sur Render - Titelli & SalonPro

## 📋 Prérequis

1. Compte Render (https://render.com)
2. Compte MongoDB Atlas (https://cloud.mongodb.com) pour la base de données
3. Code source sur GitHub/GitLab
4. Clé Stripe (optionnel, pour les paiements)

---

## 🗄️ ÉTAPE 1 : Créer la Base de Données MongoDB Atlas

### 1.1 Créer un cluster MongoDB Atlas (GRATUIT)

1. Aller sur https://cloud.mongodb.com
2. Créer un compte ou se connecter
3. **Create a Deployment** → Choisir **M0 FREE**
4. Région : Choisir **Europe (Paris)** ou proche de vous
5. Cluster Name : `titelli-cluster`
6. Cliquer **Create Deployment**

### 1.2 Configurer l'accès

1. **Database Access** → **Add New Database User**
   - Username : `titelli_admin`
   - Password : (générer un mot de passe fort, le noter !)
   - Role : `Atlas admin`
   - Cliquer **Add User**

2. **Network Access** → **Add IP Address**
   - Cliquer **Allow Access from Anywhere** (0.0.0.0/0)
   - Cliquer **Confirm**

### 1.3 Obtenir l'URL de connexion

1. Aller dans **Database** → **Connect**
2. Choisir **Connect your application**
3. Driver : Python, Version 3.12 or later
4. Copier l'URL, elle ressemble à :
```
mongodb+srv://titelli_admin:<password>@titelli-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
```
5. **IMPORTANT** : Remplacer `<password>` par votre vrai mot de passe

---

## 🚀 ÉTAPE 2 : Déployer TITELLI sur Render

### 2.1 Structure du Repository GitHub

Votre repo doit avoir cette structure :
```
titelli/
├── backend/
│   ├── server.py
│   ├── requirements.txt
│   └── .env (NE PAS COMMIT - ajouter au .gitignore)
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── .env (NE PAS COMMIT)
└── README.md
```

### 2.2 Déployer le Backend Titelli (Web Service)

1. **Render Dashboard** → **New** → **Web Service**
2. Connecter votre repo GitHub
3. Remplir les champs :

| Champ | Valeur |
|-------|--------|
| **Name** | `titelli-backend` |
| **Region** | `Frankfurt (EU Central)` |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn server:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | `Free` (ou `Starter` pour prod) |

4. **Environment Variables** (cliquer "Add Environment Variable") :

| Clé | Valeur |
|-----|--------|
| `MONGO_URL` | `mongodb+srv://titelli_admin:VOTRE_MDP@titelli-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority` |
| `DB_NAME` | `titelli_db` |
| `JWT_SECRET` | `votre_secret_jwt_tres_long_et_complexe_minimum_32_caracteres` |
| `STRIPE_API_KEY` | `sk_live_xxxx` (ou `sk_test_xxxx` pour test) |
| `SALONPRO_URL` | `https://salonpro-backend.onrender.com` (à ajouter après déploiement SalonPro) |
| `SALONPRO_WEBHOOK_URL` | `https://salonpro-backend.onrender.com` |
| `SALONPRO_WEBHOOK_SECRET` | `titelli_salonpro_sync_secret_2024` |

5. Cliquer **Create Web Service**
6. Attendre le déploiement (~5-10 min)
7. Noter l'URL : `https://titelli-backend.onrender.com`

### 2.3 Déployer le Frontend Titelli (Static Site)

1. **Render Dashboard** → **New** → **Static Site**
2. Connecter le même repo GitHub
3. Remplir les champs :

| Champ | Valeur |
|-------|--------|
| **Name** | `titelli-frontend` |
| **Branch** | `main` |
| **Root Directory** | `frontend` |
| **Build Command** | `yarn install && yarn build` |
| **Publish Directory** | `build` |

4. **Environment Variables** :

| Clé | Valeur |
|-----|--------|
| `REACT_APP_BACKEND_URL` | `https://titelli-backend.onrender.com` |

5. Cliquer **Create Static Site**
6. Attendre le déploiement (~3-5 min)
7. URL finale : `https://titelli-frontend.onrender.com`

### 2.4 Configurer les Redirects (SPA React)

Dans Render, pour le Static Site, ajouter un fichier `_redirects` dans `frontend/public/` :

```
/*    /index.html   200
```

Ou dans Render → Static Site → **Redirects/Rewrites** :
- Source : `/*`
- Destination : `/index.html`
- Action : `Rewrite`

---

## 🏪 ÉTAPE 3 : Déployer SALONPRO sur Render

### 3.1 Créer le repo SalonPro

Créer un nouveau repo GitHub `salonpro` avec cette structure :
```
salonpro/
├── backend/
│   ├── server.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
└── README.md
```

### 3.2 Backend SalonPro - requirements.txt

```txt
fastapi==0.109.0
uvicorn==0.27.0
motor==3.3.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
httpx==0.26.0
pydantic==2.5.3
```

### 3.3 Backend SalonPro - server.py (Minimal)

```python
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from jose import jwt
import os
import logging

# Configuration
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'titelli_db')  # MÊME BASE QUE TITELLI
JWT_SECRET = os.environ.get('JWT_SECRET')
TITELLI_WEBHOOK_SECRET = os.environ.get('TITELLI_WEBHOOK_SECRET', 'titelli_salonpro_sync_secret')

app = FastAPI(title="SalonPro API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============ AUTH ============

async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token manquant")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("user_id")
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalide")


# ============ AUTO-LOGIN FROM TITELLI ============

@app.get("/api/auth/autologin")
async def autologin_from_titelli(autologin_token: str):
    """
    Permet la connexion automatique depuis Titelli avec un token temporaire.
    Le token est généré par Titelli et contient les infos de l'entreprise.
    """
    try:
        payload = jwt.decode(autologin_token, JWT_SECRET, algorithms=["HS256"])
        
        if payload.get("purpose") != "salonpro_autologin":
            raise HTTPException(status_code=400, detail="Token invalide")
        
        enterprise_id = payload.get("enterprise_id")
        user_id = payload.get("user_id")
        
        # Vérifier que l'entreprise existe dans la base partagée
        enterprise = await db.enterprises.find_one({"id": enterprise_id}, {"_id": 0})
        if not enterprise:
            raise HTTPException(status_code=404, detail="Entreprise non trouvée")
        
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Créer un nouveau token de session pour SalonPro
        session_token = jwt.encode(
            {
                "user_id": user_id,
                "enterprise_id": enterprise_id,
                "email": user.get("email"),
                "exp": datetime.now(timezone.utc) + timedelta(hours=24)
            },
            JWT_SECRET,
            algorithm="HS256"
        )
        
        return {
            "success": True,
            "token": session_token,
            "user": {
                "id": user_id,
                "email": user.get("email"),
                "first_name": user.get("first_name"),
                "last_name": user.get("last_name")
            },
            "enterprise": {
                "id": enterprise_id,
                "business_name": enterprise.get("business_name"),
                "category": enterprise.get("category")
            }
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")


# ============ WEBHOOK FROM TITELLI ============

@app.post("/api/webhook/titelli")
async def receive_titelli_webhook(request: Request):
    """
    Reçoit les webhooks de Titelli pour synchroniser les données.
    Events: enterprise_created, appointment_created, service_created, order_created
    """
    try:
        data = await request.json()
        
        # Vérifier le secret
        if data.get("secret") != TITELLI_WEBHOOK_SECRET:
            raise HTTPException(status_code=403, detail="Secret invalide")
        
        event_type = data.get("event_type")
        event_data = data.get("data", {})
        
        logger.info(f"Webhook reçu de Titelli: {event_type}")
        
        if event_type == "enterprise_created":
            # L'entreprise est déjà dans la même base, rien à faire
            logger.info(f"Entreprise sync: {event_data.get('business_name')}")
            
        elif event_type == "appointment_created":
            # Stocker le RDV dans une collection SalonPro spécifique si nécessaire
            appointment_id = event_data.get("appointment_id")
            logger.info(f"RDV sync: {appointment_id}")
            
            # Optionnel: créer une entrée dans une collection SalonPro
            await db.salonpro_appointments.update_one(
                {"titelli_appointment_id": appointment_id},
                {"$set": {
                    **event_data,
                    "synced_from": "titelli",
                    "synced_at": datetime.now(timezone.utc).isoformat()
                }},
                upsert=True
            )
            
        elif event_type == "order_created":
            # Stocker les commandes pour la section "Commandes validées"
            order_id = event_data.get("order_id")
            logger.info(f"Commande sync: {order_id}")
            
            await db.salonpro_orders.update_one(
                {"titelli_order_id": order_id},
                {"$set": {
                    **event_data,
                    "synced_from": "titelli",
                    "synced_at": datetime.now(timezone.utc).isoformat()
                }},
                upsert=True
            )
            
        elif event_type == "order_status_updated":
            order_id = event_data.get("order_id")
            new_status = event_data.get("status")
            await db.salonpro_orders.update_one(
                {"titelli_order_id": order_id},
                {"$set": {"status": new_status, "updated_at": event_data.get("updated_at")}}
            )
            
        elif event_type == "service_created":
            logger.info(f"Service sync: {event_data.get('name')}")
        
        return {"status": "received", "event_type": event_type}
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ DASHBOARD DATA ============

@app.get("/api/dashboard/appointments")
async def get_dashboard_appointments(current_user: dict = Depends(get_current_user)):
    """Récupère les RDV pour le dashboard SalonPro"""
    enterprise = await db.enterprises.find_one({"user_id": current_user["id"]}, {"_id": 0})
    if not enterprise:
        raise HTTPException(status_code=404, detail="Entreprise non trouvée")
    
    # Récupérer depuis la collection agenda de Titelli
    appointments = await db.agenda.find(
        {"enterprise_id": enterprise["id"]},
        {"_id": 0}
    ).sort("start_datetime", -1).to_list(100)
    
    return {"appointments": appointments}


@app.get("/api/dashboard/orders")
async def get_dashboard_orders(current_user: dict = Depends(get_current_user)):
    """Récupère les commandes validées pour le dashboard SalonPro"""
    enterprise = await db.enterprises.find_one({"user_id": current_user["id"]}, {"_id": 0})
    if not enterprise:
        raise HTTPException(status_code=404, detail="Entreprise non trouvée")
    
    # Récupérer les commandes synchronisées
    orders = await db.salonpro_orders.find(
        {"enterprise_id": enterprise["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    # Si vide, récupérer directement depuis Titelli orders
    if not orders:
        orders = await db.orders.find(
            {"enterprise_id": enterprise["id"]},
            {"_id": 0}
        ).sort("created_at", -1).to_list(100)
    
    return {"orders": orders}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "salonpro"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

### 3.4 Déployer Backend SalonPro sur Render

1. **Render Dashboard** → **New** → **Web Service**
2. Connecter le repo `salonpro`
3. Configuration :

| Champ | Valeur |
|-------|--------|
| **Name** | `salonpro-backend` |
| **Region** | `Frankfurt (EU Central)` |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn server:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | `Free` |

4. **Environment Variables** :

| Clé | Valeur |
|-----|--------|
| `MONGO_URL` | `mongodb+srv://titelli_admin:VOTRE_MDP@titelli-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority` |
| `DB_NAME` | `titelli_db` |
| `JWT_SECRET` | `votre_secret_jwt_tres_long_et_complexe_minimum_32_caracteres` |
| `TITELLI_WEBHOOK_SECRET` | `titelli_salonpro_sync_secret_2024` |

**⚠️ IMPORTANT** : Utiliser les MÊMES valeurs pour `MONGO_URL`, `DB_NAME` et `JWT_SECRET` que Titelli !

5. Cliquer **Create Web Service**
6. Noter l'URL : `https://salonpro-backend.onrender.com`

### 3.5 Déployer Frontend SalonPro sur Render

1. **Render Dashboard** → **New** → **Static Site**
2. Configuration :

| Champ | Valeur |
|-------|--------|
| **Name** | `salonpro-frontend` |
| **Branch** | `main` |
| **Root Directory** | `frontend` |
| **Build Command** | `yarn install && yarn build` |
| **Publish Directory** | `build` |

3. **Environment Variables** :

| Clé | Valeur |
|-----|--------|
| `REACT_APP_BACKEND_URL` | `https://salonpro-backend.onrender.com` |

4. Ajouter Redirect pour SPA dans `frontend/public/_redirects` :
```
/*    /index.html   200
```

5. URL finale : `https://salonpro-frontend.onrender.com`

---

## 🔗 ÉTAPE 4 : Connecter Titelli et SalonPro

### 4.1 Mettre à jour Titelli Backend

Après le déploiement de SalonPro, retourner dans Render → `titelli-backend` → **Environment** et ajouter/modifier :

| Clé | Valeur |
|-----|--------|
| `SALONPRO_URL` | `https://salonpro-frontend.onrender.com` |
| `SALONPRO_WEBHOOK_URL` | `https://salonpro-backend.onrender.com` |

Cliquer **Save Changes** → Le service va redémarrer automatiquement.

### 4.2 Vérifier la connexion

Tester l'auto-login :
```bash
# 1. Se connecter à Titelli et récupérer le token
TOKEN=$(curl -s -X POST "https://titelli-backend.onrender.com/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"spa.luxury@titelli.com","password":"Demo123!"}' | jq -r '.token')

# 2. Obtenir le token SalonPro
curl -s "https://titelli-backend.onrender.com/api/auth/salonpro-token" \
  -H "Authorization: Bearer $TOKEN" | jq

# 3. Vérifier le webhook
curl -s -X POST "https://salonpro-backend.onrender.com/api/webhook/titelli" \
  -H "Content-Type: application/json" \
  -d '{"event_type":"test","secret":"titelli_salonpro_sync_secret_2024","data":{}}' | jq
```

---

## 📝 ÉTAPE 5 : Domaines Personnalisés (Optionnel)

### 5.1 Ajouter un domaine personnalisé sur Render

1. Acheter un domaine (OVH, Namecheap, Gandi, etc.)
2. Dans Render → Votre service → **Settings** → **Custom Domains**
3. Ajouter : `titelli.com` et `www.titelli.com`
4. Render affichera les enregistrements DNS à configurer

### 5.2 Configuration DNS

Chez votre registrar, ajouter :

**Pour le frontend (titelli.com) :**
```
Type: CNAME
Name: @
Value: titelli-frontend.onrender.com
```

**Pour le backend (api.titelli.com) :**
```
Type: CNAME  
Name: api
Value: titelli-backend.onrender.com
```

### 5.3 Mettre à jour les variables d'environnement

Frontend :
```
REACT_APP_BACKEND_URL=https://api.titelli.com
```

---

## 🔐 RÉCAPITULATIF DES VARIABLES D'ENVIRONNEMENT

### Titelli Backend
```env
MONGO_URL=mongodb+srv://titelli_admin:xxx@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=titelli_db
JWT_SECRET=votre_secret_jwt_32_caracteres_minimum
STRIPE_API_KEY=sk_live_xxx
SALONPRO_URL=https://salonpro-frontend.onrender.com
SALONPRO_WEBHOOK_URL=https://salonpro-backend.onrender.com
SALONPRO_WEBHOOK_SECRET=titelli_salonpro_sync_secret_2024
```

### Titelli Frontend
```env
REACT_APP_BACKEND_URL=https://titelli-backend.onrender.com
```

### SalonPro Backend
```env
MONGO_URL=mongodb+srv://titelli_admin:xxx@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=titelli_db
JWT_SECRET=votre_secret_jwt_32_caracteres_minimum
TITELLI_WEBHOOK_SECRET=titelli_salonpro_sync_secret_2024
```

### SalonPro Frontend
```env
REACT_APP_BACKEND_URL=https://salonpro-backend.onrender.com
```

---

## ⚠️ Points Importants

1. **MÊME BASE MONGODB** : Titelli et SalonPro partagent la même base de données pour que les entreprises et utilisateurs soient synchronisés automatiquement.

2. **MÊME JWT_SECRET** : Les deux applications doivent utiliser le même secret JWT pour que l'auto-login fonctionne.

3. **Free Tier Render** : Les services gratuits s'endorment après 15 min d'inactivité. Premier accès = ~30 sec de chargement. Pour la prod, utiliser "Starter" ($7/mois).

4. **HTTPS automatique** : Render gère automatiquement les certificats SSL.

5. **Logs** : Render Dashboard → Service → **Logs** pour débugger.

---

## 🧪 Checklist Post-Déploiement

- [ ] MongoDB Atlas accessible (IP 0.0.0.0/0 autorisée)
- [ ] Titelli Backend répond (`/api/health`)
- [ ] Titelli Frontend charge sans erreur
- [ ] Login fonctionne sur Titelli
- [ ] SalonPro Backend répond (`/api/health`)
- [ ] SalonPro Frontend charge
- [ ] Auto-login Titelli → SalonPro fonctionne
- [ ] Webhook test réussi
- [ ] Stripe webhook configuré (optionnel)

---

*Guide créé le 26 Janvier 2026*
