# security.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

# À adapter selon ton projet :
SECRET_KEY = "un_secret_a_definir"  # Remplace par une clé secrète solide
ALGORITHM = "HS256"

# Ce schéma permet de récupérer le token "Bearer ..." dans l'en-tête Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        is_admin: bool = payload.get("is_admin", False)
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Non authentifié",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"username": username, "is_admin": is_admin}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )

def admin_required(current_user=Depends(get_current_user)):
    if not current_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Réservé à l'administrateur",
        )
    return current_user
