import argparse
import pkg_resources

from tornado import web, ioloop
from sockjs.tornado import SockJSRouter, SockJSConnection


class IndexHandler(web.RequestHandler):
  def get(self):
    self.render('index.html')


class NotifierConnection(SockJSConnection):
  def on_open(self, info):
    pass

  def on_message(self, msg):
    pass

  def on_close(self):
    pass


def log_request(rh):
  print "  * {:.2f}ms ({}) {}".format(
    rh.request.request_time() * 1000,
    rh.get_status(),
    rh.request.uri,
  )


def main():
  # Parse args
  parser = argparse.ArgumentParser(description="Dead simple commits feed.")
  parser.add_argument('-p', '--port', type=int, default=5000)
  args = parser.parse_args()

  # Setup app
  notifier = SockJSRouter(NotifierConnection, '/notifier')
  static_path = pkg_resources.resource_filename(__package__, 'static')
  app = web.Application(
    [
      (r'/', IndexHandler),
    ] + notifier.urls,
    gzip=True,
    static_path=static_path,
    log_function=log_request,
  )
  app.listen(args.port)

  print "\n  Revfeed\n"
  print "  * listening to {}".format(args.port)

  # Start IOLoop
  ioloop.IOLoop.instance().start()
