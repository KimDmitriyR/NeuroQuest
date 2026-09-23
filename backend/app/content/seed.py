"""Run with: python -m app.content.seed"""

import asyncio

from app.content.loader import load_all_cards
from app.db.session import AsyncSessionLocal


async def main() -> None:
    async with AsyncSessionLocal() as db:
        loaded = await load_all_cards(db)
        for card in loaded:
            print(f"loaded: {card.title} ({card.qr_token})")
        if not loaded:
            print("nothing new to load")


if __name__ == "__main__":
    asyncio.run(main())
