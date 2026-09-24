"""Run with: python -m app.content.seed"""

import asyncio

from app.content.loader import load_all_cards, load_all_missions
from app.db.session import AsyncSessionLocal


async def main() -> None:
    async with AsyncSessionLocal() as db:
        loaded_cards = await load_all_cards(db)
        for card in loaded_cards:
            print(f"loaded card: {card.title} ({card.qr_token})")

        loaded_missions = await load_all_missions(db)
        for mission in loaded_missions:
            print(f"loaded mission: {mission.title}")

        if not loaded_cards and not loaded_missions:
            print("nothing new to load")


if __name__ == "__main__":
    asyncio.run(main())
