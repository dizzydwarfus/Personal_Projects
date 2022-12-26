import pandas as pd
import openpyxl
import json

etoro_lists = 'D:\lianz\Desktop\Python\data_science_discovery\personal_finance\etoro_listings\etoro-account-statement-10-1-2021-12-23-2022.xlsx'
investment_history = pd.read_excel(etoro_lists, sheet_name='Account Activity')

tickers = list(investment_history[investment_history['Asset type']
                                  == 'Stocks']['Details'].str.split('/', expand=True)[0].unique())
