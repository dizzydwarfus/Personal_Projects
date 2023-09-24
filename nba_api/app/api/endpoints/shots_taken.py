from fastapi import APIRouter, Depends, HTTPException
from ...database.sql_connector import DB
from ...database.db import get_db
from sqlalchemy import text
from ...models.models import ShotsResponse
from ...services import shotstaken_service
from ...utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=ShotsResponse)
async def get_shots(team_name: str = None, home_team: str = None, away_team: str = None, player_name: str = None, player_id: int = None, arena_name: str = None, game_info: bool = True, limit: int = 100, db: DB = Depends(get_db)):
    logger.info(
        f"Fetching shots with team_name: {team_name}, home_team: {home_team}, away_team: {away_team}, player_name: {player_name}, player_id: {player_id}, game_info: {game_info}, limit: {limit}")

    try:
        shots, column_names = shotstaken_service.get_shots(
            db, team_name, home_team, away_team, player_name, player_id, arena_name, game_info, limit)

        shots_list = [{col: getattr(s, col) for col in column_names}
                      for s in shots]

        shots_response = {"shots": shots_list if len(
            shots_list) > 0 else "No shots found."}

        ShotsResponse(**shots_response)
        return shots_response

    except Exception as e:
        logger.error(f"Error in get_shots endpoint: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch shots: {e}")
