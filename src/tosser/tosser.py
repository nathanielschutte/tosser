import os
from typing import Optional, Union
from pathlib import Path
import logging

from tosser.logs import LOG_MAIN
from tosser.exceptions import TosserException
from tosser.endpoint.source import ISource
from tosser.endpoint.target import ITarget

class Tosser:
    def __init__(self, work_dir: Optional[Union[str, Path]] = None) -> None:
        self._log = logging.getLogger(LOG_MAIN)
        
        self.is_setup = False

        self.work_dir: Path = Path('.')
        if work_dir is not None:
            self.set_work_dir(work_dir)

        self.is_setup = self.setup()
        if not self.is_setup:
            raise TosserException('Failed to set up Tosser')
        
    def set_source(self, str) -> None:
        ...

    def set_work_dir(self, path: Union[str, Path]) -> None:
        if self.is_setup and os.path.isdir(self.work_dir) and not self._work_dir_in_use():
            os.rmdir(self.work_dir / '._tosser')
        if isinstance(path, str):
            path = Path(path)
        self.work_dir = path

    def setup(self) -> bool:
        if not os.path.isdir(self.work_dir):
            try:
                os.mkdir(self.work_dir)
            except OSError as e:
                self._log.error(f'Failed to create working directory \'{self.work_dir}\': {e}')
                return False
        
        return True
    
    def _work_dir_in_use(self) -> bool:
        return os.path.isfile(self.work_dir / '._tosser')

    def _set_work_dir_in_use(self) -> None:
        if not os.path.isfile(self.work_dir / '._tosser'):
            with open(self.work_dir / '._tosser', 'w') as f:
                f.write('')
