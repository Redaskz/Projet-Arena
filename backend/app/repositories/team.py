"""Accès aux données de la ressource `teams`.

Construit sur le gabarit de `repositories/game.py` : cette couche ne fait QUE
parler à la base de données.

Ce qu'on ne met JAMAIS ici :
- des HTTPException : le repository ignore qu'il existe une API HTTP. Si une
  équipe n'existe pas, il renvoie None, et c'est le service qui décide que cela
  vaut un 404. Ces fonctions restent ainsi réutilisables par le seed, les tests
  ou un script de maintenance, sans traîner le vocabulaire du web.
- des règles métier : « deux équipes ne peuvent pas avoir le même nom » est une
  décision, pas une requête. Ici on sait seulement CHERCHER une équipe par son
  nom (get_team_by_name) ; c'est le service qui en tire une conclusion.
- des schémas Pydantic : le repository reçoit des types Python simples et
  renvoie des objets SQLAlchemy.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.team import Team


def list_teams(
    db: Session,
    game_id: int | None = None,
    search: str | None = None,
) -> list[Team]:
    """Renvoie les équipes, filtrées par les critères fournis.

    Les deux filtres sont facultatifs et se cumulent. Aucun filtre fourni
    signifie « toutes les équipes ».
    """
    # `select(Team)` construit la requête sans l'exécuter : on peut donc
    # l'enrichir progressivement avant de l'envoyer.
    query = select(Team)

    # On ajoute une condition SEULEMENT si le paramètre a été fourni. Plutôt
    # qu'une requête différente par combinaison de filtres, on part d'une
    # requête de base et on empile les conditions présentes.
    if game_id is not None:
        query = query.where(Team.game_id == game_id)

    if search is not None:
        # `ilike` = comparaison texte insensible à la casse (le i de
        # insensitive). Les % encadrants signifient « contient ».
        query = query.where(Team.name.ilike(f"%{search}%"))

    # Tri stable par nom : sans ORDER BY, PostgreSQL ne garantit aucun ordre et
    # l'affichage pourrait changer d'un rafraîchissement à l'autre.
    query = query.order_by(Team.name)

    return list(db.execute(query).scalars().all())


def get_team_by_id(db: Session, team_id: int) -> Team | None:
    """Renvoie une équipe par son identifiant, ou None si elle n'existe pas.

    On renvoie None et non une exception : décider qu'une équipe introuvable
    mérite un 404 est une règle métier, donc c'est au service de le faire.
    """
    # `db.get()` est le raccourci de SQLAlchemy pour une recherche par clé
    # primaire : plus court qu'un select().where() et plus rapide, car il
    # regarde d'abord si l'objet est déjà chargé en mémoire.
    return db.get(Team, team_id)


def get_team_by_name(db: Session, name: str) -> Team | None:
    """Renvoie l'équipe portant exactement ce nom, ou None.

    Cette fonction existe pour la règle d'unicité du nom appliquée par le
    service. Elle ne fait que CHERCHER : elle ne juge pas, et ne lève donc
    aucune exception si elle trouve quelque chose.
    """
    # Comparaison stricte avec `==` et non `ilike` : l'unicité est celle de la
    # colonne `unique=True` en base, qui est elle aussi sensible à la casse.
    # Utiliser `ilike` ici refuserait « navi » alors que PostgreSQL l'accepte,
    # et le service deviendrait plus strict que la base — deux règles
    # différentes pour la même contrainte.
    query = select(Team).where(Team.name == name)

    # `scalar_one_or_none()` et non `.all()` : on attend au plus une ligne,
    # puisque la colonne est unique. Cette méthode renvoie donc directement
    # l'objet ou None, sans liste intermédiaire à déballer.
    return db.execute(query).scalar_one_or_none()


def create_team(db: Session, data: dict) -> Team:
    """Insère une nouvelle équipe et renvoie l'objet créé.

    `data` est un dictionnaire de champs déjà validés par Pydantic et vérifiés
    par le service.
    """
    # Team(**data) construit l'objet en dépliant le dictionnaire :
    # {"name": "NAVI", "tag": ...} devient Team(name="NAVI", tag=...).
    team = Team(**data)

    # Les trois étapes de toute écriture :
    db.add(team)  # 1. je place l'objet dans la session, rien n'est encore écrit
    db.commit()  # 2. j'envoie réellement l'INSERT à PostgreSQL
    db.refresh(team)  # 3. je relis la ligne pour récupérer ce que la base a
    #                    rempli elle-même : l'id auto-incrémenté et created_at.
    #                    Sans ce refresh, team.id vaudrait None et la réponse
    #                    de l'API serait invalide.
    return team


def update_team(db: Session, team: Team, data: dict) -> Team:
    """Modifie une équipe existante et renvoie l'objet à jour.

    `team` est un objet déjà récupéré par le service (donc déjà vérifié comme
    existant), et `data` ne contient QUE les champs réellement envoyés par le
    client, grâce au model_dump(exclude_unset=True) appliqué dans le service.
    """
    # setattr(objet, "name", valeur) équivaut à objet.name = valeur, mais
    # permet d'utiliser un nom de champ contenu dans une variable. C'est ce qui
    # rend cette fonction valable pour n'importe quelle combinaison de champs
    # modifiés, sans écrire un if par champ.
    for field, value in data.items():
        setattr(team, field, value)

    # Pas de db.add() ici : l'objet vient de la session, SQLAlchemy suit déjà
    # ses modifications et générera l'UPDATE tout seul au commit.
    db.commit()
    db.refresh(team)
    return team


def delete_team(db: Session, team: Team) -> None:
    """Supprime une équipe.

    Ne renvoie rien : la route répondra 204, c'est-à-dire « c'est fait, et il
    n'y a rien à afficher ».

    Les joueurs de l'équipe disparaissent avec elle, grâce au
    `ondelete="CASCADE"` déclaré sur players.team_id : c'est PostgreSQL qui
    s'en charge, il n'y a donc aucune boucle de suppression à écrire ici.
    """
    db.delete(team)
    db.commit()
