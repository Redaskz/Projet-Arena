"""Routes de l'authentification : inscription, connexion, profil courant.

Le routeur reste une simple porte d'entrée : il déclare la route, le code de
statut et le schéma de réponse, puis délègue tout au service.
"""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserRead
from app.services import auth as auth_service
from app.services.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    # response_model=UserRead : c'est ce qui garantit que hashed_password ne
    # sort pas, même si le service renvoie l'objet SQLAlchemy complet.
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un compte",
)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register(db, payload)


@router.post("/login", response_model=Token, summary="Se connecter et obtenir un JWT")
def login(
    # OAuth2PasswordRequestForm lit un formulaire (et non du JSON) avec les
    # champs `username` et `password` : c'est le format imposé par la norme
    # OAuth2, et celui qu'utilise le bouton « Authorize » de Swagger.
    # Le champ `username` accepte ici un nom d'utilisateur OU un email.
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    return auth_service.login(db, form_data.username, form_data.password)


@router.get("/me", response_model=UserRead, summary="Utilisateur connecté")
def read_me(current_user: User = Depends(get_current_user)):
    # Aucune requête ici : get_current_user a déjà validé le token et chargé
    # l'utilisateur. Sans token valide, FastAPI a répondu 401 avant d'arriver là.
    return current_user
