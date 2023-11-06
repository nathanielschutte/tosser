import datetime
import os
from flask import Flask, render_template
from typing import Dict, Any
import logging

from tosser_http.api import TosserApi
from tosser_http.logs import LOGGING_CONFIG
from tosser.logs import LOG_MAIN

HTML_DIR = os.path.abspath(os.path.dirname(__file__)) + '/html'
BASE_PATH = '/tosser'

log_config: Dict[str, Any] = LOGGING_CONFIG.copy()
log_config['handlers']['log']['filename'] = os.getenv('TOSS_BROWSER_LOG') or 'out.log'
logging.config.dictConfig(log_config)

app = Flask(__name__, template_folder=HTML_DIR, static_folder=HTML_DIR)
logging.getLogger(LOG_MAIN).info(f'Flask server started on port {os.getenv("FLASK_RUN_PORT")}')
api = TosserApi()

@app.route("/")
def root():
    return app.redirect(BASE_PATH)

@app.route(BASE_PATH)
def hello_world():
    return render_template('index.html', utc_dt=datetime.datetime.utcnow())
