"""
Repository des tournois.

Cette couche contient uniquement les opérations d'accès à la base de données.
Les décisions métier et les HTTPException restent dans le service.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tournament import Tournament, TournamentStatus


def list_tournaments(
    db: Session,
    game_id: int | None = None,
    status: TournamentStatus | None = None,
) -> list[Tournament]:
    """
    Récupère les tournois avec des filtres optionnels.

    Les filtres sont appliqués uniquement lorsqu'ils sont fournis afin
    de permettre à la route GET /tournaments de gérer plusieurs cas
    avec une seule fonction de repository.
    """

    query = select(Tournament)

    if game_id is not None:
        query = query.where(Tournament.game_id == game_id)

    if status is not None:
        query = query.where(Tournament.status == status)

    query = query.order_by(Tournament.start_date)

    return list(db.execute(query).scalars().all())


def get_tournament_by_id(
    db: Session,
    tournament_id: int,
) -> Tournament | None:
    """
    Récupère un tournoi grâce à son identifiant.

    db.get() est adapté ici car on recherche directement une ligne
    grâce à sa clé primaire.
    """

    return db.get(Tournament, tournament_id)


def create_tournament(
    db: Session,
    data: dict,
) -> Tournament:
    """
    Crée un tournoi en base.

    Le service fournit un dictionnaire déjà validé et préparé.
    Le repository se contente de créer et sauvegarder l'objet SQLAlchemy.
    """

    tournament = Tournament(**data)

    db.add(tournament)
    db.commit()
    db.refresh(tournament)

    return tournament


def update_tournament(
    db: Session,
    tournament: Tournament,
    data: dict,
) -> Tournament:
    """
    Met à jour un tournoi existant.

    Seuls les champs présents dans data sont modifiés.
    """

    for field, value in data.items():
        setattr(tournament, field, value)

    db.commit()
    db.refresh(tournament)

    return tournament


def delete_tournament(
    db: Session,
    tournament: Tournament,
) -> None:
    """
    Supprime un tournoi de la base.
    """

    db.delete(tournament)
    db.commit()