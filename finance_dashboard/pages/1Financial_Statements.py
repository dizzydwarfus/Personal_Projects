import pandas as pd
import streamlit as st
import numpy as np
from pymongo import ASCENDING, DESCENDING
from functions import balance_sheet_collection, income_collection, cash_collection, company_profile, terms_interested, company_statements, read_statement, generate_key_metrics, create_financial_page, make_pretty, read_profile, statements_type

#####################################################

# Define dropdowns and set page config

#####################################################


tickers = list(set([i['symbol'] for i in balance_sheet_collection.find()]))

ticker_list_box = st.sidebar.selectbox(
    "Select a ticker symbol:", sorted(tickers), key="ticker_list")

companyA_info = read_profile(ticker_list_box)[0]

same_sector = sorted([i for i in tickers if read_profile(i)[0]['sector'] == companyA_info['sector']])

ticker_compare = st.sidebar.selectbox("Select a ticker symbol to compare:", same_sector, key="ticker_compare")

companyB_info = read_profile(ticker_compare)[0]

compare_companies = st.sidebar.checkbox('Compare', key='compare_companies')

#####################################################

# FInancial Statements Page

#####################################################

if compare_companies:
    l0, l1 = st.columns([1,1])
    t0, t1 = st.columns([1,1])
    p1, p2, p3, p4, p5, p6 = st.columns([1, 1, 1, 1, 1, 1])
    c1, c2 = st.columns([1,1])

    create_financial_page(ticker_list_box, companyA_info, l0, t0, c1, [p1,p2,p3])
    create_financial_page(ticker_compare, companyB_info, l1, t1, c2, [p4,p5,p6])

else:
    p1, p2, p3 = st.columns([1, 1, 1])

    create_financial_page(ticker_list_box, companyA_info, st, st, st, [p1,p2,p3])


st.markdown("***Data provided by Financial Modeling Prep***")
