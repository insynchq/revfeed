from os import environ


# Defaults

DEBUG = False

WEB_HOST = "localhost"
WEB_PORT = 5000

REDIS_HOST = "localhost"
REDIS_PORT = 6379

REPO_DIRS = {}

COMMITS_PER_FETCH = 10


# Get config from ENV

_locals = locals()

for key in _locals.keys():
    if key.isupper():
        value = environ.get(key)
        if value:
            _locals[key] = value


WEB_PORT = int(WEB_PORT)
REDIS_PORT = int(REDIS_PORT)
if isinstance(REPO_DIRS, str):
    for repo_entry in REPO_DIRS.split(','):
        repo_name, repo_dir = repo_entry.split('=')
        REPO_DIRS[repo_name] = repo_dir
