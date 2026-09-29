"""
Schémas Pydantic utilisés pour les matchs.

Les schémas valident les données reçues par l'API et définissent
la structure des données renvoyées au client.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.match import MatchStatus


class MatchCreate(BaseModel):
    """Données nécessaires pour créer un match."""

    tournament_id: int = Field(
        gt=0,
    )

    round: int = Field(
        ge=1,
    )

    team_a_id: int = Field(
        gt=0,
    )

    team_b_id: int = Field(
        gt=0,
    )

    score_a: int | None = Field(
        default=None,
        ge=0,
    )

    score_b: int | None = Field(
        default=None,
        ge=0,
    )

    status: MatchStatus = MatchStatus.scheduled

    scheduled_at: datetime | None = None


class MatchUpdate(BaseModel):
    """
    Données modifiables lors d'une mise à jour.

    Tous les champs sont optionnels afin que PATCH puisse modifier
    uniquement les informations réellement envoyées.
    """

    tournament_id: int | None = Field(
        default=None,
        gt=0,
    )

    round: int | None = Field(
        default=None,
        ge=1,
    )

    team_a_id: int | None = Field(
        default=None,
        gt=0,
    )

    team_b_id: int | None = Field(
        default=None,
        gt=0,
    )

    score_a: int | None = Field(
        default=None,
        ge=0,
    )

    score_b: int | None = Field(
        default=None,
        ge=0,
    )

    status: MatchStatus | None = None

    scheduled_at: datetime | None = None


class MatchRead(BaseModel):
    """
    Données renvoyées par l'API.

    from_attributes=True permet de construire le schéma directement
    depuis un objet SQLAlchemy.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    tournament_id: int
    round: int
    team_a_id: int
    team_b_id: int
    score_a: int | None
    score_b: int | None
    status: MatchStatus
    scheduled_at: datetime | None
    created_at: datetime