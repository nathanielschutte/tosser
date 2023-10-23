from typing import List, Dict, Optional
import dataclasses
from enum import Enum

from tosser.endpoint.target import ITarget


class TransactionType(Enum):
    CREATE_TABLE = 'create_table'
    INSERT = 'insert'
    BATCH_INSERT = 'batch_insert'
    ALTER_COLUMN = 'alter_column'
    ADD_COLUMN = 'add_column'


@dataclasses.dataclass
class Transaction:
    type: TransactionType
    query: str


class TransactionBatch(Transaction):
    batch: List[Transaction]
    type = TransactionType.BATCH_INSERT

    def add(self, transaction: Transaction) -> None:
        self.batch.append(transaction)

    def __len__(self) -> int:
        return len(self.batch)


class Transactor:
    def __init__(self) -> None:
        self.queue: List[Transaction]
        self.target: ITarget


    def enqueue(self, transaction: Transaction) -> None:
        """Queue a Transaction"""
        
        self.queue.append(transaction)
