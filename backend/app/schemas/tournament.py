"""
Schémas Pydantic utilisés pour les tournois.

Les schémas servent à :
- valider les données reçues par l'API ;
- définir les données renvoyées par l'API ;
- séparer la validation HTTP de la logique métier et de la base de données.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.tournament import TournamentStatus


class TournamentCreate(BaseModel):
    """Données nécessaires pour créer un tournoi."""

    name: str = Field(
        min_length=1,
        max_length=100,
    )

    game_id: int = Field(
        gt=0,
    )

    status: TournamentStatus = TournamentStatus.upcoming

    start_date: date

    max_teams: int = Field(
        ge=2,
    )


class TournamentUpdate(BaseModel):
    """
    Données modifiables lors d'une mise à jour.

    Tous les champs sont optionnels car l'endpoint utilise PATCH :
    le client peut donc modifier uniquement les informations souhaitées.
    """

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    game_id: int | None = Field(
        default=None,
        gt=0,
    )

    status: TournamentStatus | None = None

    start_date: date | None = None

    max_teams: int | None = Field(
        default=None,
        ge=2,
    )


class TournamentRead(BaseModel):
    """
    Données renvoyées par l'API.

    from_attributes=True permet à Pydantic de construire le schéma
    directement depuis un objet SQLAlchemy.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    game_id: int
    status: TournamentStatus
    start_date: date
    max_teams: int
    created_at: datetime