from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.players import router as players_router
from app.api.quests import router as quests_router

app = FastAPI(
    title="NeuroQuest API",
    version="0.1.0",
)

app.include_router(players_router)
app.include_router(quests_router)


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok"
    }


@app.get("/api/health/db")
async def database_health_check(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": result.scalar(),
    }
