import logging

from tosser.logs import LOG_DEBUG, LOG_ENDPOINT, LOG_MAIN

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
        },
        'log': {
            'formatter': 'default',
            'level': logging.DEBUG,
            'class': 'logging.FileHandler',
            'filename': 'out.log',
            'mode': 'a'
        }
    },
    'loggers': {
        LOG_MAIN: {
            'level': logging.DEBUG,
            'handlers': ['log']
        },
        LOG_DEBUG: {
            'level': logging.DEBUG,
            'handlers': ['log']
        },
        LOG_ENDPOINT: {
            'level': logging.DEBUG,
            'handlers': ['log']
        }
    }
}
