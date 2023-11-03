import pandas as pd
from pymongo import MongoClient, ASCENDING, DESCENDING
import timeit
from pprint import pprint
from supermarktconnector.ah import AHConnector
import sys

client = MongoClient("mongodb+srv://dizzydwarfus:981128@clustermain.pjcbteq.mongodb.net/?retryWrites=true&w=majority") # initiate client connection
db = client.groceries # defining database to access - access 'groceries' database
meat_collection = db.meat # defining which collection to access - accessing the 'meat' collection


def upload_to_mongo(collection, dict_list: list):
    
    collection.insert_many(dict_list)

if __name__ == '__main__':
    upload_to_mongo(sys.argv[1], sys.argv[2])