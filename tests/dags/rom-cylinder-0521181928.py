from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.contrib.kubernetes.volume_mount import VolumeMount
from airflow.contrib.kubernetes.volume import Volume
from airflow.kubernetes.secret import Secret
from airflow import DAG
from airflow.utils.dates import days_ago

args = {
    "project_id": "rom-cylinder-0521181928",
}

dag = DAG(
    "rom-cylinder-0521181928",
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
    image="ghcr.io/victorfonseca/rom-fluid-dynamics:latest",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && python3 -c 'import sys; import os; import subprocess; import tempfile; import tarfile; from urllib.request import urlopen; from urllib.parse import urljoin; cos_endpoint = \"http://minio.minio-system.svc.cluster.local:9000\"; cos_bucket = \"rom-data\"; cos_directory = \"rom-cylinder-0521181928\"; cos_dependencies_archive = \"0_fetch_data-6014d4a5-f553-44a8-abfa-dae58417a28c.tar.gz\"; notebook_file = \"work/0_fetch_data.ipynb\"; print(f\"Downloading dependencies from {cos_endpoint}/{cos_bucket}/{cos_directory}/{cos_dependencies_archive}\" ); url = urljoin(f\"{cos_endpoint}/\", f\"{cos_bucket}/{cos_directory}/{cos_dependencies_archive}\"); with urlopen(url) as response, tempfile.NamedTemporaryFile() as temp_file: temp_file.write(response.read()); temp_file.flush(); with tarfile.open(temp_file.name, \"r:gz\") as tar: tar.extractall(\".\"); print(f\"Executing notebook {notebook_file}\"); subprocess.run([\"papermill\", notebook_file, notebook_file, \"-p\", \"cos-endpoint\", cos_endpoint, \"-p\", \"cos-bucket\", cos_bucket, \"-p\", \"cos-directory\", cos_directory, \"-p\", \"cos-dependencies-archive\", cos_dependencies_archive], check=True)'"
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
    image="ghcr.io/victorfonseca/rom-fluid-dynamics:latest",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && python3 -c 'import sys; import os; import subprocess; import tempfile; import tarfile; from urllib.request import urlopen; from urllib.parse import urljoin; cos_endpoint = \"http://minio.minio-system.svc.cluster.local:9000\"; cos_bucket = \"rom-data\"; cos_directory = \"rom-cylinder-0521181928\"; cos_dependencies_archive = \"0_fetch_data-6014d4a5-f553-44a8-abfa-dae58417a28c.tar.gz\"; notebook_file = \"work/0_fetch_data.ipynb\"; print(f\"Downloading dependencies from {cos_endpoint}/{cos_bucket}/{cos_directory}/{cos_dependencies_archive}\" ); url = urljoin(f\"{cos_endpoint}/\", f\"{cos_bucket}/{cos_directory}/{cos_dependencies_archive}\"); with urlopen(url) as response, tempfile.NamedTemporaryFile() as temp_file: temp_file.write(response.read()); temp_file.flush(); with tarfile.open(temp_file.name, \"r:gz\") as tar: tar.extractall(\".\"); print(f\"Executing notebook {notebook_file}\"); subprocess.run([\"papermill\", notebook_file, notebook_file, \"-p\", \"cos-endpoint\", cos_endpoint, \"-p\", \"cos-bucket\", cos_bucket, \"-p\", \"cos-directory\", cos_directory, \"-p\", \"cos-dependencies-archive\", cos_dependencies_archive], check=True)'"
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
    image="ghcr.io/victorfonseca/rom-fluid-dynamics:latest",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && python3 -c 'import sys; import os; import subprocess; import tempfile; import tarfile; from urllib.request import urlopen; from urllib.parse import urljoin; cos_endpoint = \"http://minio.minio-system.svc.cluster.local:9000\"; cos_bucket = \"rom-data\"; cos_directory = \"rom-cylinder-0521181928\"; cos_dependencies_archive = \"0_fetch_data-6014d4a5-f553-44a8-abfa-dae58417a28c.tar.gz\"; notebook_file = \"work/0_fetch_data.ipynb\"; print(f\"Downloading dependencies from {cos_endpoint}/{cos_bucket}/{cos_directory}/{cos_dependencies_archive}\" ); url = urljoin(f\"{cos_endpoint}/\", f\"{cos_bucket}/{cos_directory}/{cos_dependencies_archive}\"); with urlopen(url) as response, tempfile.NamedTemporaryFile() as temp_file: temp_file.write(response.read()); temp_file.flush(); with tarfile.open(temp_file.name, \"r:gz\") as tar: tar.extractall(\".\"); print(f\"Executing notebook {notebook_file}\"); subprocess.run([\"papermill\", notebook_file, notebook_file, \"-p\", \"cos-endpoint\", cos_endpoint, \"-p\", \"cos-bucket\", cos_bucket, \"-p\", \"cos-directory\", cos_directory, \"-p\", \"cos-dependencies-archive\", cos_dependencies_archive], check=True)'"
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
    image="ghcr.io/victorfonseca/rom-fluid-dynamics:latest",
    cmds=["sh", "-c"],
    arguments=[
        "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && python3 -c 'import sys; import os; import subprocess; import tempfile; import tarfile; from urllib.request import urlopen; from urllib.parse import urljoin; cos_endpoint = \"http://minio.minio-system.svc.cluster.local:9000\"; cos_bucket = \"rom-data\"; cos_directory = \"rom-cylinder-0521181928\"; cos_dependencies_archive = \"0_fetch_data-6014d4a5-f553-44a8-abfa-dae58417a28c.tar.gz\"; notebook_file = \"work/0_fetch_data.ipynb\"; print(f\"Downloading dependencies from {cos_endpoint}/{cos_bucket}/{cos_directory}/{cos_dependencies_archive}\" ); url = urljoin(f\"{cos_endpoint}/\", f\"{cos_bucket}/{cos_directory}/{cos_dependencies_archive}\"); with urlopen(url) as response, tempfile.NamedTemporaryFile() as temp_file: temp_file.write(response.read()); temp_file.flush(); with tarfile.open(temp_file.name, \"r:gz\") as tar: tar.extractall(\".\"); print(f\"Executing notebook {notebook_file}\"); subprocess.run([\"papermill\", notebook_file, notebook_file, \"-p\", \"cos-endpoint\", cos_endpoint, \"-p\", \"cos-bucket\", cos_bucket, \"-p\", \"cos-directory\", cos_directory, \"-p\", \"cos-dependencies-archive\", cos_dependencies_archive], check=True)'"
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
