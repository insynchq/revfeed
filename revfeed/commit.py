class Commit(object):

  _fields = (
    'repo',
    'hex',
    'author',
    'timestamp',
    'timezone',
    'message',
    'branch',
  )

  def __init__(self, **kwargs):
    for f in self._fields:
      setattr(self, f, kwargs[f])

  @property
  def key(self):
    return self.repo, self.hex

  @property
  def tags_list(self):
    return self.tags.split(',')

  @property
  def utc_timestamp(self):
    return int(float(self.timestamp) - int(self.timezone))
