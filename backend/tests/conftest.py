import os

# Ensure DB URL is set before importing app/modules during test collection
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:3000")

