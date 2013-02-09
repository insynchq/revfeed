import redis

from revfeed import settings


db = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
