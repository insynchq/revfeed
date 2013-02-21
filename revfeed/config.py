from os import environ
import re


# Defaults

DEBUG = False

WEB_HOST = "localhost"
WEB_PORT = 5000

REDIS_HOST = "localhost"
REDIS_PORT = 6379

COMMITS_PER_FETCH = 20

COMMIT_URL_PATTERN = '/var/repos/(?P<path>.+)$'
COMMIT_URL_REPL = 'http://repos.local/\g<path>/{hex}'


# Get config from ENV

_locals = locals()

for key in _locals.keys():
    if key.isupper():
        value = environ.get(key)
        if value:
            _locals[key] = value


WEB_PORT = int(WEB_PORT)
REDIS_PORT = int(REDIS_PORT)
COMMITS_PER_FETCH = int(COMMITS_PER_FETCH)

COMMIT_URL_PATTERN = re.compile(COMMIT_URL_PATTERN)
