from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db

router = APIRouter(prefix="/pandemies", tags=["pandemies"])

@router.get("/", response_model=list[schemas.Pandemie])
def read_pandemies(db: Session = Depends(get_db)):
    return crud.get_pandemies(db)

@router.post("/", response_model=schemas.Pandemie)
def create_pandemie(pandemie: schemas.PandemieCreate, db: Session = Depends(get_db)):
    return crud.create_pandemie(db, pandemie)
