import pandas as pd
import streamlit as st
# import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from functions import balance_sheet_collection, income_collection, cash_collection, company_profile, terms_interested, company_statements, read_statement, generate_key_metrics, generate_plots, create_financial_page, make_pretty, read_profile, statements_type

tickers = list(set([i['symbol'] for i in balance_sheet_collection.find()]))

ticker_list_box = st.sidebar.selectbox(
    "Select a ticker symbol:", sorted(list(set(tickers))), key="ticker_list")


st.title(f"""

{ticker_list_box}

""")

st.write(f"""

    # Financials Growth (last {len(read_statement(statements_type[0],ticker_list_box))} years)

    """)

key_metrics_table = generate_key_metrics(read_statement(statements_type[0],ticker_list_box), terms_interested.values())

chart_select = st.multiselect('*Select charts to show:*', terms_interested.keys())



generate_plots(key_metrics_table, [1])
key_metrics_table

"""
Show eps by industry/sector: create lists containing ticker
                            symbols belonging to an industry
                            use the selectbox to select the lists.
"""

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