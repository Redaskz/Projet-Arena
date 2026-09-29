"""
Service de calcul du classement d'un tournoi (fonctionnalité avancée n°2).

Le classement est calculé À LA VOLÉE à chaque appel, à partir des matchs
joués : aucune table de classement, aucune écriture en base.

Pourquoi ne pas le stocker : un classement enregistré serait une copie des
scores, qu'il faudrait mettre à jour à chaque saisie, correction ou
suppression de match. Au moindre oubli, les deux divergeraient. En le
recalculant, les matchs restent l'unique source de vérité, et le coût est
négligeable pour quelques dizaines de matchs par tournoi.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.match import MatchStatus
from app.repositories import match as match_repository
from app.repositories import tournament as tournament_repository
from app.schemas.standing import StandingRead

# Barème classique du football, repris par la plupart des championnats
# e-sport en format ligue. Regroupé ici pour être modifié en un seul endroit.
POINTS_WIN = 3
POINTS_DRAW = 1
POINTS_LOSS = 0


def compute_standings(
    db: Session,
    tournament_id: int,
) -> list[StandingRead]:
    """
    Calcule le classement d'un tournoi.

    Trié par points décroissants, puis par différence de buts décroissante.
    Lève une 404 si le tournoi n'existe pas : sans cela, un tournoi inconnu
    renverrait un classement vide en 200, indiscernable d'un tournoi qui n'a
    simplement pas encore commencé.
    """

    if tournament_repository.get_tournament_by_id(db, tournament_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournoi introuvable.",
        )

    matches = match_repository.list_matches(
        db,
        tournament_id=tournament_id,
    )

    # Une entrée par équipe apparaissant dans le calendrier, y compris celles
    # qui n'ont encore joué aucun match : elles figurent au classement avec
    # zéro partout, comme dans un vrai championnat en début de saison.
    table: dict[int, dict] = {}

    for match in matches:
        for team in (match.team_a, match.team_b):
            table.setdefault(
                team.id,
                {
                    "team_id": team.id,
                    "team_name": team.name,
                    "played": 0,
                    "wins": 0,
                    "draws": 0,
                    "losses": 0,
                    "points": 0,
                    "goals_for": 0,
                    "goals_against": 0,
                },
            )

    for match in matches:
        # Seuls les matchs joués comptent. On ignore aussi un match marqué
        # « played » sans score : la donnée est incohérente, et la compter
        # comme un 0-0 fausserait le classement sans que personne le voie.
        if (
            match.status != MatchStatus.played
            or match.score_a is None
            or match.score_b is None
        ):
            continue

        # Chaque match est traité des deux points de vue : les buts marqués
        # par l'un sont les buts encaissés par l'autre.
        for team_id, scored, conceded in (
            (match.team_a_id, match.score_a, match.score_b),
            (match.team_b_id, match.score_b, match.score_a),
        ):
            row = table[team_id]
            row["played"] += 1
            row["goals_for"] += scored
            row["goals_against"] += conceded

            if scored > conceded:
                row["wins"] += 1
                row["points"] += POINTS_WIN
            elif scored == conceded:
                row["draws"] += 1
                row["points"] += POINTS_DRAW
            else:
                row["losses"] += 1
                row["points"] += POINTS_LOSS

    standings = [
        StandingRead(
            **row,
            goal_difference=row["goals_for"] - row["goals_against"],
        )
        for row in table.values()
    ]

    # Clé de tri négative pour obtenir un ordre décroissant sur les deux
    # critères demandés. Le nom de l'équipe sert de dernier départage, afin
    # que deux équipes à égalité parfaite apparaissent toujours dans le même
    # ordre d'un appel à l'autre.
    standings.sort(
        key=lambda standing: (
            -standing.points,
            -standing.goal_difference,
            standing.team_name,
        )
    )

    return standings
