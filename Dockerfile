FROM python:3.11 as python-base

WORKDIR /app

COPY requirements/. /app/requirements/
COPY src/. /app/src/

FROM python-base as ci

RUN pip install -r requirements/requirements_dev.txt
