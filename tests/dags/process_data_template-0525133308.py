from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.contrib.kubernetes.volume_mount import VolumeMount
from airflow.contrib.kubernetes.volume import Volume
from airflow.kubernetes.secret import Secret
from airflow import DAG
from airflow.utils.dates import days_ago

args = {
    "project_id": "process_data_template-0525133308",
}

dag = DAG(
    "process_data_template-0525133308",
    default_args=args,
    schedule_interval="@once",
    start_date=days_ago(1),
    description="""
Created with Elyra 3.15.0 pipeline editor using `process_data_template.pipeline`.
    """,
    is_paused_upon_creation=False,
)


# Operator source: work/load_data_from_s3.py

op_618674d3_d83b_4775_8972_5c33f604c683 = KubernetesPodOperator(
    name="load_from_s3",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'process_data_template' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'process_data_template-0525133308' --cos-dependencies-archive 'load_data_from_s3-618674d3-d83b-4775-8972-5c33f604c683.tar.gz' --file 'work/load_data_from_s3.py' "
    ],
    task_id="load_from_s3",
    env_vars={
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "INPUT_CSV": "sxmlready_encoded_all.csv",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "pipeline-data",
        "OUTPUT_FILENAME": "input_data.pkl",
        "TEST_MODE": "s3",
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


# Operator source: work/validate_data_quality.py

op_data_validation_node = KubernetesPodOperator(
    name="validate_data_quality",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'process_data_template' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'process_data_template-0525133308' --cos-dependencies-archive 'validate_data_quality-data-validation-node.tar.gz' --file 'work/validate_data_quality.py' "
    ],
    task_id="validate_data_quality",
    env_vars={
        "TEST_MODE": "s3",
        "INPUT_SOURCE": "raw",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
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

op_data_validation_node << op_618674d3_d83b_4775_8972_5c33f604c683


# Operator source: work/clean_null_values.py

op_4010f843_aac6_4a94_8306_7bdefaeb5f25 = KubernetesPodOperator(
    name="clean_null_values",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'process_data_template' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'process_data_template-0525133308' --cos-dependencies-archive 'clean_null_values-4010f843-aac6-4a94-8306-7bdefaeb5f25.tar.gz' --file 'work/clean_null_values.py' "
    ],
    task_id="clean_null_values",
    env_vars={
        "TEST_MODE": "s3",
        "INPUT_SOURCE": "validated",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "pipeline-data",
        "OUTPUT_BUCKET": "customer-bucket",
        "NULL_STRATEGY": "fill_median",
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

op_4010f843_aac6_4a94_8306_7bdefaeb5f25 << op_data_validation_node


# Operator source: work/remove_duplicates.py

op_be6e9a7c_9b3d_45d9_aa2f_34fd06ee840b = KubernetesPodOperator(
    name="remove_duplicates",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'process_data_template' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'process_data_template-0525133308' --cos-dependencies-archive 'remove_duplicates-be6e9a7c-9b3d-45d9-aa2f-34fd06ee840b.tar.gz' --file 'work/remove_duplicates.py' "
    ],
    task_id="remove_duplicates",
    env_vars={
        "TEST_MODE": "s3",
        "INPUT_SOURCE": "null_cleaned",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "pipeline-data",
        "OUTPUT_BUCKET": "customer-bucket",
        "DUPLICATE_SUBSET": "customer_id,email",
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

op_be6e9a7c_9b3d_45d9_aa2f_34fd06ee840b << op_4010f843_aac6_4a94_8306_7bdefaeb5f25


# Operator source: work/remove_outliers.py

op_f61cada5_8829_4b5c_8956_1cd2eb84687f = KubernetesPodOperator(
    name="remove_outliers",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'process_data_template' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'process_data_template-0525133308' --cos-dependencies-archive 'remove_outliers-f61cada5-8829-4b5c-8956-1cd2eb84687f.tar.gz' --file 'work/remove_outliers.py' "
    ],
    task_id="remove_outliers",
    env_vars={
        "TEST_MODE": "s3",
        "INPUT_SOURCE": "deduplicated",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "pipeline-data",
        "OUTPUT_BUCKET": "customer-bucket",
        "OUTLIER_METHOD": "iqr",
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

op_f61cada5_8829_4b5c_8956_1cd2eb84687f << op_be6e9a7c_9b3d_45d9_aa2f_34fd06ee840b


# Operator source: work/feature_engineering.py

op_feature_engineering_node = KubernetesPodOperator(
    name="feature_engineering",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'process_data_template' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'process_data_template-0525133308' --cos-dependencies-archive 'feature_engineering-feature-engineering-node.tar.gz' --file 'work/feature_engineering.py' "
    ],
    task_id="feature_engineering",
    env_vars={
        "TEST_MODE": "s3",
        "INPUT_SOURCE": "outliers_removed",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "pipeline-data",
        "OUTPUT_BUCKET": "customer-bucket",
        "FEATURE_SCALING": "true",
        "SCALING_METHOD": "standard",
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

op_feature_engineering_node << op_f61cada5_8829_4b5c_8956_1cd2eb84687f


# Operator source: work/split_data.py

op_data_split_node = KubernetesPodOperator(
    name="split_data",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'process_data_template' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'process_data_template-0525133308' --cos-dependencies-archive 'split_data-data-split-node.tar.gz' --file 'work/split_data.py' "
    ],
    task_id="split_data",
    env_vars={
        "TEST_MODE": "s3",
        "INPUT_SOURCE": "features_engineered",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
        "OUTPUT_PREFIX": "pipeline-data",
        "OUTPUT_BUCKET": "customer-bucket",
        "TRAIN_SIZE": "0.7",
        "VALIDATION_SIZE": "0.15",
        "TEST_SIZE": "0.15",
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

op_data_split_node << op_feature_engineering_node


# Operator source: work/final_validation_report.py

op_final_validation_node = KubernetesPodOperator(
    name="final_validation_reporting",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'process_data_template' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket customer-bucket --cos-directory 'process_data_template-0525133308' --cos-dependencies-archive 'final_validation_report-final-validation-node.tar.gz' --file 'work/final_validation_report.py' "
    ],
    task_id="final_validation_reporting",
    env_vars={
        "TEST_MODE": "s3",
        "MINIO_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "minio123",
        "INPUT_BUCKET": "customer-bucket",
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

op_final_validation_node << op_data_split_node
