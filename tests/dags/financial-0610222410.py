from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import models as k8s
from airflow.providers.cncf.kubernetes.secret import Secret
from airflow import DAG
import pendulum

args = {
    "project_id": "financial-0610222410",
}

dag = DAG(
    dag_id="financial-0610222410",
    default_args=args,
    schedule="@once",
    start_date=pendulum.today("UTC").add(days=-1),
    description="""
Created with Elyra 4.0.0.dev0 pipeline editor using `financial.pipeline`.
    """,
    is_paused_upon_creation=False,
)


# Operator source: work/elyra-poc/pipelines/FINANCIAL_DATA/financial_data_processor.py

op_2e17f0c2_14be_437d_8d3e_b040ec4b6fcc = KubernetesPodOperator(
    name="financial_data_processor",
    namespace="airflow-elyra",
    image="continuumio/anaconda3:2024.02-1",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'financial' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket elyra-airflow --cos-directory 'financial-0610222410' --cos-dependencies-archive 'financial_data_processor-2e17f0c2-14be-437d-8d3e-b040ec4b6fcc.tar.gz' --file 'work/elyra-poc/pipelines/FINANCIAL_DATA/financial_data_processor.py' "
    ],
    task_id="financial_data_processor",
    env_vars={
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "financial-{{ ts_nodash }}",
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


# Operator source: work/elyra-poc/pipelines/FINANCIAL_DATA/financial_data_visualizer.py

op_fa6932c1_13da_48a4_bcd1_e526e5b24220 = KubernetesPodOperator(
    name="financial_data_visualizer",
    namespace="airflow-elyra",
    image="continuumio/anaconda3:2024.02-1",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'financial' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket elyra-airflow --cos-directory 'financial-0610222410' --cos-dependencies-archive 'financial_data_visualizer-fa6932c1-13da-48a4-bcd1-e526e5b24220.tar.gz' --file 'work/elyra-poc/pipelines/FINANCIAL_DATA/financial_data_visualizer.py' "
    ],
    task_id="financial_data_visualizer",
    env_vars={
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "financial-{{ ts_nodash }}",
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

op_fa6932c1_13da_48a4_bcd1_e526e5b24220 << op_2e17f0c2_14be_437d_8d3e_b040ec4b6fcc
