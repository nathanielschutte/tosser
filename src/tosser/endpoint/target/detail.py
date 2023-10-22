import json

from tosser.endpoint.target import ITarget, TargetDriver

class DetailTarget(ITarget):
    def __init__(self, path: str) -> None:
        super().__init__(json.dumps('{}'))

        self.driver = TargetDriver.DETAIL
