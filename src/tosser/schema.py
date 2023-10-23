import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging
import dataclasses

from tosser.logs import LOG_MAIN
from tosser.exceptions import TosserSchemaException
from tosser.object import TosserObject
from tosser.traverse import Traverser
from tosser.schema_types import TosserSchemaTypeVar
from tosser.types import TossPathT
from tosser.util import resolve_path_ref

SCHEMA_FILE_EXT = 'toss'
SCHEMA_DEFAULT_FILE_NAME = 'schema'


@dataclasses.dataclass()
class TosserSchemaColumn:
    table_name: str
    column_name: str
    type_var: TosserSchemaTypeVar
    enum: List[Any]
    max_length: int


class TosserSchema:
    """Tosser schema data structure"""
    
    def __init__(self, path: Optional[TossPathT] = None) -> None:
        self._log = logging.getLogger(LOG_MAIN)

        self.complete = True
        self.filename = TosserSchema.default_file_string()
        self.path = Path(self.filename)
        if path is not None:
            self.path = resolve_path_ref(path)
            self.filename = os.path.basename(self.path)
        self.schema: Dict[str, List[TosserSchemaColumn]] = {}

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
            # print(f'{Traverser.get_trail_string(trail)} = {value}')
        
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
        
        self._log.info(f'Loading schema from file: {self.filename}')
        with open(self.path, 'r') as f:
            data = json.load(f)
        
        self.schema = {
            table_name: [
                TosserSchemaColumn(
                    table_name=table_name,
                    column_name=column_name,
                    type_var=TosserSchemaTypeVar.from_string(type_string),
                    enum=enum,
                    max_length=max_length,
                )
                for column_name, (type_string, enum, max_length) in columns.items()
            ]
            for table_name, columns in data.items()
        }


    def write_file(self, work_dir: Path) -> None:
        """Write schema to file"""

        filepath = work_dir / self.filename
        self._log.info(f'Writing schema to file: {filepath}')
        with open(filepath, 'w') as f:
            f.write(self._render())


    def _render(self) -> str:
        data = {
            table_name: columns
            for table_name, columns in self.schema.items()
        }
        return json.dumps(data, indent=4)


    @staticmethod
    def default_file_string() -> str:
        return f'{SCHEMA_DEFAULT_FILE_NAME}.{SCHEMA_FILE_EXT}'
