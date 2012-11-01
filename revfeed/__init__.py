from gevent import monkey
monkey.patch_all()

import logging

from flask import Flask
from socketio.server import SocketIOServer
import msgpack
import redis

from revfeed import settings


logger = logging.getLogger('revfeed')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

db = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


def update_db():
    logger.info("Updating DB...\n")
    from revfeed import repos
    commits = repos.update(db)
    if commits:
        logger.info("Pushing to notifier...\n")
        # Publish to revfeed
        revfeed_commits = [item for sublist in commits.values() for item in
                           sublist]
        # Sort by time
        revfeed_commits = list(sorted(revfeed_commits,
                                      key=lambda c: c['time']))
        db.publish('notifier', msgpack.packb(['revfeed', revfeed_commits]))
        # Publish to each repo
        for repo_name in commits.keys():
            db.publish('notifier', msgpack.packb([repo_name,
                                                  commits[repo_name]]))


def create_app():
    from revfeed import views
    app = Flask(__name__)
    app.config.from_object(settings)
    app.register_blueprint(views.api)
    app.register_blueprint(views.pages)
    app.register_blueprint(views.ws)
    return app


def run_server():
    app = create_app()
    try:
        bind = (settings.WEB_HOST, settings.WEB_PORT)
        logger.info("Started server (%s:%d)", *bind)
        server = SocketIOServer(bind, app, resource='socket.io')
        server.serve_forever()
    except KeyboardInterrupt:
        pass
