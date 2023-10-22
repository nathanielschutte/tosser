import os
import json
import glob
from typing import List
from pathlib import Path

from tosser.endpoint.endpoint import EndpointType
from tosser.endpoint.source import ISource, SourceDriver
from tosser.parsers.common import FileParser

class FileSource(ISource):
    def __init__(self, path: str) -> None:
        super().__init__(json.dumps({
            'path': path
        }))
        assert self.config.get('path') == path

        self.driver = SourceDriver.FILE
        self.parser: FileParser = FileParser()
        
        self.file_list: List[Path] = []
        self.expand_file_list(self.config['path'])

    def expand_file_list(self, path: str) -> List[Path]:
        if os.path.isfile(path):
            return [Path(path)]
        try_glob: list[str] = glob.glob(path, recursive=True)
        path_glob = [Path(p) for p in try_glob]
        return path_glob
    