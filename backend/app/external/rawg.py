"""Client de l'API externe RAWG.

GABARIT D'ARCHITECTURE : la couche `external` regroupe les clients des API
tierces. Elle ne connaît ni la base de données, ni les schémas Pydantic, ni
les codes HTTP de NOTRE API. Elle parle à un service extérieur et renvoie des
données Python simples.

RÈGLE ABSOLUE DE CE FICHIER : aucune fonction ici ne doit lever d'exception.
RAWG est un service tiers, sur Internet, que nous ne contrôlons pas. S'il est
lent, en panne, ou s'il ne connaît pas le jeu demandé, la création du jeu doit
se poursuivre normalement avec des champs vides. La démonstration devant le
jury ne peut pas dépendre de la disponibilité d'un site web extérieur.

C'est pour cela que toutes les erreurs sont attrapées ici et transformées en
« pas de données », plutôt que remontées à l'appelant.
"""

import logging
from datetime import date
from typing import Any

import httpx

from app.core.config import settings

# Un logger nommé d'après le module. Quand un enrichissement échoue, la trace
# indique `app.external.rawg`, donc on sait immédiatement d'où vient le message.
# On journalise au lieu de planter : l'incident est visible dans la console
# sans interrompre l'utilisateur.
logger = logging.getLogger(__name__)

RAWG_SEARCH_URL = "https://api.rawg.io/api/games"

# 5 secondes maximum. Sans timeout, httpx attendrait indéfiniment une réponse :
# un RAWG lent gèlerait la création de jeu et, de là, toute l'API.
RAWG_TIMEOUT_SECONDS = 5.0


def _empty_enrichment() -> dict[str, Any]:
    """Les quatre champs RAWG, tous vides.

    Cette valeur de repli est renvoyée dans TOUS les cas d'échec. La fonction
    publique renvoie donc toujours la même forme de dictionnaire, ce qui évite
    à l'appelant d'avoir à tester si l'enrichissement a fonctionné.
    """
    return {
        "cover_url": None,
        "rating": None,
        "released_at": None,
        "rawg_id": None,
    }


def _parse_released_date(value: Any) -> date | None:
    """Convertit la date texte de RAWG ("2023-09-27") en objet date Python.

    RAWG peut renvoyer None, une chaîne vide, ou une date mal formée pour un
    jeu dont la sortie n'est pas connue. Dans tous ces cas on renvoie None
    plutôt que de laisser l'erreur remonter.
    """
    if not isinstance(value, str):
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        logger.warning("RAWG a renvoyé une date illisible : %r", value)
        return None


def fetch_game_enrichment(name: str) -> dict[str, Any]:
    """Cherche un jeu sur RAWG et renvoie ses données d'enrichissement.

    Renvoie toujours un dictionnaire des 4 mêmes clés : cover_url, rating,
    released_at et rawg_id. Les valeurs sont à None si RAWG est injoignable,
    répond mal, ou ne connaît pas ce jeu.
    """
    try:
        response = httpx.get(
            RAWG_SEARCH_URL,
            params={
                # La clé d'API vient du .env via la configuration de Victor.
                # Elle n'apparaît jamais en dur dans le code, donc jamais dans
                # un commit.
                "key": settings.rawg_api_key,
                "search": name,
                # On ne veut que le meilleur résultat : inutile de télécharger
                # vingt jeux pour n'en garder qu'un.
                "page_size": 1,
            },
            timeout=RAWG_TIMEOUT_SECONDS,
        )
        # Transforme un code 4xx ou 5xx en exception, attrapée juste en dessous.
        # Sans cette ligne, une réponse « 401 clé invalide » serait traitée
        # comme un succès et on tenterait de lire un JSON d'erreur.
        response.raise_for_status()
        payload = response.json()

    # httpx.HTTPError est la classe parente de toutes les erreurs httpx :
    # délai dépassé, DNS injoignable, pas de réseau, code 4xx/5xx. Une seule
    # clause suffit donc à couvrir tous les cas de panne réseau.
    except httpx.HTTPError as error:
        logger.warning("RAWG injoignable pour %r : %s", name, error)
        return _empty_enrichment()

    # Réponse reçue mais corps illisible : RAWG a renvoyé du HTML ou du vide
    # au lieu du JSON attendu.
    except ValueError:
        logger.warning("RAWG a renvoyé une réponse illisible pour %r", name)
        return _empty_enrichment()

    # `or []` protège contre deux cas d'un coup : la clé "results" absente,
    # et la clé présente mais valant None.
    results = payload.get("results") or []

    if not results:
        # Ce n'est pas une panne : RAWG a répondu correctement, il ne connaît
        # simplement pas ce jeu. On journalise en info, pas en warning.
        logger.info("Aucun résultat RAWG pour %r", name)
        return _empty_enrichment()

    first_result = results[0]

    # `.get()` et non `[...]` sur chaque champ : si RAWG modifie le nom d'une
    # clé ou l'omet pour un jeu obscur, on obtient None au lieu d'une KeyError.
    return {
        "cover_url": first_result.get("background_image"),
        "rating": first_result.get("rating"),
        "released_at": _parse_released_date(first_result.get("released")),
        "rawg_id": first_result.get("id"),
    }
