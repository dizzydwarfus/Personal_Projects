import pandas as pd
import streamlit as st
import json
import string
import numpy as np
from pymongo import MongoClient
from bson.objectid import ObjectId


with open('D:\lianz\Desktop\Python\personal_projects\personal_finance\mongodb_api.txt','r') as f:
    cluster = f.readlines()[0]
    
client = MongoClient(cluster)

# print(client.list_database_names())

db = client.FinanceApp

balance_sheet_collection = db.balance_sheet
income_collection = db.income_statement
cash_collection = db.cash_flow_statement

#####################################################

# Define dropdowns and set page config

#####################################################

tickers = list(set([i['symbol'] for i in balance_sheet_collection.find()]))

ticker_list_box = st.sidebar.selectbox(
    "Select a ticker symbol:", sorted(tickers), key="ticker_list")

company_statements = ['income-statement',
                      'cash-flow-statement', 'balance-sheet-statement']

if tickers != None:   
    with open(f'D:\lianz\Desktop\Python\\personal_projects\personal_finance\{company_statements[0]}\{ticker_list_box}.json', 'r') as f:
        income_statement = json.load(f)

    with open(f'D:\lianz\Desktop\Python\\personal_projects\personal_finance\{company_statements[1]}\{ticker_list_box}.json', 'r') as f:
        cash_flow_statement = json.load(f)

    with open(f'D:\lianz\Desktop\Python\\personal_projects\personal_finance\{company_statements[2]}\{ticker_list_box}.json', 'r') as f:
        balance_sheet = json.load(f)


#####################################################

# Define functions to create dictionaries for
# historical data

#####################################################

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
                    'Free Cash Flow per Share': 'freeCashFlow / shares outstanding',
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


#####################################################

# FInancial Statements Page

#####################################################
st.write(f"""

# {ticker_list_box}

""")

income_tab, cash_tab, balance_tab, key_metrics_tab = st.tabs(
    ["Income Statement", "Cash Flow", "Balance Sheet", "Key Metrics"], )

for i, x in enumerate([income_tab, cash_tab, balance_tab]):
    with x:
        with open(f'D:\lianz\Desktop\Python\\personal_projects\personal_finance\{company_statements[i]}\{ticker_list_box}.json', 'r') as f:
            tab_statement = json.load(f)

        year_range = st.slider('Select year range (past n years):',
                                min_value=1,
                                max_value=int(
                                    tab_statement[0]['calendarYear'])-int(tab_statement[-1]['calendarYear'])+1,
                                key=f'{ticker_list_box}_{x}_{i}')

        year_list = list(range(year_range))

        st.checkbox("Use container width",
                    value=False,
                    key=f'use_container_width_{x}_{i}')

        df_financial_statements = pd.DataFrame.from_records(
            tab_statement[year_list[0]:year_list[-1]+1],
            index=[tab_statement[i]['calendarYear'] for i in year_list]).T

        st.dataframe(df_financial_statements,
                        use_container_width=bool(f'st.session_state.use_container_width_income_tab'))

with key_metrics_tab:
    master_table = pd.concat([generate_key_metrics(read_statement(f'D:\lianz\Desktop\Python\\personal_projects\personal_finance\{x}\{ticker_list_box}.json','r'), terms_interested.values()) for x in company_statements],axis=0).drop_duplicates()
    mt_growth = master_table.T.pct_change(periods=1)
    # mt_growth.apply(lambda x: "{:.0%}".format(x))

    st.dataframe(mt_growth)

    # Container to show some key metrics from table
    metric_container = st.container()
    metric_columns = st.columns([1,1,1,1,1])

    # st.metric(label=f'{mt_growth.columns[0]}', value=mt_growth.iloc[:,0].mean(skipna=True)/len(mt_growth.index), delta=mt_growth.iloc[-1,0])

    # To create the master key metrics table compiled from statements
    st.dataframe(master_table)

    
# TODO: create function to combine all three statements so generate_key_metrics can be used on a single object instead of multiple filepaths

#####################################################

# DCF Calculator

#####################################################


# st.title("DCF Calculator")

# st.write("""

# - show current growth rates (considering past 5 years)
# - show current stock price
# - use input fields for discount rate, growth rate, and terminal multiple
# - discount rate: use WACC, or expected return rate, or 10Y treasury yield
# - choose either growth on dividend (for slow growth), eps, or free cash flow
# - terminal multiple: what is the projected PE ratio 10 years from now?

# """)
# c1, c2, c3 = st.columns([1, 1, 1])

# # c2.metric(label=f'EPS Growth (1Y)',
# #           value=f'{sum(df(income_statement))}',
# #           delta='0.5%')

# todos = [
#     'net present value',
#     'private market value - conservative historical value',
#     'personal value - how much you would pay personally based on assets for the business',
#     'liquidation value - best for unprofitable businesses trading below book value',
#     'Stock market value - compare similar businesses (potential spin-off)',
#     'Reflexivity - how rising stock prices influence underlying values (raising capital when stock prices are high)'
# ]

# for items in todos:
#     st.checkbox(f"{items}")


st.markdown("***Data provided by Financial Modeling Prep***")
