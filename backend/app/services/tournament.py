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


def _ensure_name_is_available(
    db: Session,
    name: str,
    current_tournament_id: int | None = None,
) -> None:
    """
    Vérifie qu'aucun autre tournoi ne porte déjà ce nom, sinon lève une 409.

    Même règle que pour les équipes : deux tournois homonymes rendraient
    le calendrier et le classement ambigus pour les joueurs.

    `current_tournament_id` sert au PATCH : un tournoi qui renvoie son
    propre nom se retrouve forcément en base, ce n'est pas un conflit.
    """

    existing = tournament_repository.get_tournament_by_name(
        db,
        name,
    )

    if existing is None or existing.id == current_tournament_id:
        return

    # 409 et non 400 : la requête est valide, c'est l'état actuel de la
    # base (nom déjà pris) qui l'empêche d'aboutir.
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Ce nom de tournoi est déjà pris.",
    )


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

    # Vérifié avant l'INSERT : sans cela, l'index unique ferait échouer la
    # requête en 500 au lieu d'un 409 explicite.
    _ensure_name_is_available(
        db,
        payload.name,
    )

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

    # `in data` : on ne revérifie l'unicité que si le client renomme
    # réellement le tournoi.
    if "name" in data:
        _ensure_name_is_available(
            db,
            data["name"],
            current_tournament_id=tournament.id,
        )

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
