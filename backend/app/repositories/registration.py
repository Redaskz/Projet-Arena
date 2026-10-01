from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.registration import Registration


def list_registrations(db: Session) -> list[Registration]:
    query = select(Registration).order_by(Registration.registered_at)
    return list(db.execute(query).scalars().all())


def list_registrations_by_tournament(
    db: Session,
    tournament_id: int,
) -> list[Registration]:
    query = (
        select(Registration)
        .where(Registration.tournament_id == tournament_id)
        .order_by(Registration.registered_at)
    )
    return list(db.execute(query).scalars().all())


def get_registration_by_id(
    db: Session,
    registration_id: int,
) -> Registration | None:
    return db.get(Registration, registration_id)


def get_registration_by_tournament_and_team(
    db: Session,
    tournament_id: int,
    team_id: int,
) -> Registration | None:
    query = select(Registration).where(
        Registration.tournament_id == tournament_id,
        Registration.team_id == team_id,
    )

    return db.execute(query).scalar_one_or_none()


def count_registrations_by_tournament(
    db: Session,
    tournament_id: int,
) -> int:
    query = (
        select(func.count())
        .select_from(Registration)
        .where(Registration.tournament_id == tournament_id)
    )

    return db.execute(query).scalar_one()


def create_registration(
    db: Session,
    data: dict,
) -> Registration:
    registration = Registration(**data)

    db.add(registration)
    db.commit()
    db.refresh(registration)

    return registration


def update_registration(
    db: Session,
    registration: Registration,
    data: dict,
) -> Registration:
    for field, value in data.items():
        setattr(registration, field, value)

    db.commit()
    db.refresh(registration)

    return registration


def delete_registration(
    db: Session,
    registration: Registration,
) -> None:
    db.delete(registration)
    db.commit()