import json
from typing import Dict, Any
from pathlib import Path
import logging

from tosser.logs import LOG_DEBUG

SCHEMA_FILE_EXT = 'toss'
SCHEMA_DEFAULT_FILE_NAME = 'schema'

class TosserSchema:
    """Tosser schema data structure"""
    
    def __init__(self) -> None:
        self._log = logging.getLogger(LOG_DEBUG)

        self.filename = f'{SCHEMA_DEFAULT_FILE_NAME}.{SCHEMA_FILE_EXT}'
        self.schema: Dict[str, Any] = {}


    def write_file(self, work_dir: Path) -> None:
        filepath = work_dir / self.filename
        self._log.debug(f'Writing schema to file: {filepath}')
        with open(filepath, 'w') as f:
            f.write(self._render())


    def _render(self) -> str:
        return json.dumps(self.schema)
