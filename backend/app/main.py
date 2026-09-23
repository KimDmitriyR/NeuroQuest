from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import AsyncGenerator
from app.db.session import AsyncSessionLocal

app = FastAPI(
    title = "NeuroQuest API",
    version = "0.1.0",
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/api/health")
async def health_check():
    return{
        "status" : "ok"
    }

@app.get("/api/health/db")
async def database_health_check(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("SELECT 1"))

    return{
        "status": "ok",
        "database": result.scalar(),
    }