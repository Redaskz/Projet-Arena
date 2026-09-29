"""Accès aux données de la ressource `users`.

Construit sur le gabarit de repositories/game.py : uniquement des requêtes,
ni HTTPException, ni règle métier, ni schéma Pydantic.
Le repository manipule `hashed_password` comme n'importe quelle colonne : il ne
hache rien lui-même, c'est le service qui lui transmet un hash déjà calculé.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def list_users(db: Session) -> list[User]:
    """Renvoie tous les utilisateurs, triés par nom d'utilisateur."""
    query = select(User).order_by(User.username)
    return list(db.execute(query).scalars().all())


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Renvoie un utilisateur par son identifiant, ou None s'il n'existe pas."""
    return db.get(User, user_id)


def get_user_by_username(db: Session, username: str) -> User | None:
    """Renvoie un utilisateur par son nom d'utilisateur, ou None.

    `scalar_one_or_none()` : la colonne est UNIQUE, il y a donc au plus une
    ligne. On récupère directement l'objet, ou None si aucune ligne.
    """
    query = select(User).where(User.username == username)
    return db.execute(query).scalar_one_or_none()


def get_user_by_email(db: Session, email: str) -> User | None:
    """Renvoie un utilisateur par son adresse email, ou None."""
    query = select(User).where(User.email == email)
    return db.execute(query).scalar_one_or_none()


def create_user(db: Session, data: dict) -> User:
    """Insère un nouvel utilisateur et renvoie l'objet créé.

    `data` contient déjà `hashed_password` et non `password` : la
    transformation a été faite par le service.
    """
    user = User(**data)
    db.add(user)
    db.commit()
    # refresh : récupère l'id, created_at et le rôle par défaut posés par la base.
    db.refresh(user)
    return user


def update_user(db: Session, user: User, data: dict) -> User:
    """Modifie un utilisateur existant et renvoie l'objet à jour."""
    for field, value in data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    """Supprime un utilisateur."""
    db.delete(user)
    db.commit()
