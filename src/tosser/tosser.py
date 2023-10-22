import os
from typing import Optional, Union, List
from pathlib import Path
import logging
from dotenv import load_dotenv
import asyncio

from tosser.logs import LOG_MAIN, LOG_DEBUG
from tosser.exceptions import TosserException
import tosser.endpoint.source as endpoint_source
import tosser.endpoint.target as endpoint_target 
from tosser.schema import TosserSchema
from tosser.object import TosserObject


class Tosser:
    """Context object for tosser operations"""

    def __init__(self, work_dir: Optional[Union[str, Path]] = None) -> None:
        load_dotenv()
        
        self._log = logging.getLogger(LOG_MAIN)
        self._debug = logging.getLogger(LOG_DEBUG)
        
        self.is_setup = False

        # Keeping the async loop in the main thread within context object
        # Going to spawn thread pool to handle async compute tasks
        self.loop = asyncio.get_event_loop()

        # Workspace setup
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
        
        self._set_work_dir_in_use()
        

    def generate(self) -> None:
        self.require_source('generate schema')

        objs = self.loop.run_until_complete(self.source.collect_objects())
        print(objs)

        schema = TosserSchema()
        schema.write_file(self.work_dir)
        

    def set_source(self, endpoint: Union[endpoint_source.ISource, str]) -> None:
        """Sets the tosser context source endpoint"""

        if isinstance(endpoint, endpoint_source.ISource):
            self.source = endpoint
            return

        temp_source = endpoint_source.ISource(endpoint)
        driver = temp_source.get_endpoint_driver()
        if driver is None:
            # self._log.error('No driver value found for source config')
            raise TosserException('No driver value found for source config')
        if driver not in endpoint_source.SOURCE_DRIVERS.keys():
            raise TosserException(f'Driver not found for source: {driver}')
        driver_class = endpoint_source.SOURCE_DRIVERS[driver]
        self._debug.debug(f'Source driver: {driver} [{driver_class}]')
        self.source = driver_class(endpoint)


    def set_target(self, endpoint: Union[endpoint_target.ITarget, str]) -> None:
        """Sets the tosser context target endpoint"""

        if isinstance(endpoint, endpoint_target.ITarget):
            self.target = endpoint
            return

        temp_target = endpoint_target.ITarget(endpoint)
        driver = temp_target.get_endpoint_driver()
        if driver is None:
            raise TosserException('No driver value found for target config')
        if driver not in endpoint_target.TARGET_DRIVERS.keys():
            raise TosserException(f'Driver not found for target: {driver}')
        driver_class = endpoint_target.TARGET_DRIVERS[driver]
        self._debug.debug(f'Target driver: {driver} [{driver_class}]')
        self.target = driver_class(endpoint)


    def require_source(self, reason: Optional[str] = None) -> None:
        if self.source is None:
            raise TosserException(f'Source endpoint required, reason: {reason}')
        
    
    def require_target(self, reason: Optional[str] = None) -> None:
        if self.target is None:
            raise TosserException(f'Target endpoint required, reason: {reason}')


    def set_work_dir(self, path: Union[str, Path]) -> None:
        """Sets the tosser context working directory"""

        if self.is_setup and os.path.isdir(self.work_dir) and not self._work_dir_in_use():
            os.rmdir(self.work_dir / '.tosser')
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
        return os.path.isfile(self.work_dir / '.tosser')


    def _set_work_dir_in_use(self) -> None:
        if not os.path.isfile(self.work_dir / '.tosser'):
            with open(self.work_dir / '.tosser', 'w') as f:
                f.write('')
