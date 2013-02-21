from gevent import monkey
monkey.patch_all()

import logging
import os
import sys

from flask import Flask
from socketio.server import SocketIOServer
import msgpack

from revfeed import repos, config 
from revfeed.db import db
from revfeed.logger import logger


def update_db():
    logger.info("Updating DB...\n")
    commits = repos.update(db)
    # FIXME: Only push notification and but get commits from api
    if commits:
        logger.info("Pushing to notifier...\n")
        # Publish to revfeed
        revfeed_commits = [item for sublist in commits.values() for item in
                           sublist]
        # Sort by time
        revfeed_commits = list(sorted(revfeed_commits,
                                      key=lambda c: c['time']))
        db.publish('notifier', msgpack.packb(['revfeed', revfeed_commits]))
        # TODO: Push to per repo


def create_app():
    from revfeed import views
    app = Flask(__name__)
    app.config.from_object(config)
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
        bind = (config.WEB_HOST, config.WEB_PORT)
        logger.info("Started server (%s:%d)", *bind)
        serve(bind, app, resource='socket.io', policy_server=True)
    except KeyboardInterrupt:
        pass



def print_help():
    logger.info("""
Usage:
revfeed command [args]

Commands:
update_db
run_server
add_repo repo_name repo_dir
rm_repo repo_name

""")


def cli():
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'update_db':
            update_db()
        elif cmd == 'run_server':
            run_server()
        elif cmd == 'add_repo':
            repo_name, repo_dir = sys.argv[2:]
            repo_type = repos.get_repo_type(repo_dir)
            if not os.path.exists(repo_dir):
                logger.info('Repo dir does not exist')
            elif not repo_type:
                logger.info('Not a valid repo')
            else:
                db.hset('revfeed:repo_dirs', repo_name, repo_dir)
                logger.info('Added %s (%s)', repo_name, repo_dir)
        elif cmd == 'rm_repo':
            repo_name = sys.argv[2]
            if db.hget('revfeed:repo_dirs', repo_name):
                # Remove commits from revfeed set
                for commit_key in db.zrange('revfeed:%s' % repo_name, 0, -1):
                    db.zrem('revfeed', commit_key)
                # Remove repo set
                db.delete('revfeed:%s' % repo_name)
                # Remove repo latest commit
                db.delete('revfeed:%s:latest_commit' % repo_name)
                # Remove from repo dirs
                db.hdel('revfeed:repo_dirs', repo_name)
                logger.info('Deleted %s', repo_name)
            else:
                logger.info('%s does not exist', repo_name)
        elif cmd == 'ls_repo':
            for repo_name, repo_dir in db.hgetall('revfeed:repo_dirs').iteritems():
                logger.info('%s: %s', repo_name, repo_dir)
    else:
        print_help()
