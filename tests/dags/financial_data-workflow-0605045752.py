from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import models as k8s
from airflow.providers.cncf.kubernetes.secret import Secret
from airflow import DAG
import pendulum

args = {
    "project_id": "financial_data-workflow-0605045752",
}

dag = DAG(
    dag_id="financial_data-workflow-0605045752",
    default_args=args,
    schedule="@once",
    start_date=pendulum.today("UTC").add(days=-1),
    description="""
Created with Elyra 4.0.0.dev0 pipeline editor using `test-workflow.pipeline`.
    """,
    is_paused_upon_creation=False,
)


# Operator source: work/elyra-poc/pipelines/TEST_PIPELINE/financial_data_visualizer.py

op_6c6e8841_8f15_400f_97e0_73d3229a1b16 = KubernetesPodOperator(
    name="financial_data_visualizer",
    namespace="airflow-elyra",
    image="continuumio/anaconda3:2024.02-1",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'financial_data-workflow' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket elyra-airflow --cos-directory 'financial_data-workflow-0605045752' --cos-dependencies-archive 'financial_data_visualizer-6c6e8841-8f15-400f-97e0-73d3229a1b16.tar.gz' --file 'work/elyra-poc/pipelines/TEST_PIPELINE/financial_data_visualizer.py' "
    ],
    task_id="financial_data_visualizer",
    env_vars={
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "financial_data-workflow-{{ ts_nodash }}",
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


# Operator source: work/elyra-poc/pipelines/TEST_PIPELINE/financial_data_processor.py

op_2595adb1_507c_4da5_83f8_c9a9d07abebe = KubernetesPodOperator(
    name="financial_data_processor",
    namespace="airflow-elyra",
    image="continuumio/anaconda3:2024.02-1",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'financial_data-workflow' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket elyra-airflow --cos-directory 'financial_data-workflow-0605045752' --cos-dependencies-archive 'financial_data_processor-2595adb1-507c-4da5-83f8-c9a9d07abebe.tar.gz' --file 'work/elyra-poc/pipelines/TEST_PIPELINE/financial_data_processor.py' "
    ],
    task_id="financial_data_processor",
    env_vars={
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "financial_data-workflow-{{ ts_nodash }}",
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

op_2595adb1_507c_4da5_83f8_c9a9d07abebe << op_6c6e8841_8f15_400f_97e0_73d3229a1b16
