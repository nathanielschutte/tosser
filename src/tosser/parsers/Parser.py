from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging

from pathlib import Path
from typing import IO, Callable, Dict, Iterable, Iterator, Optional, Union, Any


@dataclass
class BaseObject:
    data: dict
    complete: bool = False


class Parser(ABC):
    def __init__(self) -> None:
        self._log = logging.getLogger()
        self._has_stream = False

    @abstractmethod
    def get_stream(self, path: Path) -> IO[Any]:
        ...

    @abstractmethod
    def next_line(self, line, result):
        ...

    def get_objects(self, path: Path, object: type = BaseObject) -> Iterable[BaseObject]:
        stream = self.get_stream(path)
        result = object(data={})
        for line in stream:
            line = line.strip('\n')
            self.next_line(line, result)
            if result.complete:
                yield BaseObject(data=line)
