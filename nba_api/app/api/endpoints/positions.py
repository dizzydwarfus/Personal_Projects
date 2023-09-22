from fastapi import APIRouter, Depends, HTTPException
from ...database.sql_connector import DB
from ...database.db import get_db
from sqlalchemy import text
from ...models.models import PositionsResponse
from ...services import position_service

router = APIRouter()


@router.get("/", response_model=PositionsResponse)
async def get_positions(db: DB = Depends(get_db)):
    try:

        positions, column_names = position_service.get_position(db)

        position_list = {"positions": [{col: getattr(row, col)
                                        for col in column_names} for row in positions]}

        PositionsResponse(**position_list)

        return position_list

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch positions: {e}")
