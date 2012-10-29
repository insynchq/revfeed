import os.path

from revfeed import logger, settings
from revfeed.repos import git, hg


def _get_repos():
    repos = []
    repo_names = set()
    for repo_dir in settings.REPO_DIRS:
        if repo_dir.endswith('.git'):
            get_repo = git.get_repo
        elif os.path.exists(os.path.join(repo_dir, '.hg')):
            get_repo = hg.get_repo
        repo = get_repo(repo_dir)
        if repo['name'] in repo_names:
            raise KeyError("Duplicate repo name")
        repos.append(repo)
    return repos


def update(db):
    commits = {}

    for repo in _get_repos():
        logger.info(repo['name'])
        logger.info("=" * len(repo['name']))

        # Add repo to repo set
        db.sadd('revfeed:repos', repo['name'])

        # Get last latest_commit
        latest_commit = db.get('revfeed:%s:latest_commit' % repo['name'])

        for commit in repo['get_commits']():
            if commit['hex'] == latest_commit:
                break

            commit_key = 'revfeed:%s:%s' % (repo['name'], commit['hex'])

            # Set repo name for reference
            commit['repo_name'] = repo['name']

            # Add commit hash
            db.hmset(commit_key, commit)

            # Add commit to repo set
            db.zadd('revfeed:%s' % repo['name'], commit['time'],
                    commit_key)

            # Add commit to revfeed set
            db.zadd('revfeed', commit['time'], commit_key)

            logger.info("%s: %s", commit['hex'][:8], commit['message'].strip())

            # Add to return value
            commits.setdefault(repo['name'], []).append(commit)

        db.set('revfeed:%s:latest_commit' % repo['name'],
               repo['latest_commit'])

    return commits
