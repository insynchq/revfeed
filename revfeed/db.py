import redis

from revfeed import config 


db = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT)
