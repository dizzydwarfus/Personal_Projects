from fastapi import FastAPI
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


@app.get("/")
async def root():
    db = DB(db_name="NBA")

    if db.test_connection():
        return {"message": "Please navigate to /api/players to see the players."}
    else:
        return {"message": "Failed to connect to the database."}


@app.get("/api/players")
async def get_players():
    db = DB(db_name="NBA")
    # Fetch players from the database
    with db.engine.connect() as connection:
        try:
            players = connection.execute(
                text("""SELECT 
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
                            Position AS Pos ON P.PositionID = Pos.PositionID;
                     """)).fetchall()
            return {"players": [{"PlayerID": p[0],
                                 "PlayerName": p[1],
                                 "FromYear": p[2],
                                 "ToYear": p[3],
                                 "PositionID": p[4],
                                 "Height": p[5],
                                 "Weight": p[6],
                                 "BirthDate": p[7],
                                 "College": p[8]} for p in players]}
        except Exception as e:
            return {"error": f"Failed to fetch players: {e}"}


@app.get("/api/tables")
async def get_tables():
    db = DB(db_name="NBA")
    # Fetch players from the database
    with db.engine.connect() as connection:
        try:
            tables = connection.execute(
                text("SELECT * FROM INFORMATION_SCHEMA.TABLES")).fetchall()
            tables_list = [{"database": t[0], "schema": t[1],
                            "table_name": t[2], "table_type": t[3]} for t in tables]

            return {"tables": tables_list}
        except Exception as e:
            return {"error": f"Failed to fetch tables: {e}"}


@app.get("/api/positions")
async def get_tables():
    db = DB(db_name="NBA")
    # Fetch players from the database
    with db.engine.connect() as connection:
        try:
            positions = connection.execute(
                text("SELECT * FROM Position")).fetchall()
            position_list = [{"PositionID": p[0], "PositionName": p[1],
                              "Description": p[2]} for p in positions]

            return {"positions": position_list}
        except Exception as e:
            return {"error": f"Failed to fetch tables: {e}"}


@app.get("/api/shots")
async def get_shots(player_id: int):
    db = DB(db_name="NBA")
    with db.engine.connect() as connection:
        try:
            # Update the SQL query to filter by player_id
            shots = connection.execute(
                text("SELECT * FROM ShotsTaken WHERE player_id = :player_id"),
                {"player_id": player_id}
            ).fetchall()

            shots_list = [{"game_id": s[0], "player_name": s[1],
                           "x_shot_pos": s[2], "y_shot_pos": s[3]} for s in shots]

            return {"shots": shots_list}
        except Exception as e:
            return {"error": f"Failed to fetch shots: {e}"}


if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, log_level="info", reload=True)
