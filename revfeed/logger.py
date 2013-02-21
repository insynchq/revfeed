import logging

from revfeed import config 


logger = logging.getLogger('revfeed')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG if config.DEBUG else logging.INFO)
