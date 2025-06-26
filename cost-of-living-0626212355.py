from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import models as k8s
from airflow.providers.cncf.kubernetes.secret import Secret
from airflow import DAG
import pendulum

args = {
    "project_id": "cost-of-living-0626212355",
}

dag = DAG(
    dag_id="cost-of-living-0626212355",
    default_args=args,
    schedule="@once",
    start_date=pendulum.today("UTC").add(days=-1),
    description="""
Created with Elyra 4.0.0.dev0 pipeline editor using `cost-of-living.pipeline`.
    """,
    is_paused_upon_creation=False,
)


# Operator source: /home/jovyan/elyra-poc/pipelines/COST_OF_LIVING/cost_data_fetcher.py

op_ed3d4d7e_f2bc_44f5_ab4f_34934227c964 = KubernetesPodOperator(
    name="FETCH_DATA",
    namespace="airflow-elyra",
    image="continuumio/anaconda3:2024.10-1",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'cost-of-living' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket elyra-airflow --cos-directory 'cost-of-living-0626212355' --cos-dependencies-archive 'cost_data_fetcher-ed3d4d7e-f2bc-44f5-ab4f-34934227c964.tar.gz' --file '/home/jovyan/elyra-poc/pipelines/COST_OF_LIVING/cost_data_fetcher.py' "
    ],
    task_id="FETCH_DATA",
    env_vars={
        "MINIO_ENDPOINT": "minio.minio-system.svc.cluster.local:9000",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_RUNTIME_ENV": "airflow",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "cost-of-living-{{ ts_nodash }}",
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


# Operator source: /home/jovyan/elyra-poc/pipelines/COST_OF_LIVING/cost_data_visualizer.py

op_327d8e30_50de_46d0_acd2_ce7edc656b8b = KubernetesPodOperator(
    name="VISUALIZATION",
    namespace="airflow-elyra",
    image="continuumio/anaconda3:2024.10-1",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'cost-of-living' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket elyra-airflow --cos-directory 'cost-of-living-0626212355' --cos-dependencies-archive 'cost_data_visualizer-327d8e30-50de-46d0-acd2-ce7edc656b8b.tar.gz' --file '/home/jovyan/elyra-poc/pipelines/COST_OF_LIVING/cost_data_visualizer.py' "
    ],
    task_id="VISUALIZATION",
    env_vars={
        "MINIO_ENDPOINT": "minio.minio-system.svc.cluster.local:9000",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_RUNTIME_ENV": "airflow",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "cost-of-living-{{ ts_nodash }}",
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

op_327d8e30_50de_46d0_acd2_ce7edc656b8b << op_ed3d4d7e_f2bc_44f5_ab4f_34934227c964
