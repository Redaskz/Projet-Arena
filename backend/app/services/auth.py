"""Règles métier de l'authentification, et dépendances de protection des routes.

Ce fichier fournit les deux dépendances utilisées par TOUTES les ressources :
- get_current_user  : « qui es-tu ? »             -> 401 si on ne sait pas
- get_current_admin : « as-tu le droit ? » (admin) -> 403 si non

La distinction 401 / 403 est volontaire :
- 401 UNAUTHORIZED : authentification. Pas de token, token faux ou expiré,
  utilisateur inconnu. Le client doit se (re)connecter.
- 403 FORBIDDEN : autorisation. On sait parfaitement qui est le client, mais
  son rôle ne lui permet pas l'action. Se reconnecter n'y changera rien.

Elles sont placées dans `services/` car elles lèvent des HTTPException, et
c'est la seule couche qui en a le droit.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserRole
from app.repositories import user as user_repository
from app.schemas.auth import Token
from app.schemas.user import UserCreate
from app.services import user as user_service

# OAuth2PasswordBearer fait deux choses :
# 1. à chaque requête, il lit l'en-tête « Authorization: Bearer <token> » et
#    renvoie le token. Si l'en-tête est absent, il lève lui-même une 401.
# 2. il déclare le schéma de sécurité dans OpenAPI : c'est ce qui fait
#    apparaître le bouton « Authorize » dans Swagger (/docs).
# `tokenUrl` indique à Swagger quelle route appeler pour obtenir le token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Message UNIQUE pour tout échec de login. Si on répondait « utilisateur
# inconnu » dans un cas et « mot de passe incorrect » dans l'autre, un
# attaquant pourrait tester une liste d'emails et savoir lesquels ont un compte
# (énumération des utilisateurs).
INVALID_CREDENTIALS = "Identifiants invalides."

# Hash d'un mot de passe quelconque, calculé une fois au démarrage.
# Il sert quand l'utilisateur n'existe pas (voir login ci-dessous).
_DUMMY_HASH = hash_password("arena-dummy-password")


def register(db: Session, payload: UserCreate) -> User:
    """Inscrit un nouvel utilisateur.

    Toute la logique (unicité, hachage, rôle par défaut) est déjà dans le
    service users : on la réutilise plutôt que de la recopier.
    """
    return user_service.create_user(db, payload)


def login(db: Session, identifier: str, password: str) -> Token:
    """Vérifie les identifiants et renvoie un JWT, ou lève une 401.

    `identifier` peut être le nom d'utilisateur OU l'email : Swagger envoie un
    champ nommé « username », et le frontend se connecte par email.
    """
    user = user_repository.get_user_by_username(db, identifier)
    if user is None:
        user = user_repository.get_user_by_email(db, identifier)

    # Si l'utilisateur n'existe pas, on vérifie quand même le mot de passe
    # contre un faux hash. bcrypt est lent (volontairement) : sans cette ligne,
    # « utilisateur inconnu » répondrait beaucoup plus vite que « mauvais mot de
    # passe », et le temps de réponse trahirait l'existence du compte.
    hashed_password = user.hashed_password if user is not None else _DUMMY_HASH
    password_ok = verify_password(password, hashed_password)

    if user is None or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(access_token=create_access_token(user.id))


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Dépendance : renvoie l'utilisateur connecté, ou lève une 401.

    Chaîne complète : en-tête Authorization -> token -> vérification de la
    signature et de l'expiration -> "sub" -> utilisateur en base.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider l'authentification.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Lève elle-même une 401 si le token est faux ou expiré.
    payload = decode_access_token(token)

    # Un token correctement signé mais sans "sub" exploitable n'identifie
    # personne : on le refuse aussi.
    subject = payload.get("sub")
    if subject is None:
        raise credentials_exception

    try:
        user_id = int(subject)
    except ValueError:
        raise credentials_exception

    # Le token peut être valide alors que le compte a été supprimé depuis :
    # un token n'est pas révocable, c'est donc la base qui a le dernier mot.
    user = user_repository.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dépendance : renvoie l'utilisateur connecté s'il est admin, sinon 403.

    Elle s'appuie sur get_current_user : une requête sans token reçoit donc
    d'abord une 401, et seulement un utilisateur authentifié mais non admin
    reçoit une 403.
    """
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action réservée aux administrateurs.",
        )

    return current_user
