from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import models as k8s
from airflow.providers.cncf.kubernetes.secret import Secret
from airflow import DAG
import pendulum

args = {
    "project_id": "cost_of_living-0528154228",
}

dag = DAG(
    dag_id="cost_of_living-0528154228",
    default_args=args,
    schedule="@once",
    start_date=pendulum.today("UTC").add(days=-1),
    description="""
A pipeline that fetches cost of living data and generates Plotly visualizations using Airflow XCom
    """,
    is_paused_upon_creation=False,
)


# Operator source: fetch_cost_of_living.py

op_fetch_cost_of_living = KubernetesPodOperator(
    name="Fetch_Cost_of_Living_Data",
    namespace="airflow-elyra",
    image="continuumio/anaconda3:2024.10-1",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'cost_of_living' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'cost_of_living-0528154228' --cos-dependencies-archive 'fetch_cost_of_living-fetch_cost_of_living.tar.gz' --file 'fetch_cost_of_living.py' "
    ],
    task_id="Fetch_Cost_of_Living_Data",
    env_vars={
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "cost_of_living-{{ ts_nodash }}",
    },
    volumes=[],
    volume_mounts=[],
    secrets=[],
    annotations={},
    labels={},
    tolerations=[],
    in_cluster=True,
    config_file=None,
    dag=dag,
)


# Operator source: generate_plotly_json.py

op_generate_plotly_json = KubernetesPodOperator(
    name="Generate_Plotly_JSON",
    namespace="airflow-elyra",
    image="continuumio/anaconda3:2024.10-1",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'cost_of_living' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'cost_of_living-0528154228' --cos-dependencies-archive 'generate_plotly_json-generate_plotly_json.tar.gz' --file 'generate_plotly_json.py' "
    ],
    task_id="Generate_Plotly_JSON",
    env_vars={
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "cost_of_living-{{ ts_nodash }}",
    },
    volumes=[],
    volume_mounts=[],
    secrets=[],
    annotations={},
    labels={},
    tolerations=[],
    in_cluster=True,
    config_file=None,
    dag=dag,
)

op_generate_plotly_json << op_fetch_cost_of_living
