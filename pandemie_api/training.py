#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
training.py

Script d'entraînement d'un modèle RandomForest par pays.
- Génération de lags, rolling stats, indicateurs et variables cycliques
- Transformation log1p de la cible pour stabiliser la variance
- TimeSeriesSplit en cross-validation pour robustesse
- Recherche d'hyperparamètres (GridSearchCV)
- Évaluation finale sur hold-out
- Sauvegarde du meilleur modèle et des noms de features
"""
import os
import joblib
import argparse
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error

# ----------------------------------------------------------------------
def get_engine():
    """Initialise un SQLAlchemy Engine d'après le .env."""
    load_dotenv()
    uri = (
        f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST','localhost')}:{os.getenv('DB_PORT','3306')}/" 
        f"{os.getenv('DB_NAME')}"
    )
    return create_engine(uri)

# ----------------------------------------------------------------------
def charger_donnees(pandemie_id: int) -> pd.DataFrame:
    df = pd.read_sql("SELECT * FROM suivi_pandemie WHERE id_pandemie = %s",
                     con=get_engine(), params=(pandemie_id,))
    if df.empty:
        raise ValueError(f"Aucune donnée pour pandémie {pandemie_id}.")
    df["date_jour"] = pd.to_datetime(df["date_jour"])
    return df.set_index("date_jour").sort_index()

# ----------------------------------------------------------------------
def creer_features(df: pd.DataFrame, n_lags: int = 7) -> pd.DataFrame:
    feats_list = []
    for pays_id, group in df.groupby("pays_id"):
        g = (group.groupby(level=0).agg({'nouveau_cas': 'sum', 'nouveau_mort': 'sum', 'total_cas': 'max'})
                .reindex(pd.date_range(group.index.min(), group.index.max(), freq='D'), fill_value=0))
        feats = pd.DataFrame(index=g.index)
        feats[['nouveau_cas','nouveau_mort','total_cas']] = g[['nouveau_cas','nouveau_mort','total_cas']]
        # lags
        for lag in range(1, n_lags+1):
            feats[f'lag_cas_{lag}']  = feats['nouveau_cas'].shift(lag)
            feats[f'lag_mort_{lag}'] = feats['nouveau_mort'].shift(lag)
        # rolling stats
        feats['roll_mean_7'] = feats['nouveau_cas'].rolling(7).mean()
        feats['roll_std_7']  = feats['nouveau_cas'].rolling(7).std()
        # taux et mortalité
        feats['taux_croissance'] = feats['total_cas'].pct_change().fillna(0)
        feats['taux_mortalite']  = (
            feats['nouveau_mort']
            .div(feats['nouveau_cas'].replace(0, np.nan))
            .fillna(0)
        )
        # cyclique
        jours = feats.index.dayofweek
        feats['sin_jour'] = np.sin(2*np.pi*jours/7)
        feats['cos_jour'] = np.cos(2*np.pi*jours/7)
                # Nettoyage infinities et outliers négatifs
        feats = feats.replace([np.inf, -np.inf], np.nan)
        feats = feats.clip(lower=0)
        feats = feats.dropna()
        feats_list.append(feats)
    return pd.concat(feats_list).sort_index()

# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('pandemie_id', type=int)
    parser.add_argument('-l','--n_lags', type=int, default=7)
    parser.add_argument('-o','--out', type=str, default='model/')
    args = parser.parse_args()

    # données & features
    df = charger_donnees(args.pandemie_id)
    df_feats = creer_features(df, args.n_lags)
    X = df_feats.drop(columns=['nouveau_cas','nouveau_mort','total_cas']).values
    y = np.log1p(df_feats['nouveau_cas'].values)
    feature_cols = df_feats.drop(columns=['nouveau_cas','nouveau_mort','total_cas']).columns.tolist()

    # split train/test chrono
    n = len(X)
    split_idx = int(0.9*n)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    dates_test = df_feats.index[split_idx:]

    # CV time-series
    tscv = TimeSeriesSplit(n_splits=5)
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [5, 10, None],
        'min_samples_leaf': [1, 5, 10]
    }
    rf = RandomForestRegressor(random_state=42)
    grid = GridSearchCV(rf, param_grid, cv=tscv, scoring='neg_mean_absolute_error', n_jobs=-1)
    grid.fit(X_train, y_train)
    best = grid.best_estimator_
    print('Best params:', grid.best_params_)

    # prédiction & évaluation
    y_pred_log = best.predict(X_test)
    y_pred = np.clip(np.expm1(y_pred_log), 0, None)
    y_true = np.expm1(y_test)
    mae  = mean_absolute_error(y_true, y_pred)
    mse  = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mape = np.mean(np.abs((y_true - y_pred)/np.where(y_true==0,1,y_true))) *100
    print(f"MAE:{mae:.2f}|RMSE:{rmse:.2f}|MAPE:{mape:.2f}%")

    # sauvegarde
    os.makedirs(args.out, exist_ok=True)
    joblib.dump(best, os.path.join(args.out,'RandomForest_covid.pkl'))
    joblib.dump(feature_cols, os.path.join(args.out,'feature_names.pkl'))
    print('Model & features saved')

if __name__=='__main__':
    main()
