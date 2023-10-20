[![Tests and Analysis](https://github.com/nathanielschutte/tosser/actions/workflows/tosser_test.yml/badge.svg)](https://github.com/nathanielschutte/tosser/actions/workflows/tosser_test.yml)

# tosser
Ingest objects into relational schema

## Install
```bash
pip install -r requirements/requirements.txt
pip install -e .
```

## Browser
Run a local Flask development server in debug mode
```bash
toss open
# runs on localhost:5000 by default, override with --port or -p
```
**Production server should not be run with this command**

## CLI
```bash
toss --help
```

Synthesize source schema by specifying config location
```bash
toss generate path/to/config.ini --output schema.toss
```

Ingest file to a configured target
```bash
toss in path/to/file.json --schema schema.toss --target mysql-endpoint.json

# with
cat mysql-endpoint.json
{
    "host": "localhost",
    "port": 3306
    "username": "root",
    "password": "password"
    "database": "data"
}

# or pass endpoint config json directly to the --target option
```

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
import tosser
```
