import datetime
import os
from flask import Flask, render_template

HTML_DIR = os.path.abspath(os.path.dirname(__file__)) + '/html'
BASE_PATH = '/tosser'

app = Flask(__name__, template_folder=HTML_DIR, static_folder=HTML_DIR)

@app.route("/")
def root():
    return app.redirect(BASE_PATH)

@app.route(BASE_PATH)
def hello_world():
    return render_template('index.html', utc_dt=datetime.datetime.utcnow())
