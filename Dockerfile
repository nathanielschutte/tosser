FROM python:3.11 as python-base

WORKDIR /app

COPY requirements/. /app/requirements/
COPY src/. /app/src/
COPY .env.example /app/.env
COPY .flaskenv.example /app/.flaskenv
COPY pyproject.toml /app/pyproject.toml

FROM python-base as ci
WORKDIR /app
RUN pip install -r requirements/requirements_dev.txt
RUN pip install -e .

FROM python-base as prod
WORKDIR /app
RUN pip install -r requirements/requirements.txt
RUN pip install -e .
