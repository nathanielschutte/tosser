import typer
import os
import json
import sys
from typing import Optional
from typing_extensions import Annotated
from pathlib import Path
from dotenv import load_dotenv
import logging

from tosser import Tosser
from tosser.logs import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)

app = typer.Typer(
    pretty_exceptions_short=True,
    pretty_exceptions_show_locals=False
)
tosser = Tosser()


@app.command()
def generate(
        source: Optional[Annotated[str, typer.Option(help='Source endpoint config file or JSON')]] = None,
        files: Optional[Annotated[str, typer.Option(help='Quick way to set a file glob as the source')]] = None
    ):

    if files is not None:
        source = json.dumps({
            'driver': 'file',
            'path': files
        })
    if source is None:
        print('Error: source must be set', file=sys.stderr)
        sys.exit(1)

    tosser.set_source(source)
    tosser.generate()


@app.command(name='open')
def _open(
    mode: Annotated[Optional[str], typer.Option(help='Set the server mode')] = None,
    host: Annotated[Optional[str], typer.Option(help='Specify host to bind server to')] = '127.0.0.1',
    port: Annotated[Optional[int], typer.Option(help='Specify port to run server on')] = 5000
):
    server_prod = True
    if mode in ['dev', 'development']:
        server_prod = False
    if os.getenv('TOSS_ENV') in ['dev', 'development']:
        server_prod = False
    if os.getenv('FLASK_ENV') is None:
        os.environ['FLASK_ENV'] = 'production' if server_prod else 'development'

    from tosser_http.app import app as flask_app

    if server_prod:
        from waitress import serve
        print('Starting production server...')
        serve(flask_app, host=host, port=port)
    else:
        flask_app.run(debug=True, host=host, port=port)


@app.command(name='in')
def _in():
    ...


def main():
    load_dotenv()
    app()
