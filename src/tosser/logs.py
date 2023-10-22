import logging

LOG_DEBUG = 'debug'
LOG_MAIN = 'tosser'
LOG_ENDPOINT = 'endpoint'

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s: %(name)s | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'formatter': 'default',
            'level': logging.DEBUG,
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        }
    },
    'loggers': {
        LOG_MAIN: {
            'level': logging.INFO,
            'handlers': ['console']
        },
        LOG_DEBUG: {
            'level': logging.DEBUG,
            'handlers': ['console']
        },
        LOG_ENDPOINT: {
            'level': logging.DEBUG,
            'handlers': ['console']
        }
    }
}
