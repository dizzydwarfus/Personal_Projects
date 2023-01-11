import pandas as pd
import streamlit as st
import json
from tickerlist import tickers
import string
import plotly.express as px
import numpy as np

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

#####################################################

# Define dropdowns and set page config

#####################################################

st.set_page_config(page_title="Investment Dashboard",
                   page_icon=":moneybag:",
                   layout="wide")

page_placeholder = st.sidebar.selectbox('What do you want to see?', [
                                        'Financial Statements', 'DCF Calculator', 'Charts'])

ticker_list_box = st.sidebar.selectbox(
    "Select a ticker symbol:", tickers, key="ticker_list")

company_statements = ['income-statement',
                      'cash-flow-statement', 'balance-sheet-statement']

with open(f'D:\lianz\Desktop\Python\data_science_discovery\personal_finance\{company_statements[0]}\{ticker_list_box}.json', 'r') as f:
    income_statement = json.load(f)

with open(f'D:\lianz\Desktop\Python\data_science_discovery\personal_finance\{company_statements[1]}\{ticker_list_box}.json', 'r') as f:
    cash_flow_statement = json.load(f)

with open(f'D:\lianz\Desktop\Python\data_science_discovery\personal_finance\{company_statements[2]}\{ticker_list_box}.json', 'r') as f:
    balance_sheet = json.load(f)


#####################################################

# Define functions to create dictionaries for
# historical data

#####################################################

terms_interested = {'Revenue': 'revenue',
                    'Gross margin%': 'grossProfitRatio',
                    'Operating Income': 'operatingIncome',
                    'Operating Margin %': 'operatingIncomeRatio',
                    'Net Income': 'netincome',
                    'Net Income Margin': 'netincomeRatio',
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
        l, index=[items for items in list_of_metrics if items in columns]).T

    return df


def generate_plots(dataframe, arrangement: tuple):

    # create columns to place charts based on arrangement specified (columns in each row)
    cols = st.columns(arrangement)

    m = 0

    for i, n in enumerate(terms_interested.values()):
        if n in dataframe.columns:
            if m >= len(cols):
                m = 0
            else:
                fig = px.line(dataframe[f'{n}'], title=f"{n.capitalize()}")
                fig.update_layout(showlegend=False,
                                  xaxis_title='Year', yaxis_title=f'{n}')
                fig.add_hline(y=dataframe[f'{n}'].max(
                ), line_color='green', line_dash='dash')
                fig.add_hline(y=dataframe[f'{n}'].min(
                ), line_color='red', line_dash='dash')
                cols[m].plotly_chart(
                    fig, use_container_width=True,)
                m += 1

#####################################################

# FInancial Statements Page

#####################################################


if page_placeholder == 'Financial Statements':

    st.write(f"""

    # {ticker_list_box}

    """)

    income_tab, cash_tab, balance_tab = st.tabs(
        ["Income Statement", "Cash Flow", "Balance Sheet"], )

    for i, x in enumerate([income_tab, cash_tab, balance_tab]):
        with x:
            with open(f'D:\lianz\Desktop\Python\data_science_discovery\personal_finance\{company_statements[i]}\{ticker_list_box}.json', 'r') as f:
                tab_statement = json.load(f)

            year_range = st.slider('Select year range (past n years):',
                                   min_value=1,
                                   max_value=int(
                                       tab_statement[0]['calendarYear'])-int(tab_statement[-1]['calendarYear'])+1,
                                   key=f'{ticker_list_box}_{x}_{i}')

            year_list = list(range(year_range))

            st.checkbox("Use container width",
                        value=False,
                        key=f'use_container_width_{x}_{i}')

            st.dataframe(pd.DataFrame.from_records(
                tab_statement[year_list[0]:year_list[-1]+1],
                index=[tab_statement[i]['calendarYear'] for i in year_list]).T,
                use_container_width=bool(f'st.session_state.use_container_width_income_tab'))

    # for i, x in enumerate(company_statements):
    #     if st.checkbox(f'Show {x}'):
    #         st.header(f'{x.capitalize()}')
    #         with open(f'D:\lianz\Desktop\Python\data_science_discovery\personal_finance\{x}\{ticker_list_box}.json', 'r') as f:
    #             statement = json.load(f)

    #         # year_selection = st.selectbox(
    #         #     "Select year:", range(len(statement)), format_func=lambda a: f"{statement[a]['calendarYear']}", key=f"year_selection{x}")

    #         year_range = st.slider('Select year range (past n years):',
    #                                min_value=1,
    #                                max_value=int(
    #                                    statement[0]['calendarYear'])-int(statement[-1]['calendarYear'])+1,
    #                                key=f'{ticker_list_box}_{x}_{i}')

    #         year_list = list(range(year_range))

    #         st.checkbox("Use container width",
    #                     value=False,
    #                     key=f'use_container_width_{i}')

    #         st.dataframe(pd.DataFrame.from_records(
    #             statement[year_list[0]:year_list[-1]+1],
    #             index=[statement[i]['calendarYear'] for i in year_list]).T,
    #             use_container_width=bool(f'st.session_state.use_container_width_{x}'))


#####################################################

# DCF Calculator

#####################################################

if page_placeholder == 'DCF Calculator':
    st.title("DCF Calculator")

    st.write("""

    - show current growth rates (considering past 5 years)
    - show current stock price
    - use input fields for discount rate, growth rate, and terminal multiple
    - discount rate: use WACC, or expected return rate, or 10Y treasury yield
    - choose either growth on dividend (for slow growth), eps, or free cash flow
    - terminal multiple: what is the projected PE ratio 10 years from now?

    """)
    c1, c2, c3 = st.columns([1, 1, 1])

    # c2.metric(label=f'EPS Growth (1Y)',
    #           value=f'{sum(df(income_statement))}',
    #           delta='0.5%')

#####################################################

# Charts Page

#####################################################

if page_placeholder == 'Charts':

    # statement_selection = st.selectbox(
    #     "Select:", company_statements, format_func=lambda a: string.capwords(a.replace("-", " ")))

    with open(f'D:\lianz\Desktop\Python\data_science_discovery\personal_finance\{company_statements[0]}\{ticker_list_box}.json', 'r') as f:
        statement = json.load(f)

    st.title(f"""

    {ticker_list_box}

    """)

    st.write(f"""

        # Financials Growth (last {len(statement)} years)

        """)

    key_metrics_table = generate_key_metrics(
        statement, terms_interested.values())

    generate_plots(key_metrics_table, [1, 1, 1, 1, 1, 1])
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
    todos = [
        'net present value',
        'private market value - conservative historical value',
        'personal value - how much you would pay personally based on assets for the business',
        'liquidation value - best for unprofitable businesses trading below book value',
        'Stock market value - compare similar businesses (potential spin-off)',
        'Reflexivity - how rising stock prices influence underlying values (raising capital when stock prices are high)'
    ]

    for items in todos:
        st.checkbox(f"{items}")

    """
    Session state and how to utilize it
    -> if "photo" not in st.session_state:
        st.session_state['photo'] = 'not done'

    def change_photo_state():
        st.session_state['photo'] = 'done'

    a streamlit function (on_change=change_photo_state)
    """
st.markdown("***Data provided by Financial Modeling Prep***")
