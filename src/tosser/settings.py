
# Ingest options

import os
import logging
from enum import Enum

from pydantic import BaseSettings, BaseModel, Field, SecretStr, validator

logger = logging.getLogger(__name__)


class Environment(Enum):
    PRODUCTION = 'PRODUCTION'
    DEVELOPMENT = 'DEVELOPMENT'


class Credentials(BaseSettings):
    """Secret configuration"""
    host = 'localhost'
    


class Configuration(BaseSettings):
    """Nonsensitive configuration"""
    
    env: Environment = Environment.DEVELOPMENT
    dryrun: bool = False
    log_level: str = 'INFO'

    @validator("log_level")
    def _is_valid_log_level(cls, log_level: str) -> str:
        numeric_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Unrecognized log level {log_level}")

        return log_level.upper()

class Settings(BaseModel):
    creds: Credentials = Field(default_factory=lambda: Credentials())
    config: Configuration = Field(default_factory=lambda: Configuration())

