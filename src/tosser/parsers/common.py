from typing import IO, Any, Iterable

from pathlib import Path

from tosser.parsers.Parser import Parser
from tosser.parsers.Parser import BaseObject


class FileParser(Parser):
    def __init__(self):
        super().__init__()

    def get_stream(self, path: Path) -> IO[Any]:
        return open(path, 'rU')

    def next_line(self):
        ...


class JsonParser(FileParser):
    def __init__(self):
        super().__init__()

    def next_line(self):
        return super().next_line()
