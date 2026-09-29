"""Route de santé de l'API : vérifie que le serveur ET la base répondent.

Déplacée depuis main.py pour que main.py ne fasse plus que de l'assemblage
(création de l'application, middlewares, include_router), comme pour les
autres ressources.

C'est la seule route du projet qui touche la session sans passer par un
service ni un repository, et c'est assumé : `SELECT 1` n'est ni une règle
métier ni une lecture de données, c'est un simple test de connexion. Créer
un service et un repository pour une requête qui ne lit aucune table
ajouterait deux fichiers sans rien clarifier.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

# Pas de `prefix` : la route doit rester exactement /health, l'URL
# conventionnelle qu'un outil de supervision interroge sans configuration.
# `tags=["Health"]` la range dans sa propre section de /docs plutôt que dans
# « default ».
router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Indique si l'API est démarrée et si la base de données répond.

    Répond {"status": "ok", "database": "connected"} quand tout va bien.
    """
    # `Depends(get_db)` remplace le SessionLocal() ouvert à la main dans
    # l'ancienne version : FastAPI ferme la session dans tous les cas, même si
    # la base est injoignable et que la requête lève une exception.
    # `text()` est obligatoire : SQLAlchemy 2 refuse une chaîne SQL brute,
    # pour qu'aucune requête textuelle ne soit exécutée par inadvertance.
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
