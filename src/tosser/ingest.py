import asyncio
import logging

from typing import List, Optional
from pathlib import Path

from tosser.parsers.parser import Parser, BaseObject
from tosser.constants import IngestState
from tosser.context import Context
from tosser.exceptions import IngestException
from tosser.logs import LOG_MAIN, LOG_DEBUG
from tosser.endpoint.target import ITarget
from tosser.endpoint.source import ISource

class Ingest:
    def __init__(
        self, 
        source: ISource,
        target: ITarget,
    ) -> None:
        self.logger = logging.getLogger(LOG_DEBUG)

        self.source = source
        self.target = target

        self.context: Context = Context()

        self.state: IngestState = IngestState.IDLE

    @classmethod
    def _get_log(cls):
        return logging.getLogger(LOG_DEBUG)

    def _update_state(self, new_state: IngestState):
        self.logger.debug(f'State changed {self.state.value} -> {new_state.value}')
        self.state = new_state

    def _traverse(self):
        ...

    def generate_schema(
        self,
        input: Path,
        output: Path
    ) -> None:

        # Start in the reading state
        self._update_state(IngestState.READING)
