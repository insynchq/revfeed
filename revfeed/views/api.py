import os.path


from pygit2 import Repository, GIT_SORT_TIME
from flask import Blueprint, current_app, jsonify


api = Blueprint('api', __name__, url_prefix='/api')


def _get_commits(repo, start=None, count=10):
    start = repo.head.oid if not start else start
    return [commit for commit in repo.walk(start, GIT_SORT_TIME)]


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


@api.route('/repos')
def repos():
    repos = [Repository(repo_dir) for repo_dir in
             current_app.config['REPO_DIRS']]
    return jsonify({
        'repos': [
            {
                'workdir': repo.workdir,
                'commits': map(_commit_to_dict, _get_commits(repo)),
                'name': os.path.split(os.path.dirname(repo.workdir))[1],
            }
            for repo in repos
        ]
    })
