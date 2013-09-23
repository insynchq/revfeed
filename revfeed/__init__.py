'''dead simple commits feed'''  # extension help


from .ext import reposetup
from .server import startserver


cmdtable = dict(revfeed=(
  startserver,
  [
    ('p', 'port', 5000, 'port to listen'),
    ('', 'redis-prefix', 'revfeed', 'redis prefix'),
    ('', 'redis-host', 'localhost', 'redis port'),
    ('', 'redis-port', 6379, 'redis port'),
  ],
))
