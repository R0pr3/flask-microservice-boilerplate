from datetime import datetime

from .extensions import db


def utcnow() -> datetime:
    return datetime.utcnow()


class Device(db.Model):
    """A network device reachable over SSH (radio, switch, router)."""

    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    host = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, nullable=False, default=22)
    username = db.Column(db.String(120), nullable=False, default="operator")
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "created_at": self.created_at.isoformat(),
        }


class Job(db.Model):
    """An operational task tracked across its lifecycle."""

    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), nullable=True)
    kind = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(16), nullable=False, default="queued")
    output = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=utcnow, onupdate=utcnow)

    device = db.relationship("Device", backref="jobs")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "device_id": self.device_id,
            "kind": self.kind,
            "status": self.status,
            "output": self.output,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
