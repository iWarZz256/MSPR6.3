from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db

router = APIRouter(prefix="/logs", tags=["logs"])

@router.get("/", response_model=list[schemas.LoggingInsert])
def read_logs(db: Session = Depends(get_db)):
    return crud.get_logs(db)

@router.post("/", response_model=schemas.LoggingInsert)
def create_log(log: schemas.LoggingInsertCreate, db: Session = Depends(get_db)):
    return crud.create_log(db, log)
