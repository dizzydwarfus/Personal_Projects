import pandas as pd
import json
import streamlit as st
import requests
from pymongo import MongoClient,ASCENDING, DESCENDING
from functions import balance_sheet_collection, income_collection, cash_collection, company_profile, terms_interested, company_statements, read_statement, generate_key_metrics, create_financial_page

# replace filepath with fmp API link
# with open('D:\lianz\Desktop\Python\personal_projects\\finance_dashboard\\fmp_api.txt','r') as f:
#     fmp_api = f.readlines()[0]

fmp_api = 'eb29218df82acef0486b5c014ccec868'

#####################################################

# Set page config

#####################################################

st.set_page_config(page_title="Investment Dashboard",
                   page_icon=":moneybag:",
                   layout="wide")

#####################################################

# Generate Ticker List and Download Statements

#####################################################
st.markdown(
    """

# Generate Financial Statements

---

##### Step 1: Please provide a list of ticker symbols to generate financial overview for:

""")


col1, col2 = st.columns([1, 1])

etoro_list = col1.file_uploader(
    "Upload your file here :file_folder:", key='uploaded_file', label_visibility="hidden")

manual_list = list(set(col2.text_area(
    "Type your tickers here:", label_visibility="visible").split("\n")))

tickers = []

cont1 = st.container()
col3, col4, col5, col6, col7, col8, col9 = cont1.columns([0.5,0.5,1,1,1,0.5,0.5])

cont2 = st.container()

# Append etoro tickers to list: tickers
if etoro_list is not None:

    investment_history = pd.read_excel(
        etoro_list, sheet_name='Account Activity')

    tickers.extend(list(investment_history[investment_history['Asset type']
                                           == 'Stocks']['Details'].str.split('/', expand=True)[0].unique()))
    # col1.write(tickers)

# Append manual entries to list: tickers
if manual_list != "" and manual_list not in tickers:
    tickers.extend(manual_list)
    # col2.write(tickers)

# def is_non_zero_file(fpath):
#     return os.path.isfile(fpath) and os.path.getsize(fpath) > 0


# def no_file(fpath):
#     return not os.path.isfile(fpath) or os.path.getsize(fpath) == 0


# st.write(st.session_state)

# Check list of tickers in database instead of locally
balance_list = list(set([i['symbol'] for i in balance_sheet_collection.find()]))
income_list = list(set([i['symbol'] for i in income_collection.find()]))
cash_list = list(set([i['symbol'] for i in cash_collection.find()]))
company_list = list(set([i['symbol'] for i in company_profile.find()]))
list_tickers = ['balance_list', 'income_list', 'cash_list', 'company_list','manual_list']

list_tickers = col3.selectbox("*Choose a list to scan/download*:",list_tickers, key="select_ticker_list")
ticker_list_json = json.dumps(eval(list_tickers), indent=2)
missing_tickers = [i for i in tickers if i not in eval(list_tickers)]



st.session_state['balance_list'] = balance_list
st.session_state['income_list'] = income_list
st.session_state['cash_list'] = cash_list
st.session_state['company_list'] = company_list
st.session_state['tickers'] = tickers
st.session_state['missing_tickers'] = missing_tickers

# Show tickers in database
if col4.button("Show Scanned Ticker List", key='show_scanned'):
    col3.write("###### *Tickers in Database:*")
    col3.write(eval(list_tickers))

# Download tickers list in database

col4.download_button(
    label="Download Ticker List as JSON file",
    data=ticker_list_json,
    file_name='tickers.json',
    mime="application/json"
)


# Show current session list
if col5.button("Show Current list", key="show_current"):
    col5.write("###### *Tickers in current session:*")
    col5.write(tickers)

# Show tickers not in database
if col6.button("Show Missing Tickers List", key="show_missing"):
    col6.write("###### *Tickers not in database:*")
    col6.write(missing_tickers)

if col7.button("Overwrite Ticker List", key="overwrite_ticker"):
    col7.write("###### *Ticker List to be downloaded:*")
    col7.write(manual_list)

def change_state():
    if st.session_state['show_all']:
        show_bal_list = col3.write(f"Balance sheet: {len(st.session_state['balance_list'])}")
        show_income_list = col3.write(f"Income statement: {len(st.session_state['income_list'])}")
        show_cash_list = col3.write(f"Cash flow: {len(st.session_state['cash_list'])}")
        show_company_list = col3.write(f"Company profile: {len(st.session_state['company_list'])}")
        show_ticks = col5.write(st.session_state['tickers'])
        show_missing = col6.write(st.session_state['missing_tickers'])
    
    elif st.session_state['hide_all']:
        pass

col8.button("Show All", key='show_all', on_click=change_state)
col9.button("Hide All", key="hide_all")


#####################################################

# Download Statements to Local Machine

#####################################################

# Read from financialmodelingAPI
def select_quote(ticker, statement):
    r = requests.get(
        f"https://financialmodelingprep.com/api/v3/{statement}/{ticker}?limit=120&apikey={fmp_api}")
    r = r.json()
    return r
def select_profile(ticker, statement):
    r = requests.get(
        f"https://financialmodelingprep.com/api/v3/{statement}/{ticker}?apikey={fmp_api}")
    r = r.json()
    return r
# Save the read file to json


def save_to_json(ticker_symbol, statement):

    file = select_quote(ticker_symbol, statement)

    with open(f'D:\lianz\Desktop\Python\personal_projects\personal_finance\{statement}/{ticker_symbol}.json', 'w+') as p:
        json.dump(file, p, indent=4)


possible_statements = ['income-statement',
                       'balance-sheet-statement', 'cash-flow-statement']



st.write(
    """

---


##### Step 2: *Click this button to download files to mongoDB*

""")


# Function for creating id in each json file
def define_id(json_file, second_key):
    for i in json_file:
        i['index_id'] = f"{i['symbol']}_{i[second_key]}"

# Functino for accessing specific entry in mongodb
def access_entry(collection_name, entry_name, entry_value, return_value):
    data = collection_name.find({entry_name:entry_value})

    data = [f"{i[return_value]}" for i in data]

    return data

cont3 = st.container()
col10, col11, col12, col13 = cont3.columns([0.3,0.3,0.3,1.5])


profile_update = col10.checkbox("Enable company profile update", key='profile_update')
manual_download = col11.checkbox("Enable manual download of all statements", key='update_list')

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


if st.button("Download Statements :ledger:"):
    if manual_download:
        for i,x in enumerate(eval(list_tickers)):
            
            insert_to_mongoDB(income_collection, x, 'income-statement', 'date')
            insert_to_mongoDB(balance_sheet_collection, x, 'balance-sheet-statement', 'date')
            insert_to_mongoDB(cash_collection, x, 'cash-flow-statement', 'date')
            insert_to_mongoDB(company_profile, x, 'profile', 'ipoDate')

            # current += step

            # progress_bar.progress(current)

            if i == len(eval(list_tickers))-1:
                st.success(f"All downloads are completed.", icon="💯")

    elif profile_update:
        for i,x in enumerate(eval(list_tickers)):
            insert_to_mongoDB(company_profile, x, 'profile', 'ipoDate')
    
        if i == len(eval(list_tickers))-1:
            st.success(f"All downloads are completed.", icon="💯")

    else:
        for i,x in enumerate(missing_tickers):
            
            insert_to_mongoDB(income_collection, x, 'income-statement', 'date')
            insert_to_mongoDB(balance_sheet_collection, x, 'balance-sheet-statement', 'date')
            insert_to_mongoDB(cash_collection, x, 'cash-flow-statement', 'date')
            insert_to_mongoDB(company_profile, x, 'profile', 'ipoDate')

            # current += step

            # progress_bar.progress(current)

            if i == len(missing_tickers)-1:
                st.success(f"All downloads are completed.", icon="💯")

# st.write(st.session_state)
