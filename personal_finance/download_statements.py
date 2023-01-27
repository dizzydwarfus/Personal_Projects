import pandas as pd
import json
import requests
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

cluster = "mongodb+srv://dizzydwarfus:981128@cluster0.yxzbors.mongodb.net/FinanceApp?retryWrites=true&w=majority"

client = MongoClient(cluster)

# print(client.list_database_names())

db = client.FinanceApp
balance_sheet_collection = db.Statements
print(balance_sheet_collection)

arr = os.listdir(r"D:\\lianz\Desktop\\Python\\data_science_discovery\\personal_finance\\balance-sheet-statement")

print(arr)

#TODO: store downloaded statements in mongodb and retrieve them via mongodb

for i in arr:
    with open(f"D:\\lianz\Desktop\\Python\\data_science_discovery\\personal_finance\\balance-sheet-statement\\{i}") as f:
        file_data = json.load(f)
    
