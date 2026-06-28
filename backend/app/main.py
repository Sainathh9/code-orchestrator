# pyrefly: ignore-errors
from fastapi import FastAPI
from app.routers.orchestrator import router


app = FastAPI(
    title="Self-Healing Code Orchestrator",
    version="0.1.0"
)

app.include_router(router)


@app.get("/health")
def health():
    return {
        "status": "ok"
    }