from collections import defaultdict
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
import models, schemas

# ----- Continent -----
def get_continents(db: Session):
    return db.query(models.Continent).all()

def create_continent(db: Session, continent: schemas.ContinentCreate):
    db_continent = models.Continent(**continent.dict())
    db.add(db_continent)
    db.commit()
    db.refresh(db_continent)
    return db_continent

# ----- Pays -----
def get_pays(db: Session):
    return db.query(models.Pays).all()

def create_pays(db: Session, pays: schemas.PaysCreate):
    db_pays = models.Pays(**pays.dict())
    db.add(db_pays)
    db.commit()
    db.refresh(db_pays)
    return db_pays

# ----- Famille -----
def get_familles(db: Session):
    return db.query(models.Famille).all()

def create_famille(db: Session, famille: schemas.FamilleCreate):
    db_famille = models.Famille(**famille.dict())
    db.add(db_famille)
    db.commit()
    db.refresh(db_famille)
    return db_famille

# ----- Virus -----
def get_virus(db: Session):
    return db.query(models.Virus).all()

def create_virus(db: Session, virus: schemas.VirusCreate):
    db_virus = models.Virus(**virus.dict())
    db.add(db_virus)
    db.commit()
    db.refresh(db_virus)
    return db_virus

# ----- LoggingInsert -----
def get_logs(db: Session):
    return db.query(models.LoggingInsert).all()

def create_log(db: Session, log: schemas.LoggingInsertCreate):
    db_log = models.LoggingInsert(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# ----- Pandemie -----
def get_pandemies(db: Session):
    return db.query(models.Pandemie).all()

def create_pandemie(db: Session, pandemie: schemas.PandemieCreate):
    db_pandemie = models.Pandemie(**pandemie.dict())
    db.add(db_pandemie)
    db.commit()
    db.refresh(db_pandemie)
    return db_pandemie

# ----- SuiviPandemie -----


def create_suivi(db: Session, suivi: schemas.SuiviPandemieCreate):
    db_suivi = models.SuiviPandemie(**suivi.dict())
    db.add(db_suivi)
    db.commit()
    db.refresh(db_suivi)
    return db_suivi

def get_last_suivi_by_pays(db: Session):
    # pays_isos = {p: p.code_lettre for p in db.query(models.Pays).all()}
    pays_isos = {p.id: p.code_lettre for p in db.query(models.Pays).all()}  # <-- correction ici
    # pandemie_noms = {p.id_pandemie: p.nom_maladie for p in db.query(models.Pandemie).all()}
    pandemie_noms = {p.id_pandemie: p.nom_maladie for p in db.query(models.Pandemie).all()}  # <-- ici
    subquery = (
        db.query(
            models.SuiviPandemie.pays_id,
            func.max(models.SuiviPandemie.date_jour).label("max_date")
        )
        .group_by(models.SuiviPandemie.pays_id)
        .subquery()
    )
    suivis = db.query(models.SuiviPandemie).join(
        subquery,
        (models.SuiviPandemie.pays_id == subquery.c.pays_id) &
        (models.SuiviPandemie.date_jour == subquery.c.max_date)
    ).all()
    result = []
    for suivi in suivis:
        suivi_dict = suivi.__dict__.copy()
        suivi_dict["pays_iso"] = pays_isos.get(suivi.pays_id, "UNK")
        suivi_dict["pandemie"] = pandemie_noms.get(suivi.id_pandemie, "Inconnue")  # <-- ici
        suivi_dict.pop("pays_id", None)
        suivi_dict.pop("id_pandemie", None)  # <-- ici
        result.append(suivi_dict)
    return result

def get_last_suivi_by_continent(db: Session, pandemie_nom: str = None):
    # Préparer les correspondances
    pays_continents = {p.id: p.continent_id for p in db.query(models.Pays).all()}
    continents = {c.id: c.nom_continent for c in db.query(models.Continent).all()}
    pandemie_noms = {p.id_pandemie: p.nom_maladie for p in db.query(models.Pandemie).all()}

    # Filtrage optionnel sur la pandémie
    pandemie_query = db.query(models.Pandemie)
    if pandemie_nom:
        pandemie = pandemie_query.filter(models.Pandemie.nom_maladie == pandemie_nom).first()
        if not pandemie:
            raise HTTPException(status_code=404, detail="Pandémie non trouvée")
        pandemie_ids = [pandemie.id_pandemie]
    else:
        pandemie_ids = [p.id_pandemie for p in pandemie_query.all()]

    # Sous-requête pour le dernier jour de chaque pays
    subquery = (
        db.query(
            models.SuiviPandemie.pays_id,
            func.max(models.SuiviPandemie.date_jour).label("max_date")
        )
        .group_by(models.SuiviPandemie.pays_id)
        .subquery()
    )

    # Récupérer tous les suivis du dernier jour pour chaque pays, filtrés par pandémie si besoin
    suivis = db.query(models.SuiviPandemie).join(
        subquery,
        (models.SuiviPandemie.pays_id == subquery.c.pays_id) &
        (models.SuiviPandemie.date_jour == subquery.c.max_date)
    ).filter(models.SuiviPandemie.id_pandemie.in_(pandemie_ids)).all()

    # Initialiser les résultats par (continent, pandemie)
    result = {}
    champs = [
        "total_mort",
        "nouveau_cas",
        "nouvelle_guerison",
        "total_cas",
        "guerison",
        "nouveau_mort"
    ]

    # Agréger les données par continent et pandémie
    for suivi in suivis:
        continent_id = pays_continents.get(suivi.pays_id)
        continent_nom = continents.get(continent_id, "Inconnu")
        pandemie_nom_val = pandemie_noms.get(suivi.id_pandemie, "Inconnue")
        key = (continent_nom, pandemie_nom_val)
        if key not in result:
            result[key] = {champ: 0 for champ in champs}
        for champ in champs:
            val = getattr(suivi, champ, 0)
            if val is None:
                val = 0
            result[key][champ] += val

    # Mise en forme de la réponse
    response = []
    for (continent_nom, pandemie_nom_val), data in result.items():
        item = {"continent": continent_nom, "pandemie": pandemie_nom_val}
        item.update(data)
        response.append(item)
    return response

def get_suivis(db: Session):
    pays_isos = {p.id: p.code_lettre for p in db.query(models.Pays).all()}
    pandemie_noms = {p.id_pandemie: p.nom_maladie for p in db.query(models.Pandemie).all()}
    suivis = db.query(models.SuiviPandemie).all()
    result = []
    for suivi in suivis:
        suivi_dict = suivi.__dict__.copy()
        suivi_dict["pays_iso"] = pays_isos.get(suivi.pays_id, "UNK")
        suivi_dict["pandemie"] = pandemie_noms.get(suivi.id_pandemie, "Inconnue")
        suivi_dict.pop("pays_id", None)
        suivi_dict.pop("id_pandemie", None)
        # Correction ici : valeurs par défaut si None
        for champ in ["guerison", "nouvelle_guerison"]:
            if suivi_dict.get(champ) is None:
                suivi_dict[champ] = 0
        result.append(suivi_dict)
    return result


def get_last_suivi_by_virus(db: Session):
    # Préparer les correspondances
    pandemie_virus = {p.id_pandemie: p.virus_id for p in db.query(models.Pandemie).all()}
    virus_noms = {v.id: v.nom_virus for v in db.query(models.Virus).all()}

    # Sous-requête pour le dernier jour de chaque pays
    subquery = (
        db.query(
            models.SuiviPandemie.pays_id,
            func.max(models.SuiviPandemie.date_jour).label("max_date")
        )
        .group_by(models.SuiviPandemie.pays_id)
        .subquery()
    )

    suivis = db.query(models.SuiviPandemie).join(
        subquery,
        (models.SuiviPandemie.pays_id == subquery.c.pays_id) &
        (models.SuiviPandemie.date_jour == subquery.c.max_date)
    ).all()

    result = {}
    champs = [
        "total_mort",
        "nouveau_cas",
        "nouvelle_guerison",
        "total_cas",
        "guerison",
        "nouveau_mort"
    ]

    for suivi in suivis:
        virus_id = pandemie_virus.get(suivi.id_pandemie)
        virus_nom = virus_noms.get(virus_id, "Inconnu")
        if virus_nom not in result:
            result[virus_nom] = {champ: 0 for champ in champs}
        for champ in champs:
            val = getattr(suivi, champ, 0)
            if val is None:
                val = 0
            result[virus_nom][champ] += val

    response = []
    for virus_nom, data in result.items():
        item = {"virus": virus_nom}
        item.update(data)
        response.append(item)
    return response

def get_suivis_by_pays_code(db: Session, code_lettre: str, pandemie_nom: str = None):
    pays = db.query(models.Pays).filter(models.Pays.code_lettre == code_lettre).first()
    if not pays:
        return []
    pays_id = pays.id

    pandemie_query = db.query(models.Pandemie)
    if pandemie_nom:
        pandemie = pandemie_query.filter(models.Pandemie.nom_maladie == pandemie_nom).first()
        if not pandemie:
            raise HTTPException(status_code=404, detail="Pandémie non trouvée")
        pandemie_ids = [pandemie.id_pandemie]
    else:
        pandemie_ids = [p.id_pandemie for p in pandemie_query.all()]

    pandemie_noms = {p.id_pandemie: p.nom_maladie for p in db.query(models.Pandemie).all()}

    query = db.query(models.SuiviPandemie).filter(models.SuiviPandemie.pays_id == pays_id)
    if pandemie_nom:
        query = query.filter(models.SuiviPandemie.id_pandemie.in_(pandemie_ids))
    suivis = query.all()

    result = []
    for suivi in suivis:
        suivi_dict = suivi.__dict__.copy()
        suivi_dict.pop("_sa_instance_state", None)
        suivi_dict["pays_iso"] = code_lettre
        suivi_dict["pandemie"] = pandemie_noms.get(suivi.id_pandemie, "Inconnue")
        suivi_dict.pop("pays_id", None)
        suivi_dict.pop("id_pandemie", None)
        for champ in ["guerison", "nouvelle_guerison"]:
            if suivi_dict.get(champ) is None:
                suivi_dict[champ] = 0
        result.append(suivi_dict)
    return result