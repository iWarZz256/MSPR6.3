from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db

router = APIRouter(prefix="/pays", tags=["pays"])

@router.get("/", response_model=list[schemas.Pays])
def read_pays(db: Session = Depends(get_db)):
    return crud.get_pays(db)

@router.post("/", response_model=schemas.Pays)
def create_pays(pays: schemas.PaysCreate, db: Session = Depends(get_db)):
    return crud.create_pays(db, pays)
