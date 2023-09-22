from fastapi import APIRouter, Depends, HTTPException
from ...database.sql_connector import DB
from ...database.db import get_db
from sqlalchemy import text
from ...models.models import PlayersResponse
from ...services import player_service
router = APIRouter()


@router.get("/", response_model=PlayersResponse)
async def get_players(player_name: str = None, player_id: int = None, limit: int = 10, db: DB = Depends(get_db)):
    try:
        players, column_names = player_service.get_players_by_id(
            db, player_name, player_id, limit)

        # Convert the SQL result to use dynamic column names
        players_list = [{col: getattr(row, col)
                         for col in column_names} for row in players]
        player_response = {"players": players_list if len(
            players_list) > 0 else "No players found."}

        PlayersResponse(**player_response)

        return player_response

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch players: {e}")
