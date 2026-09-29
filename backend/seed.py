"""Script de peuplement de la base Arena, pour la démonstration.

À lancer depuis le dossier backend/, une fois PostgreSQL démarré :

    python seed.py

Le script crée les tables manquantes puis insère un jeu de données cohérent :
des utilisateurs de démonstration, des jeux, des équipes rattachées à ces jeux,
des joueurs rattachés à ces équipes, deux tournois, le calendrier de l'un
d'eux et quelques scores. La démonstration ne part donc pas d'une base vide,
et le calendrier comme le classement ont quelque chose à montrer.

POURQUOI CE SCRIPT PASSE PAR LES REPOSITORIES et non par du SQL écrit à la main :
c'est exactement la raison pour laquelle la couche `repositories` ne contient
aucune HTTPException. Elle ne sait pas qu'une API HTTP existe, donc elle est
réutilisable ici, dans un script lancé en ligne de commande, sans rien
adapter. Si les requêtes avaient été écrites dans les routeurs, il faudrait les
recopier dans ce fichier.

En revanche le script n'appelle PAS les services : ceux-ci lèvent des
HTTPException, un vocabulaire qui n'a aucun sens hors d'une requête web. Les
quelques vérifications utiles au seed sont donc faites ici, en clair.

UNE EXCEPTION ASSUMÉE : le calendrier est généré par services/schedule.py.
L'algorithme de répartition en rounds vit dans ce service, et le recopier ici
créerait deux versions à maintenir. Surtout, c'est la fonctionnalité avancée
qu'on veut voir tourner pendant la démo. Le script vérifie en amont les cas
où le service lèverait une HTTPException (voir seed_schedule), pour qu'aucune
ne puisse remonter jusqu'ici.

Le script est IDEMPOTENT : relancé sur une base déjà peuplée, il ne duplique
rien et ne supprime rien. On peut donc le lancer sans crainte juste avant la
soutenance.
"""

from datetime import date, timedelta

from sqlalchemy.exc import NoReferencedTableError

from app.core.database import Base, SessionLocal, engine

# Le hachage est celui de l'application, importé tel quel : réécrire bcrypt
# ici donnerait deux façons de hacher, et un compte seedé risquerait de ne
# plus pouvoir se connecter le jour où l'une des deux change.
from app.core.security import hash_password

# Les modules de modèles doivent être importés AVANT create_all, même si on
# n'utilise pas directement les classes ici. C'est leur import qui les
# enregistre dans Base.metadata ; sans lui, create_all ne verrait aucune table
# à créer et ne ferait rien, sans le moindre message d'erreur.
from app.models import game as game_model  # noqa: F401  (enregistre la table games)
from app.models import player as player_model  # noqa: F401  (table players)
from app.models import team as team_model  # noqa: F401  (table teams)
from app.models import user as user_model  # noqa: F401  (table users)
from app.models.match import MatchStatus  # (enregistre aussi la table matches)
from app.models.tournament import TournamentStatus  # (et la table tournaments)
from app.models.user import UserRole
from app.repositories import game as game_repository
from app.repositories import match as match_repository
from app.repositories import player as player_repository
from app.repositories import team as team_repository
from app.repositories import tournament as tournament_repository
from app.repositories import user as user_repository
from app.services import schedule as schedule_service


# --- Les données de démonstration ---------------------------------------------
# Elles sont regroupées en haut du fichier, sous forme de simples listes de
# dictionnaires, pour qu'on puisse les relire ou les compléter sans toucher à la
# logique d'insertion plus bas.

# Identifiants de démonstration, regroupés ici pour être retrouvés d'un coup
# d'œil le jour de la soutenance (ils sont aussi réimprimés en fin de script).
# Ce sont des comptes de DÉMO : ces mots de passe ne doivent jamais servir sur
# une base réelle. Ils ne sont écrits en clair qu'ici ; en base, seul leur
# hash est stocké.
# Les adresses utilisent un vrai domaine de premier niveau (.fr) : EmailStr
# refuse des domaines réservés comme .local, et GET /users ou /auth/me
# échoueraient alors à la sérialisation de ces comptes.
DEMO_USERS = [
    {
        "username": "admin",
        "email": "admin@arena.fr",
        "password": "Admin1234!",
        "role": UserRole.admin,
    },
    {
        "username": "joueur",
        "email": "joueur@arena.fr",
        "password": "Joueur1234!",
        "role": UserRole.player,
    },
]

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
# Quatre équipes sur Counter-Strike 2 et non deux : c'est le jeu du tournoi en
# cours. Avec deux équipes, le round-robin ne produirait qu'UN match, et le
# classement ne pourrait jamais montrer à la fois une victoire, un nul et une
# défaite. Quatre équipes donnent 6 matchs répartis sur 3 rounds.
TEAMS = [
    {"name": "Natus Vincere", "tag": "NAVI", "game": "Counter-Strike 2"},
    {"name": "FaZe Clan", "tag": "FAZE", "game": "Counter-Strike 2"},
    {"name": "Team Vitality", "tag": "VIT", "game": "Counter-Strike 2"},
    {"name": "Team Spirit", "tag": "SPIRIT", "game": "Counter-Strike 2"},
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
    # Team Vitality — Counter-Strike 2
    {"gamertag": "apEX", "role": "IGL", "country": "France", "team": "Team Vitality"},
    {"gamertag": "ZywOo", "role": "AWPer", "country": "France", "team": "Team Vitality"},
    {"gamertag": "flameZ", "role": "Rifler", "country": "Israël", "team": "Team Vitality"},
    {"gamertag": "mezii", "role": "Rifler", "country": "Royaume-Uni", "team": "Team Vitality"},
    {"gamertag": "Spinx", "role": "Rifler", "country": "Israël", "team": "Team Vitality"},
    # Team Spirit — Counter-Strike 2
    {"gamertag": "chopper", "role": "IGL", "country": "Russie", "team": "Team Spirit"},
    {"gamertag": "donk", "role": "Rifler", "country": "Russie", "team": "Team Spirit"},
    {"gamertag": "sh1ro", "role": "AWPer", "country": "Russie", "team": "Team Spirit"},
    {"gamertag": "zont1x", "role": "Rifler", "country": "Ukraine", "team": "Team Spirit"},
    {"gamertag": "magixx", "role": "Rifler", "country": "Russie", "team": "Team Spirit"},
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

# Les dates sont calculées par rapport au jour du lancement plutôt qu'écrites
# en dur : un tournoi « en cours » qui aurait commencé il y a deux ans, ou un
# tournoi « à venir » déjà passé, rendrait la démo incohérente.
# `max_teams` est égal ou supérieur au nombre d'équipes du jeu déjà seedées :
# le calendrier prend toutes les équipes du jeu, un plafond plus bas serait
# donc contredit dès la génération.
TOURNAMENTS = [
    {
        # Tournoi en cours : c'est lui qui reçoit le calendrier et les scores.
        "name": "Arena Masters CS2",
        "game": "Counter-Strike 2",
        "status": TournamentStatus.ongoing,
        "start_date": date.today() - timedelta(days=7),
        "max_teams": 4,  # les 4 équipes CS2 de TEAMS
    },
    {
        # Tournoi à venir : laissé sans calendrier, pour que la démo puisse
        # montrer la génération en direct via POST /tournaments/{id}/schedule.
        "name": "Arena Cup League of Legends",
        "game": "League of Legends",
        "status": TournamentStatus.upcoming,
        "start_date": date.today() + timedelta(days=30),
        "max_teams": 4,  # 2 équipes LoL inscrites, 2 places encore libres
    },
]

# Scores posés sur les premiers matchs du calendrier, dans l'ordre (round,
# id). On vise les trois issues possibles : une victoire de l'équipe A, un nul,
# une victoire de l'équipe B. Le classement affiche donc au moins une
# victoire, un nul et une défaite. Les autres matchs restent « scheduled »,
# pour que la démo montre les deux états.
DEMO_SCORES = [(13, 8), (12, 12), (9, 13)]


def create_tables() -> None:
    """Crée les tables manquantes, ou explique précisément ce qui bloque.

    create_all ne touche pas aux tables qui existent déjà : il ne peut donc pas
    effacer de données. C'est ce qui rend cet appel sûr à répéter.
    """
    try:
        Base.metadata.create_all(bind=engine)

    # NoReferencedTableError signifie qu'une clé étrangère vise une table que
    # SQLAlchemy ne connaît pas, parce que le module du modèle correspondant
    # n'a pas été importé en haut de ce fichier.
    # On attrape l'erreur pour la traduire en message lisible : sans ce
    # try/except, le script s'arrêterait sur une trace technique de vingt lignes
    # où la vraie cause est difficile à repérer.
    except NoReferencedTableError as error:
        raise SystemExit(
            "Impossible de créer les tables : une clé étrangère vise une table "
            "qui n'est pas encore définie.\n"
            f"Détail SQLAlchemy : {error}\n\n"
            "Cause probable : un module de app/models/ n'est pas importé en "
            "haut de seed.py."
        ) from error


def seed_users(db, summary: dict[str, int]) -> list[int]:
    """Insère les comptes de démonstration absents et renvoie leurs identifiants.

    Les identifiants renvoyés servent de capitaines aux équipes, qui ont
    besoin d'un utilisateur existant (teams.captain_id -> users.id).
    """
    user_ids: list[int] = []

    for payload in DEMO_USERS:
        # Idempotence par nom d'utilisateur, colonne unique : relancé, le
        # script retrouve le compte au lieu de tenter un INSERT refusé.
        existing = user_repository.get_user_by_username(db, payload["username"])

        if existing is not None:
            print(f"  = utilisateur déjà présent : {payload['username']}")
            user_ids.append(existing.id)
            continue

        user = user_repository.create_user(
            db,
            {
                "username": payload["username"],
                "email": payload["email"],
                # Le repository attend un hash, jamais un mot de passe en clair :
                # c'est la même transformation que dans services/user.py.
                "hashed_password": hash_password(payload["password"]),
                "role": payload["role"],
            },
        )
        user_ids.append(user.id)
        summary["utilisateurs"] += 1
        print(f"  + utilisateur créé : {user.username} ({user.role.value})")

    return user_ids


def seed_games(db, summary: dict[str, int]) -> dict[str, int]:
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
        summary["jeux"] += 1
        print(f"  + jeu créé : {game.name}")

    return existing


def seed_teams(
    db, game_ids: dict[str, int], captain_ids: list[int], summary: dict[str, int]
) -> dict[str, int]:
    """Insère les équipes absentes et renvoie la correspondance nom -> identifiant.

    Il y a moins de comptes de démonstration que d'équipes : les capitaines
    sont donc réutilisés en boucle. Rien dans le modèle n'interdit à une
    personne de capitainer plusieurs équipes.
    """
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
                # Le modulo fait tourner les capitaines sur la liste des comptes.
                "captain_id": captain_ids[position % len(captain_ids)],
            },
        )
        created[team.name] = team.id
        summary["équipes"] += 1
        print(f"  + équipe créée : {team.name} [{team.tag}]")

    return created


def seed_players(db, team_ids: dict[str, int], summary: dict[str, int]) -> None:
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
        summary["joueurs"] += 1
        print(f"  + joueur créé : {payload['gamertag']} ({payload['role']})")


def seed_tournaments(
    db, game_ids: dict[str, int], summary: dict[str, int]
) -> dict[str, int]:
    """Insère les tournois absents et renvoie la correspondance nom -> identifiant."""
    created: dict[str, int] = {}

    for payload in TOURNAMENTS:
        # Le nom d'un tournoi est unique en base : c'est donc lui qui sert de
        # test d'existence, comme pour les équipes.
        existing = tournament_repository.get_tournament_by_name(db, payload["name"])

        if existing is not None:
            print(f"  = tournoi déjà présent : {payload['name']}")
            created[payload["name"]] = existing.id
            continue

        tournament = tournament_repository.create_tournament(
            db,
            {
                "name": payload["name"],
                "game_id": game_ids[payload["game"]],
                "status": payload["status"],
                "start_date": payload["start_date"],
                "max_teams": payload["max_teams"],
            },
        )
        created[tournament.name] = tournament.id
        summary["tournois"] += 1
        print(f"  + tournoi créé : {tournament.name} ({tournament.status.value})")

    return created


def seed_schedule(db, tournament_id: int, summary: dict[str, int]) -> None:
    """Génère le calendrier du tournoi en cours via le service, une seule fois.

    PIÈGE : generate_schedule lève une 409 si le tournoi a déjà des matchs.
    Au second lancement du seed, l'appel ferait donc remonter une
    HTTPException et arrêterait le script. On vérifie AVANT d'appeler, avec le
    même repository que le service, et on saute l'étape si le calendrier
    existe : l'idempotence est assurée sans attraper d'exception HTTP, ce qui
    aurait supposé que le script connaisse le vocabulaire du web.
    Les deux autres cas d'erreur du service (tournoi absent, moins de 2
    équipes) ne peuvent pas se produire ici : le tournoi vient d'être lu ou
    créé, et TEAMS fournit 4 équipes au jeu de ce tournoi.
    """
    if match_repository.list_matches(db, tournament_id=tournament_id):
        print("  = calendrier déjà généré, étape ignorée")
        return

    matches = schedule_service.generate_schedule(db, tournament_id)
    rounds = len({match.round for match in matches})
    summary["matchs"] += len(matches)
    print(f"  + calendrier généré : {len(matches)} matchs sur {rounds} rounds")


def seed_scores(db, tournament_id: int, summary: dict[str, int]) -> None:
    """Pose les scores de DEMO_SCORES sur les premiers matchs du tournoi.

    Passe par le repository et non par services/match.py : le service refuse
    de modifier le score d'un match déjà joué en levant une 409, ce qui ferait
    planter le second lancement. Ici on saute simplement ces matchs.
    """
    # list_matches trie par (round, id) : les matchs visés sont donc toujours
    # les mêmes d'un lancement à l'autre.
    matches = match_repository.list_matches(db, tournament_id=tournament_id)

    for match, (score_a, score_b) in zip(matches, DEMO_SCORES):
        label = f"{match.team_a.name} - {match.team_b.name}"

        # Idempotence : un match déjà joué n'est pas réécrit, même si son score
        # a été modifié à la main entre-temps pendant une répétition de démo.
        if match.status == MatchStatus.played:
            print(f"  = score déjà saisi : {label}")
            continue

        match_repository.update_match(
            db,
            match,
            {"score_a": score_a, "score_b": score_b, "status": MatchStatus.played},
        )
        summary["scores"] += 1
        print(f"  + score saisi : {label} {score_a}-{score_b}")


def main() -> None:
    """Enchaîne la création des tables puis les vagues d'insertion.

    L'ordre est imposé par les clés étrangères : un utilisateur doit exister
    avant l'équipe qu'il capitaine, un jeu avant ses équipes et ses tournois,
    une équipe avant ses joueurs, et un tournoi avant ses matchs.
    """
    print("Création des tables manquantes...")
    create_tables()

    # Compteurs de ce qui a RÉELLEMENT été créé pendant ce lancement : au
    # second passage ils restent à zéro, ce qui prouve d'un coup d'œil que
    # le script est idempotent.
    summary = {
        "utilisateurs": 0,
        "jeux": 0,
        "équipes": 0,
        "joueurs": 0,
        "tournois": 0,
        "matchs": 0,
        "scores": 0,
    }

    # On ouvre la session à la main, avec SessionLocal, et non via get_db :
    # get_db est un générateur conçu pour l'injection de dépendances de FastAPI.
    # Hors d'une requête web, on n'a rien pour le consommer.
    db = SessionLocal()

    try:
        print("\nUtilisateurs :")
        user_ids = seed_users(db, summary)

        print("\nJeux :")
        game_ids = seed_games(db, summary)

        print("\nÉquipes :")
        team_ids = seed_teams(db, game_ids, user_ids, summary)

        print("\nJoueurs :")
        seed_players(db, team_ids, summary)

        print("\nTournois :")
        tournament_ids = seed_tournaments(db, game_ids, summary)

        # Seul le premier tournoi de TOURNAMENTS (celui en cours) reçoit un
        # calendrier et des scores.
        ongoing_id = tournament_ids[TOURNAMENTS[0]["name"]]

        print("\nCalendrier :")
        seed_schedule(db, ongoing_id, summary)

        print("\nScores :")
        seed_scores(db, ongoing_id, summary)

        print("\nTerminé. Objets créés pendant ce lancement :")
        for resource, count in summary.items():
            print(f"  {resource:<13}: {count}")

        print("\nComptes de démonstration :")
        for payload in DEMO_USERS:
            print(
                f"  {payload['role'].value:<7} identifiant : {payload['username']:<8}"
                f" mot de passe : {payload['password']}"
            )

    finally:
        # `finally` et non un simple appel en fin de bloc : la session doit être
        # rendue au pool même si une insertion échoue en cours de route.
        db.close()


# Cette condition n'est vraie que si le fichier est lancé directement
# (« python seed.py »), et fausse s'il est importé par un autre module. Sans
# elle, un simple `import seed` déclencherait le peuplement de la base.
if __name__ == "__main__":
    main()
