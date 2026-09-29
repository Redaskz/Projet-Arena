"""
Routes HTTP liées aux tournois.

Le router reçoit les requêtes HTTP et délègue la logique métier
au service. Il ne contient donc pas de règles métier.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tournament import TournamentStatus
from app.schemas.match import MatchRead
from app.schemas.tournament import (
    TournamentCreate,
    TournamentRead,
    TournamentUpdate,
)
from app.services import match as match_service
from app.services import tournament as tournament_service


router = APIRouter(
    prefix="/tournaments",
    tags=["Tournaments"],
)


@router.get(
    "",
    response_model=list[TournamentRead],
)
def list_tournaments(
    game_id: int | None = Query(
        default=None,
        gt=0,
    ),
    tournament_status: TournamentStatus | None = Query(
        default=None,
        alias="status",
    ),
    db: Session = Depends(get_db),
):
    """
    Retourne la liste des tournois.

    Les paramètres game_id et status sont optionnels afin de permettre
    de filtrer les résultats sans créer plusieurs endpoints différents.
    """

    return tournament_service.list_tournaments(
        db,
        game_id=game_id,
        tournament_status=tournament_status,
    )


@router.get(
    "/{tournament_id}/matches",
    response_model=list[MatchRead],
)
def list_tournament_matches(
    tournament_id: int,
    db: Session = Depends(get_db),
):
    """
    Retourne tous les matchs appartenant à un tournoi.

    La récupération est déléguée au service des matchs afin de conserver
    la séparation des responsabilités entre les différentes couches.
    """

    return match_service.list_matches(
        db,
        tournament_id=tournament_id,
    )


@router.get(
    "/{tournament_id}",
    response_model=TournamentRead,
)
def get_tournament(
    tournament_id: int,
    db: Session = Depends(get_db),
):
    """Retourne un tournoi grâce à son identifiant."""

    return tournament_service.get_tournament(
        db,
        tournament_id,
    )


@router.post(
    "",
    response_model=TournamentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_tournament(
    payload: TournamentCreate,
    db: Session = Depends(get_db),
):
    """Crée un nouveau tournoi."""

    return tournament_service.create_tournament(
        db,
        payload,
    )


@router.patch(
    "/{tournament_id}",
    response_model=TournamentRead,
)
def update_tournament(
    tournament_id: int,
    payload: TournamentUpdate,
    db: Session = Depends(get_db),
):
    """Met à jour les champs envoyés d'un tournoi."""

    return tournament_service.update_tournament(
        db,
        tournament_id,
        payload,
    )


@router.delete(
    "/{tournament_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_tournament(
    tournament_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Supprime un tournoi."""

    tournament_service.delete_tournament(
        db,
        tournament_id,
    )