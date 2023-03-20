# from streamlit.source_util import (
#     page_icon_and_name,
#     calc_md5,
#     get_pages,
#     _on_pages_changed
# )

import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from pymongo import MongoClient, ASCENDING, DESCENDING
import datetime as dt

# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.cache_resource
def init_connection():
    return MongoClient(**st.secrets["mongo"])

# function to get api keys from secrets
@st.cache_resource
def get_api():
    fmp_api = st.secrets["fmp_api"]
    alpha_vantage_api = st.secrets["rapidapi_key"]
    return fmp_api,alpha_vantage_api

fmp_api, alpha_vantage_api = get_api()

# Initialize collection connection
@st.cache_resource(ttl=86400)  # only refresh after 24h
def get_data():
    client = init_connection()
    db = client.FinanceApp
    balance_sheet_collection = db.balance_sheet
    income_collection = db.income_statement
    cash_collection = db.cash_flow_statement
    company_profile = db.company_profile
    historical = db.historical
    stock_split = db.stock_split
    return balance_sheet_collection, income_collection, cash_collection, company_profile, historical, stock_split


balance_sheet_collection, income_collection, cash_collection, company_profile, historical, stock_split = get_data()

# with open('D:\lianz\Desktop\Python\personal_projects\\finance_dashboard\\mongodb_api.txt','r') as f:
#     cluster = f.readlines()[0]
# with open('D:\lianz\Desktop\Python\personal_projects\\finance_dashboard\\fmp_api.txt','r') as f:
#     fmp_api = f.readlines()[0]

# client = MongoClient(cluster)

# print(client.list_database_names())


# def delete_page(main_script_path_str, page_name):

#     current_pages = get_pages(main_script_path_str)
#     # st.write(current_pages)
#     for key, value in current_pages.items():
#         if value['page_name'] == page_name:
#             del current_pages[key]
#             break
#         else:
#             pass
#     _on_pages_changed.send()


# delete_page("D:\lianz\Desktop\Python\personal_projects\personal_finance\Ticker_List.py", "classes")


@st.cache_data
def get_tickers():
    tickers = list(set([i['symbol'] for i in balance_sheet_collection.find()]))
    return tickers


tickers = get_tickers()

company_statements = [income_collection,
                      cash_collection, balance_sheet_collection]

statements_type = ['Income Statement', 'Cash Flow Statement', 'Balance Sheet']


@st.cache_data
def generate_terms():
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
                        'Free Cash Flow per Share': 'freeCashFlowpershare',
                        'Working Capital': 'totalCurrentAssets - totalCurrentLiabilities',
                        'Net Debt': 'netDebt'
                        }
    return terms_interested


terms_interested = generate_terms()


@st.cache_data
def read_profile(ticker):

    statement = [i for i in company_profile.find(
        {'symbol': ticker}).sort('date', DESCENDING)]

    return statement


@st.cache_data
def read_statement(type_statement, ticker):

    if type_statement == 'Income Statement':
        statement = [i for i in income_collection.find(
            {'symbol': ticker}).sort('date', DESCENDING)]

    elif type_statement == 'Cash Flow Statement':
        statement = [i for i in cash_collection.find(
            {'symbol': ticker}).sort('date', DESCENDING)]

    else:
        statement = [i for i in balance_sheet_collection.find(
            {'symbol': ticker}).sort('date', DESCENDING)]

    return statement


# generate key metrics table
def generate_key_metrics(financial_statement, _list_of_metrics):
    l = []
    dict_holder = {}
    columns = financial_statement[0].keys()

    # loop over the list of interested columns (metrics)
    for n in _list_of_metrics:

        if n in columns:  # check if columns in interested list can be found in columns of financial statement
            # loop over the range of years
            for i, x in enumerate(financial_statement[::-1]):
                dict_holder[x['calendarYear']] = x[f'{n}']

            l.append(dict_holder)
            dict_holder = {}

        else:
            pass

    df = pd.DataFrame.from_records(
        l, index=[items for items in _list_of_metrics if items in columns])

    # df.style.format({f"{df}": "{:,}"})

    return df


# download company financial statements
def select_quote(ticker, statement):
    r = requests.get(
        f"https://financialmodelingprep.com/api/v3/{statement}/{ticker}?limit=120&apikey={fmp_api}")
    r = r.json()
    return r


# download company profile
def select_profile(ticker, statement):
    r = requests.get(
        f"https://financialmodelingprep.com/api/v3/{statement}/{ticker}?apikey={fmp_api}")
    r = r.json()
    return r


# download stock split
def download_stocksplit(ticker):
    r = requests.get(
        f"https://financialmodelingprep.com/api/v3/historical-price-full/stock_split/{ticker}?apikey={fmp_api}"
    )
    r = r.json()
    return r


# download stock price
def stock_price_api(ticker):
    url = "https://alpha-vantage.p.rapidapi.com/query"
    headers = {"X-RapidAPI-Key": alpha_vantage_api,
               "X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com"}
    querystring = {"function":"TIME_SERIES_DAILY","symbol":f"{ticker}","outputsize":"full","datatype":"json"}
    response = requests.request("GET", url=url, headers=headers, params=querystring)
    return response.json()


# Save the read file to json
def save_to_json(ticker_symbol, statement):

    file = select_quote(ticker_symbol, statement)

    with open(f'D:\lianz\Desktop\Python\personal_projects\personal_finance\{statement}/{ticker_symbol}.json', 'w+') as p:
        json.dump(file, p, indent=4)


# define index for each json
def define_id(json_file):
    for i in json_file:
        i['index_id'] = f"{i['symbol']}_{i['date']}"


# access entries in collection
def access_entry(_collection_name, entry_name, entry_value, return_value):
    data = _collection_name.find({entry_name: entry_value})

    data = [i[return_value] for i in data]

    return data


# Function to insert file to database
def insert_to_mongoDB(collection, ticker, statement, second_key):
    if statement == 'profile':
        file = select_profile(ticker, statement)
        file[0]['index_id'] = f"{file[0]['symbol']}_{file[0][second_key]}"

        if st.session_state['profile_update']:
            collection.delete_one({'symbol': ticker})
        try:
            collection.insert_one(file[0])
            return st.success(f"{ticker} {statement} updated!", icon="✅")
        except:
            return st.error(f"{ticker} {statement} already exists", icon="🚨")
    elif statement == 'stock_price':
        file = stock_price_api(ticker)
        for i,x in file['Time Series (Daily)'].items():    
            x['index_id'] = f"{ticker}_{i}"
            x['symbol'] = f"{ticker}"
            x[second_key] = dt.datetime.strptime(i, '%Y-%m-%d')
            x['open'] = x['1. open']
            x['high'] = x['2. high']
            x['low'] = x['3. low']
            x['close'] = x['4. close']
            x['volume'] = x['5. volume']
            x.pop('1. open')
            x.pop('2. high')
            x.pop('3. low')
            x.pop('4. close')
            x.pop('5. volume')

        ids = [x['index_id'] for i,x in file['Time Series (Daily)'].items() if x['index_id']
                   not in access_entry(collection, 'symbol', ticker, 'index_id')]
        try:
            collection.insert_many([x for i,x in file['Time Series (Daily)'].items() if x['index_id'] in ids])
            return st.success(f"{ticker} {statement} updated!", icon="✅")

        except:
            return st.error(f"{ticker} {statement} already exists", icon="🚨")
    
    elif statement == 'stock_split':
        file = download_stocksplit(ticker)
        for i in file['historical']:
            i['index_id'] = f"{file['symbol']}_{i[second_key]}"
            i['symbol'] = f"{file['symbol']}"
            i[second_key] = dt.datetime.strptime(i['date'], '%Y-%m-%d')
            

        ids = [i['index_id'] for i in file['historical'] if i['index_id'] not in access_entry(collection, 'symbol', ticker, 'index_id')]

        try:
            collection.insert_many([i for i in file['historical'] if i['index_id'] in ids])
            return st.success(f"{ticker} {statement} updated!", icon="✅")

        except:
            return st.error(f"{ticker} {statement} already exists", icon="🚨")
    else:
        file = select_quote(ticker, statement)

        if len(file) <= 1:
            pass
        else:
            for i in file:
                i['index_id'] = f"{i['symbol']}_{i[second_key]}"

            ids = [i['index_id'] for i in file if i['index_id']
                   not in access_entry(collection, 'symbol', ticker, 'index_id')]

            try:
                collection.insert_many(
                    [i for i in file if i['index_id'] in ids])
                return st.success(f"{ticker} {statement} updated!", icon="✅")
            except:
                return st.error(f"{ticker} {statement} already exists", icon="🚨")


# function to generate growth over time plots
@st.cache_data
def generate_plots(dataframe, arrangement: tuple, metric):

    # create columns to place charts based on arrangement specified (columns in each row)
    cols = st.columns(arrangement)
    dataframe = dataframe.T
    metric2 = [terms_interested[i] for i in metric]
    m = 0

    for i, n in enumerate(metric2):
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
                              #   template='plotly_dark',
                              paper_bgcolor='#1c2541',
                              plot_bgcolor="#0b132b",
                              xaxis_title='Year',
                              #   yaxis_title=f'{n}',
                              title={'text': f'<b>{metric[i].capitalize()}</b> (last {len(dataframe)} years)',
                                     'x': 0.5,
                                     'xanchor': 'center',
                                     'font': {'size': 25}},
                              font={'size': 15})
            fig.update_yaxes(showgrid=False, zeroline=True, secondary_y=False)
            fig.update_yaxes(
                title_text="Growth Y-o-Y", secondary_y=True, showgrid=False, zeroline=False)

            # # Add horizontal lines to show max and min values
            # fig.add_hline(y=dataframe[f'{n}'].max(
            # ), line_color='green', line_dash='dash')
            # fig.add_hline(y=dataframe[f'{n}'].min(
            # ), line_color='red', line_dash='dash')

            # Plot the chart in its respective column based on loop
            cols[m].plotly_chart(
                fig, use_container_width=True,)


# generate plots for historical price
@st.cache_data
def historical_plots(dataframe, arrangement, date):
    cols = st.columns(arrangement)
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces (graphs)
    fig.add_trace(
        go.Candlestick(
            x=dataframe.loc[(dataframe.index.date >= date[0]) & (dataframe.index.date < date[-1])].index, open=dataframe[f'1. open'], high=dataframe['2. high'], low=dataframe['3. low'], close=dataframe[f'4. close']),
        secondary_y=False,
    )

    fig.add_trace(
        go.Bar(
            x=dataframe.loc[(dataframe.index.date >= date[0]) & (dataframe.index.date < date[-1])].index, y=dataframe['5. volume'], opacity=0.2, marker=dict({'color': 'darkorange'}), textposition="inside", name="Daily Volume"),
        secondary_y=True,
    )
    try:
        for i in stock_split.find({'symbol':dataframe['symbol'][0]}):
            fig.add_shape(type="line",
                    x0=i['date'], x1=i['date'], y0=dataframe['4. close'].max(), y1=dataframe['4. close'].max(),
                    line=dict(color="RoyalBlue",width=3)
            )
    except:
        pass

    # Update figure title, legend, axes
    fig.update_layout(height=1000,
                      showlegend=False,
                        #   template='plotly_dark',
                        # paper_bgcolor='#1c2541',
                        # plot_bgcolor="#0b132b",
                        # xaxis_title='Date',
                        #   yaxis_title=f'{n}',
                        title={'text': f'<b>{dataframe["symbol"][0]} price</b> (from {date[0]}-{date[-1]})',
                                'x': 0.5,
                                'xanchor': 'center',
                                'font': {'size': 25}},
                        font={'size': 15})
    fig.update_yaxes(showgrid=False, zeroline=True, secondary_y=False)
    fig.update_yaxes(
        title_text="Daily Volume", secondary_y=True, showgrid=False, zeroline=False)
    
    cols[0].plotly_chart(
        fig, use_container_width=True,)


# function to format pandas dataframe
def make_pretty(styler, use_on=None):
    # styler.set_caption("Weather Conditions")
    # styler.format(rain_condition)
    # styler.format_index(lambda v: v.strftime("%A"))
    # styler.background_gradient(axis=None, vmin=1, vmax=5, cmap="YlGnBu")
    if use_on == None:
        styler.format(precision=0, na_rep='MISSING', thousands=' ', subset=pd.IndexSlice[[
                      'revenue', 'operatingIncome', 'netIncome', 'weightedAverageShsOutDil', 'operatingCashFlow', 'netDebt', 'capitalExpenditure', 'freeCashFlow', 'dividendsPaid'], :])
        styler.format(precision=0, na_rep='MISSING', thousands=' ')
        styler.format(precision=2, na_rep='MISSING', thousands=' ', subset=pd.IndexSlice[[
                      'grossProfitRatio', 'netIncomeRatio', 'operatingIncomeRatio', 'epsdiluted'], :])
        styler.applymap(lambda x: 'color:red;' if (
            x < 0 if type(x) != str else None) else None)
    # styler.highlight_min(color='indianred', axis=0)
    # styler.highlight_max(color='green', axis=0)
    elif use_on == 'statements':
        styler.format(precision=0, na_rep='MISSING', thousands=' ', formatter={'grossProfitRatio': "{:.0%}",
                                                                               'ebitdaratio': "{:.0%}",
                                                                               'netIncomeRatio': "{:.0%}",
                                                                               'operatingIncomeRatio': "{:.0%}",
                                                                               'incomeBeforeTaxRatio': "{:.0%}",
                                                                               'eps': "{:.2f}",
                                                                               'epsdiluted': "{:.2f}"
                                                                               })
    else:
        styler.format(na_rep='-', formatter='{:.0%}')
        styler.applymap(lambda x: 'color:red;' if (
            x < 0 if type(x) != str else None) else None)

    return styler


# function to create financial_statements page
def create_financial_page(ticker, company_profile_info, col3, p: list):

    p[0].markdown(
        f"""<span style='font-size:1.5em;'>CEO</span>  
    :green[{company_profile_info['ceo']}]

    """, unsafe_allow_html=True)

    p[1].markdown(
        f"""<span style='font-size:1.5em;'>Exchange</span>  
    :green[{company_profile_info['exchangeShortName']}]

    """, unsafe_allow_html=True)

    p[2].markdown(
        f"""<span style='font-size:1.5em;'>Industry</span>  
    :green[{company_profile_info['industry']}]

    """, unsafe_allow_html=True)

    p[0].markdown(
        f"""<span style='font-size:1.5em;'>Country</span>  
    :green[{company_profile_info['country']}]

    """, unsafe_allow_html=True)

    p[1].markdown(
        f"""<span style='font-size:1.5em;'>Number of Employees</span>  
    :green[{int(company_profile_info['fullTimeEmployees']):,}]

    """, unsafe_allow_html=True)

    p[2].markdown(
        f"""<span style='font-size:1.5em;'>Sector</span>  
    :green[{company_profile_info['sector']}]

    """, unsafe_allow_html=True)

    historical_tab, income_tab, cash_tab, balance_tab, key_metrics_tab, charts_tab = col3.tabs(
        ["Historical", "Income Statement", "Cash Flow", "Balance Sheet", "Key Metrics", "Charts"], )

    for i, x in enumerate([income_tab, cash_tab, balance_tab]):
        with x:
            col3.write(f"### {statements_type[i]}")
            tab_statement = read_statement(statements_type[i], ticker)

            year_range = col3.slider('Select year range (past n years):',
                                     min_value=1,
                                     max_value=int(
                                         tab_statement[0]['calendarYear'])-int(tab_statement[-1]['calendarYear'])+1,
                                     key=f'{ticker}_{x}_{i}')

            year_list = list(range(year_range))

            # col3.checkbox("Use container width",
            #             value=False,
            #             key=f'use_container_width_{x}_{i}')

            df_financial_statements = pd.DataFrame.from_records(
                tab_statement[year_list[0]:year_list[-1]+1],
                index=[tab_statement[i]['calendarYear'] for i in year_list]).iloc[::-1, 9:]
            df_financial_statements = df_financial_statements.style.pipe(
                make_pretty, use_on='statements')

            col3.dataframe(df_financial_statements,
                           use_container_width=bool(f'st.session_state.use_container_width_income_tab'))

    with key_metrics_tab:
        master_table_unformatted = pd.concat([generate_key_metrics(read_statement(
            x, ticker), terms_interested.values()) for x in statements_type], axis=0).drop_duplicates()
        master_table_unformatted = master_table_unformatted.loc[~master_table_unformatted.index.duplicated(
            keep='first'), :]
        mt_growth = master_table_unformatted.T.pct_change(
            periods=1).T.style.pipe(make_pretty, use_on='metric')
        master_table_formatted = master_table_unformatted.style.pipe(
            make_pretty)

        # st.metric(label=f'{mt_growth.columns[0]}', value=mt_growth.iloc[:,0].mean(skipna=True)/len(mt_growth.index), delta=mt_growth.iloc[-1,0])

        # To create the master key metrics table compiled from statements
        col3.dataframe(master_table_formatted)
        col3.write("##### Y-o-Y Growth Table")
        col3.dataframe(mt_growth)

    with charts_tab:
        chart_select = st.multiselect(
            '*Select charts to show:*', terms_interested.keys(), key=f'{ticker}_multiselect')
        generate_plots(master_table_unformatted, [1], chart_select)

    with historical_tab:
        df_historical = pd.DataFrame.from_records([x for i,x in enumerate(historical.find({'symbol':ticker}))], index='date').sort_index()
        date_select = st.slider("Select date range:", min_value=df_historical.index.date[0], max_value=df_historical.index.date[-1], value=(df_historical.index.date[-365],df_historical.index.date[-1]))
        historical_plots(df_historical, [1], date_select)