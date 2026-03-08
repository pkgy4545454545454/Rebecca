# Titelli - Plateforme Marketplace

Plateforme marketplace pour les prestataires de services et produits de la région de Lausanne.

## 📁 Structure du projet

```
titelli-pure/
├── backend/
│   ├── server.js      # Serveur Node.js/Express
│   ├── seed.js        # Script de données démo
│   ├── package.json   # Dépendances
│   └── .env           # Variables d'environnement
└── frontend/
    ├── index.html             # Page d'accueil
    ├── auth.html              # Connexion/Inscription
    ├── services.html          # Liste des services
    ├── products.html          # Liste des produits
    ├── entreprises.html       # Liste des entreprises
    ├── entreprise.html        # Profil entreprise
    ├── dashboard-client.html  # Dashboard client
    ├── dashboard-entreprise.html # Dashboard entreprise
    ├── admin.html             # Dashboard admin
    ├── payment-success.html   # Page paiement réussi
    ├── payment-cancel.html    # Page paiement annulé
    ├── css/
    │   └── style.css          # Styles CSS
    └── js/
        ├── api.js             # Fonctions API
        └── app.js             # Logique JavaScript
```

## 🚀 Installation et démarrage

### Prérequis
- Node.js (v16+)
- npm ou yarn

### Backend

```bash
cd backend

# Installer les dépendances
npm install

# Configurer les variables d'environnement
# Créez un fichier .env avec :
# MONGO_URL=votre_url_mongodb
# DB_NAME=titelli
# JWT_SECRET=votre_secret_jwt
# STRIPE_SECRET_KEY=votre_cle_stripe
# PORT=8001

# Créer les données de démo (optionnel)
node seed.js

# Démarrer le serveur
node server.js
```

Le serveur démarre sur http://localhost:8001

### Frontend

Le frontend est composé de fichiers HTML/CSS/JS statiques. 
Vous pouvez l'ouvrir directement dans un navigateur ou utiliser un serveur statique :

```bash
cd frontend

# Option 1 : Ouvrir directement index.html dans votre navigateur

# Option 2 : Utiliser un serveur statique
npx serve .
# ou
python -m http.server 3000
```

## 👤 Comptes de test

Après avoir exécuté `node seed.js` :

| Rôle | Email | Mot de passe |
|------|-------|--------------|
| Admin | admin@titelli.com | Admin123! |
| Client | test@example.com | Test123! |
| Entreprise | spa.luxury@titelli.com | Demo123! |

## 🔧 Configuration

### Variables d'environnement (.env)

```env
MONGO_URL=mongodb+srv://...
DB_NAME=titelli
JWT_SECRET=votre_secret_jwt_securise
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLIC_KEY=pk_live_...
PORT=8001
```

### Configuration de l'API (frontend/js/api.js)

Par défaut, l'API pointe vers `http://localhost:8001`. 
Modifiez la variable `API_URL` si nécessaire.

## 📱 Fonctionnalités

### Pour les clients
- ✅ Inscription et connexion
- ✅ Parcourir les services et produits
- ✅ Recherche et filtres par catégorie
- ✅ Voir les profils d'entreprises
- ✅ Laisser des avis
- ✅ Système de cashback
- ✅ Historique des commandes

### Pour les entreprises
- ✅ Créer un profil entreprise
- ✅ Ajouter des services/produits
- ✅ Gérer les commandes
- ✅ Voir les avis clients
- ✅ Tableau de bord financier
- ✅ Abonnements (Standard/Premium)
- ✅ Paiement Stripe

### Pour les administrateurs
- ✅ Statistiques globales
- ✅ Gestion des utilisateurs
- ✅ Certification/Labellisation des entreprises

## 🎨 Design

- Thème sombre moderne
- Couleur primaire : Bleu (#0047AB)
- Couleur secondaire : Or (#D4AF37)
- Police : Playfair Display (titres) + Manrope (texte)

## 📄 API Endpoints

### Authentification
- `POST /api/auth/register` - Inscription
- `POST /api/auth/login` - Connexion
- `GET /api/auth/me` - Profil utilisateur

### Entreprises
- `GET /api/enterprises` - Liste des entreprises
- `GET /api/enterprises/:id` - Détails entreprise
- `POST /api/enterprises` - Créer une entreprise
- `PUT /api/enterprises/:id` - Modifier une entreprise

### Services/Produits
- `GET /api/services-products` - Liste
- `POST /api/services-products` - Créer
- `DELETE /api/services-products/:id` - Supprimer

### Catégories
- `GET /api/categories/services` - Catégories de services
- `GET /api/categories/products` - Catégories de produits

### Avis
- `GET /api/reviews/:enterprise_id` - Avis d'une entreprise
- `POST /api/reviews` - Créer un avis

### Paiements (Stripe)
- `POST /api/payments/checkout` - Créer une session de paiement
- `GET /api/payments/status/:session_id` - Statut du paiement

### Admin
- `GET /api/admin/stats` - Statistiques
- `GET /api/admin/users` - Liste des utilisateurs
- `PUT /api/admin/users/:id/verify` - Vérifier un utilisateur

## 📝 Licence

© 2024 Titelli. Tous droits réservés.
