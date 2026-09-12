from datetime import datetime, timezone

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator


with DAG(
    dag_id="gangacloud_orders_pipeline",
    description="Run and validate the GangaCloud orders data pipeline",
    schedule=None,
    start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    tags=["gangacloud", "data-engineering"],
) as dag:
    run_orders_platform_etl = BashOperator(
        task_id="run_orders_platform_etl",
        bash_command="""
        cd /opt/airflow/project &&
        python jobs/orders_platform_etl.py
        """,
    )

    validate_pipeline = BashOperator(
        task_id="validate_pipeline",
        bash_command="""
        cd /opt/airflow/project &&
        python scripts/validate_pipeline.py
        """,
    )

    run_orders_platform_etl >> validate_pipeline
