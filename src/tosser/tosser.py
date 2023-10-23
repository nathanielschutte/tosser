import os
import json
from typing import Optional, Union, Dict, Any, TypeAlias
from pathlib import Path
import logging
from dotenv import load_dotenv
import asyncio

from tosser.logs import LOG_MAIN, LOG_DEBUG
from tosser.exceptions import TosserException
import tosser.endpoint.source as endpoint_source
import tosser.endpoint.target as endpoint_target 
from tosser.schema import TosserSchema
from tosser.map import TosserMap
from tosser.types import TossPathT
from tosser.util import *
from tosser.configd import ConfigExtender

class Tosser:
    """Context object for tosser operations"""

    def __init__(
            self, 
            work_dir: TossPathT = None,
            map_file: TossPathT = None,
            config_file: TossPathT = None,
        ) -> None:
        load_dotenv()
        
        self._log = logging.getLogger(LOG_MAIN)
        self._debug = logging.getLogger(LOG_DEBUG)
        
        self.is_setup = False

        # Keeping the async loop in the main thread within context object
        # Going to spawn thread pool to handle async compute tasks
        self.loop = asyncio.get_event_loop()

        # Context
        self.map_file: Path
        self.config_file: Path
        self.map: Optional[TosserMap] = None
        self.config: Optional[Dict[str, Any]] = None

        # Workspace setup
        self._work_dir: Path = Path('.')

        self.is_setup = self.setup(
            work_dir=work_dir,
            map_file=map_file,
            config_file=config_file,
        )
        if not self.is_setup:
            raise TosserException('Failed to set up Tosser')
        
        self._set_work_dir_in_use()
        

    def generate(self) -> None:
        """Generate schema using source objects"""

        self.require_source('generate schema')

        schema = TosserSchema()
        schema.begin()

        async def _iter() -> None:
            async for obj in self.source.iter_objects():
                schema.contribute(obj)

        self.loop.run_until_complete(_iter())
        schema.end()
        schema.write_file(self._work_dir)
        

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
        """Called to indicate that a configured ISource endpoint is required"""

        if self.source is None:
            raise TosserException(f'Source endpoint required, reason: {reason}')
        
    
    def require_target(self, reason: Optional[str] = None) -> None:
        """Called to indicate that a configured ITarget endpoint is required"""

        if self.target is None:
            raise TosserException(f'Target endpoint required, reason: {reason}')


    def set_work_dir(self, path: Union[str, Path]) -> None:
        """Sets the tosser context working directory"""

        if self.is_setup and os.path.isdir(self._work_dir) and not self._work_dir_in_use():
            os.rmdir(self._work_dir / '.tosser')
        path = resolve_path_ref(path)
        self._work_dir = path


    def reload_map(self) -> None:
        if not self.map_file:
            raise TosserException('Cannot reload map before setting map file')
        ext = ConfigExtender(self.map_file, json.load)
        self.map = TosserMap.from_dict(ext.render())

        
    def reload_config(self) -> None:
        if not self.config_file:
            raise TosserException('Cannot reload config before setting config file')
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)


    def setup(
            self, 
            work_dir: TossPathT = None,
            map_file: TossPathT = None,
            config_file: TossPathT = None,
        ) -> bool:
        """Called on tosser object instantiation, sets up filesystem"""

        # Working directory
        self.set_work_dir(resolve_config('TOSS_WORKDIR', work_dir, '.'))
        self._log.debug(f'Using working directory: {self._work_dir}')

        # Map config
        map_file = resolve_config('TOSS_SCHEMA_MAP', map_file, TosserSchema.default_file_string())
        self.map_file = resolve_path_ref(map_file)
        self.reload_map()

        # Ingest config
        config_file = resolve_config('TOSS_CONFIG_FILE', config_file, 'config.json')
        self.config_file = resolve_path_ref(config_file)

        if not os.path.isdir(self._work_dir):
            try:
                os.mkdir(self._work_dir)
            except OSError as e:
                self._log.error(f'Failed to create working directory \'{self._work_dir}\': {e}')
                return False
        
        return True
    

    def _work_dir_in_use(self) -> bool:
        return os.path.isfile(self._work_dir / '.tosser')


    def _set_work_dir_in_use(self) -> None:
        if not os.path.isfile(self._work_dir / '.tosser'):
            with open(self._work_dir / '.tosser', 'w') as f:
                f.write('')
