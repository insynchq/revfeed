from flask import Blueprint, current_app, request, make_response
from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin
import gevent
import msgpack

from revfeed.db import db


ws = Blueprint('ws', __name__, url_prefix='/socket.io')


class NotifierNamespace(BaseNamespace, BroadcastMixin):

    def initialize(self):
        self.notifier_greenlet = gevent.spawn(self.notifier_listen)

    def notifier_listen(self):
        pubsub = db.pubsub()
        pubsub.subscribe('notifier')
        for msg in pubsub.listen():
            if msg['type'] == 'message' and msg['channel'] == 'notifier':
                event, data = msgpack.unpackb(msg['data'])
                self.broadcast_event(event, data)
                gevent.sleep()

    def disconnect(self, *args, **kwargs):
        self.notifier_greenlet.kill()
        super(NotifierNamespace, self).disconnect(*args, **kwargs)


@ws.route('/')
@ws.route('/<path:path>')
def catchall(path):
    try:
        socketio_manage(request.environ, {'/notifier': NotifierNamespace},
                        request)
    except:
        current_app.logger.error("Socket.IO Handler Exception", exc_info=True)

    return make_response("ok")
