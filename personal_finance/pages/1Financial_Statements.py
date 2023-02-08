import pandas as pd
import streamlit as st
import json
import string
import numpy as np
from pymongo import MongoClient,ASCENDING, DESCENDING
from bson.objectid import ObjectId


with open('D:\lianz\Desktop\Python\personal_projects\personal_finance\mongodb_api.txt','r') as f:
    cluster = f.readlines()[0]
    
client = MongoClient(cluster)

# print(client.list_database_names())

db = client.FinanceApp

balance_sheet_collection = db.balance_sheet
income_collection = db.income_statement
cash_collection = db.cash_flow_statement
company_collection = db.company_profile

#####################################################

# Define dropdowns and set page config

#####################################################

tickers = list(set([i['symbol'] for i in balance_sheet_collection.find()]))

ticker_list_box = st.sidebar.selectbox(
    "Select a ticker symbol:", sorted(tickers), key="ticker_list")

company_statements = [income_collection,
                      cash_collection, balance_sheet_collection]

if tickers != None:
    income_statement = [i for i in income_collection.find({'symbol':ticker_list_box}).sort('date', DESCENDING)]
    cash_flow_statement = [i for i in cash_collection.find({'symbol':ticker_list_box}).sort('date', DESCENDING)]
    balance_sheet = [i for i in balance_sheet_collection.find({'symbol':ticker_list_box}).sort('date', DESCENDING)]


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

def read_statement(collection, ticker):
    
        statement = [i for i in collection.find({'symbol':ticker}).sort('date', DESCENDING)]

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

def make_pretty(styler, use_on):
    # styler.set_caption("Weather Conditions")
    # styler.format(rain_condition)
    # styler.format_index(lambda v: v.strftime("%A"))
    # styler.background_gradient(axis=None, vmin=1, vmax=5, cmap="YlGnBu")
    styler.applymap(lambda x: 'color:red;' if (x < 0 if type(x) != str else None) else None)
    # styler.highlight_min(color='indianred', axis=0)
    # styler.highlight_max(color='green', axis=0)
    if use_on == 'statements':
        styler.format(precision=0, na_rep='MISSING', thousands=' ',formatter={'grossProfitRatio': "{:.0%}",
                                                                                  'ebitdaratio': "{:.0%}",
                                                                                  'netIncomeRatio': "{:.0%}",
                                                                                  'operatingIncomeRatio': "{:.0%}",
                                                                                  'incomeBeforeTaxRatio': "{:.0%}",
                                                                                  'eps': "{:.2f}",
                                                                                  'epsdiluted': "{:.2f}"
                                                                                 })
    else:
        styler.format(na_rep='-',formatter='{:.0%}')

    return styler

income_tab, cash_tab, balance_tab, key_metrics_tab = st.tabs(
    ["Income Statement", "Cash Flow", "Balance Sheet", "Key Metrics"], )

for i, x in enumerate([income_tab, cash_tab, balance_tab]):
    with x:
        tab_statement = [j for j in company_statements[i].find({'symbol':ticker_list_box}).sort('date', DESCENDING)]

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
            index=[tab_statement[i]['calendarYear'] for i in year_list]).iloc[::-1,1:]
        df_financial_statements = df_financial_statements.style.pipe(make_pretty, use_on='statements')
                                                                      

        st.dataframe(df_financial_statements,
                        use_container_width=bool(f'st.session_state.use_container_width_income_tab'))

with key_metrics_tab:
    master_table = pd.concat([generate_key_metrics(read_statement(x,ticker_list_box), terms_interested.values()) for x in company_statements],axis=0).drop_duplicates()
    master_table = master_table.loc[~master_table.index.duplicated(keep='first'),:]
    mt_growth = master_table.T.pct_change(periods=1).style.pipe(make_pretty, use_on='metric')
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
