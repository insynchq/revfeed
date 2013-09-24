from sockjs.tornado import SockJSConnection


class NotifierConnection(SockJSConnection):
  def on_open(self, info):
    pass

  def on_message(self, msg):
    pass

  def on_close(self):
    pass
