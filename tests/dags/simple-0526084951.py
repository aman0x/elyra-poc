from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.contrib.kubernetes.volume_mount import VolumeMount
from airflow.contrib.kubernetes.volume import Volume
from airflow.kubernetes.secret import Secret
from airflow import DAG
from airflow.utils.dates import days_ago

args = {
    "project_id": "simple-0526084951",
}

dag = DAG(
    "simple-0526084951",
    default_args=args,
    schedule_interval="@once",
    start_date=days_ago(1),
    description="""
Created with Elyra 3.15.0 pipeline editor using `simple.pipeline`.
    """,
    is_paused_upon_creation=False,
)


# Operator source: work/load_data_from_s3.py

op_c8caee19_145b_49de_acea_8e371f904d13 = KubernetesPodOperator(
    name="LOAD_DATA_FROM_S3",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'simple' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'simple-0526084951' --cos-dependencies-archive 'load_data_from_s3-c8caee19-145b-49de-acea-8e371f904d13.tar.gz' --file 'work/load_data_from_s3.py' "
    ],
    task_id="LOAD_DATA_FROM_S3",
    env_vars = {
        "MINIO_ENDPOINT": "{{ dag_run.conf.get('minio_endpoint', 'http://minio.minio-system.svc.cluster.local:9000') if dag_run and dag_run.conf else 'http://minio.minio-system.svc.cluster.local:9000' }}",
        "MINIO_ACCESS_KEY": "{{ dag_run.conf.get('minio_access_key', 'minio') if dag_run and dag_run.conf else 'minio' }}",
        "MINIO_SECRET_KEY": "{{ dag_run.conf.get('minio_secret_key', 'minio122') if dag_run and dag_run.conf else 'minio122' }}",
        "INPUT_CSV": "{{ dag_run.conf.get('input_csv', 'TR1_TR2.csv') if dag_run and dag_run.conf else 'TR1_TR2.csv' }}",
        "OUTPUT_BUCKET": "{{ dag_run.conf.get('output_bucket', 'customer-bucket') if dag_run and dag_run.conf else 'customer-bucket' }}",
        "OUTPUT_PREFIX": "{{ dag_run.conf.get('output_prefix', 'simple-pipeline') if dag_run and dag_run.conf else 'simple-pipeline' }}",
        "OUTPUT_FILENAME": "{{ dag_run.conf.get('output_filename', 'tr1_tr2_raw.pkl') if dag_run and dag_run.conf else 'tr1_tr2_raw.pkl' }}",
        "ELYRA_RUNTIME_ENV": "{{ dag_run.conf.get('elyra_runtime_env', 'airflow') if dag_run and dag_run.conf else 'airflow' }}",
        "AWS_ACCESS_KEY_ID": "{{ dag_run.conf.get('aws_access_key_id', 'minio') if dag_run and dag_run.conf else 'minio' }}",
        "AWS_SECRET_ACCESS_KEY": "{{ dag_run.conf.get('aws_secret_access_key', 'minio123') if dag_run and dag_run.conf else 'minio123' }}",
        "ELYRA_ENABLE_PIPELINE_INFO": "{{ dag_run.conf.get('elyra_enable_pipeline_info', 'True') if dag_run and dag_run.conf else 'True' }}",
        "ELYRA_RUN_NAME": "{{ dag_run.conf.get('elyra_run_name', 'simple-{{ ts_nodash }}') if dag_run and dag_run.conf else 'simple-{{ ts_nodash }}' }}",
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


# Operator source: work/clean_null_values.py

op_b07880ae_79d6_4db0_8887_ce295f96bb1f = KubernetesPodOperator(
    name="CLEAN_VALUES",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'simple' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'simple-0526084951' --cos-dependencies-archive 'clean_null_values-b07880ae-79d6-4db0-8887-ce295f96bb1f.tar.gz' --file 'work/clean_null_values.py' "
    ],
    task_id="CLEAN_VALUES",
    env_vars = {
        "TEST_MODE": "{{ dag_run.conf.get('test_mode', 's3') if dag_run and dag_run.conf else 's3' }}",
        "MINIO_ENDPOINT": "{{ dag_run.conf.get('minio_endpoint', 'http://minio.minio-system.svc.cluster.local:9000') if dag_run and dag_run.conf else 'http://minio.minio-system.svc.cluster.local:9000' }}",
        "MINIO_ACCESS_KEY": "{{ dag_run.conf.get('minio_access_key', 'minio') if dag_run and dag_run.conf else 'minio' }}",
        "MINIO_SECRET_KEY": "{{ dag_run.conf.get('minio_secret_key', 'minio123') if dag_run and dag_run.conf else 'minio123' }}",
        "INPUT_BUCKET": "{{ dag_run.conf.get('input_bucket', 'customer-bucket') if dag_run and dag_run.conf else 'customer-bucket' }}",
        "OUTPUT_PREFIX": "{{ dag_run.conf.get('output_prefix', 'simple-pipeline') if dag_run and dag_run.conf else 'simple-pipeline' }}",
        "OUTPUT_BUCKET": "{{ dag_run.conf.get('output_bucket', 'simple-pipeline') if dag_run and dag_run.conf else 'simple-pipeline' }}",
        "ELYRA_RUNTIME_ENV": "{{ dag_run.conf.get('elyra_runtime_env', 'airflow') if dag_run and dag_run.conf else 'airflow' }}",
        "AWS_ACCESS_KEY_ID": "{{ dag_run.conf.get('aws_access_key_id', 'minio') if dag_run and dag_run.conf else 'minio' }}",
        "AWS_SECRET_ACCESS_KEY": "{{ dag_run.conf.get('aws_secret_access_key', 'minio123') if dag_run and dag_run.conf else 'minio123' }}",
        "ELYRA_ENABLE_PIPELINE_INFO": "{{ dag_run.conf.get('elyra_enable_pipeline_info', 'True') if dag_run and dag_run.conf else 'True' }}",
        "ELYRA_RUN_NAME": "{{ dag_run.conf.get('elyra_run_name', 'simple-{{ ts_nodash }}') if dag_run and dag_run.conf else 'simple-{{ ts_nodash }}' }}",
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

op_b07880ae_79d6_4db0_8887_ce295f96bb1f << op_c8caee19_145b_49de_acea_8e371f904d13
