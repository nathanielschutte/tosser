
from typing import List

# Transactions should be committed per object
# If any part of an object fails, rollback




# Facilitate async batch uploads
class Transactor:

    def __init__(self) -> None:
        ...


    # Queue up rows to insert
    def enqueue(self, schema: str, table: str, rows: List[str]) -> None:
        '''Queue up rows to insert for a table'''
        ...


    # 
