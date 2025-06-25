from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db
from security import get_current_user, admin_required

router = APIRouter(prefix="/continents", tags=["continents"])

@router.get("/", response_model=list[schemas.Continent])
def read_continents(db: Session = Depends(get_db)):
    return crud.get_continents(db)



@router.post("/", response_model=schemas.Continent)
def create_continent(
    continent: schemas.ContinentCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_required)  
):
    return crud.create_continent(db, continent)
