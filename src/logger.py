import logging

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s: %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "main": {
            "formatter": "default",
            "level": logging.DEBUG,
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        }
    },
    "loggers": {"main": {"level": logging.INFO, "handlers": ["main"]}},
    "root": {"level": logging.INFO, "handlers": ["verbose_output"]},
}
