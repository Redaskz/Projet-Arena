"""Modèle SQLAlchemy de la ressource `players`.

Construit sur le gabarit de `models/game.py` : cette couche décrit UNIQUEMENT
la structure de la table. Aucune requête, aucune règle métier ici.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Player(Base):
    """Un joueur, membre d'une équipe."""

    __tablename__ = "players"

    # --- Identifiant ---------------------------------------------------------
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # --- Champs saisis par l'utilisateur -------------------------------------
    # Le pseudo en jeu. `index=True` car c'est la cible du filtre `search` du
    # GET /players : sans index, PostgreSQL parcourt toute la table à chaque
    # recherche.
    # Pas de `unique=True` : deux joueurs peuvent porter le même pseudo sur deux
    # jeux différents, et rien ne nous permet de trancher qui est le vrai.
    gamertag: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Texte libre et non un enum, pour la même raison que `platform` côté jeu :
    # les rôles dépendent du jeu ("AWPer" sur un FPS, "jungler" sur un MOBA) et
    # figer la liste dans un enum obligerait à modifier le type PostgreSQL à
    # chaque nouveau jeu ajouté au catalogue.
    role: Mapped[str] = mapped_column(String(50), nullable=False)

    # nullable=True car le champ est facultatif à la création (voir PlayerCreate) :
    # la colonne doit accepter NULL, sinon l'INSERT échouerait en 500 alors que
    # Pydantic a laissé passer la requête.
    country: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)

    # --- Lien vers l'équipe ---------------------------------------------------
    # `index=True` est ici le plus utile de tous : c'est exactement la colonne
    # filtrée par la route de relation GET /teams/{team_id}/players.
    # `ondelete="CASCADE"` est une instruction donnée à PostgreSQL : quand une
    # équipe est supprimée, la base supprime elle-même ses joueurs. C'est
    # cohérent avec `nullable=False` juste à côté — un joueur sans équipe serait
    # une ligne impossible à représenter. Sans ce CASCADE, un DELETE /teams/{id}
    # sur une équipe ayant des joueurs échouerait en violation de clé étrangère.
    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # --- Métadonnée technique ------------------------------------------------
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
