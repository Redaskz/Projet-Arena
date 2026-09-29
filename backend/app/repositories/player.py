"""Accès aux données de la ressource `players`.

Construit sur le gabarit de `repositories/game.py` : cette couche ne fait QUE
parler à la base de données. Ni HTTPException, ni règle métier, ni Pydantic.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.player import Player


def list_players(
    db: Session,
    team_id: int | None = None,
    role: str | None = None,
    search: str | None = None,
) -> list[Player]:
    """Renvoie les joueurs, filtrés par les critères fournis.

    Les trois filtres sont facultatifs et se cumulent. Aucun filtre fourni
    signifie « tous les joueurs ».
    """
    query = select(Player)

    # On ajoute une condition SEULEMENT si le paramètre a été fourni.
    if team_id is not None:
        query = query.where(Player.team_id == team_id)

    if role is not None:
        # `ilike` avec % encadrants : insensible à la casse et partiel, donc
        # « awp » trouve « AWPer ».
        query = query.where(Player.role.ilike(f"%{role}%"))

    if search is not None:
        query = query.where(Player.gamertag.ilike(f"%{search}%"))

    # Tri stable par pseudo : sans ORDER BY, PostgreSQL ne garantit aucun ordre.
    query = query.order_by(Player.gamertag)

    return list(db.execute(query).scalars().all())


def list_players_by_team(db: Session, team_id: int) -> list[Player]:
    """Renvoie les joueurs d'une équipe donnée.

    C'est la requête derrière la route de relation GET /teams/{team_id}/players.
    Elle délègue à `list_players` avec le seul filtre `team_id`, plutôt que de
    réécrire un select : une seule requête à maintenir, et le même tri que
    partout ailleurs.
    """
    return list_players(db, team_id=team_id)


def get_player_by_id(db: Session, player_id: int) -> Player | None:
    """Renvoie un joueur par son identifiant, ou None s'il n'existe pas.

    On renvoie None et non une exception : décider qu'un joueur introuvable
    mérite un 404 est une règle métier, donc c'est au service de le faire.
    """
    return db.get(Player, player_id)


def create_player(db: Session, data: dict) -> Player:
    """Insère un nouveau joueur et renvoie l'objet créé."""
    player = Player(**data)

    db.add(player)  # 1. l'objet entre dans la session, rien n'est encore écrit
    db.commit()  # 2. l'INSERT part vers PostgreSQL
    db.refresh(player)  # 3. on relit la ligne pour l'id et created_at, remplis
    #                     par la base elle-même.
    return player


def update_player(db: Session, player: Player, data: dict) -> Player:
    """Modifie un joueur existant et renvoie l'objet à jour.

    `data` ne contient QUE les champs réellement envoyés par le client, grâce
    au model_dump(exclude_unset=True) appliqué dans le service.
    """
    # setattr permet d'affecter un champ dont le nom est dans une variable :
    # une seule boucle couvre toutes les combinaisons de champs modifiés.
    for field, value in data.items():
        setattr(player, field, value)

    # Pas de db.add() : l'objet vient de la session, SQLAlchemy suit déjà ses
    # modifications et générera l'UPDATE au commit.
    db.commit()
    db.refresh(player)
    return player


def delete_player(db: Session, player: Player) -> None:
    """Supprime un joueur.

    Ne renvoie rien : la route répondra 204.
    """
    db.delete(player)
    db.commit()
