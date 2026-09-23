import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.choice import ChoiceOutcome
from app.models.quest_node import QuestNodeType
from app.models.quest_session import QuestSessionStatus


class StartQuestRequest(BaseModel):
    player_id: uuid.UUID
    qr_token: str


class ChoiceOption(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    label: str
    text: str


class NodeView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: QuestNodeType
    message: str
    choices: list[ChoiceOption]


class SessionView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    player_id: uuid.UUID
    quest_id: uuid.UUID
    status: QuestSessionStatus
    started_at: datetime
    completed_at: datetime | None
    current_node: NodeView


class SubmitChoiceRequest(BaseModel):
    choice_id: uuid.UUID


class AchievementView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    description: str | None


class MasterCodeLetterView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    letter: str
    position: int


class ChoiceResultView(BaseModel):
    status_label: str | None
    outcome: ChoiceOutcome
    consequence_text: str
    lesson_text: str | None
    unlock_title: str | None
    unlock_description: str | None
    achievement_granted: AchievementView | None
    completed: bool
    completion_achievement: AchievementView | None
    master_code_letter: MasterCodeLetterView | None
    next_node: NodeView | None
