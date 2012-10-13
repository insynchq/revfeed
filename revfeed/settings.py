from os import environ


# Defaults

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_KEY_PREFIX = "revfeed:cache:"

REPO_DIRS = "./.git"


# Get config from ENV

_locals = locals()

for key in _locals.keys():
    if key.isupper():
        value = environ.get(key)
        if value:
            _locals[key] = value


REPO_DIRS = REPO_DIRS.split(',')
