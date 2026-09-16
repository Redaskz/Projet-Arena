"""Schémas Pydantic de la ressource `games`.

GABARIT D'ARCHITECTURE : la couche `schemas` définit le CONTRAT de l'API,
c'est-à-dire ce que le client a le droit d'envoyer et ce que l'API renvoie.
Elle ne connaît ni la base de données ni les règles métier.

Règle à reproduire pour toutes les ressources : un schéma par usage.
- *Create : ce que le client envoie pour créer
- *Update : ce que le client envoie pour modifier (tout est facultatif)
- *Read   : ce que l'API renvoie

Ne jamais réutiliser un seul schéma pour les trois. Les champs remplis par le
serveur (id, created_at, données venues de RAWG) n'apparaissent que dans *Read :
si on les mettait dans *Create, un client pourrait inventer sa propre note ou
sa propre date de création.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

# L'enum est défini une seule fois, dans le modèle, et importé ici.
# Le dupliquer créerait deux listes de genres à maintenir en parallèle.
from app.models.game import GameGenre


# Ce que le client envoie à la création d'un jeu (POST /games).
class GameCreate(BaseModel):
    # `...` en premier argument de Field signifie « obligatoire ».
    # min_length=1 empêche la chaîne vide, que `str` seul accepterait.
    # Toute violation d'une de ces contraintes déclenche un 422 automatique :
    # c'est Pydantic qui rejette la requête, avant même d'entrer dans le routeur.
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nom du jeu, entre 1 et 100 caractères.",
    )
    genre: GameGenre = Field(
        ...,
        description="Genre du jeu. Valeurs autorisées : fps, moba, sport, fighting, battle_royale.",
    )
    platform: str | None = Field(
        None,
        max_length=100,
        description="Plateforme(s) du jeu, texte libre. Facultatif.",
    )
    team_size: int = Field(
        ...,
        ge=1,
        le=10,
        description="Nombre de joueurs par équipe, entre 1 et 10.",
    )

    # json_schema_extra n'a aucun effet sur la validation : il alimente
    # uniquement la documentation. Swagger pré-remplit le formulaire « Try it
    # out » avec cet exemple, ce qui rend l'API testable en un clic.
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Counter-Strike 2",
                "genre": "fps",
                "platform": "PC",
                "team_size": 5,
            }
        }
    )


# Ce que le client envoie pour modifier un jeu existant (PATCH /games/{id}).
class GameUpdate(BaseModel):
    # PATCH et non PUT : le client n'envoie que les champs qu'il veut changer.
    # Tous les champs sont donc facultatifs, avec None comme valeur par défaut.
    # Attention, `None` joue ici deux rôles différents, et c'est le service qui
    # les distingue avec model_dump(exclude_unset=True) :
    # - champ absent du corps de la requête     -> on n'y touche pas
    # - champ présent et explicitement à null   -> on veut l'effacer
    # exclude_unset regarde ce que le client a réellement envoyé, alors que
    # exclude_none confondrait les deux cas et rendrait tout effacement impossible.
    name: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="Nouveau nom du jeu.",
    )
    genre: GameGenre | None = Field(None, description="Nouveau genre du jeu.")
    platform: str | None = Field(
        None, max_length=100, description="Nouvelle plateforme du jeu."
    )
    team_size: int | None = Field(
        None, ge=1, le=10, description="Nouveau nombre de joueurs par équipe."
    )


# Ce que l'API renvoie pour un jeu (GET, et réponse des POST/PATCH).
class GameRead(BaseModel):
    # from_attributes=True autorise Pydantic à lire un objet Python par ses
    # attributs (game.name) et non seulement un dictionnaire (game["name"]).
    # C'est ce qui permet de renvoyer directement l'objet SQLAlchemy retourné
    # par le repository, sans le convertir à la main.
    # Syntaxe Pydantic v2 : model_config = ConfigDict(...), et non plus
    # l'ancienne classe interne `class Config` de Pydantic v1.
    model_config = ConfigDict(from_attributes=True)

    # Champs remplis par le serveur, jamais par le client.
    id: int
    created_at: datetime

    # Champs saisis par l'utilisateur.
    name: str
    genre: GameGenre
    platform: str | None
    team_size: int

    # Champs enrichis par l'API externe RAWG, tous facultatifs : ils restent à
    # null si RAWG est injoignable ou ne connaît pas le jeu. Ils sont en lecture
    # seule, d'où leur absence de GameCreate et de GameUpdate.
    cover_url: str | None
    rating: float | None
    released_at: date | None
    rawg_id: int | None
