import hashlib
import os.path

from pygit2 import Repository, GIT_SORT_TIME

from revfeed import settings, logger


def _get_repos():
    if not getattr(_get_repos, 'repos', False):
        _get_repos.repos = {}
        for repo_dir in settings.REPO_DIRS:
            repo = Repository(repo_dir)
            name = _get_repo_name(repo)
            if _get_repos.repos.get(name):
                raise KeyError("Duplicate repo name")
            _get_repos.repos[name] = repo
    return _get_repos.repos


def _gravatar(email):
    url = _gravatar.cache.get(email)
    if not url:
        url = _gravatar.cache[email] = (
            "https://gravatar.com/avatar/%s?size=20" %
            hashlib.md5(email).hexdigest())
    return url
_gravatar.cache = {}


def _get_repo_name(repo):
    return os.path.split(os.path.dirname(os.path.dirname(repo.path)))[1] + \
           '.git'


def _get_commits(repo, start):
    for commit in repo.walk(start, GIT_SORT_TIME):
        yield commit


def _commit_to_dict(commit):
    return {
        'hex': commit.hex,
        'author_email': commit.author.email,
        'author_name': commit.author.name,
        'author_avatar': _gravatar(commit.author.email),
        'message': commit.message,
        'time': commit.author.time + (commit.author.offset * 60),
    }


def update(db):
    for repo in _get_repos().values():
        repo_name = _get_repo_name(repo)

        logger.info(repo_name)
        logger.info("=" * len(repo_name))

        # Add repo to repo set
        db.sadd('revfeed:repos', repo_name)

        # Get last head
        curr_head = db.get('revfeed:%s:head' % repo_name)

        for commit in map(_commit_to_dict, _get_commits(repo, repo.head.hex)):
            if commit['hex'] == curr_head:
                break

            commit_key = 'revfeed:%s:%s' % (repo_name, commit['hex'])

            # Set repo name for reference
            commit['repo_name'] = repo_name

            # Add commit hash
            db.hmset(commit_key, commit)

            # Add commit to repo set
            db.zadd('revfeed:%s' % repo_name, commit['time'],
                    commit_key)

            # Add commit to revfeed set
            db.zadd('revfeed', commit['time'], commit_key)

            logger.info("%s: %s", commit['hex'][:8], commit['message'].strip())

        db.set('revfeed:%s:head' % repo_name, repo.head.hex)
