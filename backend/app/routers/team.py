"""Routes HTTP de la ressource `teams`.

Construit sur le gabarit de `routers/game.py` : cette couche est une PORTE
D'ENTRÉE, et rien de plus. Elle déclare l'URL, le verbe, le code de réponse et
la forme des données, récupère une session via `Depends(get_db)`, puis appelle
LE service correspondant.

Ni appel à un repository, ni HTTPException, ni `if` métier ici : tout cela est
dans `services/team.py`, y compris la règle d'unicité du nom (409).

Chaque fonction porte une docstring : FastAPI la reprend telle quelle comme
description de la route dans /docs.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.player import PlayerRead
from app.schemas.team import TeamCreate, TeamRead, TeamUpdate
from app.services import team as team_service

# Fichier au singulier (team.py), préfixe d'URL au pluriel (/teams) :
# une collection contient plusieurs éléments.
router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("", response_model=list[TeamRead])
def list_teams(
    # `Query(None, ...)` : FastAPI lit ces paramètres dans la query string
    # (?game_id=1&search=navi) et non dans le corps, et affiche la description
    # à côté du champ dans Swagger. `None` signifie « filtre non fourni ».
    game_id: int | None = Query(
        None,
        gt=0,
        description="Filtre sur le jeu de l'équipe, par identifiant.",
    ),
    search: str | None = Query(
        None,
        description="Recherche partielle dans le nom de l'équipe, insensible à la casse.",
    ),
    # `Depends(get_db)` confie l'ouverture ET la fermeture de la session à
    # FastAPI : get_db la referme dans son `finally` même si la route lève une
    # exception. Sans cette injection, une session oubliée finirait par épuiser
    # le pool de connexions PostgreSQL.
    db: Session = Depends(get_db),
):
    """Liste les équipes inscrites.

    Les deux filtres sont facultatifs et se cumulent. Sans filtre, la route
    renvoie toutes les équipes, triées par nom.
    """
    return team_service.list_teams(db, game_id=game_id, search=search)


# `{team_id}` est typé `int` dans la signature : FastAPI convertit le texte de
# l'URL en entier et répond 422 si ce n'est pas un nombre. La route ne reçoit
# donc jamais un identifiant illisible.
@router.get("/{team_id}", response_model=TeamRead)
def get_team(team_id: int, db: Session = Depends(get_db)):
    """Récupère une équipe par son identifiant.

    Répond 404 si aucune équipe ne porte cet identifiant.
    """
    return team_service.get_team(db, team_id)


# ROUTE DE RELATION : les joueurs appartiennent à une équipe, donc on les expose
# sous l'URL de cette équipe. C'est plus parlant pour le frontend que
# /players?team_id=3, car l'URL dit explicitement « les joueurs DE cette équipe ».
# Le `response_model` est `list[PlayerRead]` et non `list[TeamRead]` : la route
# est rangée avec les équipes, mais elle renvoie bien des joueurs.
@router.get("/{team_id}/players", response_model=list[PlayerRead])
def list_team_players(team_id: int, db: Session = Depends(get_db)):
    """Liste les joueurs d'une équipe.

    Répond 404 si l'équipe n'existe pas, ce qui est différent d'une équipe
    existante sans joueur : celle-ci renvoie 200 et une liste vide.
    """
    return team_service.list_team_players(db, team_id)


# `status_code=201` (CREATED) et non le 200 par défaut : la requête n'a pas
# seulement réussi, elle a créé une ressource.
@router.post("", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
def create_team(payload: TeamCreate, db: Session = Depends(get_db)):
    """Crée une équipe.

    Deux équipes ne peuvent pas porter le même nom : la route répond 409 si le
    nom est déjà pris. Elle répond 404 si le jeu visé n'existe pas.
    """
    # On renvoie `TeamRead` et non `TeamCreate` : la réponse doit contenir l'id
    # attribué par la base, que le client ne connaissait pas encore.
    return team_service.create_team(db, payload)


@router.patch("/{team_id}", response_model=TeamRead)
def update_team(team_id: int, payload: TeamUpdate, db: Session = Depends(get_db)):
    """Modifie partiellement une équipe existante.

    Seuls les champs présents dans le corps de la requête sont modifiés. Répond
    404 si l'équipe ou le jeu visé n'existe pas, et 409 si le nouveau nom est
    déjà porté par une autre équipe.
    """
    return team_service.update_team(db, team_id, payload)


# `status_code=204` (NO CONTENT) annonce une réponse sans corps : l'absence de
# `response_model` est donc volontaire, car un 204 accompagné d'un corps JSON
# serait une réponse HTTP invalide.
@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(team_id: int, db: Session = Depends(get_db)):
    """Supprime une équipe, ainsi que ses joueurs.

    Ne renvoie aucun corps de réponse. Répond 404 si l'équipe n'existe pas.
    """
    # Pas de `return` : la fonction renvoie implicitement None et FastAPI
    # produit une réponse 204 vide.
    team_service.delete_team(db, team_id)
