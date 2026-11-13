from app.blueprints.devices import service


def test_list_devices_empty(client):
    response = client.get("/api/v1/devices")
    assert response.status_code == 200
    assert response.get_json() == {"items": [], "total": 0}


def test_create_device_returns_created_payload(client):
    response = client.post(
        "/api/v1/devices",
        json={"name": "radio-01", "host": "10.0.0.5", "port": 2222},
    )
    assert response.status_code == 201
    payload = response.get_json()
    assert payload["name"] == "radio-01"
    assert payload["port"] == 2222


def test_create_device_requires_name_and_host(client):
    response = client.post("/api/v1/devices", json={"name": "radio-02"})
    assert response.status_code == 400
    assert response.get_json()["missing"] == ["host"]


def test_create_device_rejects_duplicate_name(client, device):
    response = client.post(
        "/api/v1/devices",
        json={"name": device["name"], "host": "10.0.0.9"},
    )
    assert response.status_code == 409


def test_get_device_returns_404_for_missing_id(client):
    response = client.get("/api/v1/devices/999")
    assert response.status_code == 404


def test_execute_command_returns_simulated_output(client, device):
    response = client.post(
        "/api/v1/devices/%s/command" % device["id"],
        json={"command": "uptime"},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["device"] == device["name"]
    assert "up" in payload["output"]


def test_execute_command_rejects_unsupported_command(client, device):
    response = client.post(
        "/api/v1/devices/%s/command" % device["id"],
        json={"command": "rm -rf /"},
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "unsupported_command"


def test_execute_command_delegates_to_ssh_service(client, device, monkeypatch):
    calls = {}

    def fake_run_command(device_model, command):
        calls["device"] = device_model.name
        calls["command"] = command
        return "output from ssh"

    monkeypatch.setattr(service, "run_command", fake_run_command)

    response = client.post(
        "/api/v1/devices/%s/command" % device["id"],
        json={"command": "identity"},
    )
    assert response.status_code == 200
    assert response.get_json()["output"] == "output from ssh"
    assert calls == {"device": device["name"], "command": "identity"}
