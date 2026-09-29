"""Routes HTTP de la ressource `games`.

GABARIT D'ARCHITECTURE : la couche `routers` est une PORTE D'ENTRÉE, et rien
de plus. Son travail se limite à quatre choses :
1. déclarer l'URL, le verbe HTTP et le code de réponse ;
2. déclarer la forme des entrées (corps, paramètres d'URL) et de la sortie
   (`response_model`), ce qui alimente Swagger automatiquement ;
3. récupérer une session de base de données via `Depends(get_db)` ;
4. appeler LE service correspondant et renvoyer son résultat.

Ce qu'on ne met JAMAIS ici :
- un appel à un repository ou à la session (`db.query`, `db.get`...) : le
  routeur sauterait la couche des règles métier, et ces règles ne
  s'appliqueraient alors qu'à cette route. Le routeur passe toujours par
  `services/game.py`.
- une HTTPException : décider qu'un jeu introuvable vaut un 404 est une règle
  métier, elle est déjà dans le service. La lever ici la dupliquerait.
- un `if` métier : si une condition apparaît dans une route, c'est le signe
  qu'elle doit descendre dans le service.

Chaque fonction porte une docstring : FastAPI la reprend telle quelle comme
description de la route dans /docs. C'est la documentation lue par l'équipe
frontend, elle est donc écrite pour un lecteur, pas pour nous.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.game import GameGenre
from app.schemas.game import GameCreate, GameRead, GameUpdate
from app.services import game as game_service

# Le module du service est importé sous le nom `game_service`, comme le service
# importe son repository sous le nom `game_repository`. À la lecture d'une route,
# on voit donc immédiatement que l'appel part vers la couche métier.

# `prefix="/games"` est écrit UNE fois ici plutôt que répété sur chaque route :
# le préfixe est au pluriel (une collection de jeux) alors que le fichier est au
# singulier (game.py), conformément à la convention du projet.
# `tags=["Games"]` regroupe ces routes sous un même titre dans /docs : sans lui,
# les routes de toutes les ressources apparaîtraient mélangées dans une seule
# liste « default ».
router = APIRouter(prefix="/games", tags=["Games"])


# Pas de chemin dans le décorateur : la route est donc exactement le préfixe,
# GET /games.
@router.get("", response_model=list[GameRead])
def list_games(
    # Les trois filtres sont annoncés avec `Query(None, ...)`. Deux effets :
    # FastAPI les lit dans la query string (?genre=fps&search=strike) et non
    # dans le corps, et la `description` apparaît à côté du champ dans Swagger.
    # `None` par défaut signifie « filtre non fourni », ce que le repository
    # interprète comme « ne pas filtrer sur ce critère ».
    genre: GameGenre | None = Query(
        None,
        description="Filtre sur le genre exact. Valeurs autorisées : fps, moba, sport, fighting, battle_royale.",
    ),
    platform: str | None = Query(
        None,
        description="Filtre sur la plateforme, insensible à la casse et partiel : « ps » trouve « PS5 ».",
    ),
    search: str | None = Query(
        None,
        description="Recherche partielle dans le nom du jeu, insensible à la casse.",
    ),
    # `Depends(get_db)` confie l'ouverture ET la fermeture de la session à
    # FastAPI : `get_db` ouvre la session, la cède à la route, puis la referme
    # dans son `finally` même si la route lève une exception. Sans cette
    # injection, chaque route devrait gérer son try/finally et une session
    # oubliée finirait par épuiser le pool de connexions PostgreSQL.
    db: Session = Depends(get_db),
):
    """Liste les jeux du catalogue.

    Les trois filtres sont facultatifs et se cumulent. Sans aucun filtre, la
    route renvoie tout le catalogue, trié par nom.
    """
    # `genre` est typé `GameGenre` et non `str` : FastAPI valide donc la valeur
    # avant d'entrer dans la fonction et répond 422 pour un genre inconnu.
    # Swagger affiche d'ailleurs une liste déroulante au lieu d'un champ libre.
    return game_service.list_games(db, genre=genre, platform=platform, search=search)


# `{game_id}` est un paramètre de chemin. Il est typé `int` dans la signature :
# FastAPI convertit le texte de l'URL en entier et répond 422 si ce n'est pas un
# nombre. La route ne reçoit donc jamais un identifiant illisible.
@router.get("/{game_id}", response_model=GameRead)
def get_game(game_id: int, db: Session = Depends(get_db)):
    """Récupère un jeu par son identifiant.

    Répond 404 si aucun jeu ne porte cet identifiant.
    """
    # Aucun test d'existence ici : le service lève déjà la 404. Le routeur se
    # contente de transmettre.
    return game_service.get_game(db, game_id)


# `status_code=201` (CREATED) et non le 200 par défaut : la requête n'a pas
# seulement réussi, elle a créé une ressource. On passe par `status.HTTP_...`
# plutôt que par le nombre nu, car le nom est explicite à la lecture.
@router.post("", response_model=GameRead, status_code=status.HTTP_201_CREATED)
def create_game(payload: GameCreate, db: Session = Depends(get_db)):
    """Crée un jeu dans le catalogue.

    Le jeu est ensuite enrichi automatiquement par l'API externe RAWG
    (jaquette, note, date de sortie). Si RAWG est injoignable, le jeu est créé
    quand même et ces champs restent vides.
    """
    # `payload` est typé avec un schéma Pydantic : FastAPI en déduit que la
    # donnée arrive dans le corps de la requête, la valide, et rejette en 422
    # tout corps non conforme. La fonction ne reçoit donc que du valide.
    # On renvoie `GameRead` et non `GameCreate` : la réponse doit contenir l'id
    # attribué par la base, que le client ne connaissait pas encore.
    return game_service.create_game(db, payload)


@router.patch("/{game_id}", response_model=GameRead)
def update_game(game_id: int, payload: GameUpdate, db: Session = Depends(get_db)):
    """Modifie partiellement un jeu existant.

    Seuls les champs présents dans le corps de la requête sont modifiés, les
    autres gardent leur valeur. Répond 404 si le jeu n'existe pas.
    """
    # PATCH et non PUT, d'où le schéma `GameUpdate` dont tous les champs sont
    # facultatifs. C'est le service qui distingue « champ absent » de « champ
    # mis à null », grâce à model_dump(exclude_unset=True).
    return game_service.update_game(db, game_id, payload)


# Deux précisions liées : `status_code=204` (NO CONTENT) annonce une réponse
# sans corps, et l'absence de `response_model` est donc volontaire. Un 204
# accompagné d'un corps JSON serait une réponse HTTP invalide.
@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(game_id: int, db: Session = Depends(get_db)):
    """Supprime un jeu du catalogue.

    Ne renvoie aucun corps de réponse. Répond 404 si le jeu n'existe pas.
    """
    # La fonction ne fait pas `return` : elle renvoie implicitement None, et
    # FastAPI produit une réponse 204 vide. Écrire `return None` serait
    # équivalent, mais l'absence de return rend l'intention plus visible.
    game_service.delete_game(db, game_id)
