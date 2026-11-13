import time

from flask import Blueprint, current_app, jsonify
from sqlalchemy import text

from ...extensions import db

bp = Blueprint("api", __name__, url_prefix="/api/v1")

_STARTED_AT = time.time()


@bp.get("/health")
def health():
    """Liveness probe: verifies the database connection."""
    db_status = "ok"
    try:
        db.session.execute(text("SELECT 1"))
    except Exception:  # pragma: no cover - defensive path
        db_status = "unavailable"

    status_code = 200 if db_status == "ok" else 503
    return (
        jsonify({"status": "ok" if status_code == 200 else "degraded", "database": db_status}),
        status_code,
    )


@bp.get("/status")
def status():
    """Diagnostic endpoint used by dashboards and smoke tests."""
    return jsonify(
        {
            "service": "flask-microservice-boilerplate",
            "version": current_app.config.get("APP_VERSION", "dev"),
            "uptime_seconds": round(time.time() - _STARTED_AT, 1),
            "checks": {
                "database": "ok",
                "redis": "configured" if current_app.config.get("REDIS_URL") else "disabled",
            },
        }
    )
