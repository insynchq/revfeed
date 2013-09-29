# Revfeed

Dead simple commits feed

## Usage

### Server

1. `pip install revfeed`
2. `revfeed --secret SECRET_TOKEN`

### Mercurial

1. Install `revfeed-hg` on where main repo is and where you will be pushing from
2. Enable in `.hgrc` of main repo and where you will be pushing from

  ```
  [extensions]
  ...
  revfeedhg =
  ```
  
3. Set config in main repo's `.hgrc`

  ```
  [revfeed]
  secret = SECRET_TOKEN
  server_name = http://localhost:5000
  ```
