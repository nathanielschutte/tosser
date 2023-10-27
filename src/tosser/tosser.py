import os
import json
from typing import Optional, Union, Dict, Any
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
            schema_file: TossPathT = None,
        ) -> None:
        load_dotenv()
        
        self._log = logging.getLogger(LOG_MAIN)
        self._debug = logging.getLogger(LOG_DEBUG)
        
        self.is_setup = False

        # Keeping the async loop in the main thread within context object
        # Going to spawn thread pool to handle async compute tasks
        self.loop = asyncio.get_event_loop()

        # Context
        self.schema_file: Path
        self.map_file: Path
        self.config_file: Path
        self.schema: Optional[TosserSchema] = None
        self.map: Optional[TosserMap] = None
        self.config: Optional[Dict[str, Any]] = None

        # Workspace setup
        self._work_dir: Path = Path('.')

        self.is_setup = self.setup(
            work_dir=work_dir,
            schema_file=schema_file,
            map_file=map_file,
            config_file=config_file,
        )
        if not self.is_setup:
            raise TosserException('Failed to set up Tosser')
        
        self._set_work_dir_in_use()

    
    # DECORATORS
    def _with_schema(func: Any) -> Any:
        def wrapper(*args):
            self = args[0]
            self.reload_schema()
            return func(*args)
        return wrapper


    # API
    @_with_schema
    def ingest(self):
        """Ingest objects"""

        print()
        

    def generate(self) -> None:
        """Generate schema using source objects"""

        self.require_source('generate schema')

        if self.schema is None:
            assert self.map is not None
            schema = TosserSchema(path=self.schema_file, map=self.map)
        else:
            schema = self.schema

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


    def reload_schema(self) -> None:
        """Recreates the TosserSchema object using the configured schema_file"""

        if not self.schema_file:
            raise TosserException('Cannot reload schema before setting schema file')
        assert self.map is not None
        self.schema = TosserSchema(path=self.schema_file, map=self.map)
        self.schema.load_file()


    def reload_map(self) -> None:
        """Recreates the TosserMap object using the configured map_file"""

        if not self.map_file:
            raise TosserException('Cannot reload map before setting map file')
        ext = ConfigExtender(self.map_file, json.load)
        self.map = TosserMap.from_dict(ext.render())

        
    def reload_config(self) -> None:
        """Recreates the base config dictionary using the configured config_file"""

        if not self.config_file:
            raise TosserException('Cannot reload config before setting config file')
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)


    def setup(
            self, 
            work_dir: TossPathT = None,
            schema_file: TossPathT = None,
            map_file: TossPathT = None,
            config_file: TossPathT = None,
        ) -> bool:
        """Called on Tosser object instantiation, sets up filesystem"""

        # Working directory
        self.set_work_dir(resolve_config('TOSS_WORKDIR', work_dir, '.'))
        self._log.debug(f'Using working directory: {self._work_dir}')

        # TODO make routine for path checks that should be in the workdir

        # Map config
        map_file = resolve_config('TOSS_SCHEMA_MAP', map_file, 'map.tosser.json')
        try_map_file = resolve_path_ref(map_file, check=False)
        if not try_map_file.is_absolute():
            self.map_file = self._work_dir / try_map_file
        else:
            self.map_file = try_map_file
        if self.map_file.exists():
            self._log.debug(f'Using map file: {self.map_file}')
            self.reload_map()
        else:
            self._log.error(f'Map file not found: {map_file}')
            return False
        
        # Schema config
        schema_file = resolve_config('TOSS_SCHEMA_FILE', schema_file, TosserSchema.default_file_string())
        try_schema_file = resolve_path_ref(schema_file, check=False)
        if not try_schema_file.is_absolute():
            self.schema_file = self._work_dir / try_schema_file
        else:
            self.schema_file = try_schema_file
        if self.schema_file.exists():
            self._log.debug(f'Using schema file: {self.schema_file}')
            self.reload_schema()
        else:
            self._log.debug('No existing schema file')

        # Ingest config
        config_file = resolve_config('TOSS_CONFIG_FILE', config_file, 'config.tosser.json')
        try_config_file = resolve_path_ref(config_file, check=False)
        if not try_config_file.is_absolute():
            self.config_file = self._work_dir / try_config_file
        else:
            self.config_file = try_config_file
        if self.config_file.exists():
            self._log.debug(f'Using config file: {self.config_file}')
        else:
            self._log.error(f'Config file not found: {config_file}')
            return False

        if not os.path.isdir(self._work_dir):
            try:
                os.mkdir(self._work_dir)
            except OSError as e:
                self._log.error(f'Failed to create working directory \'{self._work_dir}\': {e}')
                return False
        
        return True
    

    # INTERNAL
    def _work_dir_in_use(self) -> bool:
        return os.path.isfile(self._work_dir / '.tosser')


    def _set_work_dir_in_use(self) -> None:
        if not os.path.isfile(self._work_dir / '.tosser'):
            with open(self._work_dir / '.tosser', 'w') as f:
                f.write('')
