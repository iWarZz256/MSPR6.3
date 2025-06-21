#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
entrainement.py

Script d'entraînement amélioré d'un modèle RandomForest pour la pandémie.
Supporte l'entraînement global (tous les pays) avec feature 'pays'.
Étapes :
 1. Chargement des données depuis MySQL
 2. Création des features (lags, indicateurs, saisonnalité, encodage pays)
 3. Entraînement du modèle RandomForest
 4. Sauvegarde du pipeline dans model/
"""

import os
import joblib
import argparse
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestRegressor

# ----------------------------------------------------------------------
def get_engine():
    """
    Initialise et retourne un SQLAlchemy Engine d'après le fichier .env.
    """
    load_dotenv()
    user = os.getenv("DB_USER")
    pwd  = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    name = os.getenv("DB_NAME")
    if not all([user, pwd, name]):
        raise RuntimeError("Variables d'environnement DB_USER/DB_PASSWORD/DB_NAME manquantes.")
    uri = f"mysql+mysqlconnector://{user}:{pwd}@{host}:{port}/{name}"
    return create_engine(uri)

# ----------------------------------------------------------------------
def charger_donnees(pandemie_id: int) -> pd.DataFrame:
    """
    Charge la table `suivi_pandemie`, filtre sur `id_pandemie`,
    et renvoie un DataFrame global indexé par date_jour.
    """
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM suivi_pandemie", con=engine)
    df = df[df["id_pandemie"] == pandemie_id].copy()
    if df.empty:
        raise ValueError(f"Aucune donnée pour pandémie {pandemie_id}.")
    df["date_jour"] = pd.to_datetime(df["date_jour"])
    df = df.set_index("date_jour").sort_index()
    return df

# ----------------------------------------------------------------------
def creer_features(df: pd.DataFrame, n_lags: int = 7):
    """
    Génère lags, indicateurs, variables cycliques et feature 'pays'.
    Renvoie X (np.array), y (np.array), df_feats (DataFrame).
    """
    feats_list = []
    # Traiter chaque pays séparément
    for pays_id, group in df.groupby("pays_id"):
        # Copier et agréger les cas où plusieurs lignes ont même date
        g = group.copy()
        g = g.groupby(level=0).agg({
            'nouveau_cas': 'sum',
            'nouveau_mort': 'sum',
            'total_cas': 'max'
        })
        # Reconstitution des dates manquantes
        idx = pd.date_range(g.index.min(), g.index.max(), freq="D")
        g = g.reindex(idx)
        # Imputations
        g['nouveau_cas']  = g['nouveau_cas'].fillna(0)
        g['nouveau_mort'] = g['nouveau_mort'].fillna(0)
        g['total_cas']    = g['total_cas'].ffill().fillna(0)
        # Création des features
        feats = pd.DataFrame(index=g.index)
        feats['nouveau_cas']  = g['nouveau_cas']
        feats['nouveau_mort'] = g['nouveau_mort']
        feats['total_cas']    = g['total_cas']
        # Lags
        for lag in range(1, n_lags + 1):
            feats[f'lag_cas_{lag}']  = feats['nouveau_cas'].shift(lag)
            feats[f'lag_mort_{lag}'] = feats['nouveau_mort'].shift(lag)
        # Indicateurs
        feats['taux_croissance'] = feats['total_cas'].pct_change()
        feats['taux_mortalite']  = feats['nouveau_mort'] / feats['nouveau_cas'].replace(0, np.nan)
        # Variables cycliques (jour de la semaine)
        jours = feats.index.dayofweek
        feats['sin_jour'] = np.sin(2 * np.pi * jours / 7)
        feats['cos_jour'] = np.cos(2 * np.pi * jours / 7)
        # Ajout de la feature 'pays'
        feats['pays_id'] = pays_id
        # Nettoyage
        feats.replace([np.inf, -np.inf], np.nan, inplace=True)
        feats.dropna(inplace=True)
        feats_list.append(feats)
    # Union de tous les pays
    df_feats = pd.concat(feats_list)
    # Encodage one-hot de 'pays_id'
    df_feats = pd.get_dummies(df_feats, columns=['pays_id'], prefix='pays')
    # Séparation X / y
    y = df_feats['nouveau_cas'].values
    X = df_feats.drop(columns=['nouveau_cas', 'nouveau_mort', 'total_cas']).values
    return X, y, df_feats

# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Entraîne un RandomForest global sur tous les pays pour une pandémie donnée."
    )
    parser.add_argument(
        "pandemie_id",
        type=int,
        help="ID de la pandémie (ex. 1)"
    )
    parser.add_argument(
        "--n_lags", "-l",
        type=int,
        default=7,
        help="Nombre de lags à utiliser (défaut : 7)"
    )
    parser.add_argument(
        "--out", "-o",
        type=str,
        default="model",
        help="Répertoire de sortie (défaut : model/)"
    )
    args = parser.parse_args()

    # 1. Chargement et préparation (tous pays)
    df = charger_donnees(args.pandemie_id)
    X, y, df_feats = creer_features(df, args.n_lags)

    # 2. Séparation train (90%)
    split = int(0.9 * len(X))
    X_train, y_train = X[:split], y[:split]

    # 3. Entraînement du RandomForest
    print(f">>> Entraînement RandomForest sur {len(X_train)} échantillons...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # 4. Sauvegarde
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, "RandomForest_global.pkl")
    joblib.dump(model, path)
    print(f"✅ Modèle sauvegardé dans : {path}")

if __name__ == "__main__":
    main()
