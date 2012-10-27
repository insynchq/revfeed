from gevent import monkey
monkey.patch_all()

from socketio.server import SocketIOServer

from revfeed import create_app, logger


if __name__ == '__main__':
    app = create_app()
    logger.info("Started server")
    SocketIOServer(('', 5000), app, resource='socket.io').serve_forever()
