#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
train/analyse_performance.py

Script d'analyse de performance pour le modèle RandomForest.
Mesure les métriques MAE, RMSE, R2 et trace les résidus ainsi que les valeurs prédites vs réelles.
"""
import argparse
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Importer fonctions depuis training.py (adapter le chemin si nécessaire)
from pandemie_api.training import charger_donnees, creer_features

# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Analyse la performance du modèle RandomForest sur un jeu de données donné."
    )
    parser.add_argument(
        "model_path",
        type=str,
        help="Chemin vers le fichier du modèle (joblib .pkl)"
    )
    parser.add_argument(
        "pandemie_id",
        type=int,
        help="ID de la pandémie (ex. 1)"
    )
    parser.add_argument(
        "pays_id",
        type=int,
        help="ID du pays à tester (ex. 60), ou 0 pour global"
    )
    parser.add_argument(
        "--n_lags", "-l",
        type=int,
        default=7,
        help="Nombre de lags à utiliser (défaut : 7)"
    )
    args = parser.parse_args()

    # 1) Charger toutes les données et générer les features globales
    df_global = charger_donnees(args.pandemie_id)
    X_full, y_full, df_feats_full = creer_features(df_global, n_lags=args.n_lags)

    # 2) Filtrer si nécessaire pour un pays spécifique
    if args.pays_id == 0:
        X, y, df_feats = X_full, y_full, df_feats_full
    else:
        col_pays = f"pays_{args.pays_id}"
        if col_pays not in df_feats_full.columns:
            raise ValueError(f"La feature '{col_pays}' n'existe pas dans les données générées.")
        mask = df_feats_full[col_pays] == 1
        X = X_full[mask]
        y = y_full[mask]
        df_feats = df_feats_full.loc[mask]

    # 3) Charger le modèle
    model_file = Path(args.model_path)
    if not model_file.exists():
        project_root = Path(__file__).parent.parent
        candidate = project_root / args.model_path
        if candidate.exists():
            model_file = candidate
    if not model_file.exists():
        raise FileNotFoundError(f"Modèle non trouvé : {model_file}")
    print(f"Chargement du modèle depuis : {model_file}")
    model = joblib.load(model_file)

    # 4) Prédictions
    y_pred = model.predict(X)

    # 5) Calcul des métriques
    mae = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    r2 = r2_score(y, y_pred)
    print(f"MAE : {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"R2  : {r2:.3f}")

    # 6) Tracé
    plt.figure(figsize=(12, 5))

    # Résidus\    
    plt.subplot(1, 2, 1)
    plt.scatter(df_feats.index, y_pred - y, s=10)
    plt.axhline(0, color='black', linewidth=1)
    plt.title('Résidus (prédiction – réel)')
    plt.xlabel('Date')
    plt.ylabel('Résidu')

    # Préd vs réel
    plt.subplot(1, 2, 2)
    plt.plot(df_feats.index, y, label='Réel')
    plt.plot(df_feats.index, y_pred, label='Prédit', alpha=0.7)
    plt.title('Prédictions vs Réelles')
    plt.xlabel('Date')
    plt.ylabel('Nombre nouveaux cas')
    plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
