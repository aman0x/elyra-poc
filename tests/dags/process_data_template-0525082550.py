from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.contrib.kubernetes.volume_mount import VolumeMount
from airflow.contrib.kubernetes.volume import Volume
from airflow.kubernetes.secret import Secret
from airflow import DAG
from airflow.utils.dates import days_ago

args = {
    "project_id": "process_data_template-0525082550",
}

dag = DAG(
    "process_data_template-0525082550",
    default_args=args,
    schedule_interval="@once",
    start_date=days_ago(1),
    description="""
Created with Elyra 3.15.0 pipeline editor using `process_data_template.pipeline`.
    """,
    is_paused_upon_creation=False,
)


# Operator source: work/load_data_from_s3.py

op_8dbde37c_703c_47e0_a67f_b5979bfb5555 = KubernetesPodOperator(
    name="LOAD_DATA",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'process_data_template' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'process_data_template-0525082550' --cos-dependencies-archive 'load_data_from_s3-8dbde37c-703c-47e0-a67f-b5979bfb5555.tar.gz' --file 'work/load_data_from_s3.py' "
    ],
    task_id="LOAD_DATA",
    env_vars={
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_KEY": "sxmlready_encoded_all.csv",
        "OUTPUT_PREFIX": "process-data",
        "OUTPUT_BUCKET": "pipeline-data",
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
