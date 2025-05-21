FROM jupyter/scipy-notebook:python-3.11

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libopenmpi-dev \
    libhdf5-dev \
    attr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt file
COPY requirements.txt /tmp/requirements.txt

# Install all Python packages with pinned versions
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Create a pip.conf that prevents package changes
RUN mkdir -p /etc/pip && \
    echo "[global]" > /etc/pip/pip.conf && \
    echo "break-system-packages = false" >> /etc/pip/pip.conf && \
    echo "disable-pip-version-check = true" >> /etc/pip/pip.conf && \
    echo "no-cache-dir = true" >> /etc/pip/pip.conf

# Create a wrapper script that intercepts pip commands
RUN echo '#!/bin/bash\n\
if [[ "$1" == "install" ]]; then\n\
  echo "⚠️ Package installation blocked by system policy"\n\
  echo "⚠️ All required packages are pre-installed in this image"\n\
  echo "⚠️ If you need additional packages, please rebuild the Docker image"\n\
  exit 0\n\
else\n\
  /opt/conda/bin/pip.real "$@"\n\
fi' > /opt/conda/bin/pip.wrapper && \
    chmod +x /opt/conda/bin/pip.wrapper && \
    mv /opt/conda/bin/pip /opt/conda/bin/pip.real && \
    ln -s /opt/conda/bin/pip.wrapper /opt/conda/bin/pip

# Create a fake bootstrapper.py that does nothing but extract dependencies
RUN echo '#!/usr/bin/env python3\n\
import sys\n\
import os\n\
import subprocess\n\
import tempfile\n\
import tarfile\n\
import json\n\
from urllib.request import urlopen\n\
from urllib.parse import urljoin\n\
\n\
# Parse arguments\n\
args = {}\n\
for i in range(1, len(sys.argv)):\n\
    if sys.argv[i].startswith("--"):\n\
        if i + 1 < len(sys.argv) and not sys.argv[i+1].startswith("--"):\n\
            args[sys.argv[i][2:]] = sys.argv[i+1]\n\
        else:\n\
            args[sys.argv[i][2:]] = True\n\
\n\
# Extract required parameters\n\
cos_endpoint = args.get("cos-endpoint")\n\
cos_bucket = args.get("cos-bucket")\n\
cos_directory = args.get("cos-directory")\n\
cos_dependencies_archive = args.get("cos-dependencies-archive")\n\
notebook_file = args.get("file")\n\
pipeline_name = args.get("pipeline-name")\n\
\n\
print("🔵 BOOTSTRAPPER INTERCEPTED - SKIPPING PACKAGE INSTALLATION")\n\
print(f"🔵 Using pre-installed packages from Docker image")\n\
\n\
# Download and extract the dependencies archive\n\
print(f"🔵 Downloading dependencies archive from {cos_endpoint}/{cos_bucket}/{cos_directory}/{cos_dependencies_archive}")\n\
url = urljoin(f"{cos_endpoint}/", f"{cos_bucket}/{cos_directory}/{cos_dependencies_archive}")\n\
with urlopen(url) as response, tempfile.NamedTemporaryFile() as temp_file:\n\
    temp_file.write(response.read())\n\
    temp_file.flush()\n\
    with tarfile.open(temp_file.name, "r:gz") as tar:\n\
        tar.extractall(".")\n\
\n\
# Execute the notebook\n\
print(f"🔵 Executing notebook {notebook_file}")\n\
cmd = ["papermill", notebook_file, notebook_file]\n\
\n\
# Add parameters\n\
for key, value in args.items():\n\
    if isinstance(value, str) and not key.startswith("_"):\n\
        cmd.extend(["-p", key.replace("-", "_"), value])\n\
\n\
# Run the notebook\n\
subprocess.run(cmd, check=True)\n\
print("🔵 Notebook execution completed successfully")\n\
' > /opt/conda/bin/bootstrapper.py && \
    chmod +x /opt/conda/bin/bootstrapper.py

# Set environment variables to use local bootstrapper
ENV ELYRA_BOOTSTRAP_SCRIPT_URL="file:///opt/conda/bin/bootstrapper.py"
ENV ELYRA_SKIP_PACKAGE_INSTALL="true"

# Create working directory and ensure proper permissions
RUN mkdir -p /home/$NB_USER/jupyter-work-dir && \
    chown -R $NB_USER:users /home/$NB_USER/jupyter-work-dir && \
    chmod -R 755 /home/$NB_USER/jupyter-work-dir

# Create working directory for the pipeline
WORKDIR /home/$NB_USER/jupyter-work-dir

# Create additional directories that might be needed
RUN mkdir -p /tmp/rom-pipeline-outputs && \
    chown -R $NB_USER:users /tmp/rom-pipeline-outputs && \
    chmod -R 777 /tmp/rom-pipeline-outputs

# Add environment validation script
RUN echo '#!/usr/bin/env python3\n\
import pkg_resources\n\
import sys\n\
\n\
def validate_environment():\n\
    errors = []\n\
    with open("/tmp/requirements.txt", "r") as f:\n\
        for line in f:\n\
            line = line.strip()\n\
            if not line or line.startswith("#"):\n\
                continue\n\
            \n\
            # Parse package name and version\n\
            parts = line.split("==")\n\
            if len(parts) != 2:\n\
                continue\n\
                \n\
            package, version = parts\n\
            \n\
            try:\n\
                installed = pkg_resources.get_distribution(package)\n\
                if installed.version != version:\n\
                    errors.append(f"{package}: required {version}, found {installed.version}")\n\
            except pkg_resources.DistributionNotFound:\n\
                errors.append(f"{package}: not found")\n\
    \n\
    if errors:\n\
        print("Environment validation failed:")\n\
        for error in errors:\n\
            print(f"  - {error}")\n\
        return False\n\
    else:\n\
        print("Environment validation passed!")\n\
        return True\n\
\n\
if __name__ == "__main__":\n\
    if not validate_environment():\n\
        sys.exit(1)\n\
' > /usr/local/bin/validate_env.py && \
    chmod +x /usr/local/bin/validate_env.py

# Copy requirements.txt to a permanent location for validation
COPY requirements.txt /tmp/requirements.txt

# Switch back to non-root user for better security
USER $NB_UID

# Ensure jupyter-work-dir is usable
RUN mkdir -p /home/$NB_USER/jupyter-work-dir/test && \
    touch /home/$NB_USER/jupyter-work-dir/test/testfile && \
    rm -rf /home/$NB_USER/jupyter-work-dir/test

# Validate the environment
RUN python /usr/local/bin/validate_env.py
