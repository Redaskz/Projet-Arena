"""
Modèle SQLAlchemy représentant un tournoi.

Ce fichier suit le gabarit du modèle Game :
- les choix de structure sont faits dans le modèle ;
- les règles métier restent dans les services ;
- les relations utilisent les clés étrangères des autres ressources.
"""

import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


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

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
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