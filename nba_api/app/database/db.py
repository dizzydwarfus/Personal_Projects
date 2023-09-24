from fastapi import HTTPException
from .sql_connector import DB
from ..utils.logger import get_logger
import os

logger = get_logger(__name__)
DB_NAME = os.environ.get("DB_NAME")


def get_db():
    db = DB(db_name=DB_NAME)
    if not db.test_connection():
        logger.error("Database connection failed.")
        raise HTTPException(
            status_code=503, detail="Database connection failed.")
    return db
