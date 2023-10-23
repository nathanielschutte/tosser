import glob
import os
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, Callable, List, IO
import logging

from tosser.logs import LOG_MAIN
from tosser.types import TossPathT
from tosser.util import *

class ConfigExtender:
    """Builds a complete dict object from a config file with glob extensions"""

    def __init__(
            self,
            path: TossPathT,
            loader: Callable[[IO[Any]], Dict[str, Any]],
            include_keyword: Optional[str] = '@include',
        ) -> None:
        self._log = logging.getLogger(LOG_MAIN)

        self.path = resolve_path_ref(path)
        self.loader = loader
        self.include_keyword = include_keyword

    def _read(self, path: Path) -> Dict[str, Any]:
        with open(path, 'r') as f:
            return self.loader(f)
        
    def render(self) -> Dict[str, Any]:
        """Recursively loads included files and combines them into a single dict"""

        def _traverse(obj: Any, trail: List[str]) -> Optional[List[Tuple[List[str], List[str]]]]:
            # print(obj, trail)
            result = []
            if len(trail) > 0 and trail[-1] == self.include_keyword:
                if isinstance(obj, str):
                    result = [(trail, [obj])]
                elif isinstance(obj, list):
                    result = [(trail, obj)]
            if isinstance(obj, dict):
                for k, v in obj.items():
                    next_trail = trail.copy()
                    next_trail.append(k)
                    next_result = _traverse(v, next_trail)
                    if next_result is not None:
                        result.extend(next_result)
            return result


        def _include(path: Path) -> Dict[str, Any]:
            next_data = self._read(path)
            seek_keywords = _traverse(next_data, [])
            
            if seek_keywords is None or len(seek_keywords) == 0:
                return next_data
            
            print(f'{os.path.basename(path)}: found keywords: {seek_keywords}')

            for seek_path, seek_globs in seek_keywords:
                if len(seek_globs) < 1:
                    continue
                
                obj_ref = next_data
                while seek_path[0] != self.include_keyword:
                    obj_ref = obj_ref[seek_path.pop(0)]
                
                for seek_glob in seek_globs:
                    seek_glob = os.path.join(path.parent, seek_glob)
                    seek_files = glob.glob(seek_glob)

                    if len(seek_files) < 1:
                        self._log.warning(f'No files found for glob: {seek_glob}')
                        continue

                    for next_file in seek_files:
                        next_file_path = Path(next_file)
                        if not next_file_path.exists():
                            raise Exception(f'Include path not found: {next_file}')
                        include_data = _include(next_file_path)
                        
                        if self.include_keyword in obj_ref:
                            del obj_ref[self.include_keyword]

                        for include_key, include_val in include_data.items():
                            obj_ref[include_key] = include_val

            return next_data

        return _include(self.path)
