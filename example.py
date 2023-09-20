
from pathlib import Path

from tosser.parsers.common import JsonParser
from tosser.connections.Connection import Connection
from tosser.context import Context

from tosser.ingest import Ingest

parser = JsonParser()
connection = Connection()

ingest = Ingest(parser=parser, connection=connection)

ingest.generate_schema(input=Path('tests/basic/input/basic.data.json'), output=Path('tests/basic/output/schema.json'))
