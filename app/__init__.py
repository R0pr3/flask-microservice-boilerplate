from flask import Flask, jsonify

from .config import Config
from .extensions import db
from .logging_config import configure_logging
from .middleware import register_request_middleware


def create_app(config_class=Config):
    """Application factory: wires config, logging, extensions and blueprints."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    configure_logging(app)
    register_request_middleware(app)

    db.init_app(app)

    from .blueprints.api.routes import bp as api_bp
    from .blueprints.devices.routes import bp as devices_bp
    from .blueprints.ops.routes import bp as ops_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(ops_bp)

    if app.config.get("REDIS_URL"):
        from .realtime import init_realtime

        init_realtime(app)

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "not_found"}), 404

    @app.cli.command("init-db")
    def init_db_command():
        """Create database tables (demo helper; use migrations in production)."""
        db.create_all()
        print("Database schema created.")

    with app.app_context():
        db.create_all()

    return app
