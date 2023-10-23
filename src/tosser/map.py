import os
import json
from typing import Dict, Any, List, Optional
import dataclasses

from tosser.schema_types import TosserSchemaType, TosserSchemaTypeVar
from tosser.util import get_field

METACHAR = '@'

@dataclasses.dataclass
class MapColumn:
    m_name: str
    m_type: TosserSchemaTypeVar

    @staticmethod
    def from_dict(obj: Dict[str, Any]) -> 'MapColumn':
        return MapColumn(
            m_name=get_field(obj, 'name'),
            m_type=get_field(obj, 'type'),
        )


@dataclasses.dataclass
class MapTable:
    m_key: str
    m_source: List[str]
    m_cols: Dict[str, MapColumn]

    @staticmethod
    def from_dict(obj: Dict[str, Any]) -> 'MapTable':
        column_obj = get_field(obj, 'columns')
        m_cols = {
            k: MapColumn.from_dict(v)
            for k, v in column_obj.items()
        } if column_obj is not None else {}
        return MapTable(
            m_key=get_field(obj, 'key'),
            m_source=get_field(obj, 'source'),
            m_cols=m_cols,
        )


@dataclasses.dataclass
class TosserMap:
    m_schema: str
    m_root_table: str
    m_key_templ: str
    m_tables: Dict[str, MapTable]

    @staticmethod
    def from_dict(obj: Dict[str, Any]) -> 'TosserMap':
        table_obj = get_field(obj, 'tables')
        m_tables = {
            k: MapTable.from_dict(v)
            for k, v in table_obj.items()
        }
        return TosserMap(
            m_schema=get_field(obj, 'schema', ['defaults']),
            m_root_table=get_field(obj, 'roottable', ['defaults']),
            m_key_templ=get_field(obj, 'key', ['defaults'], default=r'{table}_id'),
            m_tables=m_tables
        )
