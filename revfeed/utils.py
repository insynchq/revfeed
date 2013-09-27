from base64 import b64encode
from os import urandom
import logging


fmt = logging.Formatter("[%(name)s][%(module)s:%(funcName)s:%(lineno)d]"
                        "%(message)s")
hdlr = logging.StreamHandler()
hdlr.setFormatter(fmt)
logger = logging.getLogger(__package__)
logger.propagate = False
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


def log_request(rh):
  logger.info("{:.2f}ms ({}) {}".format(
    rh.request.request_time() * 1000,
    rh.get_status(),
    rh.request.uri,
  ))


def redis_key(*args):
  return ':'.join(args)


def gen_secret(l):
  return b64encode(urandom(l))
