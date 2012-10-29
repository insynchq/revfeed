import logging

from flask import Flask
import redis

from revfeed import settings


logger = logging.getLogger('revfeed')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

db = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


def update_db():
    logger.info("Updating DB...\n")
    from revfeed import repos
    return repos.update(db)


def create_app():
    from revfeed import views
    app = Flask(__name__)
    app.config.from_object(settings)
    app.register_blueprint(views.api)
    app.register_blueprint(views.pages)
    app.register_blueprint(views.ws)
    return app
