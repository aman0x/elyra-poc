# Fixing Elyra Pipeline Package Downgrade Issues

## The Problem: Elyra's Forced Package Installation

When running pipelines with Elyra and Airflow, you may encounter persistent package conflicts and missing modules despite having all required packages in your Docker image. This happens because Elyra forcibly downloads and executes its own bootstrapper script, which installs specific (often older) versions of packages, overriding your carefully prepared environment.

### Symptoms

1. Packages like `boto3` are missing despite being in your Docker image
2. Critical packages are downgraded:
   - Jinja2 downgraded from 3.1.2 to 3.0.3
   - jupyter-core downgraded from 5.4.0 to 4.11.2
   - jupyter-client downgraded from 8.4.0 to 7.3.1

### Root Cause Analysis

When Elyra exports a pipeline to Airflow, it generates a DAG file with hardcoded commands that:

1. Download the bootstrapper script from GitHub:
   ```
   https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py
   ```

2. Download requirements file from GitHub:
   ```
   https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt
   ```

3. Execute `python3 -m pip install` to force specific package versions

This happens regardless of environment variables or Docker image configuration, making it impossible to prevent through standard means.

## Solutions We Tried (That Didn't Work)

### 1. Environment Variables

Setting `ELYRA_SKIP_PACKAGE_INSTALL=true` in the pipeline configuration or Dockerfile doesn't work because the DAG generation process hardcodes the bootstrapper download and execution.

### 2. Docker Image with Pip Wrappers

Creating a Docker image that intercepts pip commands doesn't work because:
- The bootstrapper can use `python -m pip` to bypass direct pip wrappers
- The bootstrapper runs inside the container at runtime, after the image is built

## The Solution: Patching the DAG File

The only reliable solution is to modify the generated DAG file to remove the bootstrapper and pip install commands.

### How to Patch Your DAG

For each KubernetesPodOperator in your DAG file, replace the `arguments` section that looks like:

```python
arguments=[
    "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output bootstrapper.py && echo 'Downloading https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/etc/generic/requirements-elyra.txt --output requirements-elyra.txt && python3 -m pip install packaging && python3 -m pip freeze > requirements-current.txt && python3 bootstrapper.py --pipeline-name 'rom-cylinder' --cos-endpoint http://minio.minio-system.svc.cluster.local:9000 --cos-bucket rom-data --cos-directory 'rom-cylinder-0521181928' --cos-dependencies-archive '0_fetch_data-6014d4a5-f553-44a8-abfa-dae58417a28c.tar.gz' --file 'work/0_fetch_data.ipynb' "
],
```

With this simplified version:

```python
arguments=[
    "mkdir -p ./jupyter-work-dir/ && cd ./jupyter-work-dir/ && python3 -c 'import sys; import os; import subprocess; import tempfile; import tarfile; from urllib.request import urlopen; from urllib.parse import urljoin; cos_endpoint = \"http://minio.minio-system.svc.cluster.local:9000\"; cos_bucket = \"rom-data\"; cos_directory = \"rom-cylinder-0521181928\"; cos_dependencies_archive = \"0_fetch_data-6014d4a5-f553-44a8-abfa-dae58417a28c.tar.gz\"; notebook_file = \"work/0_fetch_data.ipynb\"; print(f\"Downloading dependencies from {cos_endpoint}/{cos_bucket}/{cos_directory}/{cos_dependencies_archive}\" ); url = urljoin(f\"{cos_endpoint}/\", f\"{cos_bucket}/{cos_directory}/{cos_dependencies_archive}\"); with urlopen(url) as response, tempfile.NamedTemporaryFile() as temp_file: temp_file.write(response.read()); temp_file.flush(); with tarfile.open(temp_file.name, \"r:gz\") as tar: tar.extractall(\".\"); print(f\"Executing notebook {notebook_file}\"); subprocess.run([\"papermill\", notebook_file, notebook_file, \"-p\", \"cos-endpoint\", cos_endpoint, \"-p\", \"cos-bucket\", cos_bucket, \"-p\", \"cos-directory\", cos_directory, \"-p\", \"cos-dependencies-archive\", cos_dependencies_archive], check=True)'"
],
```

### What This Patch Does

1. **Skips bootstrapper download**: No more downloading from GitHub
2. **Skips requirements download**: No more downloading requirements-elyra.txt
3. **Skips pip install**: No more forced package installations or downgrades
4. **Preserves core functionality**: Still extracts dependencies and runs notebooks with papermill
5. **Maintains parameters**: All the same parameters are passed to the notebook

### Step-by-Step Process

1. Export your pipeline from Elyra to Airflow
2. Locate the generated DAG file in your Airflow DAGs directory
3. Edit the file to replace each `arguments` section as shown above
4. Make sure to update the specific parameters for each operator:
   - `cos_dependencies_archive`
   - `notebook_file`
5. Save the modified DAG file
6. Restart Airflow if necessary to pick up the changes

## Why This Approach Works

This solution works because it:

1. **Completely bypasses Elyra's bootstrapper**: No more forced package installations
2. **Preserves your Docker environment**: Your carefully prepared packages remain intact
3. **Maintains pipeline functionality**: All notebooks still run with the correct parameters
4. **Is resilient to Elyra updates**: Works regardless of Elyra version changes

## Long-term Considerations

This issue is being tracked by the Elyra team (GitHub discussion #2945), but there's no official solution yet. Until Elyra provides a proper way to disable package installation, you'll need to apply this patch each time you export a pipeline.

To make this process easier, you could:

1. Create a script to automatically patch DAG files after export
2. Set up a watcher to monitor your DAGs directory and apply patches automatically
3. Contribute to the Elyra project to implement proper support for skipping package installation

## References

- [Elyra GitHub Discussion #2945](https://github.com/elyra-ai/elyra/discussions/2945)
- [Elyra Documentation: Running in Air-gapped Environments](https://elyra.readthedocs.io/en/latest/recipes/running-elyra-in-air-gapped-environment.html)
