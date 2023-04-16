import json
import requests
from airflow import DAG
from airflow.models.baseoperator import chain
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.models import Variable
from airflow.decorators import (
    dag,
    task,
    task_group
)
import datetime as dt

alpha_vantage_api = Variable.get('alpha_vantage_api')

hook = MongoHook(mongo_conn_id='mongo_default')
client = hook.get_conn()
db = client.FinanceApp
dailyquote = db.dailyquote

@dag(
    dag_id="daily_price",
    schedule=None,
    start_date=dt.datetime(2023,4,6),
    catchup=False,
    tags= ["daily prices"],
    default_args={"owner": "Lian",
                  "retries": 2,
                  "retry_delay": dt.timedelta(minutes=5),}
)
def load_historical_data():
    
    @task()
    def set_tickerlist():
        Variable.set(key='ticker_list', value=db.company_profile.distinct('symbol'))
    

    @task_group
    def get_and_upload(ticker):
        # for ticker in Variable.get('ticker_list'):
        @task()
        def get_daily_quote():
            url = "https://alpha-vantage.p.rapidapi.com/query"
            headers={"X-RapidAPI-Key": f"{alpha_vantage_api}",
                "X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com"}
            querystring = {"function":"GLOBAL_QUOTE",
                        "symbol":f"{ticker}",
                        "datatype":"json"}
            r = requests.request("GET", url=url, headers=headers, params=querystring)
            r = r.json()
            return r['Global Quote']
        
        @task()
        def transform(output_dict: dict):
            try:
                output_dict['index_id'] = f"{output_dict['01. symbol']}_{output_dict['07. latest trading day']}"
                output_dict['symbol'] = output_dict['01. symbol']
                output_dict['open'] = float(output_dict['02. open'])
                output_dict['high'] = float(output_dict['03. high'])
                output_dict['low'] = float(output_dict['04. low'])
                output_dict['close'] = float(output_dict['05. price'])
                output_dict['volume'] = int(output_dict['06. volume'])
                output_dict['latest_trading_day'] = output_dict['07. latest trading day']
                output_dict['previous_close'] = float(output_dict['08. previous close'])
                output_dict['change'] = float(output_dict['09. change'])
                output_dict['change_pct'] = float(output_dict['10. change percent'][:-1])/100
                output_dict.pop('01. symbol')
                output_dict.pop('02. open')
                output_dict.pop('03. high')
                output_dict.pop('04. low')
                output_dict.pop('05. price')
                output_dict.pop('06. volume')
                output_dict.pop('07. latest trading day')
                output_dict.pop('08. previous close')
                output_dict.pop('09. change')
                output_dict.pop('10. change percent')

                return output_dict
            except Exception as e:
                print(f'Error transforming output of {ticker} -- {e}')

        @task()
        def uploadtomongo(transformed_dict: dict):
            try:
                dailyquote.update_one({'index_id': transformed_dict['index_id']}, [{'$set': transformed_dict }] , upsert=True)
                dailyquote.update_one({'index_id': transformed_dict['index_id']},[
                            {
                                '$set': {
                                    'latest_trading_day': {
                                        '$dateFromString': {
                                            'dateString': '$latest_trading_day',
                                            'format': '%Y-%m-%d'
                                        }
                                    },
                                    'last_updated': '$$NOW'
                                }
                            }
                        ], upsert=True)
            
            except Exception as e:
                print(f"Error uploading to MongoDB -- {e}")

        quote = get_daily_quote()
        quote = transform(quote)
        uploadtomongo(quote)

    set_ticker = set_tickerlist()
    main_task = get_and_upload('AAPL')

    chain(
        set_ticker,
        main_task
    )

load_historical_data()