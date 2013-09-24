from time import time

try:
  import json
except ImportError:
  from simplejson import json

from tornado import web

from .commit import Commit
from .utils import redis_key


class RedisHandler(web.RequestHandler):

  def __init__(self, *args, **kwargs):
    self.redis_prefix = kwargs.pop('redis_prefix')
    self.redis_conn = kwargs.pop('redis_conn')
    super(RedisHandler, self).__init__(*args, **kwargs)

  def redis_key(self, *args):
    return redis_key(self.redis_prefix, *args)


class IndexHandler(RedisHandler):

  def get(self):
    keys = self.redis_conn.zrevrange(self.redis_key('commits'), 0, 50)
    p = self.redis_conn.pipeline()
    for k in keys:
      p.hgetall(k)
    commits = [Commit(**c) for c in p.execute()]
    self.render('index.html', commits=commits)


class CommitsHandler(RedisHandler):

  def __init__(self, *args, **kwargs):
    self.secret = kwargs.pop('secret')
    super(CommitsHandler, self).__init__(*args, **kwargs)

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
    for c in data['commits']:
      commit = Commit(**c)
      # Store
      commit_key = self.redis_key('commits', *commit.key)
      now = time()
      score = now + (commit.timestamp + commit.timezone) / now
      self.redis_conn.zadd(
        self.redis_key('commits'),
        score,
        commit_key,
      )
      self.redis_conn.hmset(commit_key, commit.__dict__)

    self.write(dict(success=True))
