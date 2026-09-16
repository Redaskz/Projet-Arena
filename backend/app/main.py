from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.database import SessionLocal


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


@app.get("/health")
def health_check():
    db = SessionLocal()

    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    finally:
        db.close()
        