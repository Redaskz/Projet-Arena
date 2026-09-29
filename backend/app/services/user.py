"""Règles métier de la ressource `users`.

Construit sur le gabarit de services/game.py : c'est ici que se prennent les
décisions (404, 409, 403) et que le mot de passe en clair devient un hash.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User, UserRole
from app.repositories import user as user_repository
from app.schemas.user import UserCreate, UserUpdate


def _get_user_or_404(db: Session, user_id: int) -> User:
    """Récupère un utilisateur, ou interrompt la requête avec une erreur 404."""
    user = user_repository.get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"L'utilisateur {user_id} n'existe pas.",
        )

    return user


def _ensure_unique(
    db: Session,
    username: str | None,
    email: str | None,
    current_user_id: int | None = None,
) -> None:
    """Lève une 409 si le nom d'utilisateur ou l'email est déjà pris.

    `current_user_id` sert à la modification : un utilisateur qui renvoie son
    propre email inchangé ne doit pas être considéré comme un doublon de lui-même.

    409 CONFLICT et non 400 : la requête est bien formée, c'est l'état actuel
    de la base qui l'empêche. La contrainte UNIQUE de la base protège aussi,
    mais elle produirait une IntegrityError, donc une 500 peu parlante.
    """
    if username is not None:
        existing = user_repository.get_user_by_username(db, username)
        if existing is not None and existing.id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ce nom d'utilisateur est déjà utilisé.",
            )

    if email is not None:
        existing = user_repository.get_user_by_email(db, email)
        if existing is not None and existing.id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cette adresse email est déjà utilisée.",
            )


def _ensure_self_or_admin(current_user: User, target: User) -> None:
    """Lève une 403 si l'utilisateur connecté n'est ni le propriétaire du
    compte visé, ni un admin.

    403 et non 401 : on sait très bien QUI fait la requête (il est
    authentifié), mais il n'a pas le DROIT de toucher au compte d'un autre.
    """
    if current_user.id != target.id and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez modifier que votre propre compte.",
        )


def list_users(db: Session) -> list[User]:
    """Renvoie tous les utilisateurs."""
    return user_repository.list_users(db)


def get_user(db: Session, user_id: int) -> User:
    """Renvoie un utilisateur par son identifiant, ou lève une 404."""
    return _get_user_or_404(db, user_id)


def create_user(db: Session, payload: UserCreate) -> User:
    """Crée un compte et renvoie l'utilisateur créé.

    Utilisé à la fois par POST /auth/register et par POST /users.
    """
    _ensure_unique(db, payload.username, payload.email)

    data = payload.model_dump()

    # Le cœur de la sécurité du compte : on RETIRE le mot de passe en clair du
    # dictionnaire (pop) et on le remplace par son hash. Le repository ne voit
    # donc jamais le mot de passe en clair, et il ne peut pas finir en base.
    data["hashed_password"] = hash_password(data.pop("password"))

    # Rôle toujours imposé par le serveur à la création, jamais par le client.
    data["role"] = UserRole.player

    return user_repository.create_user(db, data)


def update_user(
    db: Session, user_id: int, payload: UserUpdate, current_user: User
) -> User:
    """Modifie partiellement un compte existant."""
    user = _get_user_or_404(db, user_id)
    _ensure_self_or_admin(current_user, user)

    data = payload.model_dump(exclude_unset=True)

    if not data:
        return user

    # Changer un rôle est une action d'administration : sans cette règle, un
    # joueur pourrait s'envoyer {"role": "admin"} et se promouvoir lui-même.
    if "role" in data and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul un administrateur peut modifier un rôle.",
        )

    # Les champs obligatoires en base ne peuvent pas être effacés : un null
    # explicite sur ces champs est refusé plutôt que de provoquer une 500.
    for field in ("username", "email", "password", "role"):
        if field in data and data[field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Le champ {field} ne peut pas être vide.",
            )

    _ensure_unique(db, data.get("username"), data.get("email"), current_user_id=user.id)

    # Même transformation qu'à la création : un nouveau mot de passe n'arrive
    # en base que sous forme de hash.
    if "password" in data:
        data["hashed_password"] = hash_password(data.pop("password"))

    return user_repository.update_user(db, user, data)


def delete_user(db: Session, user_id: int, current_user: User) -> None:
    """Supprime un compte, ou lève une 404 / 403."""
    user = _get_user_or_404(db, user_id)
    _ensure_self_or_admin(current_user, user)
    user_repository.delete_user(db, user)
