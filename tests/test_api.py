def test_health_endpoint_reports_database_ok(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["database"] == "ok"


def test_status_endpoint_exposes_version_and_checks(client):
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["service"] == "flask-microservice-boilerplate"
    assert "version" in payload
    assert payload["checks"]["redis"] == "disabled"


def test_unknown_route_returns_json_404(client):
    response = client.get("/api/v1/does-not-exist")
    assert response.status_code == 404
    assert response.get_json()["error"] == "not_found"


def test_request_id_header_is_echoed(client):
    response = client.get("/api/v1/health", headers={"X-Request-ID": "req-123"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-123"
