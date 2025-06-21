from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db

router = APIRouter(prefix="/suivis", tags=["suivis"])

@router.get("/", response_model=list[schemas.SuiviPandemieOut])
def read_suivis(db: Session = Depends(get_db)):
    return crud.get_suivis(db)

@router.post("/", response_model=schemas.SuiviPandemieOut)
def create_suivi(suivi: schemas.SuiviPandemieCreate, db: Session = Depends(get_db)):
    return crud.create_suivi(db, suivi)

@router.get("/last-per-country", response_model=list[schemas.SuiviPandemieOut])
def get_last_suivi_by_pays(db: Session = Depends(get_db)):
    """
    Retourne les dernières données de suivi pour chaque pays.
    """
    return crud.get_last_suivi_by_pays(db)

@router.get("/last-per-continent", response_model=list[schemas.SuiviContinent])
def get_last_suivi_by_continent(
    pandemie: str = None,
    db: Session = Depends(get_db)
):
    """
    Retourne les dernières données de suivi de chaque jour, regroupées par continent, optionnellement filtrées par pandémie.
    """
    return crud.get_last_suivi_by_continent(db, pandemie)

@router.get("/last-per-virus", response_model=list[schemas.SuiviVirus])
def last_suivi_by_virus(db: Session = Depends(get_db)):
    return crud.get_last_suivi_by_virus(db)

@router.get("/pays/{code_lettre}", response_model=list[schemas.SuiviPandemieOut])
def all_suivis_by_pays(
    code_lettre: str,
    pandemie: str = None,
    db: Session = Depends(get_db)
):
    return crud.get_suivis_by_pays_code(db, code_lettre, pandemie)
