from revfeed.config import WEB_HOST, WEB_PORT


bind = "{0}:{1}".format(WEB_HOST, WEB_PORT)
worker_class = "socketio.sgunicorn.GeventSocketIOWorker"
