"""
Service des tournois.

Cette couche contient la logique métier.
C'est la seule couche autorisée à lever des HTTPException.

Le service fait le lien entre :
- les schémas Pydantic utilisés par l'API ;
- le repository qui communique avec la base de données.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.tournament import TournamentStatus
from app.repositories import tournament as tournament_repository
from app.schemas.tournament import TournamentCreate, TournamentUpdate


def _get_tournament_or_404(
    db: Session,
    tournament_id: int,
):
    """
    Récupère un tournoi ou déclenche une erreur HTTP 404.

    Cette vérification est centralisée afin d'éviter de répéter
    la même logique dans plusieurs fonctions du service.
    """

    tournament = tournament_repository.get_tournament_by_id(
        db,
        tournament_id,
    )

    if tournament is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournoi introuvable.",
        )

    return tournament


def list_tournaments(
    db: Session,
    game_id: int | None = None,
    tournament_status: TournamentStatus | None = None,
):
    """
    Récupère les tournois avec les filtres demandés.

    Le service transmet les critères au repository sans déplacer
    la logique de requête SQL dans cette couche.
    """

    return tournament_repository.list_tournaments(
        db,
        game_id=game_id,
        status=tournament_status,
    )


def get_tournament(
    db: Session,
    tournament_id: int,
):
    """Récupère un tournoi existant."""

    return _get_tournament_or_404(
        db,
        tournament_id,
    )


def create_tournament(
    db: Session,
    payload: TournamentCreate,
):
    """
    Crée un tournoi.

    model_dump() permet de transformer le schéma Pydantic en dictionnaire
    simple avant de le transmettre au repository.
    """

    data = payload.model_dump()

    return tournament_repository.create_tournament(
        db,
        data,
    )


def update_tournament(
    db: Session,
    tournament_id: int,
    payload: TournamentUpdate,
):
    """
    Met à jour un tournoi.

    exclude_unset=True est important pour PATCH :
    seuls les champs réellement envoyés par le client sont modifiés.
    """

    tournament = _get_tournament_or_404(
        db,
        tournament_id,
    )

    data = payload.model_dump(
        exclude_unset=True,
    )

    if not data:
        return tournament

    return tournament_repository.update_tournament(
        db,
        tournament,
        data,
    )


def delete_tournament(
    db: Session,
    tournament_id: int,
) -> None:
    """Supprime un tournoi existant."""

    tournament = _get_tournament_or_404(
        db,
        tournament_id,
    )

    tournament_repository.delete_tournament(
        db,
        tournament,
    )