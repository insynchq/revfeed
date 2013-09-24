import argparse
import pkg_resources

from tornado import web, ioloop
from sockjs.tornado import SockJSRouter
import redis

from .handlers import IndexHandler, CommitsHandler
from .notifier import NotifierConnection
from .utils import log, log_request, redis_key, gen_secret


def main():
  log("{}\n", __package__)

  # Parse args
  parser = argparse.ArgumentParser(description="dead simple commits feed")
  parser.add_argument('-s', '--secret', type=str, default=gen_secret(18),
                      help="auth secret")
  parser.add_argument('-p', '--port', type=int, default=5000,
                      help="port")
  parser.add_argument('--redis-prefix', type=str, default='revfeed',
                      help="redis prefix")
  parser.add_argument('--redis-host', type=str, default='localhost',
                      help="redis host")
  parser.add_argument('--redis-port', type=int, default=6379,
                      help="redis port")
  parser.add_argument('--clear', action='store_true', help="clear feed")
  args = parser.parse_args()

  # Setup redis connection
  redis_prefix = args.redis_prefix
  redis_conn = redis.StrictRedis(args.redis_host, args.redis_port)

  # Clear feed if requested
  if args.clear:
    count = 0
    for key in redis_conn.keys(redis_key(redis_prefix, '*')):
      count += redis_conn.delete(key)
    log("deleted {} keys", count)
    return

  # Setup handlers
  handlers = []
  handlers.append((r'/', IndexHandler, dict(
    redis_prefix=redis_prefix,
    redis_conn=redis_conn,
  )))
  handlers.append((r'/commits', CommitsHandler, dict(
    secret=args.secret,
    redis_prefix=redis_prefix,
    redis_conn=redis_conn,
  )))
  handlers.extend(SockJSRouter(NotifierConnection, '/notifier').urls)

  # Setup app
  static_path = pkg_resources.resource_filename(__package__, 'static')
  app = web.Application(
    handlers,
    gzip=True,
    static_path=static_path,
    log_function=log_request,
  )

  app.listen(args.port)
  for a in ('secret', 'port'):
    log("{}={!r}", a, getattr(args, a))

  # Start IOLoop
  try:
    ioloop.IOLoop.instance().start()
  except (KeyboardInterrupt, SystemExit):
    pass
