import os


def _normalize_database_url(url: str) -> str:
    """Normalize legacy Heroku-style URLs to a SQLAlchemy driver URL."""
    if url.startswith("postgres://"):
        return "postgresql+psycopg2://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg2://" + url[len("postgresql://"):]
    return url


class Config:
    """Runtime configuration driven entirely by environment variables."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(
        os.environ.get(
            "DATABASE_URL",
            "postgresql://nexus:nexus@db:5432/nexus",
        )
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    REDIS_URL = os.environ.get("REDIS_URL") or None
    SIMULATE_SSH = os.environ.get("SIMULATE_SSH", "true").lower() in {"1", "true", "yes"}

    APP_VERSION = os.environ.get("APP_VERSION", "0.1.0")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
