import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PlayerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class PlayerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    created_at: datetime
    updated_at: datetime


class PlayerTokenResponse(BaseModel):
    """Credential for the child's device (sent as the X-Player-Token header)."""

    access_token: str
    token_type: str = "player"
