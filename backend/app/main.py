from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.database import Base, SessionLocal, engine

# Un modèle n'est connu de Base.metadata que si son module a été importé :
# chaque ressource doit donc importer son modèle ici pour que create_all crée
# sa table. Chaque membre ajoute sa ligne.
from app.models import user  # noqa: F401
from app.routers import auth as auth_router
from app.routers import user as user_router

# Crée les tables manquantes au démarrage (sans toucher aux tables existantes).
Base.metadata.create_all(bind=engine)


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


app.include_router(auth_router.router)
app.include_router(user_router.router)


@app.get("/health")
def health_check():
    db = SessionLocal()

    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    finally:
        db.close()
        