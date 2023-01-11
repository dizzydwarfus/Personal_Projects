import pandas as pd
import json
import requests
from tickerlist import tickers


def selectquote(ticker, statement):
    r = requests.get(
        f"https://financialmodelingprep.com/api/v3/{statement}/{ticker}?limit=120&apikey=eb29218df82acef0486b5c014ccec868")
    r = r.json()
    return r


possible_statements = ['income-statement',
                       'balance-sheet-statement', 'cash-flow-statement']

for x in tickers:
    for y in possible_statements:
        save_to_json(x, y)


# improvement: append to existing json file instead of rewriting to it with past 5 years, so longer term data can be acquired
