import pandas as pd
import streamlit as st
import numpy as np
from bson.objectid import ObjectId
from functions import tickers, company_profile, terms_interested, company_statements, statements_type, read_statement, generate_key_metrics, make_pretty

#####################################################

# DCF Calculator

#####################################################

con1, con2 = st.container(),st.container()

c1,c2,c3 = con1.columns([0.5,0.5,1])
c4,c5,c6,c7,c8,c9,c10,c11 = con2.columns([1,0.5,1,0.5,1,0.5,1,0.5])


cols = [c4,c6,c8,c10]
manual_cols = [c5,c7,c9,c11]
c1.title("DCF Calculator")

con1.markdown("""

---

""")

ticker = c2.selectbox("Select a ticker symbol:", sorted(tickers), key="DCF_tickers")


df = pd.concat([generate_key_metrics(read_statement(x,ticker),terms_interested.values()) for x in statements_type], axis=0).drop_duplicates()
df = df.loc[~df.index.duplicated(keep='first'),:]
df_growth = df.T.pct_change(periods=1).T

# con2.dataframe(df_growth.iloc[list(terms_interested.keys()).index('Revenue'):,-5:])

count = 0
for i,x in terms_interested.items():
    try:
        cols[count].markdown(
        f"""<span style='font-size:1.5em;'>{i.capitalize()} Growth</span>  
        <span style='font-size:1.2em;'>:green[{'{:.2%}'.format(df_growth.loc[x,df_growth.columns[-5]:].mean())}]</span>

        """, unsafe_allow_html=True)
        manual_cols[count].number_input(f'Manual Input:',0,100, step=1, key=f'{x}_manual_growth')
        if count < len(cols)-1:
            count += 1
        else:
            count = 0
    except:
        pass

#TODO: forecast growth 10 years ahead based on average of past n (input) years

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

