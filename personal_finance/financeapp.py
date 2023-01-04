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
                                        'Financial Statements', 'DCF Calculator', 'Charts'])

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

# DCF Calculator

#####################################################
if page_placeholder == 'DCF Calculator':
    st.title("DCF Calculator")

    st.write("""

    - show current growth rates (considering past 5 years)
    - show current stock price
    - use input fields for discount rate, growth rate, and terminal multiple
    - discount rate: use WACC, or expected return rate, or 10Y treasury yield
    - choose either growth on dividend (for slow growth), eps, or free cash flow
    - terminal multiple: what is the projected PE ratio 10 years from now?

    """)


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

        st.bar_chart(eps_df)
        eps_df

        """
        Show eps by industry/sector: create lists containing ticker
                                    symbols belonging to an industry
                                    use the selectbox to select the lists.
        """

    st.write("""

         Metrics to be shown (margin of safety):
         ---

         1. revenue
         2. gross margin%
         3. operating income
         4. operating margin%
         5. net income
         6. earnings per share
         7. dividends
         8. payout ratio%
         9. shares oustanding
         10. book value per share
         11. operating cash flow
         12. cap spending
         13. free cash flow
         14. free cash flow per share
         15. working capital
         16. 

         Keypoint
         : range of value: not exactly, value is adequate, approximate measure of intrinsic value may be sufficient(e.g. elon's twitter acquisition, "order of magnitude more valuable than current even if he is overpaying now").

         """)
    todos = [
        'net present value',
        'private market value - conservative historical value',
        'personal value - how much you would pay personally based on assets for the business',
        'liquidation value - best for unprofitable businesses trading below book value',
        'Stock market value - compare similar businesses (potential spin-off)',
        'Reflexivity - how rising stock prices influence underlying values (raising capital when stock prices are high)'
    ]

    for items in todos:
        st.checkbox(f"{items}")
