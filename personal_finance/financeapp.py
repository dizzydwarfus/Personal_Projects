import pandas as pd
import streamlit as st
import datetime as dt
import requests
import json
from tickerlist import tickers

#####################################################

# Define dropdowns and conditions

#####################################################

page_placeholder = st.sidebar.selectbox('What do you want to see?', [
                                        'Financial Statements', 'Dashboard', 'Charts'])

ticker_list_box = st.sidebar.selectbox("Select a ticker symbol:", tickers)

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

            year_selection = st.selectbox(
                "Select year:", range(len(statement)), format_func=lambda x: f"{statement[x]['calendarYear']}")

            st.write(statement[year_selection])


#####################################################

# Dashboard Page

#####################################################


#####################################################

# Charts Page

#####################################################

if page_placeholder == 'Charts':
    st.title(f"""

    {ticker_list_box}

    """)

    st.write(f"""
    
    ## Cash Flow (last 5 years)

    """)
    with open(f'D:\lianz\Desktop\Python\data_science_discovery\personal_finance\{company_statements[1]}\{ticker_list_box}.json', 'r') as f:
        statement = json.load(f)

    year_range = st.slider('View years:', min_value=int(
        statement[-1]['calendarYear']), max_value=int(statement[0]['calendarYear']))

    cash_chart = pd.DataFrame.from_dict(statement[0])

    st.line_chart(cash_chart)
    st.write(year_range)


#####################################################

# Transactions Dataframe

#####################################################

# st.write("""

# ## Transactions Log

# All transactions downloaded from banking website.

# Categories of each transactions are categorized using *classification* algorithm.

# """)

# df = pd.read_csv("D:\lianz\Desktop\Python\data_science_discovery\personal_finance\expenses.csv",
#                  sep=',', parse_dates=['Datum'])
# df['Datum'] = df['Datum'].dt.date

# df_checkbox = st.checkbox(label="Show Transactions Log",
#                           key='df_checkbox', value=True)
# if df_checkbox:
#     st.dataframe(df)
