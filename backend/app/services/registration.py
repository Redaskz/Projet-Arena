"""Règles métier de la ressource `registrations`.

Le service fait le lien entre les routeurs et les repositories.
C'est la seule couche autorisée à lever des HTTPException.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.registration import Registration
from app.models.team import Team
from app.models.tournament import Tournament
from app.repositories import registration as registration_repository
from app.schemas.registration import RegistrationCreate, RegistrationUpdate


def list_registrations(db: Session) -> list[Registration]:
    """Renvoie toutes les inscriptions."""
    return registration_repository.list_registrations(db)


def list_tournament_registrations(
    db: Session,
    tournament_id: int,
) -> list[Registration]:
    """Renvoie les inscriptions d'un tournoi existant."""
    tournament = db.get(Tournament, tournament_id)

    if tournament is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournoi introuvable.",
        )

    return registration_repository.list_registrations_by_tournament(
        db,
        tournament_id,
    )


def get_registration(
    db: Session,
    registration_id: int,
) -> Registration:
    """Renvoie une inscription existante."""
    registration = registration_repository.get_registration_by_id(
        db,
        registration_id,
    )

    if registration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inscription introuvable.",
        )

    return registration


def create_registration(
    db: Session,
    payload: RegistrationCreate,
) -> Registration:
    """Crée une inscription après vérification des règles métier."""
    tournament = db.get(Tournament, payload.tournament_id)

    if tournament is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournoi introuvable.",
        )

    team = db.get(Team, payload.team_id)

    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipe introuvable.",
        )

    # Une équipe ne peut participer qu'une seule fois au même tournoi.
    existing = registration_repository.get_registration_by_tournament_and_team(
        db,
        payload.tournament_id,
        payload.team_id,
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cette équipe est déjà inscrite à ce tournoi.",
        )

    # Les inscriptions ne sont possibles que pour un tournoi à venir.
    # Cette comparaison fonctionne si Tournament.status est un enum héritant
    # de str, comme le GameGenre du gabarit.
    tournament_status = getattr(tournament.status, "value", tournament.status)

    if tournament_status != "upcoming":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Les inscriptions sont fermées pour ce tournoi.",
        )

    registration_count = (
        registration_repository.count_registrations_by_tournament(
            db,
            payload.tournament_id,
        )
    )

    if registration_count >= tournament.max_teams:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Le nombre maximum d'équipes pour ce tournoi est atteint.",
        )

    data = payload.model_dump()
    return registration_repository.create_registration(db, data)


def update_registration(
    db: Session,
    registration_id: int,
    payload: RegistrationUpdate,
) -> Registration:
    """Modifie une inscription existante."""
    registration = get_registration(db, registration_id)

    data = payload.model_dump(exclude_unset=True)

    return registration_repository.update_registration(
        db,
        registration,
        data,
    )


def delete_registration(
    db: Session,
    registration_id: int,
) -> None:
    """Supprime une inscription existante."""
    registration = get_registration(db, registration_id)
    registration_repository.delete_registration(db, registration)