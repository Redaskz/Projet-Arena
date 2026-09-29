"""
Routes HTTP liées aux matchs.

Le router reçoit les requêtes HTTP et délègue la logique métier
au service. Il ne contient donc pas de règles métier.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.match import MatchCreate, MatchRead, MatchUpdate
from app.services import match as match_service


router = APIRouter(
    prefix="/matches",
    tags=["Matches"],
)


@router.get(
    "",
    response_model=list[MatchRead],
)
def list_matches(
    tournament_id: int | None = None,
    db: Session = Depends(get_db),
):
    """Retourne la liste des matchs avec un filtre optionnel."""

    return match_service.list_matches(
        db,
        tournament_id=tournament_id,
    )


@router.get(
    "/{match_id}",
    response_model=MatchRead,
)
def get_match(
    match_id: int,
    db: Session = Depends(get_db),
):
    """Retourne un match grâce à son identifiant."""

    return match_service.get_match(
        db,
        match_id,
    )


@router.post(
    "",
    response_model=MatchRead,
    status_code=status.HTTP_201_CREATED,
)
def create_match(
    payload: MatchCreate,
    db: Session = Depends(get_db),
):
    """Crée un nouveau match."""

    return match_service.create_match(
        db,
        payload,
    )


@router.patch(
    "/{match_id}",
    response_model=MatchRead,
)
def update_match(
    match_id: int,
    payload: MatchUpdate,
    db: Session = Depends(get_db),
):
    """
    Met à jour un match.

    La règle empêchant de modifier le score d'un match déjà joué
    est appliquée dans le service.
    """

    return match_service.update_match(
        db,
        match_id,
        payload,
    )


@router.delete(
    "/{match_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_match(
    match_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Supprime un match."""

    match_service.delete_match(
        db,
        match_id,
    )