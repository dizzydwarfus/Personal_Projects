import plotly.graph_objects as go
import numpy as np


def draw_plotly_court(fig, fig_width=800, margins=0, x_cal=0, y_cal=0):

    # From: https://community.plot.ly/t/arc-shape-with-path/7205/5
    def ellipse_arc(x_center=x_cal, y_center=y_cal, a=10.5, b=10.5, start_angle=0.0, end_angle=2 * np.pi, N=200, closed=False):
        t = np.linspace(start_angle, end_angle, N)
        x = x_center + a * np.cos(t)
        y = y_center + b * np.sin(t)
        path = f'M {x[0]}, {y[0]}'
        for k in range(1, len(t)):
            path += f'L{x[k]}, {y[k]}'
        if closed:
            path += ' Z'
        return path

    fig_height = fig_width * (470 + 2 * margins) / (500 + 2 * margins)
    fig.update_layout(width=fig_width, height=fig_height)

    # Set axes ranges
    fig.update_xaxes(range=[-250 - margins + x_cal, 250 + margins + x_cal])
    fig.update_yaxes(range=[-52.5 - margins + y_cal, 417.5 + margins + y_cal])

    threept_break_y = 89.47765084 + y_cal
    three_line_col = "black"
    main_line_col = "black"
    basket = "#981717"  # ec7607

    fig.update_layout(
        # Line Horizontal
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="#dfbb85",
        plot_bgcolor="#dfbb85",
        yaxis=dict(
            scaleanchor="x",
            scaleratio=1,
            showgrid=False,
            zeroline=True,
            showline=False,
            ticks='',
            showticklabels=False,
            fixedrange=True,
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=True,
            showline=False,
            ticks='',
            showticklabels=False,
            fixedrange=True,
        ),
        shapes=[
            dict(
                type="rect", x0=-250 + x_cal, y0=-52.5 + y_cal, x1=250 + x_cal, y1=417.5 + y_cal,
                line=dict(color=main_line_col, width=1),
                # fillcolor='#333333',
                layer='below'
            ),
            dict(
                type="rect", x0=-80 + x_cal, y0=-52.5 + y_cal, x1=80 + x_cal, y1=137.5 + y_cal,
                line=dict(color=main_line_col, width=1),
                # fillcolor='#333333',
                layer='below'
            ),
            dict(
                type="rect", x0=-60 + x_cal, y0=-52.5 + y_cal, x1=60 + x_cal, y1=137.5 + y_cal,
                line=dict(color=main_line_col, width=1),
                # fillcolor='#333333',
                layer='below'
            ),
            dict(
                type="circle", x0=-60 + x_cal, y0=77.5 + y_cal, x1=60 + x_cal, y1=197.5 + y_cal, xref="x", yref="y",
                line=dict(color=main_line_col, width=1),
                # fillcolor='#dddddd',
                layer='below'
            ),
            dict(
                type="line", x0=-60 + x_cal, y0=137.5 + y_cal, x1=60 + x_cal, y1=137.5 + y_cal,
                line=dict(color=main_line_col, width=1),
                layer='below'
            ),

            dict(
                type="rect", x0=-2 + x_cal, y0=-7.25 + y_cal, x1=2 + x_cal, y1=-12.5 + y_cal,
                line=dict(color=basket, width=2),
                fillcolor=basket,
            ),
            dict(
                type="circle", x0=-7.5 + x_cal, y0=-7.5 + y_cal, x1=7.5 + x_cal, y1=7.5 + y_cal, xref="x", yref="y",
                line=dict(color=basket, width=3),
            ),
            dict(
                type="line", x0=-30 + x_cal, y0=-12.5 + y_cal, x1=30 + x_cal, y1=-12.5 + y_cal,
                line=dict(color=basket, width=5),
            ),

            dict(type="path",
                 path=ellipse_arc(a=40, b=40, start_angle=0, end_angle=np.pi),
                 line=dict(color=main_line_col, width=1), layer='below'),
            dict(type="path",
                 path=ellipse_arc(
                     a=237.5, b=237.5, start_angle=0.386283101, end_angle=np.pi - 0.386283101),
                 line=dict(color=main_line_col, width=1), layer='below'),
            dict(
                type="line", x0=-220 + x_cal, y0=-52.5 + y_cal, x1=-220 + x_cal, y1=threept_break_y,
                line=dict(color=three_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=-220 + x_cal, y0=-52.5 + y_cal, x1=-220 + x_cal, y1=threept_break_y,
                line=dict(color=three_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=220 + x_cal, y0=-52.5 + y_cal, x1=220 + x_cal, y1=threept_break_y,
                line=dict(color=three_line_col, width=1), layer='below'
            ),

            dict(
                type="line", x0=-250 + x_cal, y0=227.5 + y_cal, x1=-220 + x_cal, y1=227.5 + y_cal,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=250 + x_cal, y0=227.5 + y_cal, x1=220 + x_cal, y1=227.5 + y_cal,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=-90 + x_cal, y0=17.5 + y_cal, x1=-80 + x_cal, y1=17.5 + y_cal,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=-90 + x_cal, y0=27.5 + y_cal, x1=-80 + x_cal, y1=27.5 + y_cal,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=-90 + x_cal, y0=57.5 + y_cal, x1=-80 + x_cal, y1=57.5 + y_cal,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=-90 + x_cal, y0=87.5 + y_cal, x1=-80 + x_cal, y1=87.5 + y_cal,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=90 + x_cal, y0=17.5 + y_cal, x1=80 + x_cal, y1=17.5 + y_cal,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=90 + x_cal, y0=27.5 + y_cal, x1=80 + x_cal, y1=27.5 + y_cal,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=90 + x_cal, y0=57.5 + y_cal, x1=80 + x_cal, y1=57.5 + y_cal,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=90 + x_cal, y0=87.5 + y_cal, x1=80 + x_cal, y1=87.5 + y_cal,
                line=dict(color=main_line_col, width=1), layer='below'
            ),

            dict(type="path",
                 path=ellipse_arc(y_center=417.5 + y_cal, a=60, b=60,
                                  start_angle=-0, end_angle=-np.pi),
                 line=dict(color=main_line_col, width=1), layer='below'),

        ]
    )
    return True
