from functools import partial
import os.path

from pygit2 import Repository, GIT_SORT_TIME

from revfeed.repos.utils import gravatar


def get_repo(repo_dir):
    repo = Repository(repo_dir)
    return {
        'name': _get_repo_name(repo),
        'get_commits': partial(_get_commits, repo),
        'latest_commit': repo.head.hex,
    }


def _get_repo_name(repo):
    return os.path.split(os.path.dirname(os.path.dirname(repo.path)))[1]


def _get_commits(repo):
    for commit in repo.walk(repo.head.hex, GIT_SORT_TIME):
        yield _commit_to_dict(commit)


def _commit_to_dict(commit):
    return {
        'hex': commit.hex,
        'author_email': commit.author.email,
        'author_name': commit.author.name,
        'author_avatar': gravatar(commit.author.email),
        'message': commit.message,
        'time': commit.author.time + (commit.author.offset * 60),
    }
