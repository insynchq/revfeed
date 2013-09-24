from base64 import b64encode
from os import urandom
from time import time
import argparse
import pkg_resources
try:
  import json
except ImportError:
  from simplejson import json

from tornado import web, ioloop
from sockjs.tornado import SockJSRouter, SockJSConnection
import redis


class IndexHandler(web.RequestHandler):
  def get(self):
    self.render('index.html')


class CommitsHandler(web.RequestHandler):

  def __init__(self, *args, **kwargs):
    self.redis_prefix = kwargs.pop('redis_prefix')
    self.redis_conn = kwargs.pop('redis_conn')
    self.secret = kwargs.pop('secret')
    super(CommitsHandler, self).__init__(*args, **kwargs)

  def redis_key(self, *args):
    return redis_key(self.redis_prefix, *args)

  def post(self):
    # Check auth header
    auth = self.request.headers['Authorization']
    if not auth.startswith('revfeed-secret'):
      self.send_error(401)
      return
    secret = auth.split(' ', 1)[1]
    if secret != self.secret:
      self.send_error(401)
      return

    # Persist
    data = json.loads(self.request.body)
    for commit in data['commits']:
      # Prepare
      commit['tags'] = ', '.join(commit['tags'])
      commit['timestamp'], commit['timezone'] = commit.pop('date')
      # Store
      commit_key = self.redis_key('commits', commit['repo'], commit['hex'])
      self.redis_conn.zadd(
        self.redis_key('commits'),
        int(time()),
        commit_key,
      )
      self.redis_conn.hmset(commit_key, commit)

    self.write(dict(success=True))


class NotifierConnection(SockJSConnection):
  def on_open(self, info):
    pass

  def on_message(self, msg):
    pass

  def on_close(self):
    pass


def log_request(rh):
  print "{:.2f}ms ({}) {}".format(
    rh.request.request_time() * 1000,
    rh.get_status(),
    rh.request.uri,
  )


def redis_key(*args):
  return ':'.join(args)


def gen_secret(l):
  return b64encode(urandom(l))


def main():
  print "{}\n".format(__package__)

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
    print "deleted {} keys".format(count)
    return

  # Setup handlers
  handlers = []
  handlers.append((r'/', IndexHandler))
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
    print "{}={!r}".format(a, getattr(args, a))

  # Start IOLoop
  try:
    ioloop.IOLoop.instance().start()
  except (KeyboardInterrupt, SystemExit):
    pass
