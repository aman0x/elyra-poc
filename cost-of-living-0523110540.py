from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.contrib.kubernetes.volume_mount import VolumeMount
from airflow.contrib.kubernetes.volume import Volume
from airflow.kubernetes.secret import Secret
from airflow import DAG
from airflow.utils.dates import days_ago

args = {
    "project_id": "cost-of-living-0523110540",
}

dag = DAG(
    "cost-of-living-0523110540",
    default_args=args,
    schedule_interval="@once",
    start_date=days_ago(1),
    description="""
Created with Elyra 3.15.0 pipeline editor using `cost-of-living.pipeline`.
    """,
    is_paused_upon_creation=False,
)


# Operator source: work/COST OF LIVING/cost_data_fetcher.py

op_71211e52_fe23_490a_a481_c1128c73e361 = KubernetesPodOperator(
    name="cost_data_fetcher",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'cost-of-living' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket elyra-airflow --cos-directory 'cost-of-living-0523110540' --cos-dependencies-archive 'cost_data_fetcher-71211e52-fe23-490a-a481-c1128c73e361.tar.gz' --file 'work/COST OF LIVING/cost_data_fetcher.py' "
    ],
    task_id="cost_data_fetcher",
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
    config_file="None",
    dag=dag,
)


# Operator source: work/COST OF LIVING/cost_data_visualizer.py

op_53136309_0b4b_496d_ab5c_4abf6c8c0264 = KubernetesPodOperator(
    name="cost_data_visualizer",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'cost-of-living' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket elyra-airflow --cos-directory 'cost-of-living-0523110540' --cos-dependencies-archive 'cost_data_visualizer-53136309-0b4b-496d-ab5c-4abf6c8c0264.tar.gz' --file 'work/COST OF LIVING/cost_data_visualizer.py' "
    ],
    task_id="cost_data_visualizer",
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
    config_file="None",
    dag=dag,
)

op_53136309_0b4b_496d_ab5c_4abf6c8c0264 << op_71211e52_fe23_490a_a481_c1128c73e361
