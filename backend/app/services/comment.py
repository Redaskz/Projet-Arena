"""Règles métier de la ressource `comments`.

Toutes les erreurs HTTP concernant les commentaires sont produites ici.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.tournament import Tournament
from app.repositories import comment as comment_repository
from app.schemas.comment import CommentCreate, CommentUpdate


def list_comments(db: Session) -> list[Comment]:
    """Renvoie tous les commentaires."""
    return comment_repository.list_comments(db)


def list_tournament_comments(
    db: Session,
    tournament_id: int,
) -> list[Comment]:
    """Renvoie les commentaires d'un tournoi existant."""
    tournament = db.get(Tournament, tournament_id)

    if tournament is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournoi introuvable.",
        )

    return comment_repository.list_comments_by_tournament(
        db,
        tournament_id,
    )


def get_comment(
    db: Session,
    comment_id: int,
) -> Comment:
    """Renvoie un commentaire existant."""
    comment = comment_repository.get_comment_by_id(db, comment_id)

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commentaire introuvable.",
        )

    return comment


def create_comment(
    db: Session,
    payload: CommentCreate,
    current_user,
) -> Comment:
    """Crée un commentaire au nom de l'utilisateur authentifié."""
    tournament = db.get(Tournament, payload.tournament_id)

    if tournament is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournoi introuvable.",
        )

    data = payload.model_dump()

    # Le user_id vient exclusivement de l'utilisateur authentifié.
    # Il n'est jamais fourni par le client.
    data["user_id"] = current_user.id

    return comment_repository.create_comment(db, data)


def update_comment(
    db: Session,
    comment_id: int,
    payload: CommentUpdate,
    current_user,
) -> Comment:
    """Modifie un commentaire si l'utilisateur courant en est l'auteur."""
    comment = get_comment(db, comment_id)

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez modifier que vos propres commentaires.",
        )

    data = payload.model_dump(exclude_unset=True)

    return comment_repository.update_comment(
        db,
        comment,
        data,
    )


def delete_comment(
    db: Session,
    comment_id: int,
    current_user,
) -> None:
    """Supprime un commentaire si l'utilisateur courant en est l'auteur."""
    comment = get_comment(db, comment_id)

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez supprimer que vos propres commentaires.",
        )

    comment_repository.delete_comment(db, comment)