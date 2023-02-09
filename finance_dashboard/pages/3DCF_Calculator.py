import pandas as pd
import streamlit as st
import numpy as np
from bson.objectid import ObjectId
from functions import company_profile, terms_interested, company_statements, read_statement, generate_key_metrics, create_financial_page

#####################################################

# DCF Calculator

#####################################################


st.title("DCF Calculator")

st.write("""

- show current growth rates (considering past 5 years)
- show current stock price
- use input fields for discount rate, growth rate, and terminal multiple
- discount rate: use WACC, or expected return rate, or 10Y treasury yield
- choose either growth on dividend (for slow growth), eps, or free cash flow
- terminal multiple: what is the projected PE ratio 10 years from now?

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


st.markdown("***Data provided by Financial Modeling Prep***")