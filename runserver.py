from gevent import monkey
monkey.patch_all()

from socketio.server import SocketIOServer

from revfeed import create_app, logger, settings


if __name__ == '__main__':
    app = create_app()
    try:
        bind = (settings.WEB_HOST, settings.WEB_PORT)
        logger.info("Started server (%s:%d)", *bind)
        server = SocketIOServer(bind, app, resource='socket.io')
        server.serve_forever()
    except KeyboardInterrupt:
        pass
