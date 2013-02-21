from os import environ


# Defaults

DEBUG = False

WEB_HOST = "localhost"
WEB_PORT = 5000

REDIS_HOST = "localhost"
REDIS_PORT = 6379

COMMITS_PER_FETCH = 20


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
