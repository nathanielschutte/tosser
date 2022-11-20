
import asyncio
import logging
import logging.config

from typing import List, Optional
from pathlib import Path

from tosser.parsers.Base import BaseParser, BaseObject
from tosser.connections import BaseConn
from tosser.constants import IngestState
from tosser.context import Context
from tosser.map import Translator
from tosser.exceptions import IngestException
from tosser.logs import LOGGING_CONFIG, LOG_MAIN, LOG_DEBUG


class Ingest:
    
    def __init__(
        self, 
        parser: BaseParser, 
        connection: BaseConn
    ) -> None:
        logging.config.dictConfig(LOGGING_CONFIG)

        self.parser: BaseParser = parser
        self.conn: BaseConn = connection

        self.context: Context = Context()
        self.map: Translator = Translator()

        self.state: IngestState = IngestState.IDLE

    @classmethod
    def _get_log(cls):
        return logging.getLogger(LOG_DEBUG)

    def _update_state(self, new_state: IngestState):
        Ingest._get_log().debug(f'State changed {self.state.value} -> {new_state.value}')
        self.state = new_state

    def _traverse(self):
        ...

    def generate_schema(
        self,
        input: Optional[Path] = None,
        output: Optional[Path] = None
    ) -> None:

        if input is None or output is None:
            raise IngestException('Must specify input and output files')

        # Start in the reading state
        self._update_state(IngestState.READING)

        # Get next object
        for obj in self.parser.get_objects(path=input):
            print(obj.data)
        