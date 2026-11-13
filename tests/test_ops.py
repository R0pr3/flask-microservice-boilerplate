def test_list_jobs_empty(client):
    response = client.get("/api/v1/jobs")
    assert response.status_code == 200
    assert response.get_json() == {"items": []}


def test_create_job_starts_queued(client, device):
    response = client.post(
        "/api/v1/jobs",
        json={"kind": "scheduled_backup", "device_id": device["id"]},
    )
    assert response.status_code == 201
    payload = response.get_json()
    assert payload["status"] == "queued"
    assert payload["device_id"] == device["id"]


def test_create_job_requires_kind(client):
    response = client.post("/api/v1/jobs", json={"device_id": 1})
    assert response.status_code == 400
    assert response.get_json()["missing"] == ["kind"]


def test_create_job_rejects_unknown_device(client):
    response = client.post("/api/v1/jobs", json={"kind": "inventory_sync", "device_id": 999})
    assert response.status_code == 404


def test_get_job_returns_persisted_job(client):
    created = client.post("/api/v1/jobs", json={"kind": "inventory_sync"}).get_json()
    response = client.get("/api/v1/jobs/%s" % created["id"])
    assert response.status_code == 200
    assert response.get_json()["kind"] == "inventory_sync"


def test_update_job_status(client):
    created = client.post("/api/v1/jobs", json={"kind": "config_push"}).get_json()
    response = client.patch(
        "/api/v1/jobs/%s" % created["id"],
        json={"status": "succeeded", "output": "config applied"},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "succeeded"
    assert payload["output"] == "config applied"


def test_update_job_rejects_invalid_status(client):
    created = client.post("/api/v1/jobs", json={"kind": "config_push"}).get_json()
    response = client.patch("/api/v1/jobs/%s" % created["id"], json={"status": "finished"})
    assert response.status_code == 400


def test_update_job_returns_404_for_missing_job(client):
    response = client.patch("/api/v1/jobs/999", json={"status": "running"})
    assert response.status_code == 404
