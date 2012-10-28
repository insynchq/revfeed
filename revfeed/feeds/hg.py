import os.path
import re

from mercurial import hg, ui

from revfeed import settings, logger
from revfeed.feeds.utils import gravatar


def _get_repo_name(repo):
    return os.path.basename(repo.root) + '.hg'


def _get_repos():
    if not getattr(_get_repos, 'repos', False):
        _get_repos.repos = {}
        _ui = ui.ui()
        is_hg = lambda d: os.path.exists(os.path.join(d, '.hg'))
        for repo_dir in filter(is_hg, settings.REPO_DIRS):
            repo = hg.repository(_ui, repo_dir)
            name = _get_repo_name(repo)
            if _get_repos.repos.get(name):
                raise KeyError("Duplicate repo name")
            _get_repos.repos[name] = repo
    return _get_repos.repos


def _get_commits(repo):
    for i in reversed(xrange(len(repo))):
        commit = repo[i]
        if commit.hex() == '0000000000000000000000000000000000000000':
            break
        else:
            yield commit


USERNAME_PAT = re.compile("([^<]+)<([^>]+)>")
EMAIL_PAT = re.compile(".+@.+\..+")


def _commit_to_dict(commit):
    changeid, username, timestamp_tuple, files_changed, message, extra = \
        commit.changeset()
    match = USERNAME_PAT.search(username)
    if match:
        author_name, author_email = match.groups()
    else:
        if EMAIL_PAT.match(username):
            author_email = username
            author_name = None
        else:
            author_name = username
            author_email = None
    return {
        'hex': commit.hex(),
        'author_email': author_email,
        'author_name': author_name,
        'author_avatar': gravatar(author_email),
        'message': message,
        'time': int(sum(timestamp_tuple)),
    }


def update(db):
    commits = {}

    for repo in _get_repos().values():
        repo_name = _get_repo_name(repo)

        logger.info(repo_name)
        logger.info("=" * len(repo_name))

        # Add repo to repo set
        db.sadd('revfeed:repos', repo_name)

        # Get last head
        curr_head = db.get('revfeed:%s:head' % repo_name)

        for commit in map(_commit_to_dict, _get_commits(repo)):
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

            # Add to return value
            commits.setdefault(repo_name, []).append(commit)

        db.set('revfeed:%s:head' % repo_name, repo[repo.changelog.tip()].hex())

    return commits
