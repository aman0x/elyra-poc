from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow import DAG
from airflow.utils.dates import days_ago

args = {
    "project_id": "test_airflow-0523104948",
}

dag = DAG(
    "test_airflow-0523104948",
    default_args=args,
    schedule_interval="@once",
    start_date=days_ago(1),
    description="""
Created with Elyra 3.15.0 pipeline editor using `test_airflow.pipeline`.
    """,
    is_paused_upon_creation=False,
)


# Operator source: {"catalog_type": "airflow-package-catalog", "component_ref": {"airflow_package": "apache_airflow-1.10.15-py2.py3-none-any.whl", "file": "airflow/operators/dagrun_operator.py"}}

op_869240a6_9133_473e_86a6_02d122d397de = TriggerDagRunOperator(
    task_id="TriggerDagRunOperator",
    trigger_dag_id="rom-cylinder-0522041636",
    python_callable="",
    execution_date="",
    executor_config={},
    dag=dag,
)
