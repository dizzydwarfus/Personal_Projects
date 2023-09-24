from sqlalchemy import text


def get_players(db, player_name: str = None, player_id: int = None, limit=100):
    # Base query
    query = """
        SELECT TOP (:limit)
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
    params = {"limit": limit}

    if player_id is not None:
        query += " WHERE CAST(P.PlayerID AS VARCHAR(255)) LIKE :player_id"
        params["player_id"] = f"{player_id}%"

    elif player_name:
        query += " WHERE P.PlayerName LIKE :player_name"
        params["player_name"] = f"%{player_name}%"

    with db.engine.connect() as connection:
        result = connection.execute(text(query), params)

        return result.fetchall(), result.keys()
