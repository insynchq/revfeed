import os.path
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import msgpack

from revfeed import settings, db, update_db, logger


class NotifierHandler(FileSystemEventHandler):

    def on_modified(self, event):
        commits = update_db()

        if commits:
            # Publish to revfeed
            revfeed_commits = [item for sublist in commits.values() for item in
                               sublist]
            db.publish('notifier', msgpack.packb(['revfeed', revfeed_commits]))
            # Publish to each repo
            for repo_name in commits.keys():
                db.publish('notifier', msgpack.packb([repo_name,
                                                      commits[repo_name]]))


if __name__ == '__main__':
    observer = Observer()
    revfeed_event_handler = NotifierHandler()
    for repo_dir in settings.REPO_DIRS:
        observer.schedule(revfeed_event_handler,
                          path=os.path.join(repo_dir, 'refs/heads'),
                          recursive=True)
    observer.start()
    logger.info("Started notifier")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
