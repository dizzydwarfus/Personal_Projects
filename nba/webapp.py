import streamlit as st
from draw_baskbetball_court import *
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.engine import URL
import os
import plotly_express as px
# from sql_connector import Database

st.set_page_config(page_title="NBA Exploratory Data",
                   page_icon=":magnifying_glass_tilted_left:",
                   layout="wide")

st.markdown("""

# Basketball Court Plot

---


""")
server = os.environ.get('server')
username = os.getenv('DB_username')
password = os.getenv('DB_password')
port = os.getenv('port')
driver = 'ODBC Driver 17 for SQL Server'
connection_url = URL.create(
    "mssql+pyodbc",
    username=username,
    password=password,
    host=server,
    port=port,
    database='NBA',
    query={
        "driver": driver,
        # "TrustServerCertificate": "yes",
        # "authentication": "ActiveDirectoryIntegrated",
    }
)

nba = create_engine(url=connection_url, echo=True)


# @st.cache_data(ttl=86400)
def get_data(database, game_id):
    with database.engine.connect() as conn:
        pbp = conn.execute(
            text(f"SELECT * FROM play_by_play WHERE game_id = '{game_id}'"))
        rows = pbp.fetchall()
    pbp_df = pd.DataFrame(rows, columns=pbp.keys())
    return pbp_df


def calculate_distance(x_shot: int, y_shot: int, x_basket: int, y_basket: int):
    x = x_shot - x_basket
    y = y_shot - y_basket
    d = np.sqrt(x**2 + y**2)
    return round(d)


distance = np.vectorize(calculate_distance)


game_id = '202302151930CLEPHI'
player_name = 'Joel Embiid'
df = get_data(nba, game_id)
df['distance'] = distance(
    df['x_shot_pos'], df['y_shot_pos'] * -1, 250, -417.5) / 10

# game_id = st.selectbox('Select a game: ', pbp_df['game_id'])
all_shots = df.loc[(df['player_name'] == player_name),
                   :]
make = df.loc[(
    df['shot_status'] == 'make')
    & (df['player_name'] == player_name),
    :]
miss = df.loc[(
    df['shot_status'] == 'miss')
    & (df['player_name'] == player_name),
    :]


fig = go.Figure()
draw_plotly_court(fig, fig_width=1000, x_cal=250, y_cal=-417.5)
fig.add_trace(go.Scatter(x=[250], y=[-417.5], mode='markers',
              marker=dict(color='red', size=10), name='basket'))
fig.add_trace(go.Scatter(x=make['x_shot_pos'], y=np.array(make['y_shot_pos']) * -1,
                         customdata=make,
                         mode='markers', marker=dict(color='green', size=10), name='make',
                         hovertemplate="<b>Distance</b>: %{customdata[12]}ft"
                         + "<br><b>Player</b>: %{customdata[1]}"
                         + "<br><b>Quarter</b>: %{customdata[7]}"
                         + "<br><b>Time Left</b>: %{customdata[2]}"
                         + "<br>%{customdata[4]}"),
              )
fig.add_trace(go.Scatter(x=miss['x_shot_pos'], y=np.array(miss['y_shot_pos']) * -1,
                         customdata=miss,
                         mode='markers', marker=dict(color='red', size=10, symbol='cross'), name='miss',
                         hovertemplate="<b>Distance</b>: %{customdata[12]}ft"
                         + "<br><b>Player</b>: %{customdata[1]}"
                         + "<br><b>Quarter</b>: %{customdata[7]}"
                         + "<br><b>Time Left</b>: %{customdata[2]}"
                         + "<br>%{customdata[4]}"),
              )

fig.update_layout(hovermode='closest',
                  hoverlabel=dict(bgcolor='gray', font_size=16,
                                  font_family='Rockwell'),
                  )
fig.update_layout(showlegend=False)

st.plotly_chart(fig, use_container_width=True)

st.dataframe(all_shots, use_container_width=True)
