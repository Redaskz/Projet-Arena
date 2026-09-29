"""
Schéma Pydantic d'une ligne du classement d'un tournoi.

Fichier séparé de schemas/tournament.py : un classement n'est pas une
ressource stockée en base mais le résultat d'un calcul (voir
services/standings.py). Il n'a donc ni schéma Create ni Update, et pas de
`from_attributes` puisqu'il n'est construit à partir d'aucun objet SQLAlchemy.
"""

from pydantic import BaseModel


class StandingRead(BaseModel):
    """Une ligne du classement : le bilan d'une équipe dans un tournoi."""

    team_id: int

    # Le nom est renvoyé avec l'identifiant pour que le frontend puisse
    # afficher le tableau sans relancer une requête par équipe.
    team_name: str

    played: int
    wins: int
    draws: int
    losses: int
    points: int
    goals_for: int
    goals_against: int
    goal_difference: int
