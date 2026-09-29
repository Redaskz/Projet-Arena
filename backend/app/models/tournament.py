"""
Modèle SQLAlchemy représentant un tournoi.

Ce fichier suit le gabarit du modèle Game :
- les choix de structure sont faits dans le modèle ;
- les règles métier restent dans les services ;
- les relations utilisent les clés étrangères des autres ressources.
"""

import enum
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# Ces imports ne servent qu'aux annotations de type : à l'exécution, les
# relations désignent les classes par leur nom ("Game", "Match") et SQLAlchemy
# les résout lui-même. Les importer pour de vrai créerait un import circulaire,
# puisque match.py et game.py pointent à leur tour vers Tournament.
if TYPE_CHECKING:
    from app.models.game import Game
    from app.models.match import Match


class TournamentStatus(str, enum.Enum):
    """États possibles d'un tournoi."""

    upcoming = "upcoming"
    ongoing = "ongoing"
    finished = "finished"


class Tournament(Base):
    """Table représentant les tournois de la plateforme."""

    __tablename__ = "tournaments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    # `unique=True` en plus du contrôle fait par le service (409 lisible), comme
    # pour le nom d'une équipe : le service explique l'erreur au client, l'index
    # unique garantit qu'aucun doublon n'entre en base, même par le seed.
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[TournamentStatus] = mapped_column(
        Enum(TournamentStatus, name="tournament_status"),
        nullable=False,
        index=True,
        default=TournamentStatus.upcoming,
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    max_teams: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # --- Relations ORM -------------------------------------------------------
    # Une relation ne crée AUCUNE colonne : elle s'appuie sur la clé étrangère
    # game_id déclarée plus haut. Elle permet seulement d'écrire
    # `tournament.game` au lieu de relancer une requête à la main.
    # `back_populates` relie les deux côtés : Game.tournaments et
    # Tournament.game restent synchronisés en mémoire dans la même session.
    game: Mapped["Game"] = relationship(back_populates="tournaments")

    # `cascade="all, delete-orphan"` : un match n'a aucun sens sans son tournoi.
    # Sans cette option, supprimer un tournoi pousserait SQLAlchemy à mettre
    # matches.tournament_id à NULL, ce que la colonne refuse (nullable=False) :
    # le DELETE /tournaments/{id} finirait en erreur 500 dès qu'un calendrier
    # a été généré.
    matches: Mapped[list["Match"]] = relationship(
        back_populates="tournament",
        cascade="all, delete-orphan",
    )
