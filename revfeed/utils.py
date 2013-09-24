from base64 import b64encode
from os import urandom


def log(msg, *args):
  print msg.format(*args)


def log_request(rh):
  log(
    "{:.2f}ms ({}) {}",
    rh.request.request_time() * 1000,
    rh.get_status(),
    rh.request.uri,
  )


def redis_key(*args):
  return ':'.join(args)


def gen_secret(l):
  return b64encode(urandom(l))
