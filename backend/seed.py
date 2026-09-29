"""Script de peuplement de la base Arena, pour la démonstration.

À lancer depuis le dossier backend/, une fois PostgreSQL démarré :

    python seed.py

Le script crée les tables manquantes puis insère un jeu de données cohérent :
des jeux, des équipes rattachées à ces jeux, et des joueurs rattachés à ces
équipes. La démonstration ne part donc pas d'une base vide.

POURQUOI CE SCRIPT PASSE PAR LES REPOSITORIES et non par du SQL écrit à la main :
c'est exactement la raison pour laquelle la couche `repositories` ne contient
aucune HTTPException. Elle ne sait pas qu'une API HTTP existe, donc elle est
réutilisable ici, dans un script lancé en ligne de commande, sans rien
adapter. Si les requêtes avaient été écrites dans les routeurs, il faudrait les
recopier dans ce fichier.

En revanche le script n'appelle PAS les services : ceux-ci lèvent des
HTTPException, un vocabulaire qui n'a aucun sens hors d'une requête web. Les
quelques vérifications utiles au seed sont donc faites ici, en clair.

Le script est IDEMPOTENT : relancé sur une base déjà peuplée, il ne duplique
rien et ne supprime rien. On peut donc le lancer sans crainte juste avant la
soutenance.
"""

from sqlalchemy import inspect, text
from sqlalchemy.exc import NoReferencedTableError

from app.core.database import Base, SessionLocal, engine

# Les modules de modèles doivent être importés AVANT create_all, même si on
# n'utilise pas directement les classes ici. C'est leur import qui les
# enregistre dans Base.metadata ; sans lui, create_all ne verrait aucune table
# à créer et ne ferait rien, sans le moindre message d'erreur.
from app.models import game as game_model  # noqa: F401  (enregistre la table games)
from app.models import player as player_model  # noqa: F401  (table players)
from app.models import team as team_model  # noqa: F401  (table teams)
from app.repositories import game as game_repository
from app.repositories import player as player_repository
from app.repositories import team as team_repository


# --- Les données de démonstration ---------------------------------------------
# Elles sont regroupées en haut du fichier, sous forme de simples listes de
# dictionnaires, pour qu'on puisse les relire ou les compléter sans toucher à la
# logique d'insertion plus bas.

# Le genre est écrit en simple chaîne ("fps") et non GameGenre.fps : c'est
# possible parce que dans l'enum, le NOM du membre est identique à sa VALEUR
# (voir le commentaire de GameGenre dans models/game.py). SQLAlchemy reconnaît
# donc la chaîne sans conversion, et ces données restent lisibles telles quelles.
GAMES = [
    {"name": "Counter-Strike 2", "genre": "fps", "platform": "PC", "team_size": 5},
    {"name": "League of Legends", "genre": "moba", "platform": "PC", "team_size": 5},
    {"name": "Rocket League", "genre": "sport", "platform": "PC, PS5", "team_size": 3},
    {"name": "Street Fighter 6", "genre": "fighting", "platform": "PC, PS5", "team_size": 1},
    {"name": "Fortnite", "genre": "battle_royale", "platform": "PC, PS5, Switch", "team_size": 4},
]

# Les équipes désignent leur jeu par son NOM et non par un identifiant : les id
# sont attribués par PostgreSQL à l'insertion, on ne peut donc pas les écrire à
# l'avance. La correspondance nom -> id est faite au moment de l'insertion.
TEAMS = [
    {"name": "Natus Vincere", "tag": "NAVI", "game": "Counter-Strike 2"},
    {"name": "FaZe Clan", "tag": "FAZE", "game": "Counter-Strike 2"},
    {"name": "G2 Esports", "tag": "G2", "game": "League of Legends"},
    {"name": "T1", "tag": "T1", "game": "League of Legends"},
    {"name": "Karmine Corp", "tag": "KC", "game": "Rocket League"},
]

# Même principe : les joueurs désignent leur équipe par son nom.
# Les effectifs respectent le `team_size` du jeu correspondant (5 pour CS2 et
# League of Legends, 3 pour Rocket League), pour que les données restent
# crédibles pendant la démonstration.
PLAYERS = [
    # Natus Vincere — Counter-Strike 2
    {"gamertag": "s1mple", "role": "AWPer", "country": "Ukraine", "team": "Natus Vincere"},
    {"gamertag": "b1t", "role": "Rifler", "country": "Ukraine", "team": "Natus Vincere"},
    {"gamertag": "iM", "role": "Rifler", "country": "Roumanie", "team": "Natus Vincere"},
    {"gamertag": "jL", "role": "Rifler", "country": "Lituanie", "team": "Natus Vincere"},
    {"gamertag": "Aleksib", "role": "IGL", "country": "Finlande", "team": "Natus Vincere"},
    # FaZe Clan — Counter-Strike 2
    {"gamertag": "karrigan", "role": "IGL", "country": "Danemark", "team": "FaZe Clan"},
    {"gamertag": "rain", "role": "Rifler", "country": "Norvège", "team": "FaZe Clan"},
    {"gamertag": "frozen", "role": "Rifler", "country": "Slovaquie", "team": "FaZe Clan"},
    {"gamertag": "ropz", "role": "Rifler", "country": "Estonie", "team": "FaZe Clan"},
    {"gamertag": "broky", "role": "AWPer", "country": "Lettonie", "team": "FaZe Clan"},
    # G2 Esports — League of Legends
    {"gamertag": "BrokenBlade", "role": "Top", "country": "Allemagne", "team": "G2 Esports"},
    {"gamertag": "SkewMond", "role": "Jungle", "country": "Pays-Bas", "team": "G2 Esports"},
    {"gamertag": "Caps", "role": "Mid", "country": "Danemark", "team": "G2 Esports"},
    {"gamertag": "Hans Sama", "role": "Bot", "country": "France", "team": "G2 Esports"},
    {"gamertag": "Mikyx", "role": "Support", "country": "Slovénie", "team": "G2 Esports"},
    # T1 — League of Legends
    {"gamertag": "Doran", "role": "Top", "country": "Corée du Sud", "team": "T1"},
    {"gamertag": "Oner", "role": "Jungle", "country": "Corée du Sud", "team": "T1"},
    {"gamertag": "Faker", "role": "Mid", "country": "Corée du Sud", "team": "T1"},
    {"gamertag": "Gumayusi", "role": "Bot", "country": "Corée du Sud", "team": "T1"},
    {"gamertag": "Keria", "role": "Support", "country": "Corée du Sud", "team": "T1"},
    # Karmine Corp — Rocket League
    {"gamertag": "Vatira", "role": "Striker", "country": "France", "team": "Karmine Corp"},
    {"gamertag": "Alpha54", "role": "Midfielder", "country": "France", "team": "Karmine Corp"},
    {"gamertag": "Atow", "role": "Defender", "country": "France", "team": "Karmine Corp"},
]


def create_tables() -> None:
    """Crée les tables manquantes, ou explique précisément ce qui bloque.

    create_all ne touche pas aux tables qui existent déjà : il ne peut donc pas
    effacer de données. C'est ce qui rend cet appel sûr à répéter.
    """
    try:
        Base.metadata.create_all(bind=engine)

    # NoReferencedTableError signifie qu'une clé étrangère vise une table que
    # SQLAlchemy ne connaît pas, parce que le modèle correspondant n'a pas été
    # écrit. Aujourd'hui, c'est le cas de teams.captain_id -> users.id, en
    # attente de app/models/user.py.
    # On attrape l'erreur pour la traduire en message lisible : sans ce
    # try/except, le script s'arrêterait sur une trace technique de vingt lignes
    # où la vraie cause est difficile à repérer.
    except NoReferencedTableError as error:
        raise SystemExit(
            "Impossible de créer les tables : une clé étrangère vise une table "
            "qui n'est pas encore définie.\n"
            f"Détail SQLAlchemy : {error}\n\n"
            "Cause attendue : app/models/user.py est encore vide, alors que "
            "teams.captain_id référence users.id.\n"
            "Ce modèle est à écrire côté Victor. Dès qu'il existe, relancer "
            "simplement « python seed.py » : rien d'autre n'est à modifier."
        ) from error


def find_captain_ids(db, needed: int) -> list[int]:
    """Renvoie autant d'identifiants d'utilisateurs que d'équipes à créer.

    Chaque équipe a besoin d'un capitaine, et un capitaine est un utilisateur.
    La ressource `users` étant écrite par un autre membre du groupe, ce script
    ne crée aucun utilisateur : il se contente de réutiliser ceux qui sont déjà
    en base.

    C'est le seul endroit du projet où une requête SQL est écrite à la main
    plutôt que confiée à un repository, et c'est assumé : il n'existe pas encore
    de repositories/user.py à appeler. Cette fonction sera à remplacer par
    `user_repository.list_users(db)` le jour où ce fichier arrivera.
    """
    # On vérifie d'abord que la table existe, pour distinguer deux situations
    # très différentes : « la ressource users n'est pas encore livrée » et
    # « la table existe mais personne ne s'est inscrit ».
    if not inspect(engine).has_table("users"):
        raise SystemExit(
            "La table « users » n'existe pas en base : impossible de désigner "
            "un capitaine.\n"
            "app/models/user.py est à écrire côté Victor."
        )

    # `LIMIT` borné au nombre d'équipes : inutile de charger toute la table.
    rows = db.execute(
        text("SELECT id FROM users ORDER BY id LIMIT :limit"), {"limit": needed}
    ).all()

    captain_ids = [row[0] for row in rows]

    if not captain_ids:
        raise SystemExit(
            "Aucun utilisateur en base : impossible de désigner un capitaine "
            "d'équipe.\n"
            "Lancer d'abord le seed des utilisateurs (côté Victor), puis "
            "relancer « python seed.py »."
        )

    # S'il y a moins d'utilisateurs que d'équipes, on ne s'arrête pas pour si
    # peu : on réutilise les capitaines en boucle. Rien dans le modèle n'interdit
    # à une personne de capitainer deux équipes, et la démonstration reste
    # complète.
    while len(captain_ids) < needed:
        captain_ids.append(captain_ids[len(captain_ids) % len(rows)])

    return captain_ids


def seed_games(db) -> dict[str, int]:
    """Insère les jeux absents et renvoie la correspondance nom -> identifiant.

    La correspondance est renvoyée parce que les équipes ont besoin de l'id du
    jeu, attribué par PostgreSQL à l'insertion et donc inconnu à l'avance.
    """
    # On lit le catalogue existant UNE fois, plutôt qu'une requête par jeu.
    existing = {game.name: game.id for game in game_repository.list_games(db)}

    for payload in GAMES:
        # Le test d'existence par nom est ce qui rend le script idempotent :
        # relancé, il ne recrée pas un jeu déjà présent.
        if payload["name"] in existing:
            print(f"  = jeu déjà présent : {payload['name']}")
            continue

        # Les champs enrichis par RAWG (cover_url, rating, released_at, rawg_id)
        # ne sont pas fournis : ils resteront à NULL. C'est volontaire, le seed
        # ne doit pas dépendre d'un appel réseau pour fonctionner. Les jeux
        # créés ensuite via POST /games passent, eux, par le service et sont
        # donc enrichis normalement.
        game = game_repository.create_game(db, dict(payload))
        existing[game.name] = game.id
        print(f"  + jeu créé : {game.name}")

    return existing


def seed_teams(db, game_ids: dict[str, int], captain_ids: list[int]) -> dict[str, int]:
    """Insère les équipes absentes et renvoie la correspondance nom -> identifiant."""
    created: dict[str, int] = {}

    for position, payload in enumerate(TEAMS):
        # get_team_by_name est la fonction du repository écrite pour la règle
        # d'unicité du service : elle est réutilisée telle quelle ici.
        existing = team_repository.get_team_by_name(db, payload["name"])

        if existing is not None:
            print(f"  = équipe déjà présente : {payload['name']}")
            created[payload["name"]] = existing.id
            continue

        team = team_repository.create_team(
            db,
            {
                "name": payload["name"],
                "tag": payload["tag"],
                # Traduction du nom du jeu en identifiant réel.
                "game_id": game_ids[payload["game"]],
                # Un capitaine différent par équipe, dans l'ordre de la liste.
                "captain_id": captain_ids[position],
            },
        )
        created[team.name] = team.id
        print(f"  + équipe créée : {team.name} [{team.tag}]")

    return created


def seed_players(db, team_ids: dict[str, int]) -> None:
    """Insère les joueurs absents des équipes créées."""
    for payload in PLAYERS:
        team_id = team_ids[payload["team"]]

        # Idempotence : un joueur est considéré comme déjà présent si son pseudo
        # existe DANS CETTE ÉQUIPE. On ne teste pas le pseudo seul, car rien
        # n'interdit deux homonymes dans deux équipes différentes — c'est
        # d'ailleurs pourquoi la colonne `gamertag` n'est pas unique.
        already_there = any(
            player.gamertag == payload["gamertag"]
            for player in player_repository.list_players_by_team(db, team_id)
        )

        if already_there:
            print(f"  = joueur déjà présent : {payload['gamertag']}")
            continue

        player_repository.create_player(
            db,
            {
                "gamertag": payload["gamertag"],
                "role": payload["role"],
                "country": payload["country"],
                "team_id": team_id,
            },
        )
        print(f"  + joueur créé : {payload['gamertag']} ({payload['role']})")


def main() -> None:
    """Enchaîne la création des tables puis les trois vagues d'insertion.

    L'ordre est imposé par les clés étrangères : un jeu doit exister avant
    l'équipe qui s'y inscrit, et une équipe avant ses joueurs.
    """
    print("Création des tables manquantes...")
    create_tables()

    # On ouvre la session à la main, avec SessionLocal, et non via get_db :
    # get_db est un générateur conçu pour l'injection de dépendances de FastAPI.
    # Hors d'une requête web, on n'a rien pour le consommer.
    db = SessionLocal()

    try:
        print("\nJeux :")
        game_ids = seed_games(db)

        print("\nCapitaines :")
        captain_ids = find_captain_ids(db, needed=len(TEAMS))
        print(f"  = {len(captain_ids)} capitaine(s) retenu(s) : {captain_ids}")

        print("\nÉquipes :")
        team_ids = seed_teams(db, game_ids, captain_ids)

        print("\nJoueurs :")
        seed_players(db, team_ids)

        print("\nTerminé. La base contient un jeu de données de démonstration.")

    finally:
        # `finally` et non un simple appel en fin de bloc : la session doit être
        # rendue au pool même si une insertion échoue en cours de route.
        db.close()


# Cette condition n'est vraie que si le fichier est lancé directement
# (« python seed.py »), et fausse s'il est importé par un autre module. Sans
# elle, un simple `import seed` déclencherait le peuplement de la base.
if __name__ == "__main__":
    main()
