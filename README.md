[![Tests and Analysis](https://github.com/nathanielschutte/tosser/actions/workflows/test.yml/badge.svg)](https://github.com/nathanielschutte/tosser/actions/workflows/test.yml)

# tosser
Ingest objects into relational schema

## Install
Install requirements and package in a virtual env:
```bash
python -m venv .venv
pip install -r requirements/requirements.txt
pip install -e .
```

Copy `.env.example` to `.env` to configure behavior

## Browser
Run a local Flask development server in debug mode
```bash
toss open
```

Or run a production server
```bash
toss open --mode production
```

You can also run the flask app directly and configure Flask with environment variables or the `.env`
```bash
flask run
```

Flask app can be run programmatically by importing:
```python
from tosser_browser.browser import app as flask_app
```

## CLI
Synthesize source schema by specifying config location
```bash
toss generate
```
Uses default map config path `config.ini` and outputs to schema file `schema.toss`


Ingest file to a configured target
```bash
toss in path/to/file.json --target mysql-endpoint.json

# ex. with
cat mysql-endpoint.json
{
    "host": "localhost",
    "port": 3306
    "username": "root",
    "password": "password"
    "database": "data"
}

# or pass endpoint config JSON directly to the --target option
```
Uses default schema file `schema.toss`

Continuously ingest with
```bash
toss in --watch path/to/files/
```

Allow dynamic schema updates with
```bash
toss in --dynamic
```

## Library
Import the tosser API
```python
from tosser import Tosser
tosser = Tosser()
```
