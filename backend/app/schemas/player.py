"""Schémas Pydantic de la ressource `players`.

Construit sur le gabarit de `schemas/game.py` : un schéma par usage, et les
champs remplis par le serveur n'apparaissent que dans *Read.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# Ce que le client envoie à la création d'un joueur (POST /players).
class PlayerCreate(BaseModel):
    gamertag: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Pseudo en jeu du joueur, entre 1 et 50 caractères.",
    )
    role: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Rôle du joueur dans l'équipe, texte libre car il dépend du jeu. Exemple : « AWPer », « jungler ».",
    )
    # Facultatif, donc `None` par défaut et pas de `...` : un joueur peut être
    # enregistré sans que son pays soit connu. La colonne est nullable en base
    # pour cette raison exacte.
    country: str | None = Field(
        None,
        max_length=50,
        description="Pays du joueur. Facultatif.",
    )
    # `gt=0` : les identifiants PostgreSQL commencent à 1, donc 0 et les
    # négatifs sont refusés en 422 sans aller interroger la base.
    team_id: int = Field(
        ...,
        gt=0,
        description="Identifiant de l'équipe du joueur. L'équipe doit exister.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "gamertag": "s1mple",
                "role": "AWPer",
                "country": "Ukraine",
                "team_id": 1,
            }
        }
    )


# Ce que le client envoie pour modifier un joueur existant (PATCH /players/{id}).
class PlayerUpdate(BaseModel):
    # Tous les champs facultatifs : seuls ceux réellement envoyés seront
    # modifiés. `team_id` en fait partie, car c'est précisément ce champ qu'on
    # change pour transférer un joueur d'une équipe à une autre.
    gamertag: str | None = Field(
        None, min_length=1, max_length=50, description="Nouveau pseudo du joueur."
    )
    role: str | None = Field(
        None, min_length=1, max_length=50, description="Nouveau rôle du joueur."
    )
    country: str | None = Field(
        None, max_length=50, description="Nouveau pays du joueur."
    )
    team_id: int | None = Field(
        None, gt=0, description="Nouvelle équipe du joueur, pour un transfert."
    )


# Ce que l'API renvoie pour un joueur (GET, et réponse des POST/PATCH).
class PlayerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Champs remplis par le serveur.
    id: int
    created_at: datetime

    # Champs saisis par l'utilisateur.
    gamertag: str
    role: str
    country: str | None
    team_id: int
