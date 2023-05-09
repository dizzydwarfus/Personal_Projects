from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.engine import URL
import os
from dotenv import load_dotenv
from functools import partial
from dataclasses import dataclass


load_dotenv()


@dataclass
class Database:
    database: str
    server: str = os.environ.get('server')
    username: str = os.getenv('DB_username')
    password: str = os.getenv('DB_password')
    port: str = os.getenv('port')
    driver: str = 'ODBC Driver 17 for SQL Server'

    def __post_init__(self):
        self.connection_url = self.create_connection_url()
        self.engine = self.create_db_engine()

    def create_connection_url(self):
        self.connection_url = URL.create(
            "mssql+pyodbc",
            username=self.username,
            password=self.password,
            host=self.server,
            port=self.port,
            database=self.database,
            query={
                "driver": self.driver,
                # "TrustServerCertificate": "yes",
                # "authentication": "ActiveDirectoryIntegrated",
            }
        )
        return self.connection_url

    def create_db_engine(self):
        self.engine = create_engine(url=self.connection_url, echo=True)
        return self.engine

    def test_connection(self):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT DB_NAME()")).fetchone()
            assert result[0] is not None
            print(f'Connection to {result[0]} was successful.')
        except Exception as e:
            # If the connection fails, the test will fail with an exception
            assert False, f'Connection test failed: {e}'


Database(database='NBA',).test_connection()
