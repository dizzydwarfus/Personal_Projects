from sqlalchemy import text


def get_shots(db, player_name: str = None, player_id: int = None, game_info: bool = False, limit: int = 100):

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
                    JOIN
                    (SELECT
                        Team.TeamID, Team.TeamName
                    FROM
                        Team
                        ) as Team
                    ON
                    ShotsTaken.TeamID = Team.TeamID

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
                    ) as GameInfo
                ON
                    ShotsTaken.GameID = GameInfo.GameID
                """

    if player_id is not None:
        shots += " WHERE Player.PlayerID = :player_id"
        params["player_id"] = player_id

    elif player_name:
        shots += " WHERE Player.PlayerName LIKE :player_name"
        params["player_name"] = f"%{player_name}%"

    # Execute query
    query = text(shots)

    with db.engine.connect() as connection:
        result = connection.execute(query, params)
        return result.fetchall(), result.keys() if result else []
