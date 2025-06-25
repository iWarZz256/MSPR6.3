from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey, UniqueConstraint, Index, Boolean
from sqlalchemy.orm import relationship
from database import Base  # ton Base SQLAlchemy

class Continent(Base):
    __tablename__ = 'continent'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nom_continent = Column(String(255), nullable=False)
    
    pays = relationship('Pays', back_populates='continent')

class Famille(Base):
    __tablename__ = 'famille'
    id_famille = Column(Integer, primary_key=True, autoincrement=True)
    nom_famille = Column(String(255), nullable=False)
    
    virus = relationship('Virus', back_populates='famille')

class LoggingInsert(Base):
    __tablename__ = 'logging_insert'
    id_logging = Column(Integer, primary_key=True, autoincrement=True)
    date_insertion = Column(DateTime, nullable=False)
    description = Column(Text, nullable=True)
    
    suivis = relationship('SuiviPandemie', back_populates='logging')

class Virus(Base):
    __tablename__ = 'virus'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_famille = Column(Integer, ForeignKey('famille.id_famille'), nullable=False)
    nom_virus = Column(String(255), nullable=False)
    nom_scientifique = Column(String(255), nullable=True)
    
    famille = relationship('Famille', back_populates='virus')
    pandemies = relationship('Pandemie', back_populates='virus')

class Pandemie(Base):
    __tablename__ = 'pandemie'
    id_pandemie = Column(Integer, primary_key=True, autoincrement=True)
    virus_id = Column(Integer, ForeignKey('virus.id'), nullable=False)
    date_apparition = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    nom_maladie = Column(String(255), nullable=False)
    
    virus = relationship('Virus', back_populates='pandemies')
    suivis = relationship('SuiviPandemie', back_populates='pandemie')

class Pays(Base):
    __tablename__ = 'pays'
    id = Column(Integer, primary_key=True, autoincrement=True)
    continent_id = Column(Integer, ForeignKey('continent.id'), nullable=False)
    nom = Column(String(255), nullable=False)
    code_lettre = Column(String(3), nullable=False, unique=True)
    code_chiffre = Column(String(10), nullable=False, unique=True)
    code_iso3166 = Column(String(3), nullable=False, unique=True)
    
    continent = relationship('Continent', back_populates='pays')
    suivis = relationship('SuiviPandemie', back_populates='pays')
    
    __table_args__ = (
        UniqueConstraint('code_lettre'),
        UniqueConstraint('code_chiffre'),
        UniqueConstraint('code_iso3166'),
        Index('IDX_349F3CAE921F4C77', 'continent_id'),
    )

class SuiviPandemie(Base):
    __tablename__ = 'suivi_pandemie'
    id_suivi = Column(Integer, primary_key=True, autoincrement=True)
    id_logging = Column(Integer, ForeignKey('logging_insert.id_logging'), nullable=False)
    id_pandemie = Column(Integer, ForeignKey('pandemie.id_pandemie'), nullable=False)
    pays_id = Column(Integer, ForeignKey('pays.id'), nullable=False)
    date_jour = Column(Date, nullable=False)
    total_cas = Column(Integer, nullable=True)
    total_mort = Column(Integer, nullable=True)
    guerison = Column(Integer, nullable=True)
    nouveau_cas = Column(Integer, nullable=True)
    nouveau_mort = Column(Integer, nullable=True)
    nouvelle_guerison = Column(Integer, nullable=True)
    
    logging = relationship('LoggingInsert', back_populates='suivis')
    pandemie = relationship('Pandemie', back_populates='suivis')
    pays = relationship('Pays', back_populates='suivis')
    
    __table_args__ = (
        Index('IDX_D9D63CE71408CB8A', 'id_logging'),
        Index('IDX_D9D63CE72F3440E1', 'id_pandemie'),
        Index('IDX_D9D63CE7A6E44244', 'pays_id'),
    )

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    is_admin = Column(Boolean, default=False)
