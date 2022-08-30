from airflow import DAG
from datetime import timedelta
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

from pendulum import datetime
import pandas as pd

import sys

from satelliteTrack import api_call, load_satellite_data
from dbConnector import load_into_database



default_args = {
    'owner':'airflow',
    'depends_on_past': False,
    'start_date': datetime(2022,8,29),
    'retries': 1
}

dag = DAG(
    'Satellite_Data',
    default_args=default_args,
    description='Makes api call to space-track.org and stores data in database',
    schedule_interval=timedelta(days=1),
    catchup=False
)


t1 = BashOperator (
    task_id = 'load_into_json',
    bash_command= 'python3 /opt/airflow/dags/satelliteTrack.py',
    dag=dag
)

t2 = PythonOperator (
    task_id='load_data',
    python_callable=load_into_database,
    dag=dag
)

t1 >> t2 