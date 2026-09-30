"""Configuration commune aux tests de l'API.

Les tests utilisent une base SQLite en mémoire totalement séparée de la base
PostgreSQL de développement. Chaque test repart donc avec une base propre.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

# Ces imports enregistrent les modèles dans Base.metadata avant create_all().
from app.models.comment import Comment  # noqa: F401
from app.models.game import Game  # noqa: F401
from app.models.registration import Registration  # noqa: F401


# Base SQLite uniquement utilisée pendant les tests.
TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture()
def db() -> Session:
    """Fournit une session avec une base propre pour chaque test."""
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db: Session):
    """Fournit un client FastAPI utilisant la base de test."""

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()