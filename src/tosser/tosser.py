import os
from typing import Optional, Union
from pathlib import Path
import logging
from dotenv import load_dotenv

from tosser.logs import LOG_MAIN, LOG_DEBUG
from tosser.exceptions import TosserException
import tosser.endpoint.source as endpoint_source
import tosser.endpoint.target as endpoint_target 
from tosser.schema import TosserSchema


class Tosser:
    """Context object for tosser operations"""

    def __init__(self, work_dir: Optional[Union[str, Path]] = None) -> None:
        load_dotenv()
        
        self._log = logging.getLogger(LOG_MAIN)
        self._debug = logging.getLogger(LOG_DEBUG)
        
        self.is_setup = False

        self.work_dir: Path = Path('.')
        env_work_dir = os.getenv('TOSS_WORKDIR')
        if env_work_dir is not None:
            self.set_work_dir(env_work_dir)
        if work_dir is not None:
            self.set_work_dir(work_dir)
        self._log.debug(f'Using working directory: {self.work_dir}')

        self.is_setup = self.setup()
        if not self.is_setup:
            raise TosserException('Failed to set up Tosser')
        

    def generate(self) -> None:
        schema = TosserSchema()
        schema.write_file(self.work_dir)
        

    def set_source(self, config: str) -> None:
        """Sets the tosser context source endpoint"""

        source = endpoint_source.ISource(config)
        driver = source.get_endpoint_driver()
        if driver is None:
            # self._log.error('No driver value found for source config')
            raise TosserException('No driver value found for source config')
        if driver not in endpoint_source.SOURCE_DRIVERS.keys():
            raise TosserException(f'Driver not found for source: {driver}')
        driver_class = endpoint_source.SOURCE_DRIVERS[driver]
        self._debug.debug(f'Source driver: {driver} [{driver_class}]')


    def set_target(self, config: str) -> None:
        """Sets the tosser context target endpoint"""

        target = endpoint_target.ITarget(config)
        driver = target.get_endpoint_driver()
        if driver is None:
            raise TosserException('No driver value found for target config')
        if driver not in endpoint_target.TARGET_DRIVERS.keys():
            raise TosserException(f'Driver not found for target: {driver}')
        driver_class = endpoint_target.TARGET_DRIVERS[driver]
        self._debug.debug(f'Target driver: {driver} [{driver_class}]')


    def set_work_dir(self, path: Union[str, Path]) -> None:
        """Sets the tosser context working directory"""

        if self.is_setup and os.path.isdir(self.work_dir) and not self._work_dir_in_use():
            os.rmdir(self.work_dir / '._tosser')
        if isinstance(path, str):
            path = Path(path)
        self.work_dir = path


    def setup(self) -> bool:
        """Called on tosser object instantiation, sets up filesystem"""
        
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
