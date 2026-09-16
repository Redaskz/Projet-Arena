"""Règles métier de la ressource `games`.

GABARIT D'ARCHITECTURE : la couche `services` contient les DÉCISIONS.
C'est la seule couche autorisée à lever des HTTPException.

Pourquoi ici et pas ailleurs :
- pas dans le repository, qui doit rester réutilisable hors du web (seed,
  tests, script de maintenance) et qui ne connaît donc pas les codes HTTP ;
- pas dans le routeur, qui doit rester une simple porte d'entrée. Si la règle
  était dans le routeur, elle ne s'appliquerait qu'à cette route précise et il
  faudrait la recopier ailleurs.

Le service est aussi la couche qui traduit Pydantic vers Python simple : il
reçoit un schéma, il transmet un dictionnaire au repository.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.external import rawg
from app.models.game import Game, GameGenre
from app.repositories import game as game_repository
from app.schemas.game import GameCreate, GameUpdate

# Le module du repository est importé sous le nom `game_repository` plutôt
# qu'en important ses fonctions une par une. Deux avantages : on évite un
# conflit de nom avec la classe `Game`, et à la lecture on voit immédiatement
# quelles lignes parlent à la base (game_repository.xxx) et lesquelles sont
# des règles métier.


def _get_game_or_404(db: Session, game_id: int) -> Game:
    """Récupère un jeu, ou interrompt la requête avec une erreur 404.

    Le préfixe `_` signale une fonction interne au module : elle est appelée
    par les autres fonctions de ce fichier, pas par le routeur.

    Cette petite fonction existe parce que la même vérification serait sinon
    recopiée dans get_game, update_game et delete_game. Trois copies, c'est
    trois occasions d'oublier de la mettre à jour.
    """
    game = game_repository.get_game_by_id(db, game_id)

    if game is None:
        # 404 NOT FOUND et non 400 BAD REQUEST : la requête du client est
        # parfaitement bien formée, c'est la ressource demandée qui n'existe
        # pas. Un 400 dirait à tort au client qu'il s'est trompé de syntaxe.
        # `raise` interrompt immédiatement le traitement : FastAPI attrape
        # l'exception et fabrique la réponse HTTP. Le code qui suit dans la
        # fonction appelante ne s'exécute pas.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            # Message en français : il peut être affiché tel quel à
            # l'utilisateur par le frontend.
            detail=f"Le jeu {game_id} n'existe pas.",
        )

    return game


def list_games(
    db: Session,
    genre: GameGenre | None = None,
    platform: str | None = None,
    search: str | None = None,
) -> list[Game]:
    """Renvoie le catalogue, éventuellement filtré.

    Ce service ne fait que transmettre au repository, et c'est normal : il n'y
    a aucune règle métier sur la consultation du catalogue. On garde quand même
    la couche, pour que le routeur n'appelle jamais directement un repository.
    Le jour où une règle apparaît (masquer les jeux désactivés, par exemple),
    elle a déjà sa place, et aucune autre couche ne bouge.
    """
    return game_repository.list_games(
        db, genre=genre, platform=platform, search=search
    )


def get_game(db: Session, game_id: int) -> Game:
    """Renvoie un jeu par son identifiant, ou lève une 404."""
    return _get_game_or_404(db, game_id)


def create_game(db: Session, payload: GameCreate) -> Game:
    """Crée un jeu et renvoie l'objet créé."""
    # model_dump() convertit le schéma Pydantic en dictionnaire Python.
    # Le repository reçoit ainsi des types simples et ne dépend pas de Pydantic.
    data = payload.model_dump()

    # Enrichissement par l'API externe RAWG : jaquette, note et date de sortie.
    # fetch_game_enrichment renvoie TOUJOURS les 4 clés, remplies si RAWG a
    # répondu, à None sinon. Il ne lève jamais d'exception : c'est ce qui
    # garantit qu'un jeu se crée même sans Internet, ou avec une clé RAWG
    # invalide. Aucun try/except n'est donc nécessaire ici, la protection est
    # entièrement dans external/rawg.py.
    # `update` fusionne ces 4 clés dans le dictionnaire des champs saisis.
    data.update(rawg.fetch_game_enrichment(payload.name))

    return game_repository.create_game(db, data)


def update_game(db: Session, game_id: int, payload: GameUpdate) -> Game:
    """Modifie partiellement un jeu existant."""
    # On vérifie d'abord l'existence : inutile de préparer une modification
    # pour une ressource absente.
    game = _get_game_or_404(db, game_id)

    # exclude_unset=True est le cœur du PATCH : le dictionnaire ne contient que
    # les champs RÉELLEMENT envoyés par le client. Un champ absent du corps de
    # la requête n'apparaît pas ici, donc il ne sera pas modifié.
    # Avec exclude_none=True on obtiendrait un résultat différent et faux :
    # un champ envoyé explicitement à null serait ignoré, et il deviendrait
    # impossible d'effacer une valeur.
    data = payload.model_dump(exclude_unset=True)

    # Corps vide : le client n'a rien demandé à changer. On renvoie le jeu tel
    # quel plutôt que de faire un UPDATE inutile en base.
    if not data:
        return game

    return game_repository.update_game(db, game, data)


def delete_game(db: Session, game_id: int) -> None:
    """Supprime un jeu, ou lève une 404 s'il n'existe pas.

    Ne renvoie rien : la route répondra 204 No Content.
    """
    game = _get_game_or_404(db, game_id)
    game_repository.delete_game(db, game)
