from fastapi import APIRouter, Depends, HTTPException
from ...database.sql_connector import DB
from ...database.db import get_db
from sqlalchemy import text
from ...models.models import ShotsResponse
from ...services import shotstaken_service

router = APIRouter()


@router.get("/", response_model=ShotsResponse)
async def get_shots(player_name: str = None, player_id: int = None, game_info: bool = False, limit: int = 100, db: DB = Depends(get_db)):
    if player_id is None and player_name is None:
        raise HTTPException(
            status_code=400, detail="player_id or player_name must be provided.")

    try:
        shots, column_names = shotstaken_service.get_shots(
            db, player_name, player_id, game_info, limit)

        shots_list = [{col: getattr(s, col) for col in column_names}
                      for s in shots]

        shots_response = {"shots": shots_list if len(
            shots_list) > 0 else "No shots found."}

        ShotsResponse(**shots_response)
        return shots_response

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch shots: {e}")
