from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.database import SessionLocal
from app.routers import game as game_router
from app.routers import player as player_router
from app.routers import team as team_router


app = FastAPI(
    title="Arena API",
    description="API de la plateforme de tournois Arena",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Chaque ressource est branchée sur l'application par un include_router.
# Le préfixe (/games) et le tag (Games) sont déjà portés par l'APIRouter
# lui-même : on ne les répète pas ici, sinon le préfixe serait appliqué deux
# fois et l'URL deviendrait /games/games.
# Sans cette ligne, le fichier routers/game.py existerait sans qu'aucune de ses
# routes soit servie ni visible dans /docs.
# L'ordre des include_router ici détermine l'ordre des sections dans /docs, et
# rien d'autre : le routage lui-même repose sur les préfixes, qui ne se
# chevauchent pas. On suit donc l'ordre de lecture du modèle de données :
# un jeu, puis les équipes qui s'y inscrivent, puis les joueurs de ces équipes.
app.include_router(game_router.router)
app.include_router(team_router.router)
app.include_router(player_router.router)


@app.get("/health")
def health_check():
    db = SessionLocal()

    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    finally:
        db.close()
        