from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.comment import Comment


def list_comments(db: Session) -> list[Comment]:
    query = select(Comment).order_by(Comment.created_at)
    return list(db.execute(query).scalars().all())


def list_comments_by_tournament(
    db: Session,
    tournament_id: int,
) -> list[Comment]:
    query = (
        select(Comment)
        .where(Comment.tournament_id == tournament_id)
        .order_by(Comment.created_at)
    )

    return list(db.execute(query).scalars().all())


def get_comment_by_id(
    db: Session,
    comment_id: int,
) -> Comment | None:
    return db.get(Comment, comment_id)


def create_comment(
    db: Session,
    data: dict,
) -> Comment:
    comment = Comment(**data)

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


def update_comment(
    db: Session,
    comment: Comment,
    data: dict,
) -> Comment:
    for field, value in data.items():
        setattr(comment, field, value)

    db.commit()
    db.refresh(comment)

    return comment


def delete_comment(
    db: Session,
    comment: Comment,
) -> None:
    db.delete(comment)
    db.commit()