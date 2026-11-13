import pytest

from app import create_app
from app.config import Config
from app.extensions import db


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    REDIS_URL = None
    SIMULATE_SSH = True
    SECRET_KEY = "test-secret"
    LOG_LEVEL = "WARNING"


@pytest.fixture()
def app():
    application = create_app(TestConfig)
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def device(client):
    response = client.post(
        "/api/v1/devices",
        json={"name": "radio-sp-01", "host": "10.10.10.10", "port": 22},
    )
    assert response.status_code == 201
    return response.get_json()
