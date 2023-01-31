from pathlib import Path
from streamlit.source_util import (
    page_icon_and_name, 
    calc_md5, 
    get_pages,
    _on_pages_changed
)
import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# """
# plotly colors:
#     aliceblue, antiquewhite, aqua, aquamarine, azure,
#     beige, bisque, black, blanchedalmond, blue,
#     blueviolet, brown, burlywood, cadetblue,
#     chartreuse, chocolate, coral, cornflowerblue,
#     cornsilk, crimson, cyan, darkblue, darkcyan,
#     darkgoldenrod, darkgray, darkgrey, darkgreen,
#     darkkhaki, darkmagenta, darkolivegreen, darkorange,
#     darkorchid, darkred, darksalmon, darkseagreen,
#     darkslateblue, darkslategray, darkslategrey,
#     darkturquoise, darkviolet, deeppink, deepskyblue,
#     dimgray, dimgrey, dodgerblue, firebrick,
#     floralwhite, forestgreen, fuchsia, gainsboro,
#     ghostwhite, gold, goldenrod, gray, grey, green,
#     greenyellow, honeydew, hotpink, indianred, indigo,
#     ivory, khaki, lavender, lavenderblush, lawngreen,
#     lemonchiffon, lightblue, lightcoral, lightcyan,
#     lightgoldenrodyellow, lightgray, lightgrey,
#     lightgreen, lightpink, lightsalmon, lightseagreen,
#     lightskyblue, lightslategray, lightslategrey,
#     lightsteelblue, lightyellow, lime, limegreen,
#     linen, magenta, maroon, mediumaquamarine,
#     mediumblue, mediumorchid, mediumpurple,
#     mediumseagreen, mediumslateblue, mediumspringgreen,
#     mediumturquoise, mediumvioletred, midnightblue,
#     mintcream, mistyrose, moccasin, navajowhite, navy,
#     oldlace, olive, olivedrab, orange, orangered,
#     orchid, palegoldenrod, palegreen, paleturquoise,
#     palevioletred, papayawhip, peachpuff, peru, pink,
#     plum, powderblue, purple, red, rosybrown,
#     royalblue, saddlebrown, salmon, sandybrown,
#     seagreen, seashell, sienna, silver, skyblue,
#     slateblue, slategray, slategrey, snow, springgreen,
#     steelblue, tan, teal, thistle, tomato, turquoise,
#     violet, wheat, white, whitesmoke, yellow,
#     yellowgreen
# """



def delete_page(main_script_path_str, page_name):

    current_pages = get_pages(main_script_path_str)
    # st.write(current_pages)
    for key, value in current_pages.items():
        if value['page_name'] == page_name:
            del current_pages[key]
            break
        else:
            pass
    _on_pages_changed.send()


delete_page("D:\lianz\Desktop\Python\personal_projects\personal_finance\Ticker_List.py", "classes")



with open(r'D:\\lianz\Desktop\\Python\\personal_projects\\personal_finance\\tickers.json', 'r') as f:
    tickers = json.load(f)

company_statements = ['income-statement',
                      'cash-flow-statement', 'balance-sheet-statement']

terms_interested = {'Revenue': 'revenue',
                    'Gross margin%': 'grossProfitRatio',
                    'Operating Income': 'operatingIncome',
                    'Operating Margin %': 'operatingIncomeRatio',
                    'Net Income': 'netIncome',
                    'Net Income Margin': 'netIncomeRatio',
                    'Earnings per Share': 'epsdiluted',
                    'Shares Oustanding (diluted)': 'weightedAverageShsOutDil',
                    'Dividends': 'dividendsPaid',
                    'Operating Cash Flow': 'operatingCashFlow',
                    'Cap Spending': 'capitalExpenditure',
                    'Free Cash Flow': 'freeCashFlow',
                    'Free Cash Flow per Share': 'freeCashFlow',
                    'Working Capital': 'totalCurrentAssets - totalCurrentLiabilities',
                    'Net Debt': 'netDebt'
                    }



def read_statement(filepath, mode: list(['r','w','r+','w+'])):
    with open(filepath, f'{mode}') as f:
        statement = json.load(f)

        return statement

def generate_key_metrics(financial_statement, list_of_metrics):
    l = []
    dict_holder = {}
    columns = financial_statement[0].keys()

    for n in list_of_metrics:

        if n in columns:
            for i, x in enumerate(financial_statement[::-1]):
                dict_holder[x['calendarYear']] = x[f'{n}']

            l.append(dict_holder)
            dict_holder = {}

        else:
            pass

    df = pd.DataFrame.from_records(
        l, index=[items for items in list_of_metrics if items in columns])

    # df.style.format({f"{df}": "{:,}"})

    return df


def generate_plots(dataframe, arrangement: tuple):

    # create columns to place charts based on arrangement specified (columns in each row)
    cols = st.columns(arrangement)
    dataframe = dataframe.T
    m = 0

    for i, n in enumerate(terms_interested.values()):
        if n in dataframe.columns:

                # Define growth rates Y-o-Y
                growth = dataframe[f'{n}'].pct_change(
                    periods=1).fillna(0)
                fig = make_subplots(specs=[[{"secondary_y": True}]])

                # Add traces (graphs)
                fig.add_trace(
                    go.Scatter(
                        x=dataframe.index, y=dataframe[f'{n}'], mode="lines+markers", name=f"{n.capitalize()}"),
                    secondary_y=False,
                )

                fig.add_trace(
                    go.Bar(
                        x=dataframe.index, y=growth, text=[i for i in growth], opacity=0.3, marker=dict({'color': 'darkorange'}), texttemplate="%{value:.1%}", textposition="inside", name="Growth Y-o-Y"),
                    secondary_y=True,
                )

                # Update figure title, legend, axes
                fig.update_layout(showlegend=False,
                                  xaxis_title='Year', yaxis_title=f'{n}')
                fig.update_yaxes(
                    title_text=f"<b>{n.capitalize()}</b>", secondary_y=False)
                fig.update_yaxes(
                    title_text="Growth Y-o-Y", secondary_y=True)

                # # Add horizontal lines to show max and min values
                # fig.add_hline(y=dataframe[f'{n}'].max(
                # ), line_color='green', line_dash='dash')
                # fig.add_hline(y=dataframe[f'{n}'].min(
                # ), line_color='red', line_dash='dash')

                # Plot the chart in its respective column based on loop
                cols[m].plotly_chart(
                    fig, use_container_width=True,)