import pymysql.cursors
import pytest

from pymysql.connections import Connection


@pytest.fixture(scope="session")
def db_conn():
    _conn = pymysql.connect(
        host='localhost',
        user='nate',
        password='nate',
        database='test_ingest',
        cursorclass=pymysql.cursors.DictCursor
    )
    with _conn as conn:
        yield conn


def test_db_connect(db_conn):
    ...


def test_db_cursor(db_conn):
    print(type(db_conn))
    with db_conn.cursor() as cursor:
        sql = 'SHOW DATABASES;'
        cursor.execute(sql)
        result = cursor.fetchall()
        print(result)
