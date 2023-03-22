import pandas as pd
import streamlit as st
import numpy as np
from bson.objectid import ObjectId
from functions import tickers, company_profile, terms_interested, company_statements, statements_type, read_statement, generate_key_metrics, make_pretty, wacc, project_revenue,intrinsic_value, treasury, select_profile
import datetime as dt

#####################################################

# DCF Calculator

#####################################################

con1, con2 = st.container(), st.container()

c1, c2, c3 = con1.columns([0.5, 0.5, 1])
c4, c5, c6, c7, c8, c9, c10, c11 = con2.columns(
    [1, 0.5, 1, 0.5, 1, 0.5, 1, 0.5])


cols = [c4, c6, c8, c10]
manual_cols = [c5, c7, c9, c11]
c1.title("DCF Calculator")

con1.markdown("""

---

""")

ticker = c2.selectbox("Select a ticker symbol:",
                      sorted(tickers), key="DCF_tickers")

profile = select_profile(ticker,'profile')[0]
df = pd.concat([pd.DataFrame.from_records(read_statement(x, 'AAPL'), 
                                          index='calendarYear', 
                                          exclude=['_id','date','symbol','reportedCurrency','cik','fillingDate','acceptedDate','period','link','finalLink','index_id'])
                for x in statements_type], axis=1).T
df = df.loc[~df.index.duplicated(keep='first'), :].T.sort_index()

forecast_years = 5
historical_years = 5
# Define the financials of the company
revenues = project_revenue(df, past_n_years=10, future_n_years=forecast_years)  # Revenue forecast for the next five years based on growth of past n=10 years
depreciation = df['depreciationAndAmortization'][-historical_years:].mean()  # Depreciation as average of past n=historical_years years for the company
capital_expenditures = df['capitalExpenditure'][-historical_years:].mean()  # Capital expenditures as average of past n=historical_years years for the company
tax_rate = (df['incomeTaxExpense'][-historical_years:]/df['incomeBeforeTax'][-historical_years:]).mean()  # Tax rate as average of past n=historical_years years for the company calculated by dividing tax expense by incomebeforetax
net_working_capital = (df['totalCurrentAssets'][-historical_years:]-df['totalCurrentLiabilities'][-historical_years:]).mean()  # Net working capital (current assets - current liabilities where current generally defines period of 12 months - assets that can be liquidated/debts that must be repayed within that time period)

# # Define the assumptions for standard scenario
ebitda_margin = df['ebitdaratio'][-historical_years:].mean()  # EBITDA margin as average of past n=historical_years years for the company
avg_gr_choices = ['revenue','epsdiluted','dividendsPaid','netIncome']
average_growth_rate = df[avg_gr_choices[0]].pct_change()[-10:].mean() # this can be based on revenue, net income, dividendsPaid, epsdiluted, give a choice
terminal_growth_rate = min(0.05, average_growth_rate) # This limits the terminal growth rate to 5% maximum


# # Define the WACC assumptions
risk_free_rate = treasury(dt.date.today())[0]['year5']/100 # get latest 5Y treasury yield # treasury yield (2Y, 5Y, 10Y), get realtime by querying fedAPI
market_return = 0.08 # assume a 8% return is desired
profile = select_profile(ticker,'profile')[0]
beta = profile['beta'] # beta of stock
equity = profile['mktCap'] # market cap of stock
debt = df['totalDebt'][-historical_years:].mean() # total debt of company (excluding liabilities that are not debt)


# Display the results
st.metric("DCF: ", round(intrinsic_value(revenues,
                       ebitda_margin,
                       terminal_growth_rate,
                       wacc(df, risk_free_rate, beta, market_return, tax_rate, equity, debt, historical_years),
                       tax_rate,
                       depreciation,
                       capital_expenditures,
                       net_working_capital, 
                       forecast_years)/df['weightedAverageShsOutDil'][-1], 2))
# st.write(f"Intrinsic value (standard-case): {round(intrinsic_value(revenues,standard_ebitda_margin,standard_terminal_growth_rate), 2)}")
# st.write(f"Intrinsic value (best-case): {round(intrinsic_value(revenues,best_ebitda_margin,best_terminal_growth_rate), 2)}")


# TODO: compare DCF calculated stock price, with current price (repeat for past years, to see trend)
# TODO: show % difference for past DCF calculated values and calculate safety of margin, pick best metric from that.
# TODO: show extra tab with historical stock price using yfinance
# TODO: show technical indicators, and perform backtest
# TODO: use ML model to predict stock price

con3 = st.container()

st.markdown("***Data provided by Financial Modeling Prep***")

# st.write("""

# - show current growth rates (considering past 5 years)
# - show current stock price
# - use input fields for discount rate, growth rate, and terminal multiple
# - discount rate: use WACC, or expected return rate, or 10Y treasury yield
# - choose either growth on dividend (for slow growth), eps, or free cash flow
# - terminal multiple: what is the projected PE ratio 10 years from now?

# """)

# todos = [
#     'net present value',
#     'private market value - conservative historical value',
#     'personal value - how much you would pay personally based on assets for the business',
#     'liquidation value - best for unprofitable businesses trading below book value',
#     'Stock market value - compare similar businesses (potential spin-off)',
#     'Reflexivity - how rising stock prices influence underlying values (raising capital when stock prices are high)'
# ]

# for items in todos:
#     st.checkbox(f"{items}")
