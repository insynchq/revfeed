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


def serve(bind, app, **kw):
    _resource = kw.pop('resource', 'socket.io')

    transports = kw.pop('transports', None)
    if transports:
        transports = [x.strip() for x in transports.split(',')]

    policy_server = kw.pop('policy_server', False)
    if policy_server in (True, 'True', 'true', 'enable', 'yes', 'on', '1'):
        policy_server = True
        policy_listener_host = kw.pop('policy_listener_host', bind[0])
        policy_listener_port = int(kw.pop('policy_listener_port', 10843))
        kw['policy_listener'] = (policy_listener_host, policy_listener_port)
    else:
        policy_server = False

    server = SocketIOServer(bind,
                            app,
                            resource=_resource,
                            transports=transports,
                            policy_server=policy_server,
                            **kw)
    server.serve_forever()


def run_server():
    app = create_app()
    try:
        bind = (settings.WEB_HOST, settings.WEB_PORT)
        logger.info("Started server (%s:%d)", *bind)
        server = serve(bind, app, resource='socket.io', policy_server=True)
        server.serve_forever()
    except KeyboardInterrupt:
        pass
