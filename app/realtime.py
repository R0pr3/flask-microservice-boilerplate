import redis
from flask_socketio import SocketIO

socketio = SocketIO()


def get_redis(app):
    """Lazily create the Redis client; returns None when Redis is disabled."""
    client = app.extensions.get("redis_client")
    if client is None:
        url = app.config.get("REDIS_URL")
        if not url:
            return None
        client = redis.Redis.from_url(url, decode_responses=True)
        app.extensions["redis_client"] = client
    return client


def init_realtime(app) -> SocketIO:
    """Enable Socket.IO with Redis as the cross-worker message queue."""
    socketio.init_app(app, message_queue=app.config.get("REDIS_URL"), async_mode="threading")
    return socketio
