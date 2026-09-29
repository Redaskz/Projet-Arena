"""Routes de la ressource `users`.

Lecture publique, écriture protégée :
- POST   /users       -> admin uniquement (get_current_admin). L'inscription
                         publique passe par POST /auth/register.
- PATCH  /users/{id}  -> utilisateur connecté (get_current_user) ; le service
                         vérifie ensuite qu'il modifie SON compte, ou qu'il est admin.
- DELETE /users/{id}  -> même règle que PATCH.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services import user as user_service
from app.services.auth import get_current_admin, get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead], summary="Lister les utilisateurs")
def list_users(db: Session = Depends(get_db)):
    return user_service.list_users(db)


@router.get("/{user_id}", response_model=UserRead, summary="Détail d'un utilisateur")
def get_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.get_user(db, user_id)


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un utilisateur (admin)",
)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    # La dépendance n'est utilisée que pour son effet de garde : si le client
    # n'est pas admin, FastAPI a déjà répondu 401 ou 403 avant d'entrer ici.
    _admin: User = Depends(get_current_admin),
):
    return user_service.create_user(db, payload)


@router.patch("/{user_id}", response_model=UserRead, summary="Modifier un utilisateur")
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # current_user est transmis au service, qui décide s'il a le droit
    # de modifier ce compte (règle métier -> 403).
    return user_service.update_user(db, user_id, payload, current_user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un utilisateur",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_service.delete_user(db, user_id, current_user)
