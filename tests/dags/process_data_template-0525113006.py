from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.contrib.kubernetes.volume_mount import VolumeMount
from airflow.contrib.kubernetes.volume import Volume
from airflow.kubernetes.secret import Secret
from airflow import DAG
from airflow.utils.dates import days_ago

args = {
    "project_id": "process_data_template-0525113006",
}

dag = DAG(
    "process_data_template-0525113006",
    default_args=args,
    schedule_interval="@once",
    start_date=days_ago(1),
    description="""
Created with Elyra 3.15.0 pipeline editor using `process_data_template.pipeline`.
    """,
    is_paused_upon_creation=False,
)


# Operator source: work/load_data_from_s3.py

op_5594a068_1784_42d1_9fa4_2095df73b628 = KubernetesPodOperator(
    name="LOAD_DATA_S3",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'process_data_template' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'process_data_template-0525113006' --cos-dependencies-archive 'load_data_from_s3-5594a068-1784-42d1-9fa4-2095df73b628.tar.gz' --file 'work/load_data_from_s3.py' "
    ],
    task_id="LOAD_DATA_S3",
    env_vars={
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_KEY": "pipeline-data/input_data.pkl",
        "OUTPUT_PREFIX": "pipeline-data",
        "OUTPUT_BUCKET": "customer-bucket",
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "process_data_template-{{ ts_nodash }}",
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


# Operator source: work/remove_duplicates.py

op_5a9c7c69_e4d3_4833_8cbe_79c98a9ba60d = KubernetesPodOperator(
    name="REMOVE_DUPLICATES",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'process_data_template' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'process_data_template-0525113006' --cos-dependencies-archive 'remove_duplicates-5a9c7c69-e4d3-4833-8cbe-79c98a9ba60d.tar.gz' --file 'work/remove_duplicates.py' "
    ],
    task_id="REMOVE_DUPLICATES",
    env_vars={
        "TEST_MODE": "s3",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_KEY": "pipeline-data/input_data.pkl",
        "OUTPUT_PREFIX": "pipeline-data",
        "OUTPUT_BUCKET": "customer-bucket",
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "process_data_template-{{ ts_nodash }}",
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

op_5a9c7c69_e4d3_4833_8cbe_79c98a9ba60d << op_5594a068_1784_42d1_9fa4_2095df73b628
