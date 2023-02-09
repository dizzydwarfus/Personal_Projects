import pandas as pd
import streamlit as st
import json
# import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from classes import tickers, company_statements, terms_interested, generate_key_metrics, generate_plots


ticker_list_box = st.sidebar.selectbox(
    "Select a ticker symbol:", sorted(list(set(tickers))), key="ticker_list")


with open(f'D:\lianz\Desktop\Python\\personal_projects\personal_finance\{company_statements[0]}\{ticker_list_box}.json', 'r') as f:
    income = json.load(f)


st.title(f"""

{ticker_list_box}

""")

st.write(f"""

    # Financials Growth (last {len(income)} years)

    """)

key_metrics_table = generate_key_metrics(
    income, terms_interested.values())

generate_plots(key_metrics_table, [1])
key_metrics_table

"""
Show eps by industry/sector: create lists containing ticker
                            symbols belonging to an industry
                            use the selectbox to select the lists.
"""

st.write("""

        Metrics to be shown (margin of safety):
        ---

        From Income-Statement:
        1. revenue - 'revenue'
        2. gross margin% - 'grossProfitRatio'
        3. operating income - 'operatingIncome'
        4. operating margin% - 'operatingIncomeRatio'
        5. net income - 'netincome'
        17. net income margin - 'netincomeRatio'
        6. earnings per share - 'epsdiluted'
        9. shares oustanding - 'weightedAverageShsOutDil'

        From Cash-Flow-Statement:
        7. dividends - 'dividendsPaid' (it is in negative so make it positive)
        11. operating cash flow - 'operatingCashFlow'
        12. cap spending - 'capitalExpenditure'
        13. free cash flow - 'freeCashFlow'
        14. free cash flow per share - 'freeCashFlow'

        From Balance-Sheet:
        15. working capital - 'totalCurrentAssets' - 'totalCurrentLiabilities'
        16. Net debt - 'netDebt' (total debt minus any existing cash balances)

        Unknown:
        8. payout ratio% - ''
        10. book value per share

        Keypoint
        : range of value: not exactly, value is adequate, approximate measure of intrinsic value may be sufficient(e.g. elon's twitter acquisition, "order of magnitude more valuable than current even if he is overpaying now").

        """)