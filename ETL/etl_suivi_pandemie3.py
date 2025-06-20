# etl_suivi_pandemie3.py
import pandas as pd
import pymysql
import argparse
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Configuration des logs
def creation_logs():
    log_dir = "log"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "etl.log")
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

# Compte les valeurs nulles et doublons dans le DataFrame et les log
def count_nulls_and_duplicates(df):
    nulls = df.isnull().sum()
    duplicates = df.duplicated().sum()
    logging.info("Valeurs nulles par colonne :\n%s", nulls)
    logging.info("Nombre de doublons : %d", duplicates)

def connexion_bbd():
    # Charge le fichier .env 
    load_dotenv("../.env")
    # Connexion à la bdd
    try:
        conn = pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        logging.info("Connexion à la base de données réussie")
        return conn
    except Exception as e:
        logging.error("Erreur de connexion à la base de données : %s", e)
        return None
    
# Charge les correspondances pays depuis la base de données
def recup_pays_bdd():
    conn = None
    cursor = None
    try:
        conn = connexion_bbd()
        logging.info("Connexion à la base de données réussie")

        cursor = conn.cursor()
        cursor.execute("SELECT nom, id FROM pays")
        rows = cursor.fetchall()
        mapping = {nom: id_ for nom, id_ in rows}
        logging.info(f"Mapping chargé : {mapping}")
        return mapping
    except Exception as e:
        logging.error(f"Erreur lors du chargement des pays : {e}")
        return {}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Transforme les données : renommage, nettoyage, mapping pays, format date
def transformation_data(df, country_mapping):
    df = df.rename(columns={
        'pays': 'nom_pays',
        'date': 'date_jour',
        'total_cases': 'total_cas',
        'total_deaths': 'total_mort',
        'new_cases': 'nouveau_cas',
        'new_deaths': 'nouveau_mort'
    })

    df = df.drop_duplicates()
    df.columns = [col.lower().strip() for col in df.columns]

    num_cols = df.select_dtypes(include=["number"]).columns
    for col in num_cols:
        if df[col].isnull().any():
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
            logging.info(f"Valeurs nulles dans '{col}' remplacées par la médiane {median_val}")

    for col in num_cols:
        negative_count = (df[col] < 0).sum()
        if negative_count > 0:
            logging.info(
                "%d valeurs négatives détectées dans '%s' ➜ conversion en positif", negative_count, col
            )
            df[col] = df[col].abs()
    df['pays_id'] = df['nom_pays'].map(country_mapping)
    df = df.dropna(subset=['pays_id'])
    df['pays_id'] = df['pays_id'].astype(int)
    df['date_jour'] = pd.to_datetime(df['date_jour']).dt.date

    return df


# Insère une pandémie dans la table `pandemie` et retourne l'id généré
def insert_pandemie(df, virus_id, nom_maladie):
    try:
        conn  = connexion_bbd()
        cursor = conn.cursor()

        date_debut = df['date_jour'].min()
        date_fin = df['date_jour'].max()

        cursor.execute("""
            INSERT INTO pandemie (virus_id, nom_maladie, date_apparition, date_fin)
            VALUES (%s, %s, %s, %s)
        """, (virus_id, nom_maladie, date_debut, date_fin))
        conn.commit()

        id_pandemie = cursor.lastrowid
        logging.info(f"Pandémie insérée avec ID {id_pandemie}, maladie : {nom_maladie}, virus ID : {virus_id}, début : {date_debut}, fin : {date_fin}")
        return id_pandemie
    except Exception as e:
        logging.error(f"Erreur lors de l'insertion dans pandemie : {e}")
        return None
    finally:
        cursor.close()
        conn.close()

# Insère les données dans suivi_pandemie et log l'insertion
def insert_to_db(df, id_pandemie, description):
    conn = connexion_bbd()
    cursor = conn.cursor()
    try:
        now = datetime.now()
        cursor.execute("INSERT INTO logging_insert (date_insertion, description) VALUES (%s, %s)", (now, description))
        conn.commit()
        id_logging = cursor.lastrowid

        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO suivi_pandemie (id_logging, id_pandemie, pays_id, date_jour,total_cas, total_mort,nouveau_cas, nouveau_mort) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                id_logging, 
                id_pandemie,
                row['pays_id'], 
                row['date_jour'],
                row['total_cas'], 
                row['total_mort'],
                row['nouveau_cas'], 
                row['nouveau_mort'] 
            ))
        conn.commit()
        logging.info(f"{len(df)} lignes insérées dans suivi_pandemie avec id_logging = {id_logging} et description = '{description}'")
    except Exception as e:
        logging.error(f"Erreur MySQL : {e}")
    finally:
        cursor.close()
        conn.close()

# Fonction principale mise à jour
def main():
    creation_logs()

    parser = argparse.ArgumentParser(description="ETL vers suivi_pandemie")
    parser.add_argument("--input_file", required=True, help="Chemin du fichier CSV de données brutes")
    parser.add_argument("--virus_id", type=int, required=True, help="ID du virus à insérer dans la table pandemie")
    parser.add_argument("--nom_maladie", required=True, help="Nom de la maladie pour la table pandemie")
    parser.add_argument("--description", required=False, help="Description pour la table logging_insert")
    args = parser.parse_args()

    logging.info("Début du pipeline ETL")
    df = pd.read_csv(args.input_file)

    count_nulls_and_duplicates(df)
    country_mapping = recup_pays_bdd()
    clean_df = transformation_data(df, country_mapping)

    id_pandemie = insert_pandemie(clean_df, args.virus_id, args.nom_maladie)
    if id_pandemie:
        insert_to_db(clean_df, id_pandemie, args.description)

    logging.info("Pipeline ETL terminé")

if __name__ == "__main__":
    main()
