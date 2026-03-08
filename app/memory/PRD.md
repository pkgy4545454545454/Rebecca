# Titelli - Product Requirements Document

## Original Problem Statement
Titelli est une plateforme suisse de mise en relation entre clients et prestataires de qualité dans la région de Lausanne. L'application permet aux clients de découvrir, réserver et acheter des services et produits locaux, tandis que les entreprises peuvent développer leur visibilité et leur clientèle.

## Core Requirements
- Marketplace de services et produits locaux
- Système d'inscription et gestion des entreprises
- Réservation en ligne et paiement sécurisé
- Programme cashback pour les clients
- Certification Titelli pour les entreprises
- Offres d'emploi et formations

## Tech Stack
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Image Storage**: Cloudinary (migration effectuée)
- **Deployment**: Render

---

## CHANGELOG

### 2025-02-23 - UI/UX Améliorations
- ✅ **Section Avantages homepage** : Redesignée avec style popup (icônes, titres, descriptions, prix)
- ✅ **Boutons conditionnels** : "Réserver" pour services, "Ajouter au panier" pour produits

### 2025-02-22 - Migration Cloudinary & Features
- ✅ **Migration Cloudinary** : Toutes les images migrées vers Cloudinary (permanent storage)
- ✅ **Section "Les meilleurs produits"** : Ajoutée sur homepage
- ✅ **Page Cashback** : Créée et liée dans header
- ✅ **Popup Enterprise Benefits** : Multi-onglets avec services, fournisseurs, gestion, marketing, packs
- ✅ **3 PDFs générés** : Prospect_Rendez-vous_Client.pdf, Prospect_Telephonique.pdf, Questions_Formations.pdf
- ✅ **Filter tags** : Style text-only sans fond sur toutes les pages

---

## ROADMAP

### P0 - Critique (Résolu)
- ✅ Images Render corrigées via Cloudinary

### P1 - Haute Priorité
- [ ] Réorganiser produits homepage (priorité noms commençant par "t")
- [ ] Investiguer corruption d'images lors de l'upload

### P2 - Moyenne Priorité
- [ ] Corriger design brochure de monétisation
- [ ] Redesigner profils prestataires selon croquis utilisateur
- [ ] Créer flyer marketing avec QR code personnalisé

### P3 - Basse Priorité
- [ ] Démontrer fonctionnalité multi-tags
- [ ] Créer document CDC final
- [ ] Implémenter essai gratuit IA

---

## Key Files
- `/app/frontend/src/pages/HomePage.js` - Page d'accueil avec sections avantages
- `/app/frontend/src/components/ServiceProductCard.js` - Carte avec logique bouton conditionnel
- `/app/frontend/src/pages/EnterpriseRegistrationPage.js` - Inscription entreprise avec popup avantages
- `/app/backend/.env` - Credentials Cloudinary
- `/app/backend/migrate_to_cloudinary.py` - Script migration images
