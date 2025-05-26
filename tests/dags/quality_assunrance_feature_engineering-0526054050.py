from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.contrib.kubernetes.volume_mount import VolumeMount
from airflow.contrib.kubernetes.volume import Volume
from airflow.kubernetes.secret import Secret
from airflow import DAG
from airflow.utils.dates import days_ago

args = {
    "project_id": "quality_assunrance_feature_engineering-0526054050",
}

dag = DAG(
    "quality_assunrance_feature_engineering-0526054050",
    default_args=args,
    schedule_interval="@once",
    start_date=days_ago(1),
    description="""
Created with Elyra 3.15.0 pipeline editor using `quality_assunrance_feature_engineering.pipeline`.
    """,
    is_paused_upon_creation=False,
)


# Operator source: work/load_data_from_s3.py

op_data_loader_tr1_tr2 = KubernetesPodOperator(
    name="LOAD_TR1_TR2_DATA",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'quality_assunrance_feature_engineering' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'quality_assunrance_feature_engineering-0526054050' --cos-dependencies-archive 'load_data_from_s3-data-loader-tr1-tr2.tar.gz' --file 'work/load_data_from_s3.py' "
    ],
    task_id="LOAD_TR1_TR2_DATA",
    env_vars={
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_CSV": "TR1_TR2.csv",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "qa-pipeline",
        "OUTPUT_FILENAME": "tr1_tr2_raw.pkl",
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "quality_assunrance_feature_engineering-{{ ts_nodash }}",
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

op_initial_quality_check = KubernetesPodOperator(
    name="INITIAL_QUALITY_CHECK",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'quality_assunrance_feature_engineering' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'quality_assunrance_feature_engineering-0526054050' --cos-dependencies-archive 'clean_null_values-initial-quality-check.tar.gz' --file 'work/clean_null_values.py' "
    ],
    task_id="INITIAL_QUALITY_CHECK",
    env_vars={
        "TEST_MODE": "s3",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_KEY": "qa-pipeline/tr1_tr2_raw.pkl",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "qa-pipeline",
        "CHAIN_TRANSFORMATIONS": "false",
        "UPDATE_RAW_DATA": "false",
        "NULL_STRATEGY": "drop_cols",
        "NULL_THRESHOLD": "0.7",
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "quality_assunrance_feature_engineering-{{ ts_nodash }}",
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

op_initial_quality_check << op_data_loader_tr1_tr2


# Operator source: work/clean_null_values.py

op_feature_engineering_mean_fill = KubernetesPodOperator(
    name="FEATURE_ENG___MEAN_FILL",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'quality_assunrance_feature_engineering' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'quality_assunrance_feature_engineering-0526054050' --cos-dependencies-archive 'clean_null_values-feature-engineering-mean-fill.tar.gz' --file 'work/clean_null_values.py' "
    ],
    task_id="FEATURE_ENG___MEAN_FILL",
    env_vars={
        "TEST_MODE": "s3",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_KEY": "qa-pipeline/nulls_cleaned_data.pkl",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "qa-pipeline/mean-fill-branch",
        "CHAIN_TRANSFORMATIONS": "false",
        "UPDATE_RAW_DATA": "false",
        "NULL_STRATEGY": "fill_mean",
        "NULL_THRESHOLD": "0.5",
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "quality_assunrance_feature_engineering-{{ ts_nodash }}",
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

op_feature_engineering_mean_fill << op_initial_quality_check


# Operator source: work/clean_null_values.py

op_feature_engineering_median_fill = KubernetesPodOperator(
    name="FEATURE_ENG___MEDIAN_FILL",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'quality_assunrance_feature_engineering' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'quality_assunrance_feature_engineering-0526054050' --cos-dependencies-archive 'clean_null_values-feature-engineering-median-fill.tar.gz' --file 'work/clean_null_values.py' "
    ],
    task_id="FEATURE_ENG___MEDIAN_FILL",
    env_vars={
        "TEST_MODE": "s3",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_KEY": "qa-pipeline/nulls_cleaned_data.pkl",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "qa-pipeline/median-fill-branch",
        "CHAIN_TRANSFORMATIONS": "false",
        "UPDATE_RAW_DATA": "false",
        "NULL_STRATEGY": "fill_median",
        "NULL_THRESHOLD": "0.5",
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "quality_assunrance_feature_engineering-{{ ts_nodash }}",
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

op_feature_engineering_median_fill << op_initial_quality_check


# Operator source: work/remove_outliers.py

op_statistical_validation_zscore = KubernetesPodOperator(
    name="STATISTICAL_VALIDATION___ZSCORE",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'quality_assunrance_feature_engineering' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'quality_assunrance_feature_engineering-0526054050' --cos-dependencies-archive 'remove_outliers-statistical-validation-zscore.tar.gz' --file 'work/remove_outliers.py' "
    ],
    task_id="STATISTICAL_VALIDATION___ZSCORE",
    env_vars={
        "TEST_MODE": "s3",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_KEY": "qa-pipeline/mean-fill-branch/nulls_cleaned_data.pkl",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "qa-pipeline/mean-fill-branch",
        "CHAIN_TRANSFORMATIONS": "false",
        "UPDATE_RAW_DATA": "false",
        "OUTLIER_METHOD": "zscore",
        "OUTLIER_THRESHOLD": "2.5",
        "OUTLIER_ACTION": "remove",
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "quality_assunrance_feature_engineering-{{ ts_nodash }}",
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

op_statistical_validation_zscore << op_feature_engineering_mean_fill


# Operator source: work/remove_outliers.py

op_statistical_validation_modified_zscore = KubernetesPodOperator(
    name="STATISTICAL_VALIDATION___MOD_ZSCORE",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'quality_assunrance_feature_engineering' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'quality_assunrance_feature_engineering-0526054050' --cos-dependencies-archive 'remove_outliers-statistical-validation-modified-zscore.tar.gz' --file 'work/remove_outliers.py' "
    ],
    task_id="STATISTICAL_VALIDATION___MOD_ZSCORE",
    env_vars={
        "TEST_MODE": "s3",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_KEY": "qa-pipeline/median-fill-branch/nulls_cleaned_data.pkl",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "qa-pipeline/median-fill-branch",
        "CHAIN_TRANSFORMATIONS": "false",
        "UPDATE_RAW_DATA": "false",
        "OUTLIER_METHOD": "modified_zscore",
        "OUTLIER_THRESHOLD": "3.0",
        "OUTLIER_ACTION": "remove",
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "quality_assunrance_feature_engineering-{{ ts_nodash }}",
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

op_statistical_validation_modified_zscore << op_feature_engineering_median_fill


# Operator source: work/remove_duplicates.py

op_quality_assurance_dedup_mean_branch = KubernetesPodOperator(
    name="QA_DEDUP___MEAN_BRANCH",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'quality_assunrance_feature_engineering' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'quality_assunrance_feature_engineering-0526054050' --cos-dependencies-archive 'remove_duplicates-quality-assurance-dedup-mean-branch.tar.gz' --file 'work/remove_duplicates.py' "
    ],
    task_id="QA_DEDUP___MEAN_BRANCH",
    env_vars={
        "TEST_MODE": "s3",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_KEY": "qa-pipeline/mean-fill-branch/outliers_removed_data.pkl",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "qa-pipeline/mean-fill-branch",
        "CHAIN_TRANSFORMATIONS": "false",
        "UPDATE_RAW_DATA": "false",
        "KEEP_FIRST": "first",
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "quality_assunrance_feature_engineering-{{ ts_nodash }}",
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

op_quality_assurance_dedup_mean_branch << op_statistical_validation_zscore


# Operator source: work/remove_duplicates.py

op_quality_assurance_dedup_median_branch = KubernetesPodOperator(
    name="QA_DEDUP___MEDIAN_BRANCH",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'quality_assunrance_feature_engineering' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'quality_assunrance_feature_engineering-0526054050' --cos-dependencies-archive 'remove_duplicates-quality-assurance-dedup-median-branch.tar.gz' --file 'work/remove_duplicates.py' "
    ],
    task_id="QA_DEDUP___MEDIAN_BRANCH",
    env_vars={
        "TEST_MODE": "s3",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_KEY": "qa-pipeline/median-fill-branch/outliers_removed_data.pkl",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "qa-pipeline/median-fill-branch",
        "CHAIN_TRANSFORMATIONS": "false",
        "UPDATE_RAW_DATA": "false",
        "KEEP_FIRST": "last",
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "quality_assunrance_feature_engineering-{{ ts_nodash }}",
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

op_quality_assurance_dedup_median_branch << op_statistical_validation_modified_zscore


# Operator source: work/remove_outliers.py

op_comparative_analysis_iqr = KubernetesPodOperator(
    name="COMPARATIVE_ANALYSIS___IQR",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'quality_assunrance_feature_engineering' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'quality_assunrance_feature_engineering-0526054050' --cos-dependencies-archive 'remove_outliers-comparative-analysis-iqr.tar.gz' --file 'work/remove_outliers.py' "
    ],
    task_id="COMPARATIVE_ANALYSIS___IQR",
    env_vars={
        "TEST_MODE": "s3",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_KEY": "qa-pipeline/tr1_tr2_raw.pkl",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "qa-pipeline/comparative-iqr",
        "CHAIN_TRANSFORMATIONS": "false",
        "UPDATE_RAW_DATA": "false",
        "OUTLIER_METHOD": "iqr",
        "OUTLIER_THRESHOLD": "1.5",
        "OUTLIER_ACTION": "cap",
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "quality_assunrance_feature_engineering-{{ ts_nodash }}",
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

op_comparative_analysis_iqr << op_data_loader_tr1_tr2


# Operator source: work/remove_outliers.py

op_comparative_analysis_isolation = KubernetesPodOperator(
    name="COMPARATIVE_ANALYSIS___ISOLATION",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'quality_assunrance_feature_engineering' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'quality_assunrance_feature_engineering-0526054050' --cos-dependencies-archive 'remove_outliers-comparative-analysis-isolation.tar.gz' --file 'work/remove_outliers.py' "
    ],
    task_id="COMPARATIVE_ANALYSIS___ISOLATION",
    env_vars={
        "TEST_MODE": "s3",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_KEY": "qa-pipeline/tr1_tr2_raw.pkl",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "qa-pipeline/comparative-isolation",
        "CHAIN_TRANSFORMATIONS": "false",
        "UPDATE_RAW_DATA": "false",
        "OUTLIER_METHOD": "isolation_forest",
        "OUTLIER_THRESHOLD": "0.05",
        "OUTLIER_ACTION": "remove",
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "quality_assunrance_feature_engineering-{{ ts_nodash }}",
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

op_comparative_analysis_isolation << op_data_loader_tr1_tr2


# Operator source: work/clean_null_values.py

op_final_feature_engineering_forward_fill = KubernetesPodOperator(
    name="FINAL_FEATURE_ENG___FORWARD_FILL",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'quality_assunrance_feature_engineering' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'quality_assunrance_feature_engineering-0526054050' --cos-dependencies-archive 'clean_null_values-final-feature-engineering-forward-fill.tar.gz' --file 'work/clean_null_values.py' "
    ],
    task_id="FINAL_FEATURE_ENG___FORWARD_FILL",
    env_vars={
        "TEST_MODE": "s3",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_KEY": "qa-pipeline/comparative-iqr/outliers_removed_data.pkl",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "qa-pipeline/comparative-iqr",
        "CHAIN_TRANSFORMATIONS": "false",
        "UPDATE_RAW_DATA": "false",
        "NULL_STRATEGY": "fill_forward",
        "NULL_THRESHOLD": "0.3",
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "quality_assunrance_feature_engineering-{{ ts_nodash }}",
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

op_final_feature_engineering_forward_fill << op_comparative_analysis_iqr


# Operator source: work/clean_null_values.py

op_final_feature_engineering_mode_fill = KubernetesPodOperator(
    name="FINAL_FEATURE_ENG___MODE_FILL",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'quality_assunrance_feature_engineering' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'quality_assunrance_feature_engineering-0526054050' --cos-dependencies-archive 'clean_null_values-final-feature-engineering-mode-fill.tar.gz' --file 'work/clean_null_values.py' "
    ],
    task_id="FINAL_FEATURE_ENG___MODE_FILL",
    env_vars={
        "TEST_MODE": "s3",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_KEY": "qa-pipeline/comparative-isolation/outliers_removed_data.pkl",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "qa-pipeline/comparative-isolation",
        "CHAIN_TRANSFORMATIONS": "false",
        "UPDATE_RAW_DATA": "false",
        "NULL_STRATEGY": "fill_mode",
        "NULL_THRESHOLD": "0.3",
        "ELYRA_RUNTIME_ENV": "airflow",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "quality_assunrance_feature_engineering-{{ ts_nodash }}",
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

op_final_feature_engineering_mode_fill << op_comparative_analysis_isolation
