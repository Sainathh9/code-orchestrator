# pyrefly: ignore-errors
from fastapi import FastAPI
from app.routers.generate import router
from app.routers.executions import router as executions_router
from app.auth.router import router as auth_router


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Self-Healing Code Orchestrator",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(executions_router)
app.include_router(auth_router)



@app.get("/health")
def health():
    return {
        "status": "ok"
    }