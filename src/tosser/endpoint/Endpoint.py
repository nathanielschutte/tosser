import os
import json
from enum import Enum
from typing import Union, Optional, Dict, Any
import logging

from tosser.parsers.common import FileParser
from tosser.logs import LOG_DEBUG

class EndpointType(Enum):
    SOURCE = 'source'
    TARGET = 'target'

class IEndpoint:
    def __init__(self, config: str) -> None:
        self._log = logging.getLogger(LOG_DEBUG)

        self.endpoint_type = EndpointType.SOURCE
        self.driver: Any
        self.config = self.resolve_config(config)
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, IEndpoint):
            return False
        if self.endpoint_type != __value.endpoint_type:
            return False
        if self.driver != __value.driver:
            return False
        this_keys = set(self.config.keys())
        value_keys = set(__value.config.keys())
        if len(this_keys) != len(value_keys):
            return False
        if len(this_keys - value_keys) != 0:
            return False
        for k in this_keys:
            if self.config[k] != __value.config[k]:
                return False
        return True

    def resolve_config(self, config: str) -> Dict[str, Any]:
        if os.path.isfile(config):
            with open(config, 'r') as f:
                content = f.read()
                try:
                    file_parsed: Dict[str, Any] = json.loads(content)
                    return file_parsed
                except json.JSONDecodeError as e:
                    self._log.error(f'Failed to parse JSON config file \'{config}\': {e}')
                    raise e
        
        try:
            config_parsed: Dict[str, Any] = json.loads(config)
            return config_parsed
        except json.JSONDecodeError as e:
            self._log.error(f'Failed to parse JSON config string: {e}')
            raise e
        
    def get_endpoint_type(self) -> EndpointType:
        if self.config.get('endpoint_type') == EndpointType.TARGET:
            return EndpointType.TARGET
        return EndpointType.SOURCE
    
    def get_endpoint_driver(self) -> Any:
        if self.config.get('driver') is None:
            return None
        return self.config.get('driver')
