"""Modèle SQLAlchemy de la ressource `games`.

GABARIT D'ARCHITECTURE : ce fichier sert de référence aux autres ressources
du projet. La couche `models` décrit UNIQUEMENT la structure des tables.
Aucune règle métier et aucune requête ici : les requêtes vont dans
`repositories/`, les règles métier et les HTTPException dans `services/`.
"""

import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

# `Base` est la classe de base déclarative définie par Victor dans core/database.py.
# Tout modèle qui en hérite est automatiquement enregistré dans Base.metadata,
# ce qui permet à create_all() de créer la table correspondante au démarrage.
from app.core.database import Base


class GameGenre(str, enum.Enum):
    """Les 5 genres autorisés pour un jeu.

    Deux héritages volontaires :
    - `str` : un membre de cet enum EST une chaîne de caractères, donc il se
      sérialise directement en JSON ("fps") sans conversion manuelle.
    - `enum.Enum` : donne la liste fermée des valeurs valides, réutilisée
      telle quelle par Pydantic (validation des entrées) et par SQLAlchemy
      (type ENUM natif PostgreSQL).

    Les membres sont écrits en minuscules pour que le NOM du membre soit
    identique à sa VALEUR. C'est volontaire : par défaut SQLAlchemy stocke en
    base le nom du membre, pas sa valeur. En les gardant identiques, la valeur
    envoyée par l'API ("fps") est exactement celle stockée en base, ce qui
    évite un décalage déroutant lors d'un SELECT manuel ou d'un seed.
    """

    fps = "fps"
    moba = "moba"
    sport = "sport"
    fighting = "fighting"
    battle_royale = "battle_royale"


class Game(Base):
    """Un jeu du catalogue, autour duquel les équipes et tournois s'organisent."""

    # Le module est au singulier (models/game.py) mais la table est au pluriel :
    # une table contient plusieurs lignes. Même logique pour l'URL (/games).
    __tablename__ = "games"

    # --- Identifiant ---------------------------------------------------------
    # Entier auto-incrémenté par PostgreSQL. `primary_key=True` suffit :
    # SQLAlchemy en déduit l'auto-incrément et l'index unique.
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # --- Champs saisis par l'utilisateur -------------------------------------
    # `index=True` car le nom est la cible du filtre `search` du GET /games :
    # sans index, PostgreSQL parcourt toute la table à chaque recherche.
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Type ENUM natif PostgreSQL, construit à partir de la classe GameGenre.
    # La contrainte est donc appliquée DEUX fois : par Pydantic à l'entrée de
    # l'API, et par la base elle-même. Même un INSERT SQL direct ne peut pas
    # écrire un genre invalide.
    # `name="game_genre"` nomme explicitement le type créé dans PostgreSQL ;
    # sans ce nom, le type généré serait moins lisible dans la base.
    genre: Mapped[GameGenre] = mapped_column(
        Enum(GameGenre, name="game_genre"),
        nullable=False,
        index=True,  # indexé car c'est aussi un critère de filtrage du GET /games
    )

    # Texte libre et non un enum : un jeu peut sortir sur plusieurs supports
    # ("PC, PS5") et la liste des plateformes évolue trop souvent pour être figée.
    # nullable=True car le champ est facultatif à la création (voir GameCreate) :
    # la colonne doit accepter NULL, sinon l'INSERT échouerait en 500 alors que
    # Pydantic a laissé passer la requête.
    platform: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    # Nombre de joueurs par équipe. La borne 1..10 est validée côté Pydantic
    # (schemas/game.py) : c'est une règle de saisie, pas une règle de stockage.
    team_size: Mapped[int] = mapped_column(Integer, nullable=False)

    # --- Champs enrichis par l'API externe RAWG ------------------------------
    # Tous nullable : la création d'un jeu ne doit JAMAIS échouer parce que RAWG
    # est indisponible. Si l'appel échoue ou ne trouve rien, ces champs restent
    # à NULL et le jeu est créé quand même (voir services/game.py).
    # Ils sont créés dès maintenant, avant même le client RAWG : sans Alembic,
    # ajouter une colonne plus tard imposerait de supprimer et recréer la table.
    cover_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    released_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    rawg_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # --- Métadonnée technique ------------------------------------------------
    # `server_default=func.now()` : c'est PostgreSQL qui pose l'horodatage au
    # moment de l'INSERT, pas Python. Toutes les lignes utilisent donc la même
    # horloge, quelle que soit la machine qui exécute le code.
    # `timezone=True` stocke un timestamp avec fuseau, pour éviter toute
    # ambiguïté sur l'heure réelle d'un événement.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
