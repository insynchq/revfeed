from time import time
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
    return ':'.join([self.redis_prefix] + list(args))

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
  print "  * {:.2f}ms ({}) {}".format(
    rh.request.request_time() * 1000,
    rh.get_status(),
    rh.request.uri,
  )


def startserver(ui, repo, **kwargs):
  """
  start revfeed server
  """

  # Fix imports
  from mercurial import demandimport
  demandimport.ignore.extend([
    'select',
    'hiredis',
  ])

  # Setup redis connection
  redis_prefix = kwargs.get('redis_prefix')
  redis_conn = redis.StrictRedis(
    kwargs.get('redis_host'),
    kwargs.get('redis_port'),
  )

  # Setup handlers
  handlers = []
  handlers.append((r'/', IndexHandler))
  handlers.append((r'/commits', CommitsHandler, dict(
    secret=ui.config('revfeed', 'secret'),
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

  port = kwargs.get('port')
  app.listen(port)
  print "\n  Revfeed\n"
  print "  * listening to {}".format(port)

  # Start IOLoop
  try:
    ioloop.IOLoop.instance().start()
  except (KeyboardInterrupt, SystemExit):
    print "\n  * stopped"
