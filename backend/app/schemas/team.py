"""Schémas Pydantic de la ressource `teams`.

Construit sur le gabarit de `schemas/game.py` : cette couche définit le CONTRAT
de l'API, c'est-à-dire ce que le client a le droit d'envoyer et ce que l'API
renvoie. Elle ne connaît ni la base de données ni les règles métier.

Un schéma par usage, jamais un seul pour les trois :
- TeamCreate : ce que le client envoie pour créer
- TeamUpdate : ce que le client envoie pour modifier (tout est facultatif)
- TeamRead   : ce que l'API renvoie
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# Ce que le client envoie à la création d'une équipe (POST /teams).
class TeamCreate(BaseModel):
    # `...` signifie « obligatoire ». min_length=1 empêche la chaîne vide, que
    # `str` seul accepterait. Toute violation déclenche un 422 automatique,
    # avant même d'entrer dans le routeur.
    # L'unicité du nom n'est PAS vérifiable ici : Pydantic ne connaît pas la
    # base. C'est le service qui interroge PostgreSQL et répond 409.
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nom de l'équipe, entre 1 et 100 caractères. Doit être unique.",
    )
    tag: str = Field(
        ...,
        min_length=2,
        max_length=10,
        description="Trigramme de l'équipe, entre 2 et 10 caractères. Exemple : « NAVI ».",
    )
    # `gt=0` (strictement supérieur à 0) et non `ge=0` : les identifiants
    # PostgreSQL commencent à 1, donc 0 et les négatifs sont refusés en 422
    # plutôt que d'aller chercher en base une ligne qui ne peut pas exister.
    game_id: int = Field(
        ...,
        gt=0,
        description="Identifiant du jeu sur lequel l'équipe concourt. Le jeu doit exister.",
    )
    captain_id: int = Field(
        ...,
        gt=0,
        description="Identifiant de l'utilisateur capitaine de l'équipe.",
    )

    # json_schema_extra n'a aucun effet sur la validation : il alimente
    # uniquement la documentation. Swagger pré-remplit « Try it out » avec cet
    # exemple, ce qui rend l'API testable en un clic.
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Natus Vincere",
                "tag": "NAVI",
                "game_id": 1,
                "captain_id": 1,
            }
        }
    )


# Ce que le client envoie pour modifier une équipe existante (PATCH /teams/{id}).
class TeamUpdate(BaseModel):
    # PATCH et non PUT : le client n'envoie que les champs qu'il veut changer.
    # Tous les champs sont donc facultatifs. C'est le service qui distingue
    # « champ absent » de « champ mis à null », avec model_dump(exclude_unset=True).
    name: str | None = Field(
        None, min_length=1, max_length=100, description="Nouveau nom de l'équipe."
    )
    tag: str | None = Field(
        None, min_length=2, max_length=10, description="Nouveau trigramme de l'équipe."
    )
    game_id: int | None = Field(None, gt=0, description="Nouveau jeu de l'équipe.")
    captain_id: int | None = Field(
        None, gt=0, description="Nouveau capitaine de l'équipe."
    )


# Ce que l'API renvoie pour une équipe (GET, et réponse des POST/PATCH).
class TeamRead(BaseModel):
    # from_attributes=True autorise Pydantic à lire un objet Python par ses
    # attributs (team.name) et non seulement un dictionnaire (team["name"]).
    # C'est ce qui permet de renvoyer directement l'objet SQLAlchemy retourné
    # par le repository, sans le convertir à la main.
    model_config = ConfigDict(from_attributes=True)

    # Champs remplis par le serveur, jamais par le client : c'est pourquoi ils
    # n'apparaissent ni dans TeamCreate ni dans TeamUpdate.
    id: int
    created_at: datetime

    # Champs saisis par l'utilisateur.
    name: str
    tag: str
    game_id: int
    captain_id: int
