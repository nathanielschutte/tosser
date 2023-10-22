from enum import Enum

from tosser.endpoint.endpoint import IEndpoint, EndpointType

class SourceDriver(Enum):
    FILE = 'file'

class ISource(IEndpoint):
    def __init__(self, config: str) -> None:
        super().__init__(config)

        self.endpoint_type = EndpointType.SOURCE
