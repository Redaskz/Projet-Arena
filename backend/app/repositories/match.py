"""
Repository des matchs.

Cette couche contient uniquement les opérations d'accès à la base de données.
Les règles métier restent dans le service.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.match import Match


def list_matches(
    db: Session,
    tournament_id: int | None = None,
) -> list[Match]:
    """
    Récupère les matchs.

    Le filtre tournament_id permet notamment de récupérer les matchs
    appartenant à un tournoi précis.
    """

    query = select(Match)

    if tournament_id is not None:
        query = query.where(Match.tournament_id == tournament_id)

    query = query.order_by(
        Match.round,
        Match.id,
    )

    return list(
        db.execute(query).scalars().all()
    )


def get_match_by_id(
    db: Session,
    match_id: int,
) -> Match | None:
    """
    Récupère un match grâce à son identifiant.

    db.get() est adapté à une recherche directe par clé primaire.
    """

    return db.get(Match, match_id)


def create_match(
    db: Session,
    data: dict,
) -> Match:
    """
    Crée un match en base.

    Le service fournit les données déjà validées.
    Le repository se charge uniquement de créer et sauvegarder l'objet.
    """

    match = Match(**data)

    db.add(match)
    db.commit()
    db.refresh(match)

    return match


def create_matches(
    db: Session,
    data_list: list[dict],
) -> list[Match]:
    """
    Crée plusieurs matchs en une seule transaction.

    Utilisé par la génération de calendrier : un seul commit pour tous
    les matchs garantit qu'un échec en cours de route ne laisse pas un
    calendrier à moitié écrit en base (tout ou rien).
    """

    matches = [Match(**data) for data in data_list]

    db.add_all(matches)
    db.commit()

    for match in matches:
        db.refresh(match)

    return matches


def update_match(
    db: Session,
    match: Match,
    data: dict,
) -> Match:
    """
    Met à jour les champs fournis d'un match.

    La boucle permet de ne modifier que les valeurs présentes
    dans le dictionnaire reçu du service.
    """

    for field, value in data.items():
        setattr(match, field, value)

    db.commit()
    db.refresh(match)

    return match


def delete_match(
    db: Session,
    match: Match,
) -> None:
    """Supprime un match de la base."""

    db.delete(match)
    db.commit()
