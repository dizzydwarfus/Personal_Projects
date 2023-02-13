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

    l0.markdown(f"""
    
    ![Logo]({companyA_info['image']} "Company Logo")
    
    """)

    t0.markdown(f"""


    # {ticker_list_box} 
    ---
    ### Company Profile

    {companyA_info['description']}

    *<span style="font-size:1em;">Visit [{companyA_info['website']}]({companyA_info['website']}) to learn more.</span>*

    """, unsafe_allow_html=True)

    l1.markdown(f"""
    
    ![Logo]({companyB_info['image']} "Company Logo")
    
    """)

    t1.markdown(f"""


    # {ticker_compare} 
    ---
    ### Company Profile

    {companyB_info['description']}

    *<span style="font-size:1em;">Visit [{companyB_info['website']}]({companyB_info['website']}) to learn more.</span>*

    """, unsafe_allow_html=True)

    create_financial_page(ticker_list_box, companyA_info, c1, [p1,p2,p3])
    create_financial_page(ticker_compare, companyB_info, c2, [p4,p5,p6])

else:
    st.markdown(f"""

    ![Logo]({companyA_info['image']} "Company Logo")
    
    """)

    st.markdown(f"""


    # {ticker_list_box} 
    ---
    ### Company Profile

    {companyA_info['description']}

    *<span style="font-size:1em;">Visit [{companyA_info['website']}]({companyA_info['website']}) to learn more.</span>*

    """, unsafe_allow_html=True)

    p1, p2, p3 = st.columns([1, 1, 1])

    create_financial_page(ticker_list_box, companyA_info, st, [p1,p2,p3])

st.markdown("***Data provided by Financial Modeling Prep***")


# st.write("""

#         Metrics to be shown (margin of safety):
#         ---

#         From Income-Statement:
#         1. revenue - 'revenue'
#         2. gross margin% - 'grossProfitRatio'
#         3. operating income - 'operatingIncome'
#         4. operating margin% - 'operatingIncomeRatio'
#         5. net income - 'netincome'
#         17. net income margin - 'netincomeRatio'
#         6. earnings per share - 'epsdiluted'
#         9. shares oustanding - 'weightedAverageShsOutDil'

#         From Cash-Flow-Statement:
#         7. dividends - 'dividendsPaid' (it is in negative so make it positive)
#         11. operating cash flow - 'operatingCashFlow'
#         12. cap spending - 'capitalExpenditure'
#         13. free cash flow - 'freeCashFlow'
#         14. free cash flow per share - 'freeCashFlow'

#         From Balance-Sheet:
#         15. working capital - 'totalCurrentAssets' - 'totalCurrentLiabilities'
#         16. Net debt - 'netDebt' (total debt minus any existing cash balances)

#         Unknown:
#         8. payout ratio% - ''
#         10. book value per share

#         Keypoint
#         : range of value: not exactly, value is adequate, approximate measure of intrinsic value may be sufficient(e.g. elon's twitter acquisition, "order of magnitude more valuable than current even if he is overpaying now").

#         """)