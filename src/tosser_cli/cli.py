import typer
from typing_extensions import Annotated
from pathlib import Path

app = typer.Typer()

@app.command()
def test(schema: Annotated[str, typer.Argument()], output: Annotated[str, typer.Option()]):
    from tosser.ingest import Ingest
    from tosser.parsers.common import JsonParser
    from tosser.connections.Connection import Connection
    parser = JsonParser()
    connection = Connection()
    ingest = Ingest(parser=parser, connection=connection)
    ingest.generate_schema(Path(schema), Path(output))

@app.command(name='in')
def _in():
    ...

def main():
    app()
