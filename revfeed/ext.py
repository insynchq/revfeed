import httplib
try:
  import json
except ImportError:
  from simplejson import json


FIELDS = (
  'hex',
  'user',
  'date',
  'description',
  'branch',
  'tags',
)


def hook(ui, repo, **kwargs):
  error = None

  # Get repo name or default to repo root path
  repo_name = ui.config('revfeed', 'repo_name', repo.root)

  # Get config values
  secret = ui.config('revfeed', 'secret')
  if not secret:
    error = "no revfeed.secret specified"
  server_name = ui.config('revfeed', 'server_name')
  if not server_name:
    error = "no revfeed.server_name specified"

  # Post commit to server
  if not error:
    try:
      commits = []

      # Get new commits
      root = repo[kwargs['node']].node()
      for node in repo.changelog.nodesbetween([root])[0]:
        # Get repo info
        ctx = repo[node]
        commit = dict(repo=repo_name)
        for f in FIELDS:
          commit[f] = getattr(ctx, f)()
        commits.append(commit)

      # Post request
      data = dict(commits=commits)
      headers = {
        'Authorization': 'revfeed-secret ' + secret,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      }
      conn = httplib.HTTPConnection(server_name)
      conn.request('POST', '/commits', json.dumps(data), headers)

      # Check response
      resp = json.loads(conn.getresponse().read())
      if not resp.get('success'):
        error = resp.get('error', "unknown error")

    except Exception as e:
      error = str(e)

  if error:
    ui.warn("failed to post to revfeed: {}\n".format(error))
  else:
    ui.status("posted {} changesets to revfeed\n".format(len(commits)))


def reposetup(ui, repo):
  # Set as a changegroup hook
  ui.setconfig('hooks', 'changegroup.revfeed', hook)
