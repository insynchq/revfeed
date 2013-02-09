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

### To start web server:
`revfeed run_server`

### To update db:
`revfeed update_db`

This command also pushes notifications using websockets. You typically want to run this command this everytime
you push to a repo using commit hooks.

P.S. I don't know what I was thinking then but notifications are inefficient at the moment. Instead of just notifying
connected clients about the new commits and pulling from the api, the notifications themselves contain the commit
information :P I'll try to fix that soon or if you want to take a stab at it, you're more than welcome to do a pull
request.


## TODO

* Repo feed
* Commit details (diff view and other info)


