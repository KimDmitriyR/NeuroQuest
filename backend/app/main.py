from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.missions import router as missions_router
from app.api.players import router as players_router
from app.api.quests import router as quests_router
from app.core.config import settings

app = FastAPI(
    title="NeuroQuest API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(players_router)
app.include_router(quests_router)
app.include_router(missions_router)


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
