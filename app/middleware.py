import time
import uuid

from flask import current_app, g, request


def register_request_middleware(app) -> None:
    """Attach a request id and emit one structured access log per request."""

    @app.before_request
    def _start_timer():
        g.request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        g.start_time = time.perf_counter()

    @app.after_request
    def _log_request(response):
        started = g.get("start_time", time.perf_counter())
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        current_app.logger.info(
            "%s %s -> %s",
            request.method,
            request.path,
            response.status_code,
            extra={
                "request_id": g.get("request_id"),
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "duration_ms": duration_ms,
                "remote_addr": request.remote_addr,
            },
        )
        response.headers["X-Request-ID"] = g.get("request_id", "")
        return response
