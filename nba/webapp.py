import streamlit as st
from draw_baskbetball_court import *
import pandas as pd


st.set_page_config(page_title="NBA Exploratory Data",
                   page_icon=":magnifying_glass_tilted_left:",
                   layout="wide")

st.markdown("""

# Basketball Court Plot

---


""")
custom = pd.read_csv(
    r'D:\lianz\Desktop\Python\personal_projects\nba\data\games_played.csv')

fig = go.Figure()
draw_plotly_court(fig, fig_width=1000, x_cal=250, y_cal=-417.5)
fig.add_trace(go.Scatter(x=[250, 100, 400,], y=np.array([417.5, 100, 300]) * -1,
                         customdata=custom,
                         mode='markers', marker=dict(color='red', size=20), name='make',
                         hovertemplate="<b>Distance</b>: %{customdata[0]}ft"
                         + "<br><b>Player</b>: %{customdata[1]}"
                         + "<br><b>Quarter</b>: %{customdata[2]}"
                         + "<br><b>Time Left</b>: %{customdata[3]}"
                         + "<br>%{customdata[4]}"),
              )
fig.update_layout(hovermode='closest',
                  hoverlabel=dict(bgcolor='purple', font_size=16,
                                  font_family='Rockwell'),
                  )

st.plotly_chart(fig, use_container_width=False)

st.write(fig.data)
