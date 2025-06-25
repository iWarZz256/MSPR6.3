# routers/auth.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from jose import jwt, JWTError
from datetime import timedelta, datetime
from database import get_db
from models import User
import schemas

SECRET_KEY = "un_secret_a_definir"  # à remplacer par une vraie clé secrète !
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

router = APIRouter()

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not bcrypt.verify(password, user.password_hash):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        is_admin: bool = payload.get("is_admin", False)
        if username is None:
            raise HTTPException(status_code=401, detail="Non authentifié")
        return {"username": username, "is_admin": is_admin}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

@router.post("/login", response_model=schemas.Token)
def login(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_login.username, user_login.password)
    if not user:
        raise HTTPException(status_code=400, detail="Identifiants incorrects")
    access_token = create_access_token(data={"sub": user.username, "is_admin": user.is_admin})
    return {"access_token": access_token, "token_type": "bearer"}
