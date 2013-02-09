import logging

from revfeed import settings


logger = logging.getLogger('revfeed')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
