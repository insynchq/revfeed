import os.path

from pygit2 import Repository, GIT_SORT_TIME
from flask import Blueprint, current_app, request, jsonify, url_for


api = Blueprint('api', __name__, url_prefix='/api')


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
        'hex': commit.hex,
        'author': {
            'name': commit.author.name,
            'email': commit.author.email,
            'time': commit.author.time,
            'offset': commit.author.offset,
        },
        'message': commit.message,
        'avatar': None,
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
            next = url_for('.api_repos', repo=name, start=walker.next().hex)
        except StopIteration:
            next = None
    else:
        next = None
    return {
        'path': repo.path,
        'name': name,
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
