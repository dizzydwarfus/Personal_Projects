import pandas as pd
import streamlit as st
import numpy as np
from functions import tickers, statements_type
from functions import read_statement,  wacc, intrinsic_value, treasury, select_profile, project_metric
import datetime as dt


#####################################################

# DCF Calculator

#####################################################

con1, con2, con3 = st.container(), st.container(), st.container()

c1, c2, c3 = con1.columns([0.5, 0.5, 1])

con2.markdown("""

>##### *Set time frame (in years)*:

""")

c4, c5, c6, c7, c8, c9 = con2.columns(
    [0.5, 0.5, 0.18, 0.5, 0.5, 0.5])

con3.markdown("""

>##### *Main Inputs*:

""")
c12, c13, c14, c15, c16, c17 = con3.columns([0.5, 0.5, 0.5, 0.5, 0.5, 0.5])

c1.title("DCF Calculator")

con1.markdown("""

---

""")

ticker = c2.selectbox("Select a ticker symbol:",
                      sorted(tickers), key="DCF_tickers")
# avg_gr_choices = c3.selectbox("Choose which metric to calculate by:", ['revenue','epsdiluted','dividendsPaid','netIncome'])
avg_gr_choices = ['revenue','epsdiluted','dividendsPaid','netIncome']
profile = select_profile(ticker,'profile')[0]
df = pd.concat([pd.DataFrame.from_records(read_statement(x, 'AAPL'), 
                                          index='calendarYear', 
                                          exclude=['_id','date','symbol','reportedCurrency','cik','fillingDate','acceptedDate','period','link','finalLink','index_id'])
                for x in statements_type], axis=1).T
df = df.loc[~df.index.duplicated(keep='first'), :].T.sort_index()
forecast_n_years = c4.number_input("Forecast First n Years: ", min_value=1, step=1, value=5)
forecast_m_years = c4.number_input("Forecast Next m Years: ", min_value=1, step=1, value=5)
historical_years = c7.number_input("Past Years: ", min_value=1, step=1, value=5)


try:
    # Define the financials of the company
    first_growth = c5.number_input("Growth rate (first n years):", min_value=0.0, step=0.01, value=0.0)
    second_growth = c5.number_input("Growth rate (next m years):", min_value=0.0, step=0.01, value=0.0)
    projected_revenue = project_metric(df, avg_gr_choices[0], past_n_years=historical_years, first_n_years=forecast_n_years, second_n_years=forecast_m_years, first_growth=first_growth, second_growth=second_growth)  # Revenue forecast for the next five years based on growth of past n=10 years
    projected_eps = project_metric(df, avg_gr_choices[1], past_n_years=historical_years, first_n_years=forecast_n_years, second_n_years=forecast_m_years, first_growth=first_growth, second_growth=second_growth)  # Revenue forecast for the next five years based on growth of past n=10 years
    projected_netincome = project_metric(df, avg_gr_choices[3], past_n_years=historical_years, first_n_years=forecast_n_years, second_n_years=forecast_m_years, first_growth=first_growth, second_growth=second_growth)  # Revenue forecast for the next five years based on growth of past n=10 years
    projected_dividends = project_metric(df, avg_gr_choices[2], past_n_years=historical_years, first_n_years=forecast_n_years, second_n_years=forecast_m_years, first_growth=first_growth, second_growth=second_growth)  # Revenue forecast for the next five years based on growth of past n=10 years
    depreciation = df['depreciationAndAmortization'][-historical_years:].mean()  # Depreciation as average of past n=historical_years years for the company
    capital_expenditures = df['capitalExpenditure'][-historical_years:].mean()  # Capital expenditures as average of past n=historical_years years for the company
    tax_rate = (df['incomeTaxExpense'][-historical_years:]/df['incomeBeforeTax'][-historical_years:]).mean()  # Tax rate as average of past n=historical_years years for the company calculated by dividing tax expense by incomebeforetax
    net_working_capital = (df['totalCurrentAssets'][-historical_years:]-df['totalCurrentLiabilities'][-historical_years:]).mean()  # Net working capital (current assets - current liabilities where current generally defines period of 12 months - assets that can be liquidated/debts that must be repayed within that time period)

    # # Define the assumptions for standard scenario
    ebitda_margin = df['ebitdaratio'][-historical_years:].mean()  # EBITDA margin as average of past n=historical_years years for the company
    avg_gr_revenue = df[avg_gr_choices[0]].pct_change()[-historical_years:].mean() # this can be based on revenue, net income, dividendsPaid, epsdiluted, give a choice
    avg_gr_eps = df[avg_gr_choices[1]].pct_change()[-historical_years:].mean() # this can be based on revenue, net income, dividendsPaid, epsdiluted, give a choice
    avg_gr_dividends = df[avg_gr_choices[2]].pct_change()[-historical_years:].mean() # this can be based on revenue, net income, dividendsPaid, epsdiluted, give a choice
    avg_gr_netincome = df[avg_gr_choices[3]].pct_change()[-historical_years:].mean() # this can be based on revenue, net income, dividendsPaid, epsdiluted, give a choice
    c6.markdown(f'''
    Average over last {historical_years} years: 

    `Revenue: {"{:.0%}".format(avg_gr_revenue)}`

    `EPS: {"{:.0%}".format(avg_gr_eps)}`

    `Dividends: {"{:.0%}".format(avg_gr_dividends)}`

    `Net Income: {"{:.0%}".format(avg_gr_netincome)}`
    ''')
    terminal_gr_revenue = min(0.05, avg_gr_revenue) # This limits the terminal growth rate to 5% maximum
    terminal_gr_eps = min(0.05, avg_gr_eps) # This limits the terminal growth rate to 5% maximum
    terminal_gr_netincome = min(0.05, avg_gr_netincome) # This limits the terminal growth rate to 5% maximum
    terminal_gr_dividends = min(0.05, avg_gr_dividends) # This limits the terminal growth rate to 5% maximum

    # # Define the WACC assumptions
    treasury_rate = c12.selectbox("Risk-free Rate: ", ['month1', 'month2', 'month3', 'month6', 'year1', 'year2', 'year3', 'year5', 'year7', 'year10', 'year20', 'year30'], ) # get latest 5Y treasury yield # treasury yield (2Y, 5Y, 10Y), get realtime by querying fedAPI
    risk_free_rate = treasury(dt.date.today())[0][treasury_rate]/100
    market_return = c14.number_input("Expected Market Return:", min_value=0.0, step=0.005, value=0.08) # assume a 8% return is desired
    profile = select_profile(ticker,'profile')[0]
    beta = profile['beta'] # beta of stock
    equity = profile['mktCap'] # market cap of stock
    debt = df['totalDebt'][-historical_years:].mean() # total debt of company (excluding liabilities that are not debt)
    discount_rate = c13.number_input("Discount Rate: ", min_value=0.01, step=0.01, value=wacc(df, risk_free_rate, beta, market_return, tax_rate, equity, debt, historical_years))
    years = forecast_n_years + forecast_m_years # total years to forecast forward
    DCF_revenue = round(intrinsic_value(df, ebitda_margin, terminal_gr_revenue, discount_rate, tax_rate, depreciation, capital_expenditures, net_working_capital,  years, metric=avg_gr_choices[0], projected_metric=projected_revenue), 2)
    DCF_eps = round(intrinsic_value(df, ebitda_margin, terminal_gr_eps, discount_rate, tax_rate, depreciation, capital_expenditures, net_working_capital,  years, metric=avg_gr_choices[1], projected_metric=projected_eps), 2)
    DCF_netincome = round(intrinsic_value(df, ebitda_margin, terminal_gr_netincome, discount_rate, tax_rate, depreciation, capital_expenditures, net_working_capital,  years, metric=avg_gr_choices[3], projected_metric=projected_netincome), 2)
    DCF_dividends = round(intrinsic_value(df, ebitda_margin, terminal_gr_dividends, discount_rate, tax_rate, depreciation, capital_expenditures, net_working_capital,  years, metric=avg_gr_choices[2], projected_metric=projected_dividends), 2)
    current_price = "${:.2f}".format(profile['price'])
    # Display the results
    con3.markdown(f"""
    --------

    ### DCF Results:

    >Current Price: `{current_price}`

    """)

    con4 = st.container()
    c18, c19, c20, c21 = con4.columns([1,1,1,1])
    c18.metric("DCF from Revenue: ", DCF_revenue, label_visibility='visible')
    c19.metric("DCF from EPS: ", DCF_eps, label_visibility='visible')
    c20.metric("DCF from Net Income: ", DCF_netincome, label_visibility='visible')
    c21.metric("DCF from Dividends: ", DCF_dividends, label_visibility='visible')

except:
    pass

# st.write(f"Intrinsic value (standard-case): {round(intrinsic_value(revenues,standard_ebitda_margin,standard_terminal_growth_rate), 2)}")
# st.write(f"Intrinsic value (best-case): {round(intrinsic_value(revenues,best_ebitda_margin,best_terminal_growth_rate), 2)}")


# TODO: compare DCF calculated stock price, with current price (repeat for past years, to see trend)
# TODO: show % difference for past DCF calculated values and calculate safety of margin, pick best metric from that.
# TODO: show extra tab with historical stock price using yfinance
# TODO: show technical indicators, and perform backtest
# TODO: use ML model to predict stock price

con4 = st.container()

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
