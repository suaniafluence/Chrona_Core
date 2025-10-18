import os

# Ensure DB URL is set before importing app/modules during test collection
# Use file-based SQLite by default to avoid in-memory connection pooling issues.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:3000")
