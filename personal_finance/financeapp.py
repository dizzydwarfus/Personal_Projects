import pandas as pd
import streamlit as st
import datetime as dt
import requests
import json
from tickerlist import tickers
import string
import plotly.express as px

#####################################################

# Define dropdowns and set page config

#####################################################

st.set_page_config(page_title="Investment Dashboard",
                   page_icon=":moneybag:",
                   layout="wide")

page_placeholder = st.sidebar.selectbox('What do you want to see?', [
                                        'Financial Statements', 'Dashboard', 'Charts'])

ticker_list_box = st.sidebar.selectbox(
    "Select a ticker symbol:", tickers, key="ticker_list")

company_statements = ['income-statement',
                      'cash-flow-statement', 'balance-sheet-statement']

#####################################################

# FInancial Statements Page

#####################################################

if page_placeholder == 'Financial Statements':

    st.write(f"""

    # {ticker_list_box}

    """)
    for i, x in enumerate(company_statements):
        if st.checkbox(f'Show {x}'):
            st.header(f'{x.capitalize()}')
            with open(f'D:\lianz\Desktop\Python\data_science_discovery\personal_finance\{x}\{ticker_list_box}.json', 'r') as f:
                statement = json.load(f)

            # year_selection = st.selectbox(
            #     "Select year:", range(len(statement)), format_func=lambda a: f"{statement[a]['calendarYear']}", key=f"year_selection{x}")

            year_range = st.slider('Select year range (past n years):',
                                   min_value=1,
                                   max_value=int(
                                       statement[0]['calendarYear'])-int(statement[-1]['calendarYear'])+1,
                                   key=f'{ticker_list_box}_{x}_{i}')

            year_list = list(range(year_range))

            st.checkbox("Use container width",
                        value=False,
                        key=f'use_container_width_{i}')

            st.dataframe(pd.DataFrame.from_records(
                statement[year_list[0]:year_list[-1]+1],
                index=[statement[i]['calendarYear'] for i in year_list]).T,
                use_container_width=bool(f'st.session_state.use_container_width_{x}'))


#####################################################

# Dashboard Page

#####################################################


#####################################################

# Charts Page

#####################################################

if page_placeholder == 'Charts':

    statement_selection = st.selectbox(
        "Select:", company_statements, format_func=lambda a: string.capwords(a.replace("-", " ")))

    st.write(statement_selection)

    with open(f'D:\lianz\Desktop\Python\data_science_discovery\personal_finance\{statement_selection}\{ticker_list_box}.json', 'r') as x:
        statement = json.load(x)

    st.title(f"""

    {ticker_list_box}

    """)
    if statement_selection == company_statements[0]:  # if income statement selected

        st.write(f"""
top right
            # EPS Growth (last {len(statement)} years)

            """)

        eps_dict = {}

        for i in statement[::-1]:
            eps_dict[i['date']] = i['epsdiluted']

        eps_df = pd.DataFrame.from_dict(
            eps_dict, orient='index', columns=['epsdiluted'])

        st.line_chart(eps_df)
        eps_df

        """
        Show eps by industry/sector: create lists containing ticker
                                    symbols belonging to an industry
                                    use the selectbox to select the lists.
        """
