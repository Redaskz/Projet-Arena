"""Accès aux données de la ressource `games`.

GABARIT D'ARCHITECTURE : la couche `repositories` ne fait QUE parler à la base
de données. Elle contient toutes les requêtes SQL du projet, et rien d'autre.

Ce qu'on ne met JAMAIS ici :
- des HTTPException : le repository ignore qu'il existe une API HTTP. Si un jeu
  n'existe pas, il renvoie None, et c'est le service qui décide que cela vaut
  un 404. Ainsi ces fonctions restent réutilisables ailleurs (seed, tests,
  script de maintenance) sans traîner le vocabulaire du web.
- des règles métier : « seul le capitaine peut supprimer » est une décision,
  pas une requête. Elle appartient au service.
- des schémas Pydantic : le repository reçoit des types Python simples
  (dict, int, str) et renvoie des objets SQLAlchemy.

Toutes les fonctions prennent la session `db` en premier argument. Cette session
est fournie par `get_db` (fichier de Victor) et représente la conversation en
cours avec PostgreSQL : on y accumule des opérations, puis `commit()` les écrit
réellement en base.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.game import Game, GameGenre


def list_games(
    db: Session,
    genre: GameGenre | None = None,
    platform: str | None = None,
    search: str | None = None,
) -> list[Game]:
    """Renvoie les jeux du catalogue, filtrés par les critères fournis.

    Les trois filtres sont facultatifs et se cumulent. Aucun filtre fourni
    signifie « tout le catalogue ».
    """
    # `select(Game)` est la syntaxe SQLAlchemy 2.x. Elle construit une requête
    # sans l'exécuter : on peut donc l'enrichir progressivement avant l'envoi.
    query = select(Game)

    # On ajoute une condition SEULEMENT si le paramètre a été fourni.
    # C'est le point important de cette fonction : plutôt que d'écrire quatre
    # requêtes différentes pour toutes les combinaisons de filtres, on part
    # d'une requête de base et on empile les conditions présentes.
    if genre is not None:
        query = query.where(Game.genre == genre)

    if platform is not None:
        # `ilike` = comparaison texte insensible à la casse (le i de insensitive).
        # Les % encadrants signifient « contient », donc "ps" trouve "PS5".
        query = query.where(Game.platform.ilike(f"%{platform}%"))

    if search is not None:
        query = query.where(Game.name.ilike(f"%{search}%"))

    # Tri stable par nom : sans ORDER BY, PostgreSQL ne garantit aucun ordre,
    # et l'affichage du catalogue pourrait changer d'un rafraîchissement à l'autre.
    query = query.order_by(Game.name)

    # `execute` envoie la requête. `scalars()` demande les objets Game eux-mêmes
    # plutôt que des lignes de résultat contenant un objet chacune.
    # `all()` renvoie la liste complète.
    return list(db.execute(query).scalars().all())


def get_game_by_id(db: Session, game_id: int) -> Game | None:
    """Renvoie un jeu par son identifiant, ou None s'il n'existe pas.

    On renvoie None et non une exception : décider qu'un jeu introuvable
    mérite un 404 est une règle métier, donc c'est au service de le faire.
    """
    # `db.get()` est le raccourci de SQLAlchemy pour une recherche par clé
    # primaire. Plus court qu'un select().where(Game.id == game_id) et plus
    # rapide, car il regarde d'abord si l'objet est déjà chargé en mémoire.
    return db.get(Game, game_id)


def create_game(db: Session, data: dict) -> Game:
    """Insère un nouveau jeu et renvoie l'objet créé.

    `data` est un dictionnaire de champs déjà validés par Pydantic et
    complétés par le service (notamment les champs RAWG).
    """
    # Game(**data) construit l'objet en dépliant le dictionnaire :
    # {"name": "CS2", "genre": ...} devient Game(name="CS2", genre=...).
    game = Game(**data)

    # Les trois étapes de toute écriture, à connaître par cœur :
    db.add(game)  # 1. je place l'objet dans la session, rien n'est encore écrit
    db.commit()  # 2. j'envoie réellement l'INSERT à PostgreSQL
    db.refresh(game)  # 3. je relis la ligne pour récupérer ce que la base a
    #                    rempli elle-même : l'id auto-incrémenté et created_at.
    #                    Sans ce refresh, game.id vaudrait None et la réponse
    #                    de l'API serait invalide.
    return game


def update_game(db: Session, game: Game, data: dict) -> Game:
    """Modifie un jeu existant et renvoie l'objet à jour.

    `game` est un objet déjà récupéré par le service (donc déjà vérifié comme
    existant), et `data` ne contient QUE les champs réellement envoyés par le
    client, grâce au model_dump(exclude_unset=True) appliqué dans le service.
    """
    # setattr(objet, "name", valeur) équivaut à objet.name = valeur, mais
    # permet d'utiliser un nom de champ contenu dans une variable. C'est ce qui
    # rend cette fonction valable pour n'importe quelle combinaison de champs
    # modifiés, sans écrire un if par champ.
    for field, value in data.items():
        setattr(game, field, value)

    # Pas de db.add() ici : l'objet vient de la session, SQLAlchemy suit déjà
    # ses modifications et générera l'UPDATE tout seul au commit.
    db.commit()
    db.refresh(game)
    return game


def delete_game(db: Session, game: Game) -> None:
    """Supprime un jeu.

    Ne renvoie rien : la route répondra 204, c'est-à-dire « c'est fait, et il
    n'y a rien à afficher ».
    """
    db.delete(game)
    db.commit()
