import subprocess
import sys
from datetime import datetime

from airflow.decorators import dag, task


@dag(
    dag_id="ecommerce_pipeline",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["ecommerce"],
)
def ecommerce_pipeline():

    @task
    def ingest_raw_data():
        import importlib.util, os

        script = "/opt/airflow/data_ingestion/generate_data.py"
        spec = importlib.util.spec_from_file_location("generate_data", script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        conn = mod.get_connection()
        mod.create_tables(conn)
        mod.seed_products(conn)
        mod.generate_daily_data(conn)
        conn.close()

    @task
    def run_dbt(command: str):
        result = subprocess.run(
            ["dbt", command, "--project-dir", "/opt/airflow/dbt_project",
             "--profiles-dir", "/opt/airflow/dbt_project"],
            capture_output=True, text=True,
        )
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            raise Exception(f"dbt {command} failed")

    ingest = ingest_raw_data()
    dbt_run = run_dbt.override(task_id="dbt_run")("run")
    dbt_test = run_dbt.override(task_id="dbt_test")("test")

    ingest >> dbt_run >> dbt_test


ecommerce_pipeline()
