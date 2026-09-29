"""
Service de génération du calendrier d'un tournoi (fonctionnalité avancée n°1).

À partir d'un tournoi, on construit un championnat « chacun contre chacun »
(round-robin) : chaque équipe rencontre toutes les autres exactement une fois,
et les rencontres sont réparties en journées (rounds) numérotées à partir de 1.

Comme tout service, c'est la seule couche qui lève des HTTPException ; les
lectures et écritures passent par les repositories.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.match import Match, MatchStatus
from app.models.team import Team
from app.repositories import match as match_repository
from app.repositories import team as team_repository
from app.repositories import tournament as tournament_repository

# Uniquement des repositories, aucun autre service : un service qui en importe
# un autre finit par créer des imports circulaires.


def _build_round_robin(
    team_ids: list[int],
) -> list[list[tuple[int, int]]]:
    """
    Répartit toutes les rencontres possibles en rounds, par la méthode du
    cercle (« circle method »), l'algorithme classique des calendriers de
    championnat.

    Pourquoi cette méthode plutôt que de simplement lister toutes les paires :
    une liste brute des n(n-1)/2 paires ne dit pas QUAND jouer chaque match, et
    une équipe pourrait devoir jouer plusieurs fois dans la même journée. La
    méthode du cercle garantit qu'à chaque round, chaque équipe joue au plus
    une fois, avec le nombre minimal de rounds.

    Principe, illustré avec 6 équipes numérotées 1 à 6 :

        On les dispose sur deux rangées, la seconde lue à l'envers :

            1  2  3                round 1 : 1-6, 2-5, 3-4
            6  5  4

        On FIXE la première équipe et on fait tourner toutes les autres
        d'un cran, comme les aiguilles d'une montre :

            1  6  2                round 2 : 1-5, 6-4, 2-3
            5  4  3

        Et ainsi de suite. Après n-1 rotations, chaque équipe a rencontré
        toutes les autres exactement une fois, sans doublon : c'est le fait de
        garder une équipe fixe qui empêche de retomber sur une paire déjà vue.

    Nombre impair d'équipes : on ajoute une équipe fictive (None). L'équipe
    tirée contre elle est « exemptée » ce round-là (elle ne joue pas), et le
    match fictif n'est pas créé. Avec 5 équipes, on obtient donc 5 rounds de
    2 matchs, et chaque équipe est exemptée une fois.

    Résultat : n-1 rounds si n est pair, n rounds si n est impair, et au total
    n(n-1)/2 matchs dans les deux cas.
    """

    slots: list[int | None] = list(team_ids)

    if len(slots) % 2 == 1:
        slots.append(None)

    slot_count = len(slots)
    rounds: list[list[tuple[int, int]]] = []

    for round_index in range(slot_count - 1):
        pairings: list[tuple[int, int]] = []

        # On apparie le i-ème élément avec son symétrique en partant de la
        # fin : c'est la lecture « rangée du haut / rangée du bas » du schéma.
        for i in range(slot_count // 2):
            home = slots[i]
            away = slots[slot_count - 1 - i]

            if home is None or away is None:
                continue

            # L'équipe fixe (i == 0) serait sinon toujours « équipe A ». On
            # alterne son côté un round sur deux pour équilibrer qui est
            # nommé en premier sur la feuille de match.
            if i == 0 and round_index % 2 == 1:
                home, away = away, home

            pairings.append((home, away))

        rounds.append(pairings)

        # Rotation : la première case reste fixe, la dernière passe en
        # deuxième position et tout le reste glisse d'un cran vers la droite.
        slots = [slots[0], slots[-1], *slots[1:-1]]

    return rounds


def generate_schedule(
    db: Session,
    tournament_id: int,
) -> list[Match]:
    """
    Génère et enregistre le calendrier complet d'un tournoi.

    - 404 si le tournoi n'existe pas ;
    - 409 si des matchs existent déjà (on ne génère qu'une fois, pour ne pas
      doubler le calendrier ni écraser des scores déjà saisis) ;
    - 400 s'il y a moins de 2 équipes, car aucun match n'est alors possible.
    """

    tournament = tournament_repository.get_tournament_by_id(
        db,
        tournament_id,
    )

    if tournament is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournoi introuvable.",
        )

    # 409 et non 400 : la requête est correcte, c'est l'état de la base
    # (calendrier déjà présent) qui empêche de la satisfaire.
    if match_repository.list_matches(db, tournament_id=tournament_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Le calendrier de ce tournoi a déjà été généré.",
        )

    # Il n'existe pas encore de table d'inscription (registrations) : les
    # équipes « inscrites » sont donc celles rattachées au jeu du tournoi.
    # Le jour où les inscriptions existeront, seule cette ligne changera.
    teams: list[Team] = team_repository.list_teams(
        db,
        game_id=tournament.game_id,
    )

    if len(teams) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Il faut au moins 2 équipes inscrites pour générer un calendrier.",
        )

    rounds = _build_round_robin([team.id for team in teams])

    # `start=1` : les rounds sont numérotés à partir de 1 pour l'affichage
    # (« Journée 1 »), et le schéma MatchCreate impose d'ailleurs round >= 1.
    matches_data = [
        {
            "tournament_id": tournament_id,
            "round": round_number,
            "team_a_id": team_a_id,
            "team_b_id": team_b_id,
            "status": MatchStatus.scheduled,
        }
        for round_number, pairings in enumerate(rounds, start=1)
        for team_a_id, team_b_id in pairings
    ]

    # Un seul appel, donc un seul commit : soit tout le calendrier est
    # enregistré, soit rien ne l'est.
    return match_repository.create_matches(
        db,
        matches_data,
    )
