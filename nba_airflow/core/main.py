from typing import Annotated, Union
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from sql.sql_connector import DB  # Your database connection class
from sqlalchemy import text

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = DB(db_name="NBA")
    if not db.test_connection():
        raise HTTPException(
            status_code=500, detail="Database connection failed.")
    return db


@app.get("/")
async def root(db: DB = Depends(get_db)):
    if not db.test_connection():
        return {"message": "Failed to connect to the database."}

    return {
        "message": "Welcome to the NBA Data API!",
        "description": "This API provides information about NBA players, shots, positions, and more.",
        "endpoints": {
            "/api/players": "Retrieve details of player(s) by providing player_id or player_name as a query parameter.",
            "/api/shots": "Retrieve shot details. You can filter shots for player(s) by providing player_id or player_name as a query parameter.",
            "/api/tables": "Retrieve a list of all tables in the database.",
            "/api/positions": "Retrieve a list of all positions in the database.",

            # ... Add more endpoints here
        },
        "usage": {
            "/api/players": "Example: /api/players?player_id=5",
            "/api/shots": "Example: /api/shots?player_id=5",
            "/api/tables": "Example: /api/tables",
            "/api/positions": "Example: /api/positions",

            # ... Add usage examples for other endpoints here
        },
        "note": "Visit each endpoint or refer to the documentation for more details."
    }


@app.get("/api/players/")
async def get_players(player_name: str = None, player_id: int = None, db: DB = Depends(get_db)):
    with db.engine.connect() as connection:
        try:
            # Base query
            query = """
                SELECT 
                    P.PlayerID, 
                    P.PlayerName, 
                    P.FromYear, 
                    P.ToYear, 
                    Pos.PositionName,
                    P.Height,
                    P.Weight,
                    P.BirthDate,
                    P.College
                FROM 
                    Player AS P
                INNER JOIN 
                    Position AS Pos ON P.PositionID = Pos.PositionID
            """
            params = {}
            if player_id is not None:
                query += " WHERE P.PlayerID = :player_id"
                params["player_id"] = player_id

            elif player_name:
                query += " WHERE P.PlayerName LIKE :player_name"
                params["player_name"] = f"%{player_name}%"

            result = connection.execute(text(query), params)

            column_names = result.keys()
            players = result.fetchall()

            # Convert the SQL result to use dynamic column names
            players_list = [{col: getattr(row, col)
                             for col in column_names} for row in players]

            return {"players": players_list if len(players_list) > 0 else "No players found."}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch players: {e}")


@app.get("/api/tables")
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


@app.get("/api/positions")
async def get_positions(db: DB = Depends(get_db)):
    # Fetch players from the database
    with db.engine.connect() as connection:
        try:
            positions = connection.execute(
                text("SELECT * FROM Position")).fetchall()
            position_list = [{"PositionID": p[0], "PositionName": p[1],
                              "Description": p[2]} for p in positions]

            return {"positions": position_list}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch positions: {e}")


@app.get("/api/shots")
async def get_shots(player_name: str = None, player_id: int = None, game_info: bool = False, limit: int = 100, db: DB = Depends(get_db)):
    if player_id is None and player_name is None:
        raise HTTPException(
            status_code=400, detail="player_id or player_name must be provided.")

    with db.engine.connect() as connection:
        try:
            # Base query
            shots = """
                     SELECT TOP (:limit)
                        *
                     FROM
                        ShotsTaken 
                     JOIN 
                        (SELECT 
                            Player.PlayerID, Player.PlayerName, Position.PositionName, Player.Height, Player.Weight, Player.BirthDate, Player.College
                        FROM
                            Player
                        JOIN
                            Position
                        ON
                            Player.PositionID = Position.PositionID
                            ) as Player
                     ON 
                        ShotsTaken.PlayerID = Player.PlayerID

                     """

            params = {"limit": limit}

            if game_info:
                shots += """ JOIN
                        (SELECT
                            Arena.ArenaName, GamesPlayed.Attendance, GamesPlayed.VisitorPTS, GamesPlayed.HomePTS, GamesPlayed.GameID, GamesPlayed.HomeTeamID, GamesPlayed.VisitorTeamID, HomeTeam.TeamName as HomeTeamName, VisitorTeam.TeamName as VisitorTeamName
                        FROM
                            GamesPlayed
                        JOIN
                            Arena
                        ON
                            GamesPlayed.ArenaID = Arena.ArenaID
                        JOIN
                            (SELECT
                                Team.TeamID, Team.TeamName
                            FROM
                                Team
                                ) as HomeTeam
                            ON
                                GamesPlayed.HomeTeamID = HomeTeam.TeamID
                        JOIN
                            (SELECT
                                Team.TeamID, Team.TeamName
                            FROM
                                Team
                                ) as VisitorTeam
                            ON
                                GamesPlayed.VisitorTeamID = VisitorTeam.TeamID
                            ) as Games
                        ON 
                            ShotsTaken.GameID = Games.GameID"""

            if player_id is not None:
                shots += " WHERE Player.PlayerID = :player_id"
                params["player_id"] = player_id
            elif player_name:
                shots += " WHERE Player.PlayerName LIKE :player_name"
                params["player_name"] = f"%{player_name}%"

            shots = connection.execute(text(shots), params)
            column_names = shots.keys() if shots else []
            shots_list = [{col: getattr(s, col) for col in column_names}
                          for s in shots]

            return {"shots": shots_list if len(shots_list) > 0 else "No shots found."}

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch shots: {e}")


if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, log_level="info", reload=True)
