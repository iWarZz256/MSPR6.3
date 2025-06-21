#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
predict.py

Module FastAPI pour l'inférence du modèle RandomForest pour un modèle par pays.
Expose un router prefix "/predict" avec deux paramètres :
 - nom_maladie (str, colonne nom_maladie)
 - code_lettre (str, colonne code_lettre)
Retourne la liste des totaux cumulés prédits pour chaque date.
"""
from fastapi import APIRouter, HTTPException
import joblib
import numpy as np
import pandas as pd
from training import charger_donnees, creer_features, get_engine

# Création du router pour main.py
router = APIRouter(prefix="/predict", tags=["predict"])

# Chargement du modèle global (mais entraîné sans one-hot pays)
model = joblib.load("model/RandomForest_covid.pkl")

# Préparation de l'engine pour jointures
engine = get_engine()
# Chargement statique des tables de référence
pandi_df = pd.read_sql("SELECT id_pandemie, nom_maladie FROM pandemie", con=engine)
pays_df = pd.read_sql(
    "SELECT id AS pays_id, code_lettre FROM pays",
    con=engine
)

def get_pandemie_id_by_name(nom_maladie: str) -> int:
    match = pandi_df[pandi_df["nom_maladie"].str.lower() == nom_maladie.lower()]
    if match.empty:
        raise ValueError(f"Aucune pandémie trouvée pour '{nom_maladie}'")
    return int(match.iloc[0]["id_pandemie"])

@router.get("/{nom_maladie}/{code_lettre}")
async def predict_by_name(nom_maladie: str, code_lettre: str):
    try:
        # 1. Récupérer l'ID pandémie
        pandemie_id = get_pandemie_id_by_name(nom_maladie)

        # 2. Charger et filtrer les données du pays
        df = charger_donnees(pandemie_id)
        df = (
            df.reset_index()
              .merge(pays_df, on='pays_id', how='left')
              .set_index('date_jour')
        )
        df = df[df['code_lettre'].str.lower() == code_lettre.lower()]
        if df.empty:
            raise ValueError(f"Aucun enregistrement pour le pays '{code_lettre}'")

        # 3. Génération des features spécifiques au pays
        df_feats = creer_features(df)

        # 4. Préparer X sans one-hot globale
        feature_cols = [
            c for c in df_feats.columns
            if c not in ("nouveau_cas", "nouveau_mort", "total_cas")
        ]
        X = df_feats[feature_cols].values

        # 5. Prédiction des nouveaux cas
        y_pred = model.predict(X)
        # Forcer 0 lorsque réel == 0
        real_new = df['nouveau_cas'].reindex(df_feats.index).values
        y_pred = np.where(real_new == 0, 0, y_pred)

        # 6. Calcul du total cumulé prédit
        last_total = df['total_cas'].iloc[-1]
        if last_total != 0:
            total_pred = last_total + np.cumsum(y_pred)
        else:
            total_pred = np.cumsum(y_pred)

        # 7. Préparation de la réponse
        dates = df_feats.index.strftime('%Y-%m-%d').tolist()
        results = [
            {"date": dates[i], "prediction": float(total_pred[i])}
            for i in range(len(dates))
        ]

        return {"predictions": results}

    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur interne : {e}")
