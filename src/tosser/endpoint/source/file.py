import os
import glob
from typing import AsyncGenerator, List, Dict, Union, Any
from pathlib import Path
import logging
import aiofiles
import json

from tosser.endpoint.source import ISource, SourceDriver
from tosser.object import TosserObject
from tosser.parsers.common import FileParser
from tosser.logs import LOG_ENDPOINT

class FileSource(ISource):
    def __init__(self, config: Union[str, Dict[str, Any]]) -> None:
        super().__init__(config)
        self._log = logging.getLogger(LOG_ENDPOINT)

        self.driver = SourceDriver.FILE
        self.parser: FileParser = FileParser()
        
        self.file_list: List[Path] = self._expand_file_list(self.config['path'])
        self._log.debug(f'Source files matched: {[str(f) for f in self.file_list]}')


    async def iter_objects(self) -> AsyncGenerator[TosserObject, None]:
        for file in self.file_list:
            async with aiofiles.open(file, 'r') as f:
                contents = await f.read()
            parsed = json.loads(contents)
            self.check_keys(parsed)
            yield TosserObject(data=parsed['data'], metadata=parsed['metadata'])


    def _expand_file_list(self, path: str) -> List[Path]:
        if os.path.isfile(path):
            return [Path(path)]
        try_glob: list[str] = glob.glob(path, recursive=True)
        path_glob = [Path(p) for p in try_glob]
        return path_glob
    