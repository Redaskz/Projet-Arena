"""Modèle SQLAlchemy de la ressource `teams`.

Construit sur le gabarit de `models/game.py` : cette couche décrit UNIQUEMENT
la structure de la table. Aucune requête (elles vont dans `repositories/`),
aucune règle métier et aucune HTTPException (elles vont dans `services/`).
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Team(Base):
    """Une équipe inscrite sur la plateforme, rattachée à un jeu et à un capitaine."""

    # Module au singulier (models/team.py), table au pluriel : une table
    # contient plusieurs lignes. Même logique pour l'URL (/teams).
    __tablename__ = "teams"

    # --- Identifiant ---------------------------------------------------------
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # --- Champs saisis par l'utilisateur -------------------------------------
    # `unique=True` en plus du contrôle fait par le service (qui répond 409 avec
    # un message en français). La contrainte est donc appliquée DEUX fois, comme
    # le genre d'un jeu l'est par Pydantic puis par PostgreSQL :
    # - le service donne au client une erreur lisible et un code HTTP juste ;
    # - l'index unique garantit qu'aucun doublon ne peut entrer en base, même
    #   par un INSERT SQL direct ou par le script de seed.
    # L'index sert aussi de raccourci au service, qui cherche une équipe par son
    # nom avant chaque création.
    # Limite connue et assumée : si deux requêtes créaient la même équipe
    # exactement en même temps, le service laisserait passer les deux et c'est
    # PostgreSQL qui refuserait la seconde, en 500 plutôt qu'en 409. Un doublon
    # en base serait bien plus gênant que ce cas de course improbable en démo.
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, index=True
    )

    # Le trigramme affiché devant le nom des joueurs ("G2", "NAVI").
    # Court, mais volontairement pas unique : deux équipes de jeux différents
    # peuvent partager un tag sans que cela prête à confusion.
    tag: Mapped[str] = mapped_column(String(10), nullable=False)

    # --- Liens vers les autres tables ----------------------------------------
    # `ForeignKey("games.id")` désigne la table et la colonne visées, écrites
    # comme en SQL. PostgreSQL refusera donc une équipe rattachée à un jeu
    # inexistant : l'intégrité est garantie par la base, pas seulement par le
    # code Python.
    # `index=True` car on liste très souvent les équipes d'un jeu donné.
    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id"), nullable=False, index=True
    )

    # ATTENTION, DÉPENDANCE : cette clé étrangère vise la table `users`, définie
    # dans app/models/user.py, qui est le fichier de Victor et reste à écrire.
    # La clé est déclarée dès maintenant pour ne pas retarder les équipes, mais
    # tant que le modèle User n'existe pas, SQLAlchemy ne peut pas résoudre
    # "users.id" et create_all() échoue. Rien à changer ici le jour où le
    # fichier arrive : la résolution est automatique.
    captain_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )

    # --- Métadonnée technique ------------------------------------------------
    # `server_default=func.now()` : c'est PostgreSQL qui pose l'horodatage au
    # moment de l'INSERT, pas Python. Toutes les lignes utilisent donc la même
    # horloge, quelle que soit la machine qui exécute le code.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
