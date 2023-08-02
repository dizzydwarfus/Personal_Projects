from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import os
from dotenv import dotenv_values
from functools import partial

secrets = dotenv_values('.env')


def create_connection_url(server, database, username, password, port, driver):
    connection_url = URL.create(
        "mssql+pyodbc",
        username=username,
        password=password,
        host=server,
        port=port,
        database=database,
        query={
            "driver": driver,
            "TrustServerCertificate": "yes",
            "authentication": "ActiveDirectoryIntegrated",
        }
    )
    return connection_url


def test_connection(connection_string):
    try:
        # Replace the connection string with your own
        connection_string = connection_string
        engine = create_engine(connection_string)
        engine.execute('SELECT @@VERSION')
        row = engine.fetchone()
        assert row[0] is not None
    except Exception as e:
        # If the connection fails, the test will fail with an exception
        assert False, f'Connection test failed: {e}'


server = secrets('server')
database = 'NBA'
username = secrets('DB_username')
password = secrets('DB_password')
port = secrets('port')
driver = 'ODBC Driver 17 for SQL Server'

CreateURL = partial(create_connection_url, server=server,
                    username=username, password=password, port=port, driver=driver,)

nba_connection = CreateURL(
    database=database)


test_connection(connection_string=nba_connection)
