from fastapi import APIRouter, Depends, HTTPException
from ...database.sql_connector import DB
from ...database.db import get_db
from sqlalchemy import text
from ...models.models import PlayersResponse
from ...services import player_service
from ...utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=PlayersResponse)
async def get_players(player_name: str = None, player_id: int = None, limit: int = 10, db: DB = Depends(get_db)):
    logger.info(
        f"Fetching players with player_name: {player_name}, player_id: {player_id}, limit: {limit}")
    try:
        players, column_names = player_service.get_players(
            db, player_name, player_id, limit)

        # Convert the SQL result to use dynamic column names
        players_list = [{col: getattr(row, col)
                         for col in column_names} for row in players]
        player_response = {"players": players_list if len(
            players_list) > 0 else "No players found."}

        PlayersResponse(**player_response)

        return player_response

    except Exception as e:
        logger.error(f"Error in get_players endpoint: {e}")
        if "Invalid column name" in str(e):
            raise HTTPException(
                status_code=400, detail=f"Invalid column name.")

        elif "Invalid parameter" in str(e):
            raise HTTPException(
                status_code=400, detail=f"Invalid parameter.")

        elif "No players found" in str(e):
            raise HTTPException(
                status_code=400, detail=f"No players found.")

        else:
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch players.")
