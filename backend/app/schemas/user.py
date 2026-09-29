"""Schémas Pydantic de la ressource `users`.

Construit sur le gabarit de schemas/game.py : un schéma par usage
(*Create, *Update, *Read).

RÈGLE ABSOLUE de cette ressource : `hashed_password` ne sort JAMAIS de l'API.
- En entrée, le client envoie `password` (en clair, protégé par HTTPS) et c'est
  le service qui le transforme en hash.
- En sortie, UserRead ne déclare tout simplement pas le champ. Comme toutes les
  routes utilisent response_model=UserRead, Pydantic filtre la réponse : même si
  l'objet SQLAlchemy contient le hash, il n'est jamais sérialisé.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


# Ce que le client envoie pour créer un compte (POST /auth/register, POST /users).
class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Nom d'utilisateur unique, entre 3 et 50 caractères.",
    )
    # EmailStr vérifie le format de l'adresse (bibliothèque email-validator).
    # Une adresse mal formée est rejetée en 422 avant d'entrer dans le routeur.
    email: EmailStr = Field(..., description="Adresse email unique.")
    # max_length=72 : bcrypt ignore tout ce qui dépasse 72 octets. Sans cette
    # borne, deux mots de passe différents mais de même début seraient acceptés
    # comme identiques.
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="Mot de passe en clair, entre 8 et 72 caractères. Il n'est jamais stocké tel quel.",
    )

    # Pas de champ `role` : à l'inscription, un client ne choisit pas son rôle,
    # sinon n'importe qui pourrait s'inscrire directement en admin.
    # Le rôle est toujours "player" à la création (voir services/user.py).

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "zywoo",
                "email": "zywoo@arena.fr",
                "password": "arena1234",
            }
        }
    )


# Ce que le client envoie pour modifier un compte (PATCH /users/{id}).
class UserUpdate(BaseModel):
    # Tous facultatifs, même logique PATCH que GameUpdate (exclude_unset).
    username: str | None = Field(
        None, min_length=3, max_length=50, description="Nouveau nom d'utilisateur."
    )
    email: EmailStr | None = Field(None, description="Nouvelle adresse email.")
    password: str | None = Field(
        None, min_length=8, max_length=72, description="Nouveau mot de passe en clair."
    )
    # Le champ existe dans le contrat, mais le service refuse (403) qu'un
    # non-admin le modifie : un joueur ne peut pas se promouvoir lui-même.
    role: UserRole | None = Field(
        None, description="Nouveau rôle. Modifiable uniquement par un admin."
    )


# Ce que l'API renvoie pour un utilisateur (GET /users, GET /auth/me, etc.).
class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Champs remplis par le serveur.
    id: int
    created_at: datetime
    role: UserRole

    # Champs saisis par l'utilisateur.
    username: str
    email: EmailStr

    # PAS de hashed_password, et PAS de password : voir la docstring du module.
