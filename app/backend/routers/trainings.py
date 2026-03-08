"""
Trainings Router - Gestion des formations
"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone

router = APIRouter(prefix="/trainings", tags=["trainings"])

# Note: Ces endpoints sont actuellement dans server.py
# Ce fichier montre la structure cible du refactoring

"""
Endpoints à migrer depuis server.py:

PUBLIC:
- GET /trainings - Liste toutes les formations
- GET /trainings/{training_id} - Détail d'une formation
- GET /trainings/{training_id}/reviews - Avis sur une formation

ENTERPRISE:
- GET /enterprise/trainings - Formations de l'entreprise
- POST /enterprise/trainings - Créer une formation
- PUT /enterprise/trainings/{training_id} - Modifier une formation
- DELETE /enterprise/trainings/{training_id} - Supprimer une formation

CLIENT:
- POST /trainings/{training_id}/purchase - Acheter une formation
- POST /trainings/{training_id}/enroll - S'inscrire (formation gratuite)
- GET /client/trainings - Formations du client
- PUT /client/trainings/{enrollment_id}/complete - Marquer comme terminé
- POST /trainings/{training_id}/review - Laisser un avis
"""
