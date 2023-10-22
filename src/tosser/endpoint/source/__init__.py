from typing import Dict, Type

from tosser.endpoint.source.source import ISource, SourceDriver, REQUIRED_FIELDS
from tosser.endpoint.source.file import FileSource

SOURCE_DRIVERS: Dict[str, Type[ISource]] = {
    'file': FileSource
}

__all__ = ['ISource', 'SourceDriver', 'FileSource' 'SOURCE_DRIVERS', 'REQUIRED_FIELDS']
