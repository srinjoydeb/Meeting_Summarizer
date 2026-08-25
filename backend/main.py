from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.routes.meeting_routes import router as meeting_router


app = FastAPI(
    title="Meeting Summarizer API"
)


BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"


# Serve CSS and JS
app.mount(
    "/frontend",
    StaticFiles(directory=FRONTEND_DIR),
    name="frontend"
)


# Frontend homepage
@app.get("/")
async def home():

    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


# API routes
app.include_router(
    meeting_router,
    prefix="/api"
)