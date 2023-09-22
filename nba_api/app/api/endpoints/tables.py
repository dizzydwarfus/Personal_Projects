from fastapi import APIRouter, Depends, HTTPException
from ...database.sql_connector import DB
from ...database.db import get_db
from sqlalchemy import text

router = APIRouter()


@router.get("/")
async def get_tables(db: DB = Depends(get_db)):
    # Fetch tables from the database
    with db.engine.connect() as connection:
        try:
            tables = connection.execute(
                text("SELECT * FROM INFORMATION_SCHEMA.TABLES")).fetchall()
            tables_list = [{"database": t[0], "schema": t[1],
                            "table_name": t[2], "table_type": t[3]} for t in tables]

            return {"tables": tables_list}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch tables: {e}")
