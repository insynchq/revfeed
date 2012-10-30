from revfeed import settings


bind = "%s:%d" % (settings.WEB_HOST, settings.WEB_PORT)
worker_class = "socketio.sgunicorn.GeventSocketIOWorker"

