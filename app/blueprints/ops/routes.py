from flask import Blueprint, jsonify, request

from ...extensions import db
from ...models import Device, Job

bp = Blueprint("ops", __name__, url_prefix="/api/v1/jobs")

VALID_STATUSES = frozenset({"queued", "running", "succeeded", "failed"})


@bp.get("")
def list_jobs():
    jobs = Job.query.order_by(Job.id.desc()).limit(100).all()
    return jsonify({"items": [job.to_dict() for job in jobs]})


@bp.post("")
def create_job():
    payload = request.get_json(silent=True) or {}
    if not payload.get("kind"):
        return jsonify({"error": "validation_error", "missing": ["kind"]}), 400

    device_id = payload.get("device_id")
    if device_id is not None:
        try:
            device_id = int(device_id)
        except (TypeError, ValueError):
            return jsonify({"error": "validation_error", "message": "device_id must be an integer"}), 400
        if db.session.get(Device, device_id) is None:
            return jsonify({"error": "not_found", "message": "device not found"}), 404

    job = Job(kind=payload["kind"], device_id=device_id, status="queued")
    db.session.add(job)
    db.session.commit()
    return jsonify(job.to_dict()), 201


@bp.get("/<int:job_id>")
def get_job(job_id):
    job = db.session.get(Job, job_id)
    if job is None:
        return jsonify({"error": "not_found"}), 404
    return jsonify(job.to_dict())


@bp.patch("/<int:job_id>")
def update_job(job_id):
    job = db.session.get(Job, job_id)
    if job is None:
        return jsonify({"error": "not_found"}), 404

    payload = request.get_json(silent=True) or {}
    status = payload.get("status")
    if status is not None and status not in VALID_STATUSES:
        return jsonify({"error": "validation_error", "allowed": sorted(VALID_STATUSES)}), 400

    if status is not None:
        job.status = status
    if "output" in payload:
        job.output = payload["output"]

    db.session.commit()
    return jsonify(job.to_dict())
