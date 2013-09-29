# Revfeed

Dead simple commits feed

## Usage

### Server

1. `pip install revfeed`
2. `revfeed --secret SECRET_TOKEN`

### Mercurial

1. Install `revfeed-hg` on where repo is hosted and where you need to push
2. Enable in `.hgrc`

  ```
  [extensions]
  ...
  revfeedhg =
  ```
  
3. Set config on hosted repo's `.hgrc`

  ```
  [revfeed]
  secret = SECRET_TOKEN
  server_name = http://localhost:5000
  ```
