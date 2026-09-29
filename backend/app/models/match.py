"""
Modèle SQLAlchemy représentant un match.

Un match appartient à un tournoi et oppose deux équipes.
Les scores restent null tant que le match n'est pas joué.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# Imports réservés aux annotations de type, pour éviter un import circulaire
# avec tournament.py qui référence lui-même Match.
if TYPE_CHECKING:
    from app.models.team import Team
    from app.models.tournament import Tournament


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

    # --- Relations ORM -------------------------------------------------------
    # Pendant de Tournament.matches : `back_populates` garde les deux côtés
    # synchronisés dans la session.
    tournament: Mapped["Tournament"] = relationship(back_populates="matches")

    # `foreign_keys=` est OBLIGATOIRE ici : la table matches possède DEUX clés
    # étrangères vers teams.id (team_a_id et team_b_id). Sans précision,
    # SQLAlchemy ne sait pas laquelle utiliser pour chaque relation et lève une
    # AmbiguousForeignKeysError au premier chargement des modèles, ce qui
    # empêcherait le serveur de démarrer.
    # Pas de `back_populates` côté Team : une équipe aurait alors deux listes
    # de matchs (à domicile / à l'extérieur), peu utiles séparément. Les matchs
    # d'une équipe se récupèrent par une requête dans le repository.
    team_a: Mapped["Team"] = relationship(foreign_keys=[team_a_id])
    team_b: Mapped["Team"] = relationship(foreign_keys=[team_b_id])
