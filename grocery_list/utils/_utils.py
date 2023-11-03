import pandas as pd
import timeit
from pprint import pprint
from supermarktconnector.ah import AHConnector
import numpy as np
import time

connector = AHConnector()


def save_data(file_name: str, data: dict):
    data_path = f'../data/{file_name}.csv'
    df = pd.DataFrame(data)
    df.to_csv(data_path, index=False)
