"""Règles métier de la ressource `players`.

Construit sur le gabarit de `services/game.py` : cette couche contient les
DÉCISIONS, et c'est la seule autorisée à lever des HTTPException.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.player import Player
from app.repositories import player as player_repository
from app.repositories import team as team_repository
from app.schemas.player import PlayerCreate, PlayerUpdate


def _get_player_or_404(db: Session, player_id: int) -> Player:
    """Récupère un joueur, ou interrompt la requête avec une erreur 404.

    Le préfixe `_` signale une fonction interne au module : elle est appelée par
    les autres fonctions de ce fichier, pas par le routeur.
    """
    player = player_repository.get_player_by_id(db, player_id)

    if player is None:
        # 404 NOT FOUND et non 400 : la requête est bien formée, c'est la
        # ressource demandée qui n'existe pas.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Le joueur {player_id} n'existe pas.",
        )

    return player


def _ensure_team_exists(db: Session, team_id: int) -> None:
    """Vérifie que l'équipe visée existe, sinon lève une 404.

    Sans cette vérification, l'INSERT partirait quand même et PostgreSQL le
    refuserait au nom de la clé étrangère : le client recevrait une erreur 500
    illisible au lieu d'un message clair. La contrainte de base protège
    l'intégrité des données, elle ne sait pas l'expliquer à un humain.
    """
    if team_repository.get_team_by_id(db, team_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"L'équipe {team_id} n'existe pas, impossible d'y rattacher un joueur.",
        )


def list_players(
    db: Session,
    team_id: int | None = None,
    role: str | None = None,
    search: str | None = None,
) -> list[Player]:
    """Renvoie les joueurs, éventuellement filtrés.

    Ce service ne fait que transmettre au repository : il n'y a aucune règle
    métier sur la consultation. On garde la couche pour que le routeur n'appelle
    jamais directement un repository, et pour que la première règle qui
    apparaîtra ait déjà sa place.
    """
    return player_repository.list_players(db, team_id=team_id, role=role, search=search)


def get_player(db: Session, player_id: int) -> Player:
    """Renvoie un joueur par son identifiant, ou lève une 404."""
    return _get_player_or_404(db, player_id)


def create_player(db: Session, payload: PlayerCreate) -> Player:
    """Crée un joueur et renvoie l'objet créé.

    Refuse une équipe inexistante (404).
    """
    # La vérification passe AVANT l'écriture : un joueur sans équipe valide
    # n'aurait aucun sens, puisque team_id est obligatoire.
    _ensure_team_exists(db, payload.team_id)

    # model_dump() convertit le schéma Pydantic en dictionnaire Python, pour que
    # le repository ne dépende pas de Pydantic.
    data = payload.model_dump()

    return player_repository.create_player(db, data)


def update_player(db: Session, player_id: int, payload: PlayerUpdate) -> Player:
    """Modifie partiellement un joueur existant.

    Refuse une équipe inexistante (404) en cas de transfert.
    """
    player = _get_player_or_404(db, player_id)

    # exclude_unset=True : le dictionnaire ne contient que les champs réellement
    # envoyés par le client, donc un champ absent ne sera pas modifié.
    data = payload.model_dump(exclude_unset=True)

    # Corps vide : rien à changer, on renvoie le joueur tel quel plutôt que de
    # faire un UPDATE inutile.
    if not data:
        return player

    # Transfert d'équipe : on vérifie la nouvelle équipe seulement si le client
    # demande effectivement à la changer. `in data` et non `data.get(...)`, pour
    # ne pas confondre « champ absent » et « champ à null ».
    if "team_id" in data:
        _ensure_team_exists(db, data["team_id"])

    return player_repository.update_player(db, player, data)


def delete_player(db: Session, player_id: int) -> None:
    """Supprime un joueur, ou lève une 404 s'il n'existe pas.

    Ne renvoie rien : la route répondra 204 No Content.
    """
    player = _get_player_or_404(db, player_id)
    player_repository.delete_player(db, player)
