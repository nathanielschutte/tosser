from tosser.endpoint.source.source import ISource, SourceDriver
from tosser.endpoint.source.file import FileSource

SOURCE_DRIVERS = {
    'file': FileSource
}

__all__ = ['ISource', 'SourceDriver', 'FileSource' 'SOURCE_DRIVERS']
