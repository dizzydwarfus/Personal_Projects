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
import requests
from pymongo import MongoClient

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

with open('D:\lianz\Desktop\Python\personal_projects\personal_finance\mongodb_api.txt','r') as f:
    cluster = f.readlines()[0]
with open('D:\lianz\Desktop\Python\personal_projects\personal_finance\\fmp_api.txt','r') as f:
    fmp_api = f.readlines()[0]
    
client = MongoClient(cluster)

# print(client.list_database_names())

db = client.FinanceApp

balance_sheet_collection = db.balance_sheet
income_collection = db.income_statement
cash_collection = db.cash_flow_statement

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

def access_entry(collection_name, entry_name, entry_value, return_value):
    data = collection_name.find({entry_name:entry_value})

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
            return st.success(f"{x} {statement} updated!", icon="✅")
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
                return st.success(f"{x} {statement} updated!", icon="✅")
            except:
                return st.error(f"{ticker} {statement} already exists", icon="🚨")

            

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

