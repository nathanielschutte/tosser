import json

from tosser.endpoint.target import ITarget, TargetDriver
from tosser.endpoint.endpoint import EndpointType

class DetailTarget(ITarget):
    def __init__(self, path: str) -> None:
        super().__init__(json.dumps('{}'))

        self.endpoint_type = EndpointType.TARGET
        self.driver = TargetDriver.DETAIL
