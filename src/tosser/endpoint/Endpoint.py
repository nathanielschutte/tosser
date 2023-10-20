from enum import Enum

class EndpointType(Enum):
    SOURCE = 'source'
    TARGET = 'target'

class Endpoint:
    def __init__(self) -> None:
        self.endpoint_type: EndpointType = EndpointType.SOURCE
    