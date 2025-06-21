from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

# ----- Continent -----
class ContinentBase(BaseModel):
    nom_continent: str

class ContinentCreate(ContinentBase):
    pass

class Continent(ContinentBase):
    id: int
    class Config:
        orm_mode = True

# ----- Pays -----
class PaysBase(BaseModel):
    continent_id: int
    nom: str
    code_lettre: str
    code_chiffre: str
    code_iso3166: str

class PaysCreate(PaysBase):
    pass

class Pays(PaysBase):
    id: int
    class Config:
        orm_mode = True

# ----- Famille -----
class FamilleBase(BaseModel):
    nom_famille: str

class FamilleCreate(FamilleBase):
    pass

class Famille(FamilleBase):
    id_famille: int
    class Config:
        orm_mode = True

# ----- Virus -----
class VirusBase(BaseModel):
    id_famille: int
    nom_virus: str
    nom_scientifique: Optional[str] = None

class VirusCreate(VirusBase):
    pass

class Virus(VirusBase):
    id: int
    class Config:
        orm_mode = True

# ----- LoggingInsert -----
class LoggingInsertBase(BaseModel):
    date_insertion: datetime
    description: Optional[str] = None

class LoggingInsertCreate(LoggingInsertBase):
    pass

class LoggingInsert(LoggingInsertBase):
    id_logging: int
    class Config:
        orm_mode = True

# ----- Pandemie -----
class PandemieBase(BaseModel):
    virus_id: int
    date_apparition: date
    date_fin: Optional[date] = None
    description: Optional[str] = None
    nom_maladie: str

class PandemieCreate(PandemieBase):
    pass

class Pandemie(PandemieBase):
    id_pandemie: int
    class Config:
        orm_mode = True

# ----- SuiviPandemie -----
class SuiviPandemieBase(BaseModel):
    id_logging: int
    id_pandemie: int
    pays_id: int
    date_jour: date
    total_cas: Optional[int] = None
    total_mort: Optional[int] = None
    guerison: Optional[int] = None
    nouveau_cas: Optional[int] = None
    nouveau_mort: Optional[int] = None
    nouvelle_guerison: Optional[int] = None

class SuiviPandemieCreate(SuiviPandemieBase):
    pass

class SuiviPandemieOut(BaseModel):
    id_suivi: int
    pays_iso: str
    date_jour: date
    total_mort: int
    nouveau_cas: int
    nouvelle_guerison: int
    id_logging: int
    pandemie: str
    total_cas: int
    guerison: int
    nouveau_mort: int

    class Config:
        orm_mode = True
        
class SuiviContinent(BaseModel):
    continent: str
    pandemie: str
    total_mort: int
    nouveau_cas: int
    nouvelle_guerison: int
    total_cas: int
    guerison: int
    nouveau_mort: int

    class Config:
        orm_mode = True
        
class SuiviVirus(BaseModel):
    virus: str
    total_mort: int
    nouveau_cas: int
    nouvelle_guerison: int
    total_cas: int
    guerison: int
    nouveau_mort: int

    class Config:
        orm_mode = True
            
        
class SuiviPandemie(SuiviPandemieBase):
    id_suivi: int
    class Config:
        orm_mode = True
