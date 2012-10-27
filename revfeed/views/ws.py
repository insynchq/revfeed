from flask import Blueprint, current_app, request, make_response
from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin
import gevent
import msgpack

from revfeed import db


ws = Blueprint('ws', __name__, url_prefix='/socket.io')


class NotifierNamespace(BaseNamespace, BroadcastMixin):

    def initialize(self):
        self.is_done = gevent.event.Event()
        self.pubsub = gevent.spawn(self.start_pubsub)

    def start_pubsub(self):
        pubsub = db.pubsub()
        pubsub.subscribe('notifier')
        for msg in pubsub.listen():
            if self.is_done.is_set():
                break
            if msg['channel'] == 'notifier' and msg['type'] == 'message':
                event, data = msgpack.unpackb(msg['data'])
                self.broadcast_event(event, data)

    def recv_disconnect(self):
        self.is_done.set()
        self.disconnect(silent=True)


@ws.route('/')
@ws.route('/<path:path>')
def catchall(path):
    try:
        socketio_manage(request.environ, {'/notifier': NotifierNamespace},
                        request)
    except:
        current_app.logger.error("Socket.IO Handler Exception", exc_info=True)

    return make_response("ok")
