"""Modèle SQLAlchemy de la ressource `users`.

Construit sur le gabarit de models/game.py : uniquement la structure de la
table, aucune règle métier et aucune requête.
"""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserRole(str, enum.Enum):
    """Les rôles possibles d'un utilisateur.

    Même construction que GameGenre (str + enum.Enum, nom = valeur) : la valeur
    renvoyée par l'API est exactement celle stockée en base.
    - player : utilisateur standard, rôle attribué à toute inscription
    - admin  : peut gérer les autres comptes (voir get_current_admin)
    Les valeurs correspondent au type `User.role` déjà utilisé par le frontend.
    """

    player = "player"
    admin = "admin"


class User(Base):
    """Un compte utilisateur de la plateforme Arena."""

    __tablename__ = "users"

    # --- Identifiant ---------------------------------------------------------
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # --- Identifiants de connexion -------------------------------------------
    # `unique=True` crée une contrainte UNIQUE dans PostgreSQL : même si le
    # service oubliait de vérifier, la base refuserait un doublon.
    # `unique=True` crée aussi l'index, utile car le login cherche par ces champs.
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    # Le HASH bcrypt, jamais le mot de passe en clair (voir core/security.py).
    # Un hash bcrypt fait 60 caractères ; 255 laisse de la marge pour un
    # éventuel changement d'algorithme.
    # Ce champ n'apparaît dans AUCUN schéma de sortie (voir schemas/user.py).
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # ENUM natif PostgreSQL, comme pour le genre d'un jeu.
    # `server_default` : un INSERT direct en SQL (seed, script) sans rôle
    # obtient lui aussi "player", et non une erreur.
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        nullable=False,
        default=UserRole.player,
        server_default=UserRole.player.value,
    )

    # --- Métadonnée technique ------------------------------------------------
    # Horodatage posé par PostgreSQL au moment de l'INSERT (voir models/game.py).
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
