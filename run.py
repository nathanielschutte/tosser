
from pathlib import Path

from src.parsers.common import JsonParser
from src.connections.BaseConnection import BaseConnection
from src.context import Context

from src.ingest import Ingest

parser = JsonParser()
connection = BaseConnection()

ingest = Ingest(parser=parser, connection=connection)

ingest.generate_schema(input=Path('tests/basic/input/basic.data.json'), output=Path('tests/basic/output/schema.json'))
