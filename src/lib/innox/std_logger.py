import logging
import logging.config

logging_config = dict(
    version = 1,
    formatters = {
        'f': {'format':
              '%(asctime)s | %(levelname)s | %(module)s | %(funcName)s | %(message)s'}
        },
    handlers = {
        'h': {'class': 'logging.StreamHandler',
              'formatter': 'f',
              'level': logging.DEBUG}
        },
    root = {
        'handlers': ['h'],
        'level': logging.DEBUG,
        },
)
logging.config.dictConfig(logging_config)

logger = logging.getLogger()
