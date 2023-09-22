from fastapi import HTTPException
from .sql_connector import DB


def get_db():
    db = DB(db_name="NBA")
    if not db.test_connection():
        raise HTTPException(
            status_code=500, detail="Database connection failed.")
    return db
