"""Routes HTTP de la ressource `players`.

Construit sur le gabarit de `routers/game.py` : porte d'entrée uniquement.
Elle déclare l'URL, le verbe, le code de réponse et la forme des données,
récupère une session via `Depends(get_db)`, puis appelle `services/player.py`.

Ni appel à un repository, ni HTTPException, ni `if` métier ici.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.player import PlayerCreate, PlayerRead, PlayerUpdate
from app.services import player as player_service

# Fichier au singulier (player.py), préfixe d'URL au pluriel (/players).
router = APIRouter(prefix="/players", tags=["Players"])


@router.get("", response_model=list[PlayerRead])
def list_players(
    # Ce filtre `team_id` fait doublon apparent avec GET /teams/{id}/players,
    # mais les deux routes ne servent pas le même usage : celle-ci permet de
    # croiser plusieurs critères à la fois (l'équipe ET le rôle), tandis que la
    # route de relation répond à la question simple « qui joue dans cette
    # équipe ? » et vérifie au passage que l'équipe existe.
    team_id: int | None = Query(
        None,
        gt=0,
        description="Filtre sur l'équipe du joueur, par identifiant.",
    ),
    role: str | None = Query(
        None,
        description="Filtre sur le rôle, insensible à la casse et partiel : « awp » trouve « AWPer ».",
    ),
    search: str | None = Query(
        None,
        description="Recherche partielle dans le pseudo du joueur, insensible à la casse.",
    ),
    db: Session = Depends(get_db),
):
    """Liste les joueurs.

    Les trois filtres sont facultatifs et se cumulent. Sans filtre, la route
    renvoie tous les joueurs, triés par pseudo.
    """
    return player_service.list_players(db, team_id=team_id, role=role, search=search)


@router.get("/{player_id}", response_model=PlayerRead)
def get_player(player_id: int, db: Session = Depends(get_db)):
    """Récupère un joueur par son identifiant.

    Répond 404 si aucun joueur ne porte cet identifiant.
    """
    return player_service.get_player(db, player_id)


@router.post("", response_model=PlayerRead, status_code=status.HTTP_201_CREATED)
def create_player(payload: PlayerCreate, db: Session = Depends(get_db)):
    """Crée un joueur et le rattache à une équipe.

    Répond 404 si l'équipe visée n'existe pas.
    """
    return player_service.create_player(db, payload)


@router.patch("/{player_id}", response_model=PlayerRead)
def update_player(player_id: int, payload: PlayerUpdate, db: Session = Depends(get_db)):
    """Modifie partiellement un joueur existant.

    Seuls les champs présents dans le corps de la requête sont modifiés.
    Changer `team_id` transfère le joueur dans une autre équipe. Répond 404 si
    le joueur ou l'équipe visée n'existe pas.
    """
    return player_service.update_player(db, player_id, payload)


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player(player_id: int, db: Session = Depends(get_db)):
    """Supprime un joueur.

    Ne renvoie aucun corps de réponse. Répond 404 si le joueur n'existe pas.
    """
    player_service.delete_player(db, player_id)
