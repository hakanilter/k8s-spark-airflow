from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator

from spark_task import get_spark_task


dag = DAG(
    "sampleapp",
    default_args={"max_active_runs": 1},    
    schedule_interval=None,
    start_date=datetime(2022, 1, 1),
    catchup=False,
)

start = DummyOperator(task_id="start", dag=dag)
finish = DummyOperator(task_id="finish", dag=dag)
tasks = get_spark_task("sampleapp", dag)

start >> tasks >> finish
