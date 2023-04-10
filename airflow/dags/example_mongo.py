import os
import json
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.models import Variable
import datetime as dt

alpha_vantage_api = Variable.get('alpha_vantage_api')

def adjust_output_format(x):
    x['index_id'] = f"{x['01. symbol']}_{x['07. latest trading day']}"
    x['symbol'] = x['01. symbol']
    x['open'] = float(x['02. open'])
    x['high'] = float(x['03. high'])
    x['low'] = float(x['04. low'])
    x['close'] = float(x['05. price'])
    x['volume'] = int(x['06. volume'])
    x['latest_trading_day'] = dt.datetime.strptime(x['07. latest trading day'], '%Y-%m-%d')
    x['previous_close'] = float(x['08. previous close'])
    x['change'] = float(x['09. change'])
    x['change_pct'] = float(x['10. change percent'][:-1])/100
    x.pop('01. symbol')
    x.pop('02. open')
    x.pop('03. high')
    x.pop('04. low')
    x.pop('05. price')
    x.pop('06. volume')
    x.pop('07. latest trading day')
    x.pop('08. previous close')
    x.pop('09. change')
    x.pop('10. change percent')
    return x


def on_failure_callback(**context):
    print(f"Task {context['task_instance_key_str']} failed.")

def uploadtomongo(**context):
    try:
        hook = MongoHook(mongo_conn_id='mongo_default')
        client = hook.get_conn()
        db = client.FinanceApp
        dailyquote=db.dailyquote
        d=json.loads(context["result"])
        d = adjust_output_format(d["Global Quote"])
        dailyquote.insert_one(d)
    except Exception as e:
        print(f"Error connecting to MongoDB -- {e}")

with DAG(
    dag_id="load_historical_data",
    schedule=None,
    start_date=dt.datetime(2023,4,6),
    catchup=False,
    tags= ["prices"],
    default_args={
        "owner": "Lian",
        "retries": 2,
        "retry_delay": dt.timedelta(minutes=5),
        'on_failure_callback': on_failure_callback
    }
) as dag:
    
    get_daily_quote = SimpleHttpOperator(
        task_id='get_stock_prices',
        method='GET',
        http_conn_id='alpha_vantage',
        endpoint='/query?function=GLOBAL_QUOTE&symbol=NVDA&datatype=json',
        headers={"X-RapidAPI-Key": f"{alpha_vantage_api}",
               "X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com"},
        do_xcom_push=True,
        dag=dag)
    
    print(get_daily_quote)

    upload_to_db = PythonOperator(
        task_id='upload-mongodb',
        python_callable=uploadtomongo,
        op_kwargs={"result": get_daily_quote.output},
        dag=dag
        )

    get_daily_quote >> upload_to_db