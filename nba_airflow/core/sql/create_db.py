import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy import text
from sql_connector import *

nba = DB(db_name='NBA')
nba.test_connection()


def create_table_from_df(df, table_name):
    df.to_sql(table_name, nba.engine, if_exists='replace', index=False)


def drop_table(table_list: list):
    for table in table_list:
        with nba.engine.begin() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {table}"))


create_team_table = text("""
CREATE TABLE teams(
team_id INT PRIMARY KEY NOT NULL,
team_name VARCHAR(20),
team_abbreviation CHAR(3)
)
""")

create_player_table = text("""
CREATE TABLE players(
player_id INT PRIMARY KEY,
player_name VARCHAR(30)
) 
""")

create_team_arena = text("""
CREATE TABLE arena_history(
arena_id INT PRIMARY KEY,
arena_name VARCHAR(30),
team_year INT,
team_id INT FOREIGN KEY REFERENCES teams(team_id)
)
""")

create_player_team_table = text("""
CREATE TABLE player_team_history(
id INT NOT NULL IDENTITY(1,1),
player_id INT FOREIGN KEY REFERENCES players(player_id),
player_age INT,
team_id INT FOREIGN KEY REFERENCES teams(team_id),
year VARCHAR(10)
)
""")

create_games_played = text("""
CREATE TABLE games_played(
game_id CHAR(18) PRIMARY KEY,
game_date datetime,
visitor_team_id INT FOREIGN KEY REFERENCES teams(team_id), 
visitor_pts INT NOT NULL,
home_team_id INT FOREIGN KEY REFERENCES teams(team_id),
home_pts INT NOT NULL,
overtime VARCHAR(5),
attendance INT,
arena_id INT
)
""")

# with nba.engine.begin() as conn:
#     conn.execute(create_team_table)
#     conn.execute(create_player_table)
#     conn.execute(create_team_arena)
#     conn.execute(create_player_team_table)
#     conn.execute(create_games_played)
