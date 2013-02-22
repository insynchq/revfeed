# revfeed

Version control commits feed. Just a page full of commits. Nothing else. New commits show up as notifs twitter style.
Alpha quality and no documentation :P

## Install
```shell
mkvirtualenv revfeed
git clone https://github.com/marksteve/revfeed.git
cd revfeed
python setup.py develop/install
```

A shell script for pygit2 is included if you have troubles installing it.

## Usage

### To add repos:

`revfeed add_repo repo_name absolute_repo_dir_path`

Note that git repos should point to the .git dir (e.g. `/home/marksteve/repos/gitrepo/.git` or
`/home/marksteve/repos/gitrepo.git` for bare repos) while mercurial repos should just point to the parent (e.g.
`/home/marksteve/hgrepo`)

### To remove repos:
`revfeed rm_repo repo_name`

### To list repos added:
`revfeed ls_repo`

### To start web server:
`revfeed run_server`

### To update db:
`revfeed update_db`

This command also pushes notifications using websockets. You typically want to run this command this everytime
you push to a repo using commit hooks.

## Commit details

You can link commits to your repo web server if you want to check out more about the commit.
Just change `COMMIT_URL_PATTERN` and `COMMIT_URL_REPL` (`{hex}` contains the hex id of the commit).

## TODO

* Repo feed


