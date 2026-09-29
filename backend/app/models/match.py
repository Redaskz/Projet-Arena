"""
Modèle SQLAlchemy représentant un match.

Un match appartient à un tournoi et oppose deux équipes.
Les scores restent null tant que le match n'est pas joué.
"""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MatchStatus(str, enum.Enum):
    """États possibles d'un match."""

    scheduled = "scheduled"
    played = "played"


class Match(Base):
    """Table représentant les matchs des tournois."""

    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    tournament_id: Mapped[int] = mapped_column(
        ForeignKey("tournaments.id"),
        nullable=False,
        index=True,
    )

    round: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    team_a_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id"),
        nullable=False,
        index=True,
    )

    team_b_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id"),
        nullable=False,
        index=True,
    )

    score_a: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    score_b: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    status: Mapped[MatchStatus] = mapped_column(
        Enum(MatchStatus, name="match_status"),
        nullable=False,
        default=MatchStatus.scheduled,
        index=True,
    )

    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )