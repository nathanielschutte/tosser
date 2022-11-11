
from pathlib import Path
from typing import Callable, Dict, Iterable, Iterator, Union, Any

class BaseObject:
    def __init__(self) -> None:
        self.json = ''

class BaseParser:
    def __init__(self) -> None:
        self.stream = None
        self.callback = None

        self.object_num = -1
        self.last_one = False

    def _get_stream(self, path: Path) -> None:
        with open(path, mode='r') as f:
            self.stream = f

    def _next_line(self, line: str) -> Union[dict, Exception]:
        return { 'data': line }

    def get_objects(self, path: Path, func: Callable) -> Iterator[dict]:
        self._get_stream(path)
        return self.__iter__()

    def __iter__(self) -> Any:
        if self.stream is None or self.callback is None:
            raise StopIteration

        self.object_num = 0
        return self

    def __next__(self) -> Union[Dict, StopIteration]:
        if self.stream is None or self.callback is None:
            raise StopIteration

        if self.last_one:
            raise StopIteration
        
        self.object_num += 1
        acc = { 'complete': False, 'object_num': self.object_num }
        while True:
            try:
                nextline = self.stream.readline()
                if nextline is None:
                    self.last_one = True
                    break
                res = self._next_line(nextline)
                if isinstance(res, str):
                    res = { 'data': res }
                assert isinstance(res, dict)
                acc.update(res)
            except StopParsing:
                acc['complete'] = True
                break

        return acc


class StopParsing(Exception):
    ...
        
