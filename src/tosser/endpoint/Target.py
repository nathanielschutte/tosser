from enum import Enum

from tosser.endpoint.endpoint import IEndpoint, EndpointType

class TargetDriver(Enum):
    DETAIL = 'detail'
    MYSQL = 'mysql'

class ITarget(IEndpoint):
    def __init__(self, config: str) -> None:
        super().__init__(config)

        self.endpoint_type = EndpointType.TARGET
    
