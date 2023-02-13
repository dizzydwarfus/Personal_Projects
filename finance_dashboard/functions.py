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

# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.cache_resource
def init_connection():
    return MongoClient(**st.secrets["mongo"])

@st.cache_resource(ttl=86400) # only refresh after 24h
def get_data():
    client = init_connection()
    db = client.FinanceApp
    balance_sheet_collection = db.balance_sheet
    income_collection = db.income_statement
    cash_collection = db.cash_flow_statement
    company_profile = db.company_profile
    return balance_sheet_collection,income_collection,cash_collection,company_profile

balance_sheet_collection,income_collection,cash_collection,company_profile = get_data()

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
    
        statement = [i for i in company_profile.find({'symbol':ticker}).sort('date', DESCENDING)]

        return statement

@st.cache_data
def read_statement(type_statement, ticker):

        if type_statement == 'Income Statement':
            statement = [i for i in income_collection.find({'symbol':ticker}).sort('date', DESCENDING)]
        
        elif type_statement == 'Cash Flow Statement':
            statement = [i for i in cash_collection.find({'symbol':ticker}).sort('date', DESCENDING)]

        else:
            statement = [i for i in balance_sheet_collection.find({'symbol':ticker}).sort('date', DESCENDING)]

        return statement


def generate_key_metrics(financial_statement, _list_of_metrics):
    l = []
    dict_holder = {}
    columns = financial_statement[0].keys()

    for n in _list_of_metrics: # loop over the list of interested columns (metrics)

        if n in columns: # check if columns in interested list can be found in columns of financial statement
            for i, x in enumerate(financial_statement[::-1]): # loop over the range of years
                dict_holder[x['calendarYear']] = x[f'{n}']

            l.append(dict_holder)
            dict_holder = {}

        else:
            pass

    df = pd.DataFrame.from_records(
        l, index=[items for items in _list_of_metrics if items in columns])

    # df.style.format({f"{df}": "{:,}"})

    return df

def select_quote(ticker, statement):
    r = requests.get(
        f"https://financialmodelingprep.com/api/v3/{statement}/{ticker}?limit=120&apikey={fmp_api}")
    r = r.json()
    return r

def select_profile(ticker, statement):
    r = requests.get(
        f"https://financialmodelingprep.com/api/v3/{statement}/{ticker}?apikey={fmp_api}")

def save_to_json(ticker_symbol, statement):

    file = select_quote(ticker_symbol, statement)

    with open(f'D:\lianz\Desktop\Python\personal_projects\personal_finance\{statement}/{ticker_symbol}.json', 'w+') as p:
        json.dump(file, p, indent=4)
        

def define_id(json_file):
    for i in json_file:
        i['index_id'] = f"{i['symbol']}_{i['date']}"

def access_entry(_collection_name, entry_name, entry_value, return_value):
    data = _collection_name.find({entry_name:entry_value})

    data = [i[return_value] for i in data]

    return data

# Function to insert file to database
def insert_to_mongoDB(collection, ticker, statement, second_key):
    if statement == 'profile':
        file = select_profile(ticker, statement)
        file[0]['index_id'] = f"{file[0]['symbol']}_{file[0][second_key]}"
        
        if profile_update:
            collection.delete_one({'symbol':ticker})
        try:
            collection.insert_one(file[0])
            return st.success(f"{ticker} {statement} updated!", icon="✅")
        except:
            return st.error(f"{ticker} {statement} already exists", icon="🚨")
    else:
        if manual_update:
            collection.delete_many({})
        
        file = select_quote(ticker, statement)
        
        if len(file) <= 1:
            pass
        else:
            for i in file:
                i['index_id'] = f"{i['symbol']}_{i[second_key]}"
            
            ids = [i['index_id'] for i in file if i['index_id'] not in access_entry(collection,'symbol',ticker,'index_id')]

            try:
                collection.insert_many([i for i in file if i['index_id'] in ids])
                return st.success(f"{ticker} {statement} updated!", icon="✅")
            except:
                return st.error(f"{ticker} {statement} already exists", icon="🚨")

            
@st.cache_data
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

def make_pretty(styler, use_on=None):
    # styler.set_caption("Weather Conditions")
    # styler.format(rain_condition)
    # styler.format_index(lambda v: v.strftime("%A"))
    # styler.background_gradient(axis=None, vmin=1, vmax=5, cmap="YlGnBu")
    if use_on == None:
        styler.format(precision=2, na_rep='MISSING', thousands=' ', subset=pd.IndexSlice[['grossProfitRatio','netIncomeRatio', 'operatingIncomeRatio', 'epsdiluted'],:])
        styler.format(precision=0, na_rep='MISSING', thousands=' ', subset=pd.IndexSlice[['revenue', 'operatingIncome', 'netIncome', 'weightedAverageShsOutDil', 'operatingCashFlow', 'netDebt', 'capitalExpenditure', 'freeCashFlow', 'dividendsPaid'],:])
        styler.format(precision=0, na_rep='MISSING', thousands=' ')
        styler.applymap(lambda x: 'color:red;' if (x < 0 if type(x) != str else None) else None)
    # styler.highlight_min(color='indianred', axis=0)
    # styler.highlight_max(color='green', axis=0)
    elif use_on == 'statements':
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
        styler.applymap(lambda x: 'color:red;' if (x < 0 if type(x) != str else None) else None)

    return styler


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



    income_tab, cash_tab, balance_tab, key_metrics_tab = col3.tabs(
        ["Income Statement", "Cash Flow", "Balance Sheet", "Key Metrics"], )


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
                index=[tab_statement[i]['calendarYear'] for i in year_list]).iloc[::-1,1:]
            df_financial_statements = df_financial_statements.style.pipe(make_pretty, use_on='statements')

            col3.dataframe(df_financial_statements,
                            use_container_width=bool(f'st.session_state.use_container_width_income_tab'))

    with key_metrics_tab:
        master_table = pd.concat([generate_key_metrics(read_statement(x,ticker), terms_interested.values()) for x in statements_type],axis=0).drop_duplicates()
        master_table = master_table.loc[~master_table.index.duplicated(keep='first'),:]
        mt_growth = master_table.T.pct_change(periods=1).style.pipe(make_pretty, use_on='metric')
        master_table = master_table.style.pipe(make_pretty)
        col3.dataframe(mt_growth)

        # st.metric(label=f'{mt_growth.columns[0]}', value=mt_growth.iloc[:,0].mean(skipna=True)/len(mt_growth.index), delta=mt_growth.iloc[-1,0])

        # To create the master key metrics table compiled from statements
        col3.dataframe(master_table)