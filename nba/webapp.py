import streamlit as st
from draw_baskbetball_court import *

st.set_page_config(page_title="NBA Exploratory Data",
                   page_icon=":magnifying_glass_tilted_left:",
                   layout="wide")

st.markdown("""

# Basketball Court Plot

---


""")

fig = go.Figure()
draw_plotly_court_v2(fig, fig_width=1000, x_cal=250, y_cal=-417.5)
fig.add_trace(go.Scatter(x=[250, 100, 400,], y=np.array([417.5, 100, 300]) * -1,
                         customdata=[[5, 'Lebron James', '1st Quarter', '10:11', '1st quarter, 11:42.0 remaining<br>Austin Reaves missed 2-pointer from 4 ft<br>LA Lakers tied 0-0'], [
                             30, 'Stephen Curry', '2nd Quarter', '5:42'], [15, 'Anthony Davis', '4th Quarter', '0:12']],
                         mode='markers', marker=dict(color='red', size=20),
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

st.plotly_chart(fig, use_container_width=True)
st.write(fig.data)
