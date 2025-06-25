import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from database import Base
import crud
import schemas

# Base de données en mémoire pour les tests
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_create_continent(db):
    continent = schemas.ContinentCreate(nom_continent="Europe")
    db_cont = crud.create_continent(db, continent)
    assert db_cont.nom_continent == "Europe"
