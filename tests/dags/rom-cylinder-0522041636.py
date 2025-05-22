from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.contrib.kubernetes.volume_mount import VolumeMount
from airflow.contrib.kubernetes.volume import Volume
from airflow.kubernetes.secret import Secret
from airflow import DAG
from airflow.utils.dates import days_ago

args = {
    "project_id": "rom-cylinder-0522041636",
}

dag = DAG(
    "rom-cylinder-0522041636",
    default_args=args,
    schedule_interval="@once",
    start_date=days_ago(1),
    description="""
Proper Orthogonal Decomposition (POD) for Cylinder Flow Dataset
    """,
    is_paused_upon_creation=False,
)


# Operator source: work/0_fetch_data.ipynb

op_6014d4a5_f553_44a8_abfa_dae58417a28c = KubernetesPodOperator(
    name="0_fetch_data",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'rom-cylinder' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket rom-data --cos-directory 'rom-cylinder-0522041636' --cos-dependencies-archive '0_fetch_data-6014d4a5-f553-44a8-abfa-dae58417a28c.tar.gz' --file 'work/0_fetch_data.ipynb' "
    ],
    task_id="0_fetch_data",
    env_vars={
        "OUTPUT_DIR": "rom-pipeline/outputs",
        "S3_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_RUNTIME_ENV": "airflow",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "rom-cylinder-{{ ts_nodash }}",
    },
    resources={
        "request_cpu": "1",
        "request_memory": "4G",
    },
    volumes=[],
    volume_mounts=[],
    secrets=[],
    annotations={
        "security-context.kubernetes.io/runAsUser": "1000",
        "security-context.kubernetes.io/fsGroup": "100",
        "security-context.kubernetes.io/allowPrivilegeEscalation": "false",
    },
    labels={},
    tolerations=[],
    in_cluster=True,
    config_file="None",
    dag=dag,
)


# Operator source: work/1_preprocess_data.ipynb

op_f029183f_8c3e_458f_aeea_79bfd8c119b0 = KubernetesPodOperator(
    name="1_preprocess_data",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'rom-cylinder' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket rom-data --cos-directory 'rom-cylinder-0522041636' --cos-dependencies-archive '1_preprocess_data-f029183f-8c3e-458f-aeea-79bfd8c119b0.tar.gz' --file 'work/1_preprocess_data.ipynb' "
    ],
    task_id="1_preprocess_data",
    env_vars={
        "OUTPUT_DIR": "rom-pipeline/outputs",
        "S3_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_RUNTIME_ENV": "airflow",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "rom-cylinder-{{ ts_nodash }}",
    },
    resources={
        "request_cpu": "6",
        "request_memory": "10G",
    },
    volumes=[],
    volume_mounts=[],
    secrets=[],
    annotations={
        "security-context.kubernetes.io/runAsUser": "1000",
        "security-context.kubernetes.io/fsGroup": "100",
        "security-context.kubernetes.io/allowPrivilegeEscalation": "false",
    },
    labels={},
    tolerations=[],
    in_cluster=True,
    config_file="None",
    dag=dag,
)

op_f029183f_8c3e_458f_aeea_79bfd8c119b0 << op_6014d4a5_f553_44a8_abfa_dae58417a28c


# Operator source: work/2_rom_modeling.ipynb

op_4a25aef9_e4dd_4b4a_b281_5ff2a04ad00a = KubernetesPodOperator(
    name="2_rom_modeling",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'rom-cylinder' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket rom-data --cos-directory 'rom-cylinder-0522041636' --cos-dependencies-archive '2_rom_modeling-4a25aef9-e4dd-4b4a-b281-5ff2a04ad00a.tar.gz' --file 'work/2_rom_modeling.ipynb' "
    ],
    task_id="2_rom_modeling",
    env_vars={
        "OUTPUT_DIR": "rom-pipeline/outputs",
        "S3_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_RUNTIME_ENV": "airflow",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "rom-cylinder-{{ ts_nodash }}",
    },
    resources={
        "request_cpu": "6",
        "request_memory": "10G",
    },
    volumes=[],
    volume_mounts=[],
    secrets=[],
    annotations={
        "security-context.kubernetes.io/runAsUser": "1000",
        "security-context.kubernetes.io/fsGroup": "100",
        "security-context.kubernetes.io/allowPrivilegeEscalation": "false",
    },
    labels={},
    tolerations=[],
    in_cluster=True,
    config_file="None",
    dag=dag,
)

op_4a25aef9_e4dd_4b4a_b281_5ff2a04ad00a << op_f029183f_8c3e_458f_aeea_79bfd8c119b0


# Operator source: work/3_visuazalition.ipynb

op_501534df_7597_4371_b989_e422c7eec230 = KubernetesPodOperator(
    name="3_visuazalition",
    namespace="airflow-elyra",
    image="continuumio/anaconda3@sha256:a2816acd3acda208d92e0bf6c11eb41fda9009ea20f24e123dbf84bb4bd4c4b8",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'rom-cylinder' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket rom-data --cos-directory 'rom-cylinder-0522041636' --cos-dependencies-archive '3_visuazalition-501534df-7597-4371-b989-e422c7eec230.tar.gz' --file 'work/3_visuazalition.ipynb' "
    ],
    task_id="3_visuazalition",
    env_vars={
        "OUTPUT_DIR": "rom-pipeline/outputs",
        "S3_ENDPOINT": "http://minio.minio-system.svc.cluster.local:9000",
        "AWS_ACCESS_KEY_ID": "minio",
        "AWS_SECRET_ACCESS_KEY": "minio123",
        "ELYRA_RUNTIME_ENV": "airflow",
        "ELYRA_ENABLE_PIPELINE_INFO": "True",
        "ELYRA_RUN_NAME": "rom-cylinder-{{ ts_nodash }}",
    },
    resources={
        "request_cpu": "6",
        "request_memory": "10G",
    },
    volumes=[],
    volume_mounts=[],
    secrets=[],
    annotations={
        "security-context.kubernetes.io/runAsUser": "1000",
        "security-context.kubernetes.io/fsGroup": "100",
        "security-context.kubernetes.io/allowPrivilegeEscalation": "false",
    },
    labels={},
    tolerations=[],
    in_cluster=True,
    config_file="None",
    dag=dag,
)

op_501534df_7597_4371_b989_e422c7eec230 << op_4a25aef9_e4dd_4b4a_b281_5ff2a04ad00a
