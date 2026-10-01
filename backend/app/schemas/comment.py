from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    tournament_id: int = Field(..., gt=0)

    content: str = Field(
        ...,
        min_length=1,
        max_length=500,
    )


class CommentUpdate(BaseModel):
    content: str | None = Field(
        None,
        min_length=1,
        max_length=500,
    )


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tournament_id: int
    user_id: int
    content: str
    created_at: datetime