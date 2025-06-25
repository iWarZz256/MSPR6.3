from fastapi import APIRouter, Depends, HTTPException
from security import get_current_user, admin_required

router = APIRouter()


@router.delete("/admin/supprimer_utilisateur/{user_id}")
def supprimer_utilisateur(user_id: int, user=Depends(admin_required)):
    # Ici, tu feras la suppression dans la base si besoin
    return {"message": "Utilisateur supprimé"}
