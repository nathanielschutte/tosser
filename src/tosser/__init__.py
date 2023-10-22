import logging.config
from tosser.logs import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)

from tosser.tosser import Tosser
from tosser.exceptions import TosserException

__all__ = ['Tosser', 'TosserException']
