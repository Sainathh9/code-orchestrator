from fastapi import FastAPI

app = FastAPI(
    title = "Code Orchestrator",
    version = "0.1.0"
)

@app.get("/health")
async def gethealth():
     return {"health" : "Working well"}