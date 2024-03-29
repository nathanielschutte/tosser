from enum import Enum
from typing import Dict, Union, Any, AsyncGenerator, List

from tosser.endpoint.endpoint import IEndpoint, EndpointType
from tosser.object import TosserObject

REQUIRED_FIELDS = set(['data', 'metadata'])


class SourceDriver(Enum):
    FILE = 'file'


class SourceEndpointException(Exception):
    ...


class ISource(IEndpoint):
    """Source endpoint interface for incoming objects"""

    def __init__(self, config: Union[str, Dict[str, Any]]) -> None:
        super().__init__(config)

        self.endpoint_type = EndpointType.SOURCE

    def check_keys(self, parsed_keys):
        key_set = set(parsed_keys.keys())
        diff_set = REQUIRED_FIELDS - key_set
        if len(diff_set) > 0:
            # self._log.error(f'Object missing required fields: {diff_set}')
            raise SourceEndpointException(f'Object missing required fields: {diff_set}')
        
    async def collect_objects(self) -> List[TosserObject]:
        """Collect objects from the async generator into a list"""

        objs = []
        async for obj in self.iter_objects():
            objs.append(obj)
        return objs

    async def iter_objects(self) -> AsyncGenerator[TosserObject, None]:
        """Yield objects generated by the source"""

        yield TosserObject(data={}, metadata={})
