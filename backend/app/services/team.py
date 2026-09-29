"""Règles métier de la ressource `teams`.

Construit sur le gabarit de `services/game.py` : cette couche contient les
DÉCISIONS, et c'est la seule autorisée à lever des HTTPException.

Pourquoi ici et pas ailleurs :
- pas dans le repository, qui doit rester réutilisable hors du web (seed,
  tests, script de maintenance) et qui ne connaît donc pas les codes HTTP ;
- pas dans le routeur, qui doit rester une simple porte d'entrée. Si la règle
  était dans le routeur, elle ne s'appliquerait qu'à cette route précise et il
  faudrait la recopier ailleurs.

Ce service porte la règle métier principale des équipes : deux équipes ne
peuvent pas porter le même nom.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.player import Player
from app.models.team import Team
from app.repositories import game as game_repository
from app.repositories import player as player_repository
from app.repositories import team as team_repository
from app.schemas.team import TeamCreate, TeamUpdate

# Les modules de repositories sont importés sous des noms suffixés
# (`team_repository`) plutôt qu'en important leurs fonctions une par une. Deux
# avantages : on évite un conflit de nom avec la classe `Team`, et à la lecture
# on voit immédiatement quelles lignes parlent à la base et lesquelles sont des
# règles métier.
# Ce service utilise TROIS repositories, et c'est normal : une règle métier a le
# droit de croiser plusieurs tables (vérifier que le jeu existe, lister les
# joueurs d'une équipe). C'est justement ce qu'un routeur ne doit pas faire.


def _get_team_or_404(db: Session, team_id: int) -> Team:
    """Récupère une équipe, ou interrompt la requête avec une erreur 404.

    Le préfixe `_` signale une fonction interne au module : elle est appelée
    par les autres fonctions de ce fichier, pas par le routeur.

    Cette fonction existe parce que la même vérification serait sinon recopiée
    dans get_team, update_team, delete_team et list_team_players. Quatre
    copies, c'est quatre occasions d'oublier de la mettre à jour.
    """
    team = team_repository.get_team_by_id(db, team_id)

    if team is None:
        # 404 NOT FOUND et non 400 BAD REQUEST : la requête du client est
        # parfaitement bien formée, c'est la ressource demandée qui n'existe
        # pas. Un 400 dirait à tort au client qu'il s'est trompé de syntaxe.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            # Message en français : il peut être affiché tel quel à
            # l'utilisateur par le frontend.
            detail=f"L'équipe {team_id} n'existe pas.",
        )

    return team


def _ensure_name_is_available(
    db: Session, name: str, current_team_id: int | None = None
) -> None:
    """Vérifie qu'aucune autre équipe ne porte déjà ce nom, sinon lève une 409.

    RÈGLE MÉTIER : deux équipes ne peuvent pas avoir le même nom. Un classement
    ou une feuille de match deviendrait illisible avec deux « NAVI ».

    `current_team_id` sert au PATCH : quand une équipe se renomme, elle trouve
    forcément sa propre ligne en base. Sans cette exclusion, renvoyer le même
    nom qu'actuellement provoquerait un 409 absurde, et il deviendrait
    impossible de modifier le tag d'une équipe sans changer son nom.
    """
    existing = team_repository.get_team_by_name(db, name)

    if existing is None:
        return

    # Le nom est pris, mais peut-être par l'équipe qu'on est justement en train
    # de modifier : dans ce cas ce n'est pas un conflit.
    if existing.id == current_team_id:
        return

    # 409 CONFLICT et non 400 ni 422 : la requête est bien formée et ses champs
    # sont valides un par un. Ce qui coince, c'est l'ÉTAT actuel de la base, où
    # ce nom est déjà pris. C'est exactement ce que décrit le 409.
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"Une équipe porte déjà le nom « {name} ». Choisissez-en un autre.",
    )


def _ensure_game_exists(db: Session, game_id: int) -> None:
    """Vérifie que le jeu visé existe, sinon lève une 404.

    Sans cette vérification, l'INSERT partirait quand même et PostgreSQL le
    refuserait au nom de la clé étrangère. Le client recevrait alors une erreur
    500 illisible au lieu d'un message clair : la contrainte de base de données
    protège l'intégrité des données, elle ne sait pas expliquer l'erreur à un
    humain. C'est le rôle du service.
    """
    if game_repository.get_game_by_id(db, game_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Le jeu {game_id} n'existe pas, impossible d'y rattacher une équipe.",
        )


def list_teams(
    db: Session,
    game_id: int | None = None,
    search: str | None = None,
) -> list[Team]:
    """Renvoie les équipes, éventuellement filtrées.

    Ce service ne fait que transmettre au repository, et c'est normal : il n'y a
    aucune règle métier sur la consultation de la liste. On garde quand même la
    couche, pour que le routeur n'appelle jamais directement un repository.
    """
    return team_repository.list_teams(db, game_id=game_id, search=search)


def get_team(db: Session, team_id: int) -> Team:
    """Renvoie une équipe par son identifiant, ou lève une 404."""
    return _get_team_or_404(db, team_id)


def list_team_players(db: Session, team_id: int) -> list[Player]:
    """Renvoie les joueurs d'une équipe, ou lève une 404 si l'équipe n'existe pas.

    C'est la règle importante de cette route de relation : on vérifie D'ABORD
    que l'équipe existe. Sans cette vérification, GET /teams/999/players
    répondrait `[]` avec un code 200, ce qui laisserait croire au frontend que
    l'équipe 999 existe et n'a simplement aucun joueur. Deux situations très
    différentes méritent deux réponses différentes.
    """
    _get_team_or_404(db, team_id)

    return player_repository.list_players_by_team(db, team_id)


def create_team(db: Session, payload: TeamCreate) -> Team:
    """Crée une équipe et renvoie l'objet créé.

    Refuse un nom déjà utilisé (409) et un jeu inexistant (404).
    """
    # Les deux vérifications passent AVANT toute écriture : on ne veut pas d'un
    # INSERT à moitié préparé si l'une échoue.
    _ensure_name_is_available(db, payload.name)
    _ensure_game_exists(db, payload.game_id)

    # NOTE pour l'intégration : `captain_id` n'est pas vérifié de la même façon,
    # car la ressource `users` (models/user.py et son repository) reste à écrire
    # côté Victor. Dès qu'elle existera, ajouter ici un `_ensure_user_exists`
    # sur le même modèle que `_ensure_game_exists` suffira ; rien d'autre ne
    # bouge dans le fichier.

    # model_dump() convertit le schéma Pydantic en dictionnaire Python. Le
    # repository reçoit ainsi des types simples et ne dépend pas de Pydantic.
    data = payload.model_dump()

    return team_repository.create_team(db, data)


def update_team(db: Session, team_id: int, payload: TeamUpdate) -> Team:
    """Modifie partiellement une équipe existante.

    Refuse un nom déjà porté par une AUTRE équipe (409) et un jeu inexistant
    (404).
    """
    # On vérifie d'abord l'existence : inutile de préparer une modification
    # pour une ressource absente.
    team = _get_team_or_404(db, team_id)

    # exclude_unset=True est le cœur du PATCH : le dictionnaire ne contient que
    # les champs RÉELLEMENT envoyés par le client. Un champ absent du corps de
    # la requête n'apparaît pas ici, donc il ne sera pas modifié.
    # Avec exclude_none=True on obtiendrait un résultat faux : un champ envoyé
    # explicitement à null serait ignoré, et tout effacement deviendrait
    # impossible.
    data = payload.model_dump(exclude_unset=True)

    # Corps vide : le client n'a rien demandé à changer. On renvoie l'équipe
    # telle quelle plutôt que de faire un UPDATE inutile en base.
    if not data:
        return team

    # On ne revérifie l'unicité que si le nom fait partie des champs envoyés.
    # `in data` et non `data.get("name")` : un nom absent et un nom à null sont
    # deux cas distincts, et seul `in` les sépare correctement.
    if "name" in data:
        _ensure_name_is_available(db, data["name"], current_team_id=team.id)

    # Même logique pour le jeu : on ne vérifie son existence que si le client
    # demande effectivement à changer de jeu.
    if "game_id" in data:
        _ensure_game_exists(db, data["game_id"])

    return team_repository.update_team(db, team, data)


def delete_team(db: Session, team_id: int) -> None:
    """Supprime une équipe, ou lève une 404 si elle n'existe pas.

    Ne renvoie rien : la route répondra 204 No Content.

    Les joueurs de l'équipe sont supprimés avec elle par PostgreSQL, grâce au
    `ondelete="CASCADE"` déclaré sur players.team_id.
    """
    team = _get_team_or_404(db, team_id)
    team_repository.delete_team(db, team)
