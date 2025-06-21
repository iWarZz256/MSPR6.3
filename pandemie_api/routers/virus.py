from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db

router = APIRouter(prefix="/virus", tags=["virus"])

@router.get("/", response_model=list[schemas.Virus])
def read_virus(db: Session = Depends(get_db)):
    return crud.get_virus(db)

@router.post("/", response_model=schemas.Virus)
def create_virus(virus: schemas.VirusCreate, db: Session = Depends(get_db)):
    return crud.create_virus(db, virus)
