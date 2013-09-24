from time import time

try:
  import json
except ImportError:
  from simplejson import json

from tornado import web

from .utils import redis_key


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

