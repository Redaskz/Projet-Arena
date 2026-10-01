from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.registration import RegistrationStatus


class RegistrationCreate(BaseModel):
    tournament_id: int = Field(..., gt=0)
    team_id: int = Field(..., gt=0)


class RegistrationUpdate(BaseModel):
    status: RegistrationStatus | None = None


class RegistrationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tournament_id: int
    team_id: int
    status: RegistrationStatus
    registered_at: datetime