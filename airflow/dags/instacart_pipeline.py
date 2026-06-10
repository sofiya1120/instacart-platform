from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess
import sys
import os

SCRIPTS_DIR = '/usr/local/airflow/include/scripts'
PYTHON = sys.executable

default_args = {
    'owner': 'instacart',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
    'email_on_failure': False,
}

def run_script(script_name: str):
    result = subprocess.run(
        [PYTHON, os.path.join(SCRIPTS_DIR, script_name)],
        capture_output=True,
        text=True,
        cwd='/usr/local/airflow/include',
        env={**os.environ, 'PYTHONPATH': '/usr/local/airflow/include'},
    )
    print(result.stdout)
    if result.returncode != 0:
        raise RuntimeError(f'{script_name} failed:\n{result.stderr}')

with DAG(
    dag_id='instacart_intelligence_pipeline',
    default_args=default_args,
    description='Daily Instacart data pipeline',
    schedule='0 6 * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['instacart'],
) as dag:

    t_cohort = PythonOperator(
        task_id='cohort_analysis',
        python_callable=lambda: run_script('cohort_analysis.py'),
    )

    t_rfm = PythonOperator(
        task_id='rfm_segmentation',
        python_callable=lambda: run_script('rfm_analysis.py'),
    )

    t_funnel = PythonOperator(
        task_id='funnel_analysis',
        python_callable=lambda: run_script('funnel_analysis.py'),
    )

    t_ab = PythonOperator(
        task_id='ab_testing',
        python_callable=lambda: run_script('ab_testing.py'),
    )

    t_churn = PythonOperator(
        task_id='churn_model',
        python_callable=lambda: run_script('churn_model.py'),
    )

    # All analytics run first, then churn model
    [t_cohort, t_rfm, t_funnel, t_ab] >> t_churn