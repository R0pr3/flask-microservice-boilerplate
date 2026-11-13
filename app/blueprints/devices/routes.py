from flask import Blueprint, jsonify, request

from ...extensions import db
from ...models import Device
from . import service

bp = Blueprint("devices", __name__, url_prefix="/api/v1/devices")

ALLOWED_COMMANDS = frozenset({"uptime", "identity", "links"})


@bp.get("")
def list_devices():
    devices = Device.query.order_by(Device.id).all()
    return jsonify({"items": [device.to_dict() for device in devices], "total": len(devices)})


@bp.post("")
def create_device():
    payload = request.get_json(silent=True) or {}
    missing = [field for field in ("name", "host") if not payload.get(field)]
    if missing:
        return jsonify({"error": "validation_error", "missing": missing}), 400

    if Device.query.filter_by(name=payload["name"]).first():
        return jsonify({"error": "conflict", "message": "device name already exists"}), 409

    try:
        port = int(payload.get("port", 22))
    except (TypeError, ValueError):
        return jsonify({"error": "validation_error", "message": "port must be an integer"}), 400

    device = Device(
        name=payload["name"],
        host=payload["host"],
        port=port,
        username=payload.get("username", "operator"),
    )
    db.session.add(device)
    db.session.commit()
    return jsonify(device.to_dict()), 201


@bp.get("/<int:device_id>")
def get_device(device_id):
    device = db.session.get(Device, device_id)
    if device is None:
        return jsonify({"error": "not_found"}), 404
    return jsonify(device.to_dict())


@bp.post("/<int:device_id>/command")
def execute_command(device_id):
    device = db.session.get(Device, device_id)
    if device is None:
        return jsonify({"error": "not_found"}), 404

    payload = request.get_json(silent=True) or {}
    command = payload.get("command", "uptime")
    if command not in ALLOWED_COMMANDS:
        return (
            jsonify({"error": "unsupported_command", "allowed": sorted(ALLOWED_COMMANDS)}),
            400,
        )

    output = service.run_command(device, command)
    return jsonify({"device": device.name, "command": command, "output": output})
