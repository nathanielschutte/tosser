import json
from typing import Dict, Any
from pathlib import Path
import logging

from tosser.logs import LOG_MAIN
from tosser.exceptions import TosserSchemaException
from tosser.object import TosserObject
from tosser.traverse import Traverser

SCHEMA_FILE_EXT = 'toss'
SCHEMA_DEFAULT_FILE_NAME = 'schema'

class TosserSchema:
    """Tosser schema data structure"""
    
    def __init__(self) -> None:
        self._log = logging.getLogger(LOG_MAIN)

        self.complete = True
        self.filename = f'{SCHEMA_DEFAULT_FILE_NAME}.{SCHEMA_FILE_EXT}'
        self.schema: Dict[str, Any] = {}

        self._generating = False
        self._gen_n = 0


    def begin(self) -> None:
        """Begin a new schema generation"""
        
        self.complete = False
        self._generating = True
        self._gen_n = 0 # counting contributions

        self._log.info('Beginning new schema generation')


    def contribute(self, obj: TosserObject) -> None:
        """Contribute a TosserObject to a generating schema"""

        if not self._generating:
            raise TosserSchemaException('Cannot contribute an object to a non-generating TosserSchema')
        
        # full traverse
        tr = Traverser(rules=None)
        for trail, key, value in tr.traverse(obj):
            assert trail[-1].val == key
            print(f'{Traverser.get_trail_string(trail)} = {value}')
        
        self._log.debug(f'Contributed object [{self._gen_n}] to new schema')
        self._gen_n += 1
        


    def end(self) -> None:
        """End new schema generation"""

        if self.complete or not self._generating:
            raise TosserSchemaException('Cannot end an already complete TosserSchema')

        self.complete = True
        self._generating = False

        self._log.info(f'Ending new schema generation: contributed {self._gen_n} objects')


    def load_file(self) -> None:
        """Load schema from file"""
        ...


    def write_file(self, work_dir: Path) -> None:
        """Write schema to file"""

        filepath = work_dir / self.filename
        self._log.info(f'Writing schema to file: {filepath}')
        with open(filepath, 'w') as f:
            f.write(self._render())


    def _render(self) -> str:
        return json.dumps(self.schema)
