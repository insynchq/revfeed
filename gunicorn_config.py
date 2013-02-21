from revfeed import config 


bind = "%s:%d" % (config.WEB_HOST, config.WEB_PORT)
worker_class = "socketio.sgunicorn.GeventSocketIOWorker"
