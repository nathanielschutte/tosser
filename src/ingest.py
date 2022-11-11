
import asyncio

from typing import List, Optional
from pathlib import Path

from src.parsers.Base import BaseParser, BaseObject
from src.connections import BaseConnection

from src.constants import IngestState
from src.context import Context
from src.map import Translator

# Each table 

class Ingest:
    
    def __init__(
        self, 
        parser: BaseParser, 
        connection: BaseConnection
    ) -> None:

        self.parser: BaseParser = parser
        self.conn: BaseConnection = connection

        self.context: Context = Context()
        self.map: Translator = Translator()

        self.state: IngestState = IngestState.IDLE

    def _traverse(self):
        ...

    def generate_schema(self, output_file: Optional[Path] = None) -> None:

        # Start in the reading state
        self.state = IngestState.READING

        # Get next object
        for obj in self.parser.get_objects():
            ...
        