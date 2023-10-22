import json
import sqlalchemy
import databases

from tosser.endpoint.target import ITarget, TargetDriver

class SqlTarget(ITarget):
    def __init__(self, path: str) -> None:
        super().__init__(json.dumps('{}'))

        self.driver = TargetDriver.SQL
