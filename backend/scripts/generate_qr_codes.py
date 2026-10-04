"""Generates QR codes (and simple printable card fronts) for every quest
card and envelope mission currently in the database.

Run with: python -m scripts.generate_qr_codes [base_url]
Default base_url: http://localhost:5173

Output goes to backend/print_assets/{qr,cards}/ - gitignored, since these
are generated artifacts, not source content (re-run any time after
content changes).
"""

import asyncio
import sys
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.envelope_mission import EnvelopeMission
from app.models.quest_card import QuestCard
from app.models.sector import Sector

OUTPUT_DIR = Path(__file__).parent.parent / "print_assets"

# Cyrillic-capable TTF candidates per platform, checked in order - the card
# titles are in Russian, so this can't just fall back to PIL's tiny built-in
# bitmap font (it has no Cyrillic glyphs at all).
_BOLD_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
    "C:\\Windows\\Fonts\\arialbd.ttf",  # Windows
    "C:\\Windows\\Fonts\\segoeuib.ttf",  # Windows fallback
    "/Library/Fonts/Arial Bold.ttf",  # macOS
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",  # macOS fallback
]
_REGULAR_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
    "C:\\Windows\\Fonts\\arial.ttf",  # Windows
    "C:\\Windows\\Fonts\\segoeui.ttf",  # Windows fallback
    "/Library/Fonts/Arial.ttf",  # macOS
    "/System/Library/Fonts/Supplemental/Arial.ttf",  # macOS fallback
]


def _find_font(candidates: list[str]) -> str | None:
    for path in candidates:
        if Path(path).exists():
            return path
    return None


FONT_BOLD = _find_font(_BOLD_CANDIDATES)
FONT_REGULAR = _find_font(_REGULAR_CANDIDATES)

if FONT_BOLD is None or FONT_REGULAR is None:
    print(
        "WARNING: no Cyrillic-capable TTF font found on this system - card "
        "front titles will render as boxes/garbage. QR codes themselves are "
        "unaffected. Install a font (e.g. DejaVu Sans) or edit "
        "_BOLD_CANDIDATES/_REGULAR_CANDIDATES in this script to point at one."
    )


def slugify(text: str) -> str:
    safe = "".join(c if c.isalnum() else "-" for c in text.lower())
    while "--" in safe:
        safe = safe.replace("--", "-")
    return safe.strip("-")


def make_qr_image(data: str) -> Image.Image:
    qr = qrcode.QRCode(box_size=10, border=2, error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")


def make_card_front(title: str, subtitle: str, color_hex: str, qr_img: Image.Image) -> Image.Image:
    width, height = 640, 900
    card = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(card)

    header_h = 160
    draw.rectangle([0, 0, width, header_h], fill=color_hex)

    title_font = (
        ImageFont.truetype(FONT_BOLD, 40) if FONT_BOLD else ImageFont.load_default()
    )
    subtitle_font = (
        ImageFont.truetype(FONT_REGULAR, 24) if FONT_REGULAR else ImageFont.load_default()
    )

    _wrapped_text(draw, title, title_font, width - 60, (30, 30), fill="white")
    _wrapped_text(draw, subtitle, subtitle_font, width - 60, (30, header_h + 30), fill="#333333")

    qr_size = 380
    qr_resized = qr_img.resize((qr_size, qr_size))
    card.paste(qr_resized, ((width - qr_size) // 2, height - qr_size - 60))

    return card


def _wrapped_text(draw, text, font, max_width, xy, fill, line_spacing=8):
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + line_spacing


async def main() -> None:
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5173"

    qr_dir = OUTPUT_DIR / "qr"
    cards_dir = OUTPUT_DIR / "cards"
    qr_dir.mkdir(parents=True, exist_ok=True)
    cards_dir.mkdir(parents=True, exist_ok=True)

    async with AsyncSessionLocal() as db:
        cards_result = await db.execute(select(QuestCard))
        cards = list(cards_result.scalars().all())

        missions_result = await db.execute(select(EnvelopeMission))
        missions = list(missions_result.scalars().all())

        sectors_result = await db.execute(select(Sector))
        sectors_by_id = {s.id: s for s in sectors_result.scalars().all()}

        for card in cards:
            sector = sectors_by_id[card.sector_id]
            url = f"{base_url}/?quest={card.qr_token}"
            qr_img = make_qr_image(url)
            name = f"sector{sector.sort_order}-card{card.number}-{slugify(card.title)}"
            qr_img.save(qr_dir / f"{name}.png")

            front = make_card_front(card.title, sector.title, sector.color_token, qr_img)
            front.save(cards_dir / f"{name}.png")
            print(f"card: {card.title} -> {url}")

        for mission in missions:
            sector = sectors_by_id[mission.sector_id]
            url = f"{base_url}/mission/{mission.id}"
            qr_img = make_qr_image(url)
            name = f"mission-{slugify(mission.title)}"
            qr_img.save(qr_dir / f"{name}.png")

            front = make_card_front(mission.title, sector.title, sector.color_token, qr_img)
            front.save(cards_dir / f"{name}.png")
            print(f"mission: {mission.title} -> {url}")

    print(f"\nSaved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    asyncio.run(main())
