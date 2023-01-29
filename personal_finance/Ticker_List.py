import pandas as pd
import openpyxl
import json
import streamlit as st
from io import StringIO
import requests
import pathlib
import time
import os

#####################################################

# Set page config

#####################################################

st.set_page_config(page_title="Investment Dashboard",
                   page_icon=":moneybag:",
                   layout="wide")

#####################################################

# Generate Ticker List

#####################################################
st.markdown(
    """

# Generate Ticker List

---

##### Step 1: Please provide a list of ticker symbols to generate financial overview for:

""")

col1, col2 = st.columns([1, 1])

etoro_list = col1.file_uploader(
    "Upload your file here :file_folder:", key='uploaded_file', label_visibility="hidden")

manual_list = col2.text_area(
    "Type your tickers here:", label_visibility="visible")

tickers = []

cont1 = st.container()
col3, col4, col5 = cont1.columns([3, 2.5, 6])

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
    tickers.extend(manual_list.split("\n"))
    # col2.write(tickers)

# Load saved ticker file


def is_non_zero_file(fpath):
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0


def no_file(fpath):
    return not os.path.isfile(fpath) or os.path.getsize(fpath) == 0


file = r'D:\\lianz\Desktop\\Python\\personal_projects\\personal_finance\\tickers.json'

# st.write(st.session_state)

# Creating the first-time list
if no_file(file):
    with open(file, 'w') as f:
        json.dump(tickers, f, indent=2)

balance_sheet_filepath = 'D:\lianz\Desktop\Python\personal_projects\personal_finance\\balance-sheet-statement'
list_tickers = [i.split('.')[0] for i in os.listdir(balance_sheet_filepath)]

if st.button("Show Scanned Ticker List", key='scan_tickers'):
    cont2.write("###### *Scanned Ticker List:*")
    cont2.write(list_tickers)

if is_non_zero_file(file):
    ticker_file_read = open(file, 'r+')

    # scan file directories for current list of tickers

    with ticker_file_read as s:
        saved = json.load(s)

    # Show saved list
    if col3.button("Show Saved Tickers", key="show_tickers"):
        cont1.write("###### *Current Session List:*")
        cont1.write(saved)

    # Append new tickers to the list if not in list
    if col4.button("Save tickers list", key="save_tickers") and len(tickers) > 0:
        missing_tickers = [i for i in tickers if i not in saved]
        with open(file, 'w+') as w:
            saved.extend(missing_tickers)
            json.dump(saved, w, indent=2)

        # Overwrite instead of extending current saved list with scanned list
    if col5.button("Overwrite tickers list", key="overwrite_tickers"):
        with open(file, 'w+') as d:
            json.dump(list_tickers, d, indent=2)


#####################################################

# Download Statements to Local Machine

#####################################################

# Read from financialmodelingAPI
def selectquote(ticker, statement):
    r = requests.get(
        f"https://financialmodelingprep.com/api/v3/{statement}/{ticker}?limit=120&apikey=eb29218df82acef0486b5c014ccec868")
    r = r.json()
    return r

# Save the read file to json


def save_to_json(ticker_symbol, statement):

    file = selectquote(ticker_symbol, statement)

    with open(f'D:\lianz\Desktop\Python\personal_projects\personal_finance\{statement}/{ticker_symbol}.json', 'w+') as p:
        json.dump(file, p, indent=4)


possible_statements = ['income-statement',
                       'balance-sheet-statement', 'cash-flow-statement']

st.write(
    """

---

##### Step 2: *Click this button to download files to your local computer*

""")

if st.button("Download Statements :ledger:"):

    progress_bar = st.progress(0)  # reset progress bar to 0
    step = round(100/len(saved))
    current = 0

    for x in saved:
        for y in possible_statements:

            # Check if json file already exists
            file = pathlib.Path(
                f'D:\lianz\Desktop\Python\personal_projects\personal_finance\{y}/{x}.json')

            # If file exists (TODO: update to append new entries instead of pass)
            if file.exists():
                pass

            # If file does not exist
            else:
                save_to_json(x, y)

        current += step

        progress_bar.progress(current)

        if file.exists():
            st.success(f"{x} statements already exists", icon="✅")

        else:
            st.success(f"{x} statements download complete")


# improvement: append to existing json file instead of rewriting to it with past 5 years, so longer term data can be acquired
