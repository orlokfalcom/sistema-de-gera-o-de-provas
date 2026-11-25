import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.config import BASE_DIR, IMAGES_DIR, GENERATED_DIR
from backend.app.init_db import init_database, run_migrations
from backend.app.routers import auth, documents, questions, exams, google_sync, dashboard

# Ensure SQLite schema migrations are applied even before ASGI startup lifespan events
run_migrations()

app = FastAPI(
    title="Gerador Inteligente de Avaliações do Ensino Médio",
    description="Plataforma de consolidação de provas multidisciplinares escolares a partir de PDFs de múltiplos professores.",
    version="1.0.0"
)

# Enable CORS for cross-device & PWA usage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(questions.router)
app.include_router(exams.router)
app.include_router(google_sync.router)
app.include_router(dashboard.router)

# Mount Static Files (Extracted Images & PWA Frontend)
STATIC_DIR = BASE_DIR / "static"
ASSETS_DIR = STATIC_DIR / "assets"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")
app.mount("/static/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.on_event("startup")
def startup_event():
    init_database()

@app.get("/")
def serve_pwa_root():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {
        "status": "online",
        "app": "Gerador Inteligente de Avaliações do Ensino Médio",
        "docs": "/docs"
    }

@app.get("/manifest.json")
def get_manifest():
    return FileResponse(str(STATIC_DIR / "manifest.json"), media_type="application/manifest+json")

@app.get("/sw.js")
def get_service_worker():
    return FileResponse(str(STATIC_DIR / "sw.js"), media_type="application/javascript")
