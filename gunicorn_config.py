from revfeed import config 


bind = "{0}:{1}".format(config.WEB_HOST, config.WEB_PORT)
worker_class = "socketio.sgunicorn.GeventSocketIOWorker"
