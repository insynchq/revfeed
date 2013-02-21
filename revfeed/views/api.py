from flask import Blueprint, current_app, request, url_for, jsonify

from revfeed import config
from revfeed.db import db


api = Blueprint('api', __name__, url_prefix='/api')


def _get_commit(commit_key):
    commit = db.hgetall(commit_key)
    repo_dir = (db.hget('revfeed:repo_dirs', commit['repo_name'])
                .rstrip('/.git'))
    commit['commit_url'] = (config.COMMIT_URL_PATTERN
                            .sub(config.COMMIT_URL_REPL, repo_dir)
                            .format(hex=commit['hex']))
    return commit


def _get_commits(zkey):
    num = current_app.config['COMMITS_PER_FETCH']
    before = int(request.args.get('before', 0))

    # We fetch the next commit too in order to get the next before value

    if before:
        commit_keys = db.zrevrangebyscore(zkey, before, 0, start=0,
                                          num=num + 1)
    else:
        # Note the missing `+ 1`. ZREVRANGE is adding one to the count on its
        # own for some reason
        commit_keys = db.zrevrange(zkey, 0, num)

    commits = map(_get_commit, commit_keys)

    if len(commits) > num and commits[:num]:
        before = commits[-1]['time']
    else:
        before = None

    return commits[:num], before


@api.route('/revfeed')
def revfeed():
    commits, before = _get_commits('revfeed')
    next_url = url_for('.revfeed', before=before) if before else None
    return jsonify({
        'commits': commits,
        'next_url': next_url,
        })


@api.route('/repos/<repo_name>')
def repos(repo_name):
    commits, before = _get_commits('revfeed:{0}'.format(repo_name))
    next_url = url_for('.repos', repo_name=repo_name, before=before) if \
        before else None
    return jsonify({
        'commits': commits,
        'next_url': next_url,
        })


@api.route('/repos/<repo_name>/commits/<commit_sum>')
def commits(repo_name, commit_sum):
    return jsonify(db.hgetall('revfeed:{0}:{1}'.format(repo_name, commit_sum)))
