import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
UPLOADS_DIR = STORAGE_DIR / "uploads"
IMAGES_DIR = STORAGE_DIR / "extracted_images"
GENERATED_DIR = STORAGE_DIR / "generated_exams"

for d in [STORAGE_DIR, UPLOADS_DIR, IMAGES_DIR, GENERATED_DIR]:
    d.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'evaluations.db'}")
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-exam-generator-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# Google OAuth & Workspace config (placeholders that can be overridden via env)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "mock-google-client-id.apps.googleusercontent.com")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "mock-google-client-secret")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback")
