import typer
import os
from typing import Optional
from typing_extensions import Annotated
from pathlib import Path
from dotenv import load_dotenv

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


@app.command(name='open')
def _open(
    mode: Annotated[Optional[str], typer.Option(help='Set the server mode')] = None,
    host: Annotated[Optional[str], typer.Option(help='Specify host to bind server to')] = '127.0.0.1',
    port: Annotated[Optional[int], typer.Option(help='Specify port to run server on')] = 5000
):
    server_prod = True
    if mode in ['dev', 'development']:
        server_prod = False
    if os.getenv('TOSS_BROWSER_ENV') in ['dev', 'development']:
        server_prod = False

    from tosser_browser.browser import app

    if server_prod:
        from waitress import serve
        print('Starting production server...')
        serve(app, host=host, port=port)
    else:
        app.run(debug=True, host=host, port=port)


@app.command(name='in')
def _in():
    ...

def main():
    load_dotenv()
    app()
