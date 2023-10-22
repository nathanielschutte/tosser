from typing import List, Dict, Optional
from tosser.endpoint.endpoint import Endpoint

# Transactions should be committed per object
# If any part of an object fails, rollback


# Queue
class TransactionBatch:
    def __init__(self) -> None:
        self.batch: List[str] = []

    def enqueue(self, rows: List[str]):
        ...


# Facilitate async batch uploads
class Transactor:
    def __init__(self) -> None:
        self.batch: Dict[str, Optional[TransactionBatch]] = {}
        self.endpoint: Endpoint

    # Queue up rows to insert
    def enqueue(self, schema: str, table: str, rows: List[str]) -> None:
        """Queue up rows to insert for a table"""
        ...

        if schema not in self.batch:
            self.batch[schema] = None

        # if table not in self.batch[schema]:
        #     self.batch[schema][table] = TransactionBatch()
