import pandas as pd
import streamlit as st
import datetime as dt

#####################################################

# Streamlit page title

#####################################################

st.write("""

# Personal Finance Overview

""")

labels = ['show dataframe', 'categorize transactions', 'show categories of spending','show piechart', 'show slider to adjust for date', 'show slider to adjust for type of spending']
with st.sidebar:
    for i, value in enumerate(labels):
        if st.checkbox(labels[i]):
            st.write("Done!")

#####################################################

## Transactions Dataframe

#####################################################

st.write("""

## Transactions Log

All transactions downloaded from banking website.

Categories of each transactions are categorized using *classification* algorithm.

""")

df = pd.read_csv("D:\lianz\Desktop\Python\data_science_discovery\personal_finance\expenses.csv", sep=',', parse_dates=['Datum'])
df['Datum'] = df['Datum'].dt.date

df_checkbox = st.checkbox(label="Show Transactions Log", key='df_checkbox', value=True)
if df_checkbox:
    st.dataframe(df)

