from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import os
from dotenv import dotenv_values
from functools import partial
from sqlalchemy import text

secrets = dotenv_values(".env")


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
            "TrustServerCertificate": "No",
        }
    )
    return connection_url


def test_connection(connection_string):
    try:
        connection_string = connection_string
        engine = create_engine(connection_string)
        with engine.connect() as connection:  # get a connection
            print("Successfully connected to the database.")
            result = connection.execute(text(
                'SELECT @@VERSION'))  # execute the query
            row = result.fetchone()  # fetch the result
            print(f"SQL Server version: {row[0]}")
            assert row[0] is not None
    except Exception as e:
        # If the connection fails, the test will fail with an exception
        assert False, f'Connection test failed: {e}'


server = secrets['azure_sql_server']
database = secrets['azure_sql_database']
username = secrets['azure_DB_username']
password = secrets['azure_DB_password']
port = secrets['port']
driver = secrets['azure_DB_driver']

CreateURL = partial(create_connection_url, server=server,
                    username=username, password=password, port=port, driver=driver,)

test_connection(CreateURL(database=database))
