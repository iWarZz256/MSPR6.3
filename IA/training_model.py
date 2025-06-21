import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

def connexion_bdd():
    """
    Charge les variables d’environnement depuis le fichier .env et renvoie
    un DataFrame contenant l’ensemble du tableau 'suivi_pandemie'.
    """
    # Charge le fichier .env (chemin relatif possible à adapter selon votre structure)
    load_dotenv("../.env")

    # Récupère les variables d’environnement
    db_user = os.environ.get("DB_USER")
    db_pass = os.environ.get("DB_PASSWORD")
    db_host = os.environ.get("DB_HOST", "localhost")
    db_port = os.environ.get("DB_PORT", "3306")
    db_name = os.environ.get("DB_NAME")

    # Vérification des variables nécessaires
    if not all([db_user, db_pass, db_name]):
        raise RuntimeError(
            "Variables d'environnement manquantes : "
            "DB_USER, DB_PASSWORD et/ou DB_NAME."
        )

    # Création de l’engine SQLAlchemy
    engine = create_engine(
        f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    )

    # Lecture de la table complète
    df = pd.read_sql("SELECT * FROM suivi_pandemie", con=engine)

    # Affiche les 5 premières lignes pour vérifier la connexion
    print("Aperçu du DataFrame issu de la base de données :")
    print(df.head())

    return df

def cas_pays(pays_id=60):
    """
    Sélectionne les données pour un pays donné (par défaut pays_id=60),
    reconstitue la série temporelle journalière en comblant les jours manquants,
    et renvoie le DataFrame indexé par date_jour.
    """
    # Récupère toutes les données
    df = connexion_bdd()
    pays_cible = 60
    df_pays = df[df["pays_id"] == pays_cible].copy()
    df_pays["date_jour"] = pd.to_datetime(df_pays["date_jour"], format="%Y-%m-%d")
    df_pays = df_pays.set_index("date_jour").sort_index()

    # 4. S’assurer que la série est complète (1 point par jour)
    idx_complet = pd.date_range(start=df_pays.index.min(), end=df_pays.index.max(), freq="D")
    df_pays = df_pays.reindex(idx_complet)
    df_pays["nouveau_cas"] = df_pays["nouveau_cas"].fillna(0)
  

    return df_pays

def visualiser_serie(df_pays):
    """
    Affiche la série temporelle des nouveaux cas, ainsi que ses ACF et PACF.
    """
    # 1) Tracé de la série des 'nouveau_cas'
    plt.figure(figsize=(10, 4))
    plt.plot(
        df_pays.index,
        df_pays["nouveau_cas"],
        label="Nouveaux cas journaliers"
    )
    plt.title("Évolution des nouveaux cas")
    plt.xlabel("Date")
    plt.ylabel("Nombre de nouveaux cas")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # 2) Tracé de l’ACF et de la PACF
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    plot_acf(df_pays["nouveau_cas"], lags=30, ax=axes[0])
    axes[0].set_title("ACF des nouveaux cas")
    plot_pacf(df_pays["nouveau_cas"], lags=30, ax=axes[1])
    axes[1].set_title("PACF des nouveaux cas")
    plt.tight_layout()
    plt.show()

def main():
    # Exemple d’appel pour le pays d’ID 250
    df_pays = cas_pays(pays_id=60)
    # Appel de la fonction de visualisation
    visualiser_serie(df_pays)

if __name__ == "__main__":
    main()
