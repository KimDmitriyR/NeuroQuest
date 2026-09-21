from fastapi import FastAPI

app = FastAPI(
    title = "NeuroQuest API",
    version = "0.1.0",
)

@app.get("/api/health")
async def health_check():
    return{
        "status" : "ok"
    }
