import os
import numpy as np
import pandas as pd
import joblib
from sqlalchemy import create_engine
from dotenv import load_dotenv

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import ExtraTreesRegressor

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Import supplémentaires pour les modèles sklearn étendus
from sklearn.ensemble import GradientBoostingRegressor, AdaBoostRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsRegressor


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """
    Calcule MAE, RMSE (via sqrt de MSE) et R² entre y_true et y_pred.
    """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    # Calcul manuel du R²
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0
    return {"MAE": mae, "RMSE": rmse, "R2": r2}


def get_engine():
    """
    Renvoie un objet SQLAlchemy Engine basé sur les variables d'environnement.
    """
    load_dotenv("../.env")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME")

    if not all([db_user, db_pass, db_name]):
        raise RuntimeError("Variables d'environnement manquantes !")
    return create_engine(
        f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    )


def charger_donnees(pandemie_id: int, pays_id: int) -> pd.DataFrame:
    """
    Charge depuis la table `suivi_pandemie` les enregistrements pour (pandemie_id, pays_id),
    réindexe journalier, imputations des NaN, et retourne un DataFrame indexé par date_jour.
    """
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM suivi_pandemie", con=engine)

    df_filt = df[
        (df["id_pandemie"] == pandemie_id) & (df["pays_id"] == pays_id)
    ].copy()

    if df_filt.empty:
        raise ValueError(f"Aucune donnée pour pandemie_id={pandemie_id} et pays_id={pays_id}")

    df_filt["date_jour"] = pd.to_datetime(df_filt["date_jour"])
    df_filt = df_filt.set_index("date_jour").sort_index()

    idx_complet = pd.date_range(
        start=df_filt.index.min(), end=df_filt.index.max(), freq="D"
    )
    df_pand = df_filt.reindex(idx_complet)

    df_pand["nouveau_cas"] = df_pand["nouveau_cas"].fillna(0)
    df_pand["nouveau_mort"] = df_pand["nouveau_mort"].fillna(0)
    df_pand["nouvelle_guerison"] = df_pand["nouvelle_guerison"].fillna(0)

    df_pand["total_cas"] = df_pand["total_cas"].ffill().fillna(0)
    df_pand["total_mort"] = df_pand["total_mort"].ffill().fillna(0)
    df_pand["guerison"] = df_pand["guerison"].ffill().fillna(0)

    return df_pand


def creer_features(df: pd.DataFrame, n_lags: int = 7) -> (np.ndarray, np.ndarray, pd.DataFrame):
    """
    À partir du DataFrame indexé sur date (contenant au moins :
    total_cas, total_mort, guerison, nouveau_cas, nouveau_mort, nouvelle_guerison),
    crée :
      - n_lags lags sur `nouveau_cas` et `nouveau_mort`
      - indicateurs dérivés :
          * taux_croissance_cas   = (total_cas_t - total_cas_{t-1}) / total_cas_{t-1}
          * taux_mortalite_jour   = nouveau_mort / max(nouveau_cas, 1)
      - variables temporelles cycliques (sin_jour, cos_jour)

    Renvoie :
    ----------
    - X (np.ndarray)      : matrice de features (N_obs × n_features)
    - y (np.ndarray)      : vecteur cible (nouveau_cas) (taille N_obs)
    - df_feats (pd.DataFrame) : DataFrame complet des features (indexé par date)

    Notes :
    ------
    - On remplace systématiquement les inf et -inf par np.nan, puis on supprime les lignes
      qui contiennent encore des NaN (issues des lags ou des divisions par zéro).
    """
    df_feats = pd.DataFrame(index=df.index)

    # 1. Copier les colonnes de base
    df_feats["nouveau_cas"] = df["nouveau_cas"]
    df_feats["nouveau_mort"] = df["nouveau_mort"]
    df_feats["total_cas"] = df["total_cas"]

    # 2. Lags sur nouveau_cas et nouveau_mort
    for lag in range(1, n_lags + 1):
        df_feats[f"lag_cas_{lag}"] = df_feats["nouveau_cas"].shift(lag)
        df_feats[f"lag_mort_{lag}"] = df_feats["nouveau_mort"].shift(lag)

    # 3. Indicateurs dérivés
    df_feats["taux_croissance_cas"] = df_feats["total_cas"].pct_change()
    df_feats["taux_mortalite_jour"] = df_feats["nouveau_mort"] / df_feats["nouveau_cas"].replace(0, np.nan)

    # 4. Variables temporelles cycliques (jour de la semaine)
    df_feats["jour_semaine"] = df_feats.index.dayofweek
    df_feats["sin_jour"] = np.sin(2 * np.pi * df_feats["jour_semaine"] / 7)
    df_feats["cos_jour"] = np.cos(2 * np.pi * df_feats["jour_semaine"] / 7)

    # 5. Remplacement des inf, -inf par NaN, puis suppression des NaN
    df_feats.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_feats.dropna(inplace=True)

    # 6. Construction de X et y
    X = df_feats.drop(columns=["nouveau_cas", "nouveau_mort", "total_cas", "jour_semaine"]).values
    y = df_feats["nouveau_cas"].values

    return X, y, df_feats


def evaluer_modele(model, X: np.ndarray, y: np.ndarray) -> dict:
    """
    Calcule MAE, RMSE (via sqrt de MSE) et R² sur (X, y) pour un modèle sklearn-like.
    """
    y_pred = model.predict(X)
    return compute_metrics(y, y_pred)


def benchmark_models(
    pandemie_id: int, pays_id: int, n_lags: int = 7, modele_list: list = None
) -> pd.DataFrame:
    """
    Pour un (pandemie_id, pays_id) donné, compare plusieurs modèles sklearn :
      - RandomForest, XGBoost, LinearRegression, DecisionTree, ExtraTrees,
        GradientBoosting, AdaBoost, KNN, Ridge, Lasso, SVR.

    Renvoie un DataFrame avec les métriques (MAE, RMSE, R2) pour
    train / validation / test.
    """
    if modele_list is None:
        modele_list = ["RandomForest", "XGBoost", "LinearRegression"]

    # 1) Charger les données et dériver les features
    df_pand = charger_donnees(pandemie_id, pays_id)
    X, y, df_feats = creer_features(df_pand, n_lags=n_lags)

    # 2) Découpage temporel (75% train, 15% validation, 10% test)
    n = len(X)
    idx_train_end = int(0.75 * n)
    idx_val_end = int(0.90 * n)

    results = []

    for modele_type in modele_list:
        # --- 1) Pour les modèles sklearn “non séquentiels” (features multivariées) ---
        if modele_type in [
            "RandomForest",
            "XGBoost",
            "LinearRegression",
            "DecisionTree",
            "ExtraTrees",
            "GradientBoost",
            "AdaBoost",
            "Ridge",
            "Lasso",
            "SVR",
        ]:
            # 1.1) Découpage de X et y
            X_train, y_train = X[:idx_train_end], y[:idx_train_end]
            X_val, y_val = X[idx_train_end:idx_val_end], y[idx_train_end:idx_val_end]
            X_test, y_test = X[idx_val_end:], y[idx_val_end:]

            # 1.2) Si le modèle est sensible à l'échelle, standardiser
            if modele_type in ["Ridge", "Lasso", "SVR"]:
                scaler = StandardScaler()
                X_train = scaler.fit_transform(X_train)
                X_val = scaler.transform(X_val)
                X_test = scaler.transform(X_test)

            # 1.3) Instanciation du modèle
            if modele_type == "RandomForest":
                model = RandomForestRegressor(n_estimators=100, random_state=42)
            elif modele_type == "XGBoost":
                model = XGBRegressor(
                    n_estimators=200,
                    learning_rate=0.1,
                    random_state=42,
                    objective="reg:squarederror",
                )
            elif modele_type == "LinearRegression":
                model = LinearRegression()
            elif modele_type == "DecisionTree":
                model = DecisionTreeRegressor(random_state=42)
            elif modele_type == "ExtraTrees":
                model = ExtraTreesRegressor(n_estimators=100, random_state=42)
            elif modele_type == "GradientBoost":
                model = GradientBoostingRegressor(
                    n_estimators=100, learning_rate=0.1, random_state=42
                )
            elif modele_type == "AdaBoost":
                model = AdaBoostRegressor(
                    n_estimators=100, learning_rate=0.1, random_state=42
                )
            elif modele_type == "Ridge":
                model = Ridge(alpha=1.0)
            elif modele_type == "Lasso":
                model = Lasso(alpha=0.1)
            elif modele_type == "SVR":
                model = SVR(kernel="rbf", C=1.0, epsilon=0.1)
            else:
                raise ValueError(f"Impossible de gérer {modele_type} dans cette branche.")

            # 1.4) Entraînement et prédictions
            model.fit(X_train, y_train)
            pred_train = model.predict(X_train)
            pred_val = model.predict(X_val)
            pred_test = model.predict(X_test)

            # 1.5) Calcul des métriques pour chaque phase
            metrics_train = compute_metrics(y_train, pred_train)
            metrics_val = compute_metrics(y_val, pred_val)
            metrics_test = compute_metrics(y_test, pred_test)

            # 1.6) Stocker les résultats
            for phase, m in zip(
                ["train", "validation", "test"], [metrics_train, metrics_val, metrics_test]
            ):
                results.append(
                    {
                        "modele": modele_type,
                        "phase": phase,
                        "MAE": m["MAE"],
                        "RMSE": m["RMSE"],
                        "R2": m["R2"],
                    }
                )

        # --- 2) Pour KNeighborsRegressor (exemple avec Pipeline) ---
        elif modele_type == "KNN":
            # 2.1) Découpage
            X_train, y_train = X[:idx_train_end], y[:idx_train_end]
            X_val, y_val = X[idx_train_end:idx_val_end], y[idx_train_end:idx_val_end]
            X_test, y_test = X[idx_val_end:], y[idx_val_end:]

            # 2.2) Pipeline : standardisation + KNN
            pipeline_knn = Pipeline(
                [
                    ("scaler", StandardScaler()),
                    ("knn", KNeighborsRegressor(n_neighbors=5)),
                ]
            )

            # 2.3) Entraînement
            pipeline_knn.fit(X_train, y_train)

            # 2.4) Prédictions
            pred_train = pipeline_knn.predict(X_train)
            pred_val = pipeline_knn.predict(X_val)
            pred_test = pipeline_knn.predict(X_test)

            # 2.5) Calcul des métriques
            metrics_train = compute_metrics(y_train, pred_train)
            metrics_val = compute_metrics(y_val, pred_val)
            metrics_test = compute_metrics(y_test, pred_test)

            # 2.6) Stocker les résultats
            for phase, m in zip(
                ["train", "validation", "test"], [metrics_train, metrics_val, metrics_test]
            ):
                results.append(
                    {
                        "modele": modele_type,
                        "phase": phase,
                        "MAE": m["MAE"],
                        "RMSE": m["RMSE"],
                        "R2": m["R2"],
                    }
                )

        else:
            raise ValueError(f"Modèle non reconnu : {modele_type}")

    # Fin de la boucle sur modele_type
    df_results = pd.DataFrame(results, columns=["modele", "phase", "MAE", "RMSE", "R2"])
    return df_results


# ===================================================================
# Bloc principal : exécution en ligne de commande
# ===================================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Benchmark : plusieurs modèles sklearn "
        "sur données de pandémie (id_pandemie, pays_id)."
    )
    parser.add_argument("pandemie_id", type=int, help="ID de la pandémie (ex. 1, 2, ...)")
    parser.add_argument("pays_id", type=int, help="ID du pays (ex. 33, 44, ...)")
    parser.add_argument(
        "--n_lags",
        "-l",
        type=int,
        default=7,
        help="Nombre de lags à créer (par défaut 7).",
    )
    parser.add_argument(
        "--modeles",
        "-m",
        nargs="+",
        choices=[
            "RandomForest",
            "XGBoost",
            "LinearRegression",
            "DecisionTree",
            "ExtraTrees",
            "GradientBoost",
            "AdaBoost",
            "KNN",
            "Ridge",
            "Lasso",
            "SVR",
        ],
        default=["RandomForest", "XGBoost", "LinearRegression"],
        help="Liste des modèles sklearn à comparer.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="benchmark_results.csv",
        help="Chemin du fichier CSV dans lequel append les résultats.",
    )

    args = parser.parse_args()
    pid = args.pandemie_id
    cid = args.pays_id
    lags = args.n_lags
    modeles = args.modeles
    output_csv = args.output

    print(f">>> Lancement du benchmark pour pandemie_id={pid}, pays_id={cid}")
    print(f"    - modèles testés : {modeles}")
    print(f"    - nombre de lags   : {lags}")
    print(f"    - fichier output   : {output_csv}")

    # 1) Exécuter le benchmark
    df_bench = benchmark_models(pandemie_id=pid, pays_id=cid, n_lags=lags, modele_list=modeles)

    # 2) Récupérer le nom du pays depuis la table `pays`
    engine = get_engine()
    query = f"SELECT nom FROM pays WHERE id = {cid}"
    df_pays = pd.read_sql(query, con=engine)
    if df_pays.empty:
        nom_pays = "<inconnu>"
    else:
        nom_pays = df_pays["nom"].iloc[0]

    # 3) Ajouter les colonnes `pays_id` et `nom_pays` dans df_bench
    df_bench["pays_id"] = cid
    df_bench["nom_pays"] = nom_pays

    # 4) Enregistrer en mode append (si le fichier existe) ou write (sinon)
    if os.path.isfile(output_csv):
        df_bench.to_csv(output_csv, mode="a", header=False, index=False)
        print(f"Résultats ajoutés à la fin de {output_csv}")
    else:
        df_bench.to_csv(output_csv, mode="w", header=True, index=False)
        print(f"Fichier créé : {output_csv}")

    # 5) Afficher les résultats à l’écran
    print("\n=== Résultats du benchmark (affichage) ===")
    print(df_bench)
