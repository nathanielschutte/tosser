from enum import Enum
from typing import Dict, Union, Any

from tosser.endpoint.endpoint import IEndpoint, EndpointType

class TargetDriver(Enum):
    DETAIL = 'detail'
    MYSQL = 'mysql'

class TargetCall(Enum):
    SETUP = 'setup'
    INSERT = 'insert'

class TargetCallDynamic(Enum):
    CREATE_TABLE = 'create_table'
    ADD_COLUMN = 'add_column'
    ALTER_COLUMN = 'alter_column'

TARGET_CALLS = {t.name: t.value for t in TargetCall}
TARGET_CALLS.update({t.name: t.value for t in TargetCallDynamic})

class ITarget(IEndpoint):
    def __init__(self, config: Union[str, Dict[str, Any]]) -> None:
        super().__init__(config)

        self.endpoint_type = EndpointType.TARGET
    
    def setup(self) -> None:
        ...
        

    def create_table(self) -> None:
        ...

    def insert(self) -> None:
        ...

    def add_column(self) -> None:
        ...

    def alter_column(self) -> None:
        ...
