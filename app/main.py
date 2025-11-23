from fastapi import FastAPI
from app.routes.chat import router as chat_router

app = FastAPI(
    title="OybekCoder AI Backend",
    version="1.0.0"
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(chat_router, prefix="/chat", tags=["Chat"])
