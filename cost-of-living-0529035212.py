from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import models as k8s
from airflow.providers.cncf.kubernetes.secret import Secret
from airflow import DAG
import pendulum

args = {
    "project_id": "cost-of-living-0529035212",
}

dag = DAG(
    dag_id="cost-of-living-0529035212",
    default_args=args,
    schedule="@once",
    start_date=pendulum.today("UTC").add(days=-1),
    description="""
Created with Elyra 4.0.0.dev0 pipeline editor using `cost-of-living.pipeline`.
    """,
    is_paused_upon_creation=False,
)


# Operator source: cost_data_fetcher.py

op_7e4b725d_63f9_44d8_9932_23cb5c84cf0b = KubernetesPodOperator(
    name="FETCH_DATA",
    namespace="airflow-elyra",
    image="continuumio/anaconda3:2024.10-1",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'cost-of-living' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'cost-of-living-0529035212' --cos-dependencies-archive 'cost_data_fetcher-7e4b725d-63f9-44d8-9932-23cb5c84cf0b.tar.gz' --file 'cost_data_fetcher.py' "
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


# Operator source: cost_data_visualizer.py

op_d97df814_93aa_45cc_9761_9bac1063f925 = KubernetesPodOperator(
    name="VISUALIZATION",
    namespace="airflow-elyra",
    image="continuumio/anaconda3:2024.10-1",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/main/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'cost-of-living' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'cost-of-living-0529035212' --cos-dependencies-archive 'cost_data_visualizer-d97df814-93aa-45cc-9761-9bac1063f925.tar.gz' --file 'cost_data_visualizer.py' "
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

op_d97df814_93aa_45cc_9761_9bac1063f925 << op_7e4b725d_63f9_44d8_9932_23cb5c84cf0b
