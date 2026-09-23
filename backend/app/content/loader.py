"""Loads quest card content from YAML files into the database.

Content (sector text, quest scenario, choices, rewards) lives as data under
app/content/cards/*.yaml, not as Python code - so a card can be added or
tweaked by editing YAML, without touching the domain models or API.

This loader is intentionally simple: if a card's qr_token already exists in
the DB, loading that file is skipped entirely (no partial updates). It's a
seeding tool for initial content, not a content-sync/migration engine.
"""

from pathlib import Path

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.achievement import Achievement
from app.models.choice import Choice, ChoiceOutcome
from app.models.master_code_letter import MasterCodeLetter
from app.models.quest import Quest
from app.models.quest_card import QuestCard
from app.models.quest_node import QuestNode, QuestNodeType
from app.models.sector import Sector

CARDS_DIR = Path(__file__).parent / "cards"


async def _get_or_create_sector(db: AsyncSession, data: dict) -> Sector:
    result = await db.execute(select(Sector).where(Sector.slug == data["slug"]))
    sector = result.scalar_one_or_none()
    if sector:
        return sector

    sector = Sector(
        title=data["title"],
        slug=data["slug"],
        description=data.get("description"),
        color=data["color"],
        color_token=data["color_token"],
        sort_order=data.get("sort_order", 0),
    )
    db.add(sector)
    await db.flush()
    return sector


async def _get_or_create_achievement(db: AsyncSession, data: dict) -> Achievement:
    result = await db.execute(
        select(Achievement).where(Achievement.title == data["title"])
    )
    achievement = result.scalar_one_or_none()
    if achievement:
        return achievement

    achievement = Achievement(
        title=data["title"], is_badge=data.get("is_badge", False)
    )
    db.add(achievement)
    await db.flush()
    return achievement


async def load_card_file(db: AsyncSession, path: Path) -> QuestCard | None:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))

    existing = await db.execute(
        select(QuestCard).where(QuestCard.qr_token == raw["card"]["qr_token"])
    )
    if existing.scalar_one_or_none() is not None:
        return None  # already loaded, skip

    sector = await _get_or_create_sector(db, raw["sector"])

    achievements_by_key = {
        entry["key"]: await _get_or_create_achievement(db, entry)
        for entry in raw.get("achievements", [])
    }

    quest = Quest(title=raw["quest"]["title"], sector_id=sector.id)
    db.add(quest)
    await db.flush()

    # pass 1: create every node so choices can reference each other by key
    nodes_by_key: dict[str, QuestNode] = {}
    for node_data in raw["nodes"]:
        node = QuestNode(
            quest_id=quest.id,
            type=QuestNodeType(node_data.get("type", "choice")),
            message=node_data["message"],
            sort_order=len(nodes_by_key),
            achievement_id=(
                achievements_by_key[node_data["achievement"]].id
                if node_data.get("achievement")
                else None
            ),
            unlock_title=node_data.get("unlock_title"),
            unlock_description=node_data.get("unlock_description"),
        )
        db.add(node)
        nodes_by_key[node_data["key"]] = node
    await db.flush()

    # pass 2: create choices, now that every node has an id to link to
    for node_data in raw["nodes"]:
        node = nodes_by_key[node_data["key"]]
        for i, choice_data in enumerate(node_data.get("choices", [])):
            db.add(
                Choice(
                    node_id=node.id,
                    label=choice_data["label"],
                    text=choice_data["text"],
                    consequence_text=choice_data["consequence_text"],
                    outcome=ChoiceOutcome(choice_data["outcome"]),
                    status_label=choice_data.get("status_label"),
                    lesson_text=choice_data.get("lesson_text"),
                    achievement_id=(
                        achievements_by_key[choice_data["achievement"]].id
                        if choice_data.get("achievement")
                        else None
                    ),
                    unlock_title=choice_data.get("unlock_title"),
                    unlock_description=choice_data.get("unlock_description"),
                    next_node_id=nodes_by_key[choice_data["next"]].id,
                    sort_order=i,
                )
            )

    quest.start_node_id = nodes_by_key[raw["start_node"]].id

    card = QuestCard(
        sector_id=sector.id,
        quest_id=quest.id,
        number=raw["card"]["number"],
        title=raw["card"]["title"],
        intro_text=raw["card"]["intro_text"],
        qr_token=raw["card"]["qr_token"],
    )
    db.add(card)
    await db.flush()

    db.add(
        MasterCodeLetter(
            quest_card_id=card.id,
            letter=raw["card"]["master_code_letter"],
            position=raw["card"]["master_code_position"],
        )
    )

    await db.commit()
    return card


async def load_all_cards(db: AsyncSession) -> list[QuestCard]:
    loaded = []
    for path in sorted(CARDS_DIR.glob("*.yaml")):
        card = await load_card_file(db, path)
        if card is not None:
            loaded.append(card)
    return loaded
