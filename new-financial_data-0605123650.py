from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import models as k8s
from airflow.providers.cncf.kubernetes.secret import Secret
from airflow import DAG
import pendulum

args = {
    "project_id": "new-financial_data-0605123650",
}

dag = DAG(
    dag_id="new-financial_data-0605123650",
    default_args=args,
    schedule="@once",
    start_date=pendulum.today("UTC").add(days=-1),
    description="""
Created with Elyra 4.0.0.dev0 pipeline editor using `test-workflow.pipeline`.
    """,
    is_paused_upon_creation=False,
)


# Operator source: work/elyra-poc/pipelines/TEST_PIPELINE/financial_data_processor.py

op_ca3dd57e_83fa_45d5_aa8a_6168cfca567d = KubernetesPodOperator(
    name="financial_data_processor",
    namespace="airflow-elyra",
    image="continuumio/anaconda3:2024.02-1",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'new-financial_data' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket elyra-airflow --cos-directory 'new-financial_data-0605123650' --cos-dependencies-archive 'financial_data_processor-ca3dd57e-83fa-45d5-aa8a-6168cfca567d.tar.gz' --file 'work/elyra-poc/pipelines/TEST_PIPELINE/financial_data_processor.py' "
    ],
    task_id="financial_data_processor",
    env_vars={
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "new-financial_data-{{ ts_nodash }}",
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


# Operator source: work/elyra-poc/pipelines/TEST_PIPELINE/financial_data_visualizer.py

op_eb144010_41d6_4246_b11a_faf0b477c1d6 = KubernetesPodOperator(
    name="financial_data_visualizer",
    namespace="airflow-elyra",
    image="continuumio/anaconda3:2024.02-1",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'new-financial_data' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket elyra-airflow --cos-directory 'new-financial_data-0605123650' --cos-dependencies-archive 'financial_data_visualizer-eb144010-41d6-4246-b11a-faf0b477c1d6.tar.gz' --file 'work/elyra-poc/pipelines/TEST_PIPELINE/financial_data_visualizer.py' "
    ],
    task_id="financial_data_visualizer",
    env_vars={
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "new-financial_data-{{ ts_nodash }}",
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

op_eb144010_41d6_4246_b11a_faf0b477c1d6 << op_ca3dd57e_83fa_45d5_aa8a_6168cfca567d
