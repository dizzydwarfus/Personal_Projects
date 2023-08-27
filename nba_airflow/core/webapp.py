from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.engine import URL
import os
from dotenv import load_dotenv
from functools import partial
from dataclasses import dataclass
import streamlit as st
import pandas as pd
import numpy as np
from draw_baskbetball_court import *
load_dotenv()

st.set_page_config(page_title="NBA Exploratory Data",
                   page_icon=":magnifying_glass_tilted_left:",
                   layout="wide")

st.markdown("""

# Basketball Court Plot

---


""")


@dataclass
class Database:
    db_name: str
    server: str = os.environ.get('server')
    username: str = os.getenv('DB_username')
    password: str = os.getenv('DB_password')
    port: str = os.getenv('port')
    driver: str = 'ODBC Driver 17 for SQL Server'

    def __post_init__(self):
        self.connection_url = self.create_connection_url()
        self.engine = self.create_db_engine()

    def create_connection_url(self):
        self.connection_url = URL.create(
            "mssql+pyodbc",
            username=self.username,
            password=self.password,
            host=self.server,
            port=self.port,
            database=self.db_name,
            query={
                "driver": self.driver,
                # "TrustServerCertificate": "yes",
                # "authentication": "SqlPassword",
            }
        )
        return self.connection_url

    def create_db_engine(self):
        self.engine = create_engine(url=self.connection_url, echo=False)
        return self.engine

    def test_connection(self):
        try:
            with self.engine.connect() as connection:
                result = connection.execute(
                    text("SELECT DB_NAME()")).fetchone()
            print(f'Connection to {result[0]} was successful.')
            return True
        except Exception as e:
            return False, f'Connection test failed: {e}'


def get_info(database):
    with database.engine.connect() as conn:
        info = conn.execute(
            text(f"SELECT DISTINCT GameID, HomeTeamID FROM GamesPlayed"))
        info = info.fetchall()
    return [i[0] for i in info]


@st.cache_data
def get_data(game_id):
    with nba.engine.connect() as conn:
        pbp = conn.execute(
            text(f"""
                 SELECT 
                    ST.PlayerID,
                    ST.TimeLeft,
                    ST.TeamID,
                    ST.ScoreStatus,
                    ST.X_Shot_Pos,
                    ST.Y_Shot_Pos,
                    ST.Quarter,
                    ST.ShotStatus,
                    ST.FullText,
                    ST.GameDate,
                    ST.GameID,
                    Player.PlayerName,
                    Team.TeamName
                FROM ShotsTaken as ST
                    LEFT JOIN Team ON ST.TeamID = Team.TeamID
                    LEFT JOIN Player ON ST.PlayerID = Player.PlayerID 
                 WHERE 
                    GameID = '{game_id}'"""))

        rows = pbp.fetchall()
    pbp_df = pd.DataFrame(rows, columns=pbp.keys())
    return pbp_df


def calculate_distance(x_shot: int, y_shot: int, x_basket: int, y_basket: int):
    x = x_shot - x_basket
    y = y_shot - y_basket
    d = np.sqrt(x**2 + y**2)
    return round(d)


def get_sidebar_options(df):
    teams = df['TeamName'].unique()
    players = df.loc[df['TeamName'] == teams[0], 'PlayerName'].unique()
    return teams, players


def make_df(df):
    make = df.loc[(
        df['ShotStatus'] == 'make')]
    return make


def miss_df(df):
    miss = df.loc[(
        df['ShotStatus'] == 'miss')]
    return miss


def create_shot_chart(df, basket_x, basket_y):
    make = make_df(df)
    miss = miss_df(df)
    fig = go.Figure()

    draw_plotly_court(fig, fig_width=1000, x_cal=basket_x, y_cal=basket_y)

    fig.add_trace(go.Scatter(x=[basket_x], y=[basket_y], mode='markers',
                             marker=dict(color='red', size=10), name='basket'))

    fig.add_trace(go.Scatter(x=make['X_Shot_Pos'], y=np.array(make['Y_Shot_Pos']) * -1,
                             customdata=make,
                             mode='markers', marker=dict(color='green', size=10), name='make',
                             hovertemplate="<b>Distance</b>: %{customdata[13]}ft"
                             + "<br><b>Player</b>: %{customdata[11]}"
                             + "<br><b>Quarter</b>: %{customdata[6]}"
                             + "<br><b>Time Left</b>: %{customdata[1]}"
                             + "<br>%{customdata[3]}"),
                  )

    fig.add_trace(go.Scatter(x=miss['X_Shot_Pos'], y=np.array(miss['Y_Shot_Pos']) * -1,
                             customdata=miss,
                             mode='markers', marker=dict(color='red', size=10, symbol='cross'), name='miss',
                             hovertemplate="<b>Distance</b>: %{customdata[13]}ft"
                             + "<br><b>Player</b>: %{customdata[11]}"
                             + "<br><b>Quarter</b>: %{customdata[6]}"
                             + "<br><b>Time Left</b>: %{customdata[1]}"
                             + "<br>%{customdata[3]}"),
                  )

    fig.update_layout(hovermode='closest',
                      hoverlabel=dict(bgcolor='gray', font_size=16,
                                      font_family='Rockwell'),
                      )

    fig.update_layout(showlegend=False)
    return fig


distance = np.vectorize(calculate_distance)

nba = Database(db_name='NBA')

game_ids = get_info(nba)

with st.sidebar:
    game_id_choice = st.selectbox('Choose Game ID:', options=game_ids)

df = get_data(game_id_choice)

teams, players = get_sidebar_options(df)

with st.sidebar:
    team_choice = st.selectbox('Choose Team:', options=teams)
    player_choice = st.selectbox('Choose Player:', options=players)

df['distance'] = distance(
    df['X_Shot_Pos'], df['Y_Shot_Pos'] * -1, 250, -417.5) / 10

all_shots = df.loc[(df['GameID'] == game_id_choice)
                   & (df['TeamName'] == team_choice)
                   & (df['PlayerName'] == player_choice),
                   :]

st.plotly_chart(create_shot_chart(all_shots, basket_x=250,
                basket_y=-417.5), use_container_width=True)

with st.expander('All Shots'):
    st.dataframe(df, use_container_width=True)

with st.expander('Selected Shots'):
    st.dataframe(all_shots, use_container_width=True)
