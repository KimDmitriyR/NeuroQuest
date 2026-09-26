import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.envelope_mission import ValidationType
from app.models.mission_attempt import MissionAttemptStatus


class StartAttemptRequest(BaseModel):
    player_id: uuid.UUID


class SubmitAttemptRequest(BaseModel):
    photo_url: str | None = None
    text_answer: str | None = None


class ReviewAttemptRequest(BaseModel):
    approved: bool


class MissionView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sector_id: uuid.UUID
    title: str
    description: str
    instructions: str
    validation_type: ValidationType


class AttemptView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    player_id: uuid.UUID
    mission_id: uuid.UUID
    status: MissionAttemptStatus
    photo_url: str | None
    text_answer: str | None
    current_step: int
    started_at: datetime
    submitted_at: datetime | None
    completed_at: datetime | None


class SubmitAttemptResultView(AttemptView):
    # None for photo missions (nothing auto-checked, always needs review)
    is_correct: bool | None
    total_steps: int | None
