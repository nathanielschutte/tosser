from enum import Enum
from typing import Dict, Union, Any, AsyncGenerator

from tosser.endpoint.endpoint import IEndpoint, EndpointType
from tosser.object import TosserObject

REQUIRED_FIELDS = set(['data', 'metadata'])

class SourceDriver(Enum):
    FILE = 'file'

class SourceEndpointException(Exception):
    ...

class ISource(IEndpoint):
    def __init__(self, config: Union[str, Dict[str, Any]]) -> None:
        super().__init__(config)

        self.endpoint_type = EndpointType.SOURCE

    def check_keys(self, parsed_keys):
        key_set = set(parsed_keys.keys())
        diff_set = REQUIRED_FIELDS - key_set
        if len(diff_set) > 0:
            # self._log.error(f'Object missing required fields: {diff_set}')
            raise SourceEndpointException(f'Object missing required fields: {diff_set}')

    async def iter_objects(self) -> AsyncGenerator[TosserObject, None]:
        yield TosserObject(data={}, metadata={})
