from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db

router = APIRouter(prefix="/familles", tags=["familles"])

@router.get("/", response_model=list[schemas.Famille])
def read_familles(db: Session = Depends(get_db)):
    return crud.get_familles(db)

@router.post("/", response_model=schemas.Famille)
def create_famille(famille: schemas.FamilleCreate, db: Session = Depends(get_db)):
    return crud.create_famille(db, famille)
