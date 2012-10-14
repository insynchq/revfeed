import hashlib
import os.path

from pygit2 import Repository, GIT_SORT_TIME
from flask import Blueprint, current_app, request, jsonify, url_for


api = Blueprint('api', __name__, url_prefix='/api')


def _gravatar(email):
    url = _gravatar.cache.get(email)
    if not url:
        url = _gravatar.cache[email] = (
            "https://gravatar.com/avatar/%s?size=20" %
            hashlib.md5(email).hexdigest())
    return url
_gravatar.cache = {}


def _get_repo_name(repo):
    return os.path.split(os.path.dirname(os.path.dirname(repo.path)))[1]


def _get_commits(repo, start, count):
    commits = []
    for commit in repo.walk(start, GIT_SORT_TIME):
        commits.append(commit)
        count -= 1
        if count < 1:
            break
    return commits


def _commit_to_dict(commit):
    return {
        'id': commit.hex,
        'hex': commit.hex,
        'author': {
            'id': commit.author.email,
            'email': commit.author.email,
            'name': commit.author.name,
            'avatar': _gravatar(commit.author.email),
        },
        'message': commit.message,
        'time': (commit.author.time + (commit.author.offset * 60)) * 1000,
    }


def _repo_to_dict(repo, start=None, count=10):
    name = _get_repo_name(repo)
    start = start if start else repo.head.hex
    commits = map(_commit_to_dict, _get_commits(repo, start=start,
                                                count=count))
    if commits:
        walker = repo.walk(commits[-1]['hex'], GIT_SORT_TIME)
        walker.next()  # prep
        try:
            next = url_for('.repos', repo=name, start=walker.next().hex)
        except StopIteration:
            next = None
    else:
        next = None
    return {
        'id': name,
        'name': name,
        'path': repo.path,
        'commits': commits,
        'start': start,
        'next': next,
    }


def _get_repos():
    if not _get_repos.repos:
        for repo_dir in current_app.config['REPO_DIRS']:
            repo = Repository(repo_dir)
            name = _get_repo_name(repo)
            if _get_repos.repos.get(name):
                raise KeyError("Duplicate repo name")
            _get_repos.repos[name] = repo
    return _get_repos.repos
_get_repos.repos = {}  # memoize


@api.route('/repos')
@api.route('/repos/<repo>')
def repos(repo=None):
    if repo:
        return jsonify(_repo_to_dict(_get_repos()[repo],
                                     start=request.args.get('start')))
    else:
        return jsonify({
            'repos': map(_repo_to_dict, _get_repos().values())
        })
