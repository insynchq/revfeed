from functools import partial
import os.path
import re

from mercurial import hg, ui

from revfeed.repos.utils import gravatar

_ui = ui.ui()


def get_repo(repo_dir):
    repo = hg.repository(_ui, repo_dir)
    return {
        'name': _get_repo_name(repo),
        'get_commits': partial(_get_commits, repo),
        'latest_commit': repo[repo.changelog.tip()].hex(),
    }


def _get_repo_name(repo):
    return os.path.basename(repo.root)


def _get_commits(repo):
    for i in reversed(xrange(len(repo))):
        commit = repo[i]
        if commit.hex() == '0000000000000000000000000000000000000000':
            break
        else:
            yield _commit_to_dict(commit)


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
        'time': int(timestamp_tuple[0] - timestamp_tuple[1]),
    }
