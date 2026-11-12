from datetime import datetime, timedelta

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG

PY = "/home/airflow/pipeline-venv/bin/python"
PROJECT = "/home/airflow/project"


def transform_task(module: str) -> BashOperator:
    """One task per transform script: python -m transform.<module>"""
    return BashOperator(
        task_id=module,
        bash_command=f"cd {PROJECT} && {PY} -m transform.{module}",
    )


with DAG(
    dag_id="qanun_pulse_pipeline",
    description="Load laws, split them into articles, compute metrics",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=1)},
    tags=["qanun-pulse"],
) as dag:
    ingest = BashOperator(
        task_id="ingest",
        bash_command=f"cd {PROJECT}/ingestion && {PY} ingest.py",
    )

    split_articles = transform_task("split_articles")
    metrics_structure = transform_task("metrics_structure")
    metrics_text = transform_task("metrics_text")
    metrics_terms = transform_task("metrics_terms")

    export_dashboard_data = transform_task("export_dashboard_data")

    ingest >> split_articles >> [metrics_structure, metrics_text, metrics_terms]
    [metrics_structure, metrics_text, metrics_terms] >> export_dashboard_data