from fastapi import FastAPI

from app.api.routes.chat import router as chat_router

app = FastAPI(
    title="ResearchMate API",
    description="An AI-powered research assistant for PDF documents",
    version="0.1.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to ResearchMate!",
        "application": "ResearchMate",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

# Register the chat router
app.include_router(chat_router)