import logging.handlers

handler = logging.handlers.RotatingFileHandler(
    'app.log', maxBytes=10000, backupCount=3
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)
