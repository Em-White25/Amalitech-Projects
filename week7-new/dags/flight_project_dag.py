# dags/flight_project_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.mysql.operators.mysql import MySqlOperator
from datetime import datetime
from datetime import timedelta
from utils import (
    download_and_extract,
    load_data_to_mysql,
    validate_flight_data,
    transform_and_kpis_analysis,
    load_to_postgres
)

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 1, 1, 12, 0, 0),
    'end_date': datetime(2025, 1, 1, 13, 0, 0),
    'catchup': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    'flight_price_analysis_pipeline',
    default_args=default_args,
    schedule_interval=None,
    description='A pipeline to download, unzip, and load flight price data to MySQL.',
    tags=['flight_data', 'download', 'unzip', 'mysql'],
) as dag:

    # Task 1: Download and extract the dataset
    download_dataset = PythonOperator(
        task_id='download_dataset',
        python_callable=download_and_extract,
        dag=dag,
    )

    # Task 2: Create database
    create_database = MySqlOperator(
        task_id='create_database',
        mysql_conn_id='mysql_default',
        sql="CREATE DATABASE IF NOT EXISTS flight_db;",
        dag=dag,
    )

    # Task 3: Load the data into MySQL
    load_data = PythonOperator(
        task_id='load_data_to_mysql',
        python_callable=load_data_to_mysql,
        dag=dag,
    )

    # Task 4: Validate the data
    validate_data = PythonOperator(
        task_id='validate_flight_data',
        python_callable=validate_flight_data,
        dag=dag,
    )

    # Task 5: Transform data and compute KPIs
    transform_data = PythonOperator(
        task_id='transform_and_compute_kpis',
        python_callable=transform_and_kpis_analysis,
        dag=dag,
    )

    # Task 6: Load data to PostgreSQL
    load_to_postgres = PythonOperator(
        task_id='load_to_postgres',
        python_callable=load_to_postgres,
        dag=dag,
    )

    # Set task dependencies
    download_dataset >> create_database >> load_data >> validate_data >> transform_data >> load_to_postgres