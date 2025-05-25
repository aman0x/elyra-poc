from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.contrib.kubernetes.volume_mount import VolumeMount
from airflow.contrib.kubernetes.volume import Volume
from airflow.kubernetes.secret import Secret
from airflow import DAG
from airflow.utils.dates import days_ago

args = {
    "project_id": "process_data_template-0525140539",
}

dag = DAG(
    "process_data_template-0525140539",
    default_args=args,
    schedule_interval="@once",
    start_date=days_ago(1),
    description="""
Created with Elyra 3.15.0 pipeline editor using `process_data_template.pipeline`.
    """,
    is_paused_upon_creation=False,
)


# Operator source: work/load_data_from_s3.py

op_data_loader = KubernetesPodOperator(
    name="DATA_LOADER",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'process_data_template' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'process_data_template-0525140539' --cos-dependencies-archive 'load_data_from_s3-data-loader.tar.gz' --file 'work/load_data_from_s3.py' "
    ],
    task_id="DATA_LOADER",
    env_vars={
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_CSV": "sxmlready_encoded_all.csv",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "pipeline-data",
        "OUTPUT_FILENAME": "input_data.pkl",
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

op_initial_deduplication = KubernetesPodOperator(
    name="INITIAL_DEDUPLICATION",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'process_data_template' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'process_data_template-0525140539' --cos-dependencies-archive 'remove_duplicates-initial-deduplication.tar.gz' --file 'work/remove_duplicates.py' "
    ],
    task_id="INITIAL_DEDUPLICATION",
    env_vars={
        "TEST_MODE": "s3",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "pipeline-data",
        "INPUT_SOURCE": "raw",
        "CHAIN_TRANSFORMATIONS": "true",
        "UPDATE_RAW_DATA": "true",
        "KEEP_FIRST": "first",
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

op_initial_deduplication << op_data_loader


# Operator source: work/remove_outliers.py

op_parallel_outlier_iqr = KubernetesPodOperator(
    name="OUTLIERS_IQR_METHOD",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'process_data_template' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'process_data_template-0525140539' --cos-dependencies-archive 'remove_outliers-parallel-outlier-iqr.tar.gz' --file 'work/remove_outliers.py' "
    ],
    task_id="OUTLIERS_IQR_METHOD",
    env_vars={
        "TEST_MODE": "s3",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "OUTPUT_BUCKET": "customer-bucket",
        "INPUT_KEY": "pipeline-data/input_data.pkl",
        "OUTPUT_PREFIX": "pipeline-data/iqr-branch",
        "CHAIN_TRANSFORMATIONS": "true",
        "UPDATE_RAW_DATA": "false",
        "OUTLIER_METHOD": "iqr",
        "OUTLIER_THRESHOLD": "1.5",
        "OUTLIER_ACTION": "remove",
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

op_parallel_outlier_iqr << op_initial_deduplication


# Operator source: work/remove_outliers.py

op_parallel_outlier_isolation = KubernetesPodOperator(
    name="OUTLIERS_ISOLATION_FOREST",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'process_data_template' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'process_data_template-0525140539' --cos-dependencies-archive 'remove_outliers-parallel-outlier-isolation.tar.gz' --file 'work/remove_outliers.py' "
    ],
    task_id="OUTLIERS_ISOLATION_FOREST",
    env_vars={
        "TEST_MODE": "s3",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_KEY": "pipeline-data/input_data.pkl",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "pipeline-data/isolation-branch",
        "CHAIN_TRANSFORMATIONS": "true",
        "UPDATE_RAW_DATA": "false",
        "OUTLIER_METHOD": "isolation_forest",
        "OUTLIER_THRESHOLD": "0.1",
        "OUTLIER_ACTION": "remove",
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

op_parallel_outlier_isolation << op_initial_deduplication


# Operator source: work/remove_outliers.py

op_conservative_outlier_capping = KubernetesPodOperator(
    name="CONSERVATIVE_OUTLIER_CAPPING",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'process_data_template' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'process_data_template-0525140539' --cos-dependencies-archive 'remove_outliers-conservative-outlier-capping.tar.gz' --file 'work/remove_outliers.py' "
    ],
    task_id="CONSERVATIVE_OUTLIER_CAPPING",
    env_vars={
        "TEST_MODE": "s3",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_KEY": "pipeline-data/input_data.pkl",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "pipeline-data/conservative-branch",
        "CHAIN_TRANSFORMATIONS": "true",
        "UPDATE_RAW_DATA": "false",
        "OUTLIER_METHOD": "iqr",
        "OUTLIER_THRESHOLD": "3.0",
        "OUTLIER_ACTION": "cap",
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

op_conservative_outlier_capping << op_initial_deduplication


# Operator source: work/clean_null_values.py

op_iqr_null_median = KubernetesPodOperator(
    name="IQR_BRANCH___MEDIAN_FILL",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'process_data_template' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'process_data_template-0525140539' --cos-dependencies-archive 'clean_null_values-iqr-null-median.tar.gz' --file 'work/clean_null_values.py' "
    ],
    task_id="IQR_BRANCH___MEDIAN_FILL",
    env_vars={
        "TEST_MODE": "s3",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_KEY": "pipeline-data/iqr-branch/outliers_removed_data.pkl",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "pipeline-data/iqr-branch",
        "CHAIN_TRANSFORMATIONS": "true",
        "UPDATE_RAW_DATA": "false",
        "NULL_STRATEGY": "fill_median",
        "NULL_THRESHOLD": "0.3",
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

op_iqr_null_median << op_parallel_outlier_iqr


# Operator source: work/clean_null_values.py

op_isolation_null_drop = KubernetesPodOperator(
    name="ISOLATION_BRANCH___DROP_COLS",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'process_data_template' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'process_data_template-0525140539' --cos-dependencies-archive 'clean_null_values-isolation-null-drop.tar.gz' --file 'work/clean_null_values.py' "
    ],
    task_id="ISOLATION_BRANCH___DROP_COLS",
    env_vars={
        "TEST_MODE": "s3",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_KEY": "pipeline-data/isolation-branch/outliers_removed_data.pkl",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "pipeline-data/isolation-branch",
        "CHAIN_TRANSFORMATIONS": "true",
        "UPDATE_RAW_DATA": "false",
        "NULL_STRATEGY": "drop_cols",
        "NULL_THRESHOLD": "0.5",
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

op_isolation_null_drop << op_parallel_outlier_isolation


# Operator source: work/clean_null_values.py

op_conservative_null_forward = KubernetesPodOperator(
    name="CONSERVATIVE___FORWARD_FILL",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'process_data_template' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'process_data_template-0525140539' --cos-dependencies-archive 'clean_null_values-conservative-null-forward.tar.gz' --file 'work/clean_null_values.py' "
    ],
    task_id="CONSERVATIVE___FORWARD_FILL",
    env_vars={
        "TEST_MODE": "s3",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_KEY": "pipeline-data/conservative-branch/outliers_removed_data.pkl",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "pipeline-data/conservative-branch",
        "CHAIN_TRANSFORMATIONS": "true",
        "UPDATE_RAW_DATA": "false",
        "NULL_STRATEGY": "fill_forward",
        "NULL_THRESHOLD": "0.8",
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

op_conservative_null_forward << op_conservative_outlier_capping


# Operator source: work/remove_duplicates.py

op_final_iqr_dedup = KubernetesPodOperator(
    name="IQR_FINAL_DEDUP",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'process_data_template' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'process_data_template-0525140539' --cos-dependencies-archive 'remove_duplicates-final-iqr-dedup.tar.gz' --file 'work/remove_duplicates.py' "
    ],
    task_id="IQR_FINAL_DEDUP",
    env_vars={
        "TEST_MODE": "s3",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_KEY": "pipeline-data/iqr-branch/nulls_cleaned_data.pkl",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "pipeline-data/iqr-branch",
        "CHAIN_TRANSFORMATIONS": "true",
        "UPDATE_RAW_DATA": "false",
        "KEEP_FIRST": "last",
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

op_final_iqr_dedup << op_iqr_null_median


# Operator source: work/remove_outliers.py

op_isolation_zscore_refinement = KubernetesPodOperator(
    name="ISOLATION_Z_SCORE_REFINEMENT",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'process_data_template' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'process_data_template-0525140539' --cos-dependencies-archive 'remove_outliers-isolation-zscore-refinement.tar.gz' --file 'work/remove_outliers.py' "
    ],
    task_id="ISOLATION_Z_SCORE_REFINEMENT",
    env_vars={
        "TEST_MODE": "s3",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_KEY": "pipeline-data/isolation-branch/nulls_cleaned_data.pkl",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "pipeline-data/isolation-branch",
        "CHAIN_TRANSFORMATIONS": "true",
        "UPDATE_RAW_DATA": "false",
        "OUTLIER_METHOD": "zscore",
        "OUTLIER_THRESHOLD": "2.5",
        "OUTLIER_ACTION": "cap",
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

op_isolation_zscore_refinement << op_isolation_null_drop


# Operator source: work/clean_null_values.py

op_conservative_final_median = KubernetesPodOperator(
    name="CONSERVATIVE_FINAL_MEDIAN",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'process_data_template' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'process_data_template-0525140539' --cos-dependencies-archive 'clean_null_values-conservative-final-median.tar.gz' --file 'work/clean_null_values.py' "
    ],
    task_id="CONSERVATIVE_FINAL_MEDIAN",
    env_vars={
        "TEST_MODE": "s3",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_KEY": "pipeline-data/conservative-branch/nulls_cleaned_data.pkl",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "pipeline-data/conservative-branch",
        "CHAIN_TRANSFORMATIONS": "true",
        "UPDATE_RAW_DATA": "false",
        "NULL_STRATEGY": "fill_median",
        "NULL_THRESHOLD": "0.9",
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

op_conservative_final_median << op_conservative_null_forward
