import os
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()


def _csv_list(value: str, default: List[str]) -> List[str]:
    if not value:
        return default
    items = [v.strip() for v in value.split(",") if v.strip()]
    return items or default


def _get_allowed_origins() -> List[str]:
    raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
    items = _csv_list(raw, ["http://localhost:3000"])
    # Support wildcard via "*"
    if any(o == "*" for o in items):
        return ["*"]
    return items


def _get_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


app = FastAPI(title="Chrona Backend")

allowed_origins = _get_allowed_origins()
allow_credentials = _get_bool("ALLOW_CREDENTIALS", False)
allowed_methods = _csv_list(os.getenv("ALLOWED_METHODS", "*"), ["*"])
allowed_headers = _csv_list(os.getenv("ALLOWED_HEADERS", "*"), ["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=allowed_methods,
    allow_headers=allowed_headers,
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/")
def root() -> dict:
    return {"service": "chrona-backend"}
