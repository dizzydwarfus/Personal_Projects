from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.engine import URL
import os
from dotenv import load_dotenv
from functools import partial

load_dotenv()


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
            # "TrustServerCertificate": "yes",
            # "authentication": "ActiveDirectoryIntegrated",
        }
    )
    return connection_url


def test_connection(connection_string):
    try:
        # Replace the connection string with your own
        connection_string = connection_string
        engine = create_engine(connection_string, echo=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT DB_NAME()")).fetchone()
        assert result[0] is not None
        print(f'Connection to {result[0]} was successful.')
    except Exception as e:
        # If the connection fails, the test will fail with an exception
        assert False, f'Connection test failed: {e}'


server = os.environ.get('server')
database = 'NBA'
username = os.getenv('DB_username')
password = os.getenv('DB_password')
port = os.getenv('port')
driver = 'ODBC Driver 17 for SQL Server'

CreateURL = partial(create_connection_url, server=server,
                    username=username, password=password, port=port, driver=driver,)

nba_connection = CreateURL(
    database=database)


test_connection(connection_string=nba_connection)
