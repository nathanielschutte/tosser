import os
import json
from typing import Dict, Any, List, Optional, Tuple, Set
from pathlib import Path
import logging
import dataclasses

from tosser.logs import LOG_MAIN
from tosser.exceptions import TosserSchemaException
from tosser.object import TosserObject
from tosser.traverse import Traverser, TrailToken, TrailTokenType
from tosser.schema_types import TosserSchemaTypeVar, infer_type, ENUM_ELIGIBLE
from tosser.types import TossPathT
from tosser.util import resolve_path_ref
from tosser.map import TosserMap

SCHEMA_FILE_EXT = 'toss'
SCHEMA_DEFAULT_FILE_NAME = 'schema'
SCHEMA_NONAME_KEY = '@value'

# TODO move to config
# schema generation
SCHEMA_PREPEND_ROOT = False
SCHEMA_PREPEND_PARENT = True
# type inference
SCHEMA_ENUM_AS_HINT = True # only show enum as hint, not explicit type
SCHEMA_ENUM_MAX = 4
SCHEMA_VARLEN_AS_HINT = True # only constrain length as a hint, not explicit type
SCHEMA_VARLEN_PAD = 10 # add padding to contrained length


@dataclasses.dataclass()
class TosserSchemaColumn:
    table_name: str
    column_name: str
    type_var: TosserSchemaTypeVar
    hint_type_var: Optional[TosserSchemaTypeVar] = None
    enum: Optional[Set[Any]] = None
    max_length: Optional[int] = None

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, TosserSchemaColumn):
            return False
        return __value.table_name == self.table_name \
            and __value.column_name == self.column_name


@dataclasses.dataclass()
class TosserSchemaTable:
    table_name: str
    parent: Optional['TosserSchemaTable'] = None

    # probably getting rid of this
    # table_trail: Optional[List[TrailToken]] = None

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, TosserSchemaTable):
            return False
        return __value.table_name == self.table_name

    def __hash__(self) -> int:
        return hash(self.table_name)


class TosserSchema:
    """Tosser schema data structure"""

    DATA_KEY = 'data'
    METADATA_KEY = '__TOSSER_metadata__'
    VERSION = 1
    
    def __init__(
            self,
            map: TosserMap,
            path: Optional[TossPathT] = None
        ) -> None:
        self._log = logging.getLogger(LOG_MAIN)

        # config and metadata
        self.map = map
        self.complete = True

        # file
        self.filename = TosserSchema.default_file_string()
        self.path = Path(self.filename)
        if path is not None:
            self.path = resolve_path_ref(path, check=False)
            self.filename = os.path.basename(self.path)

        # schema data
        self.schema: Dict[TosserSchemaTable, List[TosserSchemaColumn]] = {}

        # schema generation internal
        self._generating = False
        self._gen_n = 0

        # store an instantiated root table object to avoid repeat instantiation
        self.root_table = TosserSchemaTable(
            table_name=self.map.m_root_table,
            # table_trail=[],
            parent=None
        )

    
    # def nearest_parent_table(self, trail: List[TrailToken]) -> TosserSchemaTable:
    #     ...


    def has_table(self, table: TosserSchemaTable) -> bool:
        return any(t == table for t in self.schema.keys())
    
    def has_column_name(self, table: TosserSchemaTable, column_name: str) -> bool:
        return any(c.column_name == column_name for c in self.schema[table])
    
    def get_column(self, table: TosserSchemaTable, column_name: str) -> TosserSchemaColumn:
        return next(c for c in self.schema[table] if c.column_name == column_name)

    def begin(self) -> None:
        """Begin a new schema generation"""
        
        self.complete = False
        self._generating = True
        self._gen_n = 0 # counting contributions
        self.schema = {}

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

            # determine table and column data
            # if table name does not exist, create it
            # if table depends on other tables, create those tables
            # if column name does not exist, create it
            next_table, next_column_name, table_deps = self.get_column_attributes(trail)

            print('attrs:', next_table, next_column_name, table_deps)

            # create tables if not exists in order of dependency
            # next table -> parent table -> parent's parent table -> ...
            table_create_queue = [next_table] + table_deps
            
            for table_idx, table in enumerate(reversed(table_create_queue)):
                if self.has_table(table):
                    continue

                parent_table = None
                if table_idx > 0:
                    # parent table is the table before this one in the queue
                    parent_table = table_create_queue[table_idx + 1]

                assert parent_table is None or self.has_table(parent_table)
                assert table.parent is None or table.parent == parent_table

                # note: don't think creating a duplicate table is necessary
                # table_key = dataclasses.replace(
                #     table,
                #     parent=parent_table
                # )

                self.schema[table] = []

            # new column initializations
            if not self.has_column_name(next_table, next_column_name):
                
                # infer initial
                initial_type = infer_type(value)
                
                new_column = TosserSchemaColumn(
                    table_name=next_table.table_name,
                    column_name=next_column_name,
                    type_var=initial_type,
                )

                # if initial type is enum eligible, add value to initial enum tester
                if initial_type.type in ENUM_ELIGIBLE:
                    new_column.enum = {value}

                self.schema[next_table].append(new_column)
            else:
                existing_column = self.get_column(next_table, next_column_name)
                existing_column.type_var = infer_type(value, inference=existing_column.type_var)

            print()
        
        file_id_str = ''
        if (
            obj.metadata is not None 
            and '__TOSSER_filename_key' in obj.metadata 
            and obj.metadata['__TOSSER_filename_key'] in obj.metadata
        ):
            file_id_str = f' from file {obj.metadata[obj.metadata["__TOSSER_filename_key"]]}'

        self._log.debug(f'Contributed object {self._gen_n}{file_id_str} to new schema')
        self._gen_n += 1


    def get_column_attributes(self, trail: List[TrailToken]) \
        -> Tuple[TosserSchemaTable, str, List[TosserSchemaTable]]:
        """
        Determine column attiributes from a given traversal trail.
        Includes table data object, column name, and table dependencies.

        This data is independent of the schema data structure and type inference.
        """

        root_table = self.map.m_root_table
        delim = self.map.m_table_delimeter
        SCHEMA_PREPEND_ROOT = False
        
        offset = 0
        if trail[0].val == '$':
            offset = 1
        real_trail: List[TrailToken] = trail[offset:]

        if len(real_trail) == 0:
            raise TosserSchemaException('Cannot get column attributes for empty trail')
        

        # base cases ---------------------------------------------------------
        # no trail, value directly in base table
        if len(real_trail) == 1:
            # asserting that top level data is an object
            # top level arrays are handled at an earlier stage
            assert isinstance(real_trail[0].val, str)
            return self.root_table, real_trail[0].val, []

        # putting together table and column name strings
        table_parts: List[str] = [root_table]


        # get value field name ------------------------------------------------
        value_part = real_trail[-1]

        # special case for values directly in an array
        if value_part.type == TrailTokenType.INDEX:
            value_field = SCHEMA_NONAME_KEY
        else:
            assert isinstance(value_part.val, str)
            value_field = value_part.val
        
        column_parts: List[str] = [value_field] # TODO handle 
        

        # iterate over base trail to determine attributes ---------------------
        # want:
        #  - table data
        #  - column name
        #  - table deps

        table_deps: List[TosserSchemaTable] = []
        trail_skip = 0
        trail_end = False
        follow_array = False
        traverse_trail = list(reversed(real_trail[:-1] if value_part.type == TrailTokenType.KEY else real_trail))
        # print('traverse trail:', traverse_trail)
        for trail_idx, trail_part in enumerate(traverse_trail):
            if trail_skip > 0:
                trail_skip -= 1
                continue

            next_table_parts = []
            next_column_parts = []
            is_last_token = trail_idx == len(traverse_trail) - 1

            # this is going to help look ahead for array relationship table names
            def _get_next_part(n=1) -> Optional[TrailToken]:
                if trail_idx >= len(traverse_trail) - n:
                    return None
                _part: TrailToken = traverse_trail[trail_idx + n]
                return _part

            if trail_part.type == TrailTokenType.KEY:
                if self.map.m_flatten_objects:
                    # table name does not change
                    # if we're just following an array relationship to prepend table names, skip
                    if not follow_array:
                        next_column_parts.append(trail_part.val)
                else:
                    next_table_parts.append(trail_part.val)
                    # column name does not change

                    # TODO: add this table to the table deps list

            # handle the array relationship. once table name and parent is known, stop
            elif trail_part.type == TrailTokenType.INDEX:
                seek_part = _get_next_part()
                if seek_part is None:
                    raise TosserSchemaException('root level array not supported')
                list_deps = [seek_part]
                while seek_part is not None and seek_part.type == TrailTokenType.INDEX:
                    trail_skip += 1
                    seek_part = _get_next_part(n=(trail_skip + 1))
                    if seek_part is not None:
                        list_deps.append(seek_part)
                
                print('list deps:', list_deps)
                for list_dep in list_deps:
                    next_table_parts.append(list_dep.val)

                follow_array = True
                if not SCHEMA_PREPEND_PARENT:
                    trail_end = True

            if len(next_table_parts) > 0:
                if len(table_parts) == 1 and table_parts[0] == root_table and not SCHEMA_PREPEND_ROOT:
                    table_parts = []
                for next_table_part in next_table_parts:
                    assert isinstance(next_table_part, str)
                    table_parts.insert(0, next_table_part)

            if len(next_column_parts) > 0:
                for next_column_part in next_column_parts:
                    assert isinstance(next_column_part, str)
                    column_parts.insert(0, next_column_part)

            if trail_end:
                break

        
        # finalize ------------------------------------------------------------
        # remove root table name if it should not be always prepended to flattened objects
        if len(table_parts) > 1 and table_parts[0] == root_table and not SCHEMA_PREPEND_ROOT:
            table_parts = table_parts[1:]

        table_name = delim.join(table_parts)
        column_name = delim.join(column_parts)
        
        return (
            TosserSchemaTable(
                table_name=table_name,
                # table_trail=real_trail[:-1]
            ),
            column_name,
            table_deps
        )
        

    def end(self) -> None:
        """End new schema generation"""

        if self.complete or not self._generating:
            raise TosserSchemaException('Cannot end an already complete TosserSchema')
        
        # close out all enum hints

        # finalize length hints

        self.complete = True
        self._generating = False

        self._log.info(f'Ending new schema generation: contributed {self._gen_n} objects')


    def load_file(self) -> None:
        """Load schema from file"""
        
        self._log.info(f'Loading schema from file: {self.filename}')
        with open(self.path, 'r') as f:
            data = json.load(f)

        version = None
        if TosserSchema.METADATA_KEY in data:
            metadata = data[TosserSchema.METADATA_KEY]
            version = metadata['version']
        self._log.debug(f'Loaded schema version: {version}')
        
        self.schema = {
            table_name: [
                TosserSchemaColumn(
                    table_name=table_name,
                    column_name=column_name,
                    type_var=TosserSchemaTypeVar.from_string(column_data['type']),
                    hint_type_var=TosserSchemaTypeVar.from_string(column_data['hint']) if column_data['hint'] is not None else None,
                    enum=column_data['enum'],
                    max_length=column_data['max_length'],
                )
                for column_name, column_data in columns.items()
            ]
            for table_name, columns in data[TosserSchema.DATA_KEY].items()
        }


    def write_file(self, work_dir: Path) -> None:
        """Write schema to file"""

        filepath = work_dir / self.filename
        self._log.info(f'Writing schema to file: {filepath}')
        with open(filepath, 'w') as f:
            f.write(self._render())


    def _render(self) -> str:
        data: Dict[str, Any] = {
            TosserSchema.DATA_KEY: {
                table.table_name: {
                    column.column_name: {
                        'type': str(column.type_var),
                        'hint': str(column.hint_type_var) if column.hint_type_var is not None else None,
                        'enum': column.enum,
                        'max_length': column.max_length,
                    }
                    for column in columns
                }
                for table, columns in self.schema.items()
            }
        }

        data[TosserSchema.METADATA_KEY] = {
            'version': 1
        }

        try:
            return json.dumps(data, indent=4)
        except TypeError:
            self._log.error('Failed to render schema to JSON')
            return '{}'
        

    @staticmethod
    def default_file_string() -> str:
        return f'{SCHEMA_DEFAULT_FILE_NAME}.{SCHEMA_FILE_EXT}'
