#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pandemie_api/predict.py

Module FastAPI pour l'inférence du modèle RandomForest par pays.
Expose l'endpoint "/predict/{maladie}/{pays}" qui retourne, pour chaque date,
la prédiction des nouveaux cas (après délog1p).  
Schema de sortie : date (YYYY-MM-DD) et predit (float)
"""
import os
import joblib
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from training import charger_donnees, creer_features, get_engine

# Router FastAPI
router = APIRouter(prefix="/predict", tags=["predict"])

# Paths
BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "model", "RandomForest_covid.pkl")
FEAT_PATH  = os.path.join(BASE_DIR, "model", "feature_names.pkl")

# Vérification
if not os.path.exists(MODEL_PATH):
    raise RuntimeError(f"Modèle introuvable à {MODEL_PATH}")
if not os.path.exists(FEAT_PATH):
    raise RuntimeError(f"Fichier feature_names introuvable à {FEAT_PATH}")

# Chargement du modèle et des noms de features
model = joblib.load(MODEL_PATH)
feature_cols = joblib.load(FEAT_PATH)

# Schéma de sortie
class Prediction(BaseModel):
    date: str
    predit: float

# Helpers pour récupérer les IDs
def get_pandemie_id(nom_maladie: str) -> int:
    df = pd.read_sql(
        "SELECT id_pandemie FROM pandemie WHERE nom_maladie = %s",
        con=get_engine(), params=(nom_maladie,)
    )
    if df.empty:
        raise HTTPException(status_code=404, detail=f"Pandémie '{nom_maladie}' inconnue")
    return int(df.iloc[0]["id_pandemie"])

def get_pays_id(code_lettre: str) -> int:
    df = pd.read_sql(
        "SELECT id FROM pays WHERE code_lettre = %s",
        con=get_engine(), params=(code_lettre.upper(),)
    )
    if df.empty:
        raise HTTPException(status_code=404, detail=f"Pays '{code_lettre}' inconnu")
    return int(df.iloc[0]["id"])

@router.get("/{maladie}/{pays}", response_model=List[Prediction])
def predict_by_name(maladie: str, pays: str):
    # 1. Traduction des noms en IDs
    pandemi_id = get_pandemie_id(maladie)
    pays_id    = get_pays_id(pays)

    # 2. Chargement des données brutes
    try:
        df_raw = charger_donnees(pandemi_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # 3. Filtrage par pays
    df = (
        df_raw.reset_index()
              .query("pays_id == @pays_id")
              .set_index("date_jour")
    )
    if df.empty:
        raise HTTPException(status_code=404, detail=f"Aucun enregistrement pour pays '{pays}'")

    # 4. Génération des features
    df_feats = creer_features(df)

    # 5. Préparation de X uniquement avec les features du pays
    try:
        X_df = df_feats[feature_cols]
    except KeyError as ke:
        raise HTTPException(status_code=500, detail=f"Feature manquante: {ke}")
    X = X_df.values

    # 6. Prédiction (sur échelle log1p)
    y_pred_log = model.predict(X)
    # inversion log1p + clamp
    y_pred = np.clip(np.expm1(y_pred_log), 0, None)

    # 7. Construction de la réponse en cumulant les prédictions de nouveaux cas
    dates = X_df.index.strftime('%Y-%m-%d').tolist()
    results = []
    running_total = 0.0
    for i, pred in enumerate(y_pred):
        if i == 0:
            running_total = pred
        else:
            running_total += pred
        results.append(Prediction(date=dates[i], predit=float(running_total)))

    return results
