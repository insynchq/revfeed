import os.path

from revfeed.logger import logger
from revfeed.repos import git, hg


def get_repo_type(repo_dir):
    if repo_dir.endswith('.git'):
        return 'git'
    elif os.path.exists(os.path.join(repo_dir, '.hg')):
        return 'hg'
    else:
        return False


def get_repos(db):
    repos = []
    for repo_name, repo_dir in db.hgetall('revfeed:repo_dirs').iteritems():
        repo_type = get_repo_type(repo_dir)
        if repo_type == 'git':
            get_repo = git.get_repo
        elif repo_type == 'hg':
            get_repo = hg.get_repo
        else:
            print 'Skipped {0}, {1}'.format(repo_name, repo_dir)
            continue
        repo = get_repo(repo_name, repo_dir)
        repos.append(repo)
    return repos


def update(db):
    commits = {}

    for repo in get_repos(db):
        logger.info(repo['name'])
        logger.info("=" * len(repo['name']))

        # Add repo to repo set
        db.sadd('revfeed:repos', repo['name'])

        # Get last latest_commit
        latest_commit = db.get(
            'revfeed:{0}:latest_commit'.format(repo['name'])
            )

        for commit in repo['get_commits']():
            if commit['hex'] == latest_commit:
                break

            commit_key = 'revfeed:{0}:{1}'.format(repo['name'], commit['hex'])

            # Set repo name for reference
            commit['repo_name'] = repo['name']

            # Add commit hash
            db.hmset(commit_key, commit)

            # Add commit to repo set
            db.zadd('revfeed:{0}'.format(repo['name']), commit['time'],
                    commit_key)

            # Add commit to revfeed set
            db.zadd('revfeed', commit['time'], commit_key)

            logger.info("%s: %s", commit['hex'][:8], commit['message'].strip())

            # Add to return value
            commits.setdefault(repo['name'], []).append(commit)

        db.set('revfeed:{0}:latest_commit'.format(repo['name']),
               repo['latest_commit'])

    return commits
