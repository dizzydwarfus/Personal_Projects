import pandas as pd
import streamlit as st
import re

# # NLTK sub-libraries
# import nltk as lp
# from nltk.tokenize import word_tokenize
# from nltk.corpus import stopwords
# from nltk.stem.wordnet import WordNetLemmatizer
# from nltk.stem.porter import PorterStemmer


#####################################################

# Sentiment Analysis

#####################################################




# TODO: Sentiment analysis on tickers - https://www.alphavantage.co/documentation/ for 
# TODO: compare DCF calculated stock price, with current price (repeat for past years, to see trend)
# TODO: show % difference for past DCF calculated values and calculate safety of margin, pick best metric from that.
# TODO: show extra tab with historical stock price using yfinance
# TODO: show technical indicators, and perform backtest
# TODO: use ML model to predict stock price

#####################################################

# Show Calculated DCF and filter for undervalued/overvalued companies based on each of the 4 DCF calculations
# Get quarterly reports as well as yearly

st.markdown("***[Data provided by Financial Modeling Prep](https://financialmodelingprep.com/developer/docs/)***", unsafe_allow_html=True)
