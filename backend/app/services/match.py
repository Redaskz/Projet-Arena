"""
Service des matchs.

Cette couche contient la logique métier liée aux matchs.
C'est la seule couche autorisée à lever des HTTPException.

Le service fait le lien entre les schémas Pydantic et le repository.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.match import MatchStatus
from app.repositories import match as match_repository
from app.schemas.match import MatchCreate, MatchUpdate


def _get_match_or_404(
    db: Session,
    match_id: int,
):
    """
    Récupère un match ou déclenche une erreur HTTP 404.

    La vérification est centralisée afin d'éviter de répéter
    cette logique dans les différentes fonctions du service.
    """

    match = match_repository.get_match_by_id(
        db,
        match_id,
    )

    if match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match introuvable.",
        )

    return match


def list_matches(
    db: Session,
    tournament_id: int | None = None,
):
    """
    Récupère les matchs avec un filtre optionnel sur le tournoi.
    """

    return match_repository.list_matches(
        db,
        tournament_id=tournament_id,
    )


def get_match(
    db: Session,
    match_id: int,
):
    """Récupère un match existant."""

    return _get_match_or_404(
        db,
        match_id,
    )


def create_match(
    db: Session,
    payload: MatchCreate,
):
    """
    Crée un match.

    La validation des données est réalisée par Pydantic avant
    d'arriver dans le service.
    """

    data = payload.model_dump()

    return match_repository.create_match(
        db,
        data,
    )


def update_match(
    db: Session,
    match_id: int,
    payload: MatchUpdate,
):
    """
    Met à jour un match.

    Un score ne peut pas être enregistré sur un match déjà joué.
    Cette règle est placée dans le service car elle correspond
    à une décision métier et non à un accès à la base.
    """

    match = _get_match_or_404(
        db,
        match_id,
    )

    data = payload.model_dump(
        exclude_unset=True,
    )

    if not data:
        return match

    score_is_being_recorded = (
        "score_a" in data
        or "score_b" in data
    )

    if (
        score_is_being_recorded
        and match.status == MatchStatus.played
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Impossible d'enregistrer un score sur un match déjà joué.",
        )

    return match_repository.update_match(
        db,
        match,
        data,
    )


def delete_match(
    db: Session,
    match_id: int,
) -> None:
    """Supprime un match existant."""

    match = _get_match_or_404(
        db,
        match_id,
    )

    match_repository.delete_match(
        db,
        match,
    )