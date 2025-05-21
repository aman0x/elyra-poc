FROM jupyter/scipy-notebook:python-3.11

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libopenmpi-dev \
    libhdf5-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt file
COPY requirements.txt /tmp/requirements.txt

# Copy custom bootstrapper and patch scripts
COPY custom_bootstrapper.py /opt/conda/bin/custom_bootstrapper.py
COPY patch_dag.py /opt/conda/bin/patch_dag.py

# Install all Python packages with pinned versions
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    # Create a backup of installed packages
    pip freeze > /opt/conda/requirements-current.txt && \
    # Make scripts executable
    chmod +x /opt/conda/bin/custom_bootstrapper.py && \
    chmod +x /opt/conda/bin/patch_dag.py

# Make pip directories writable for all users
RUN chmod -R 777 /opt/conda/lib/python3.11/site-packages && \
    chmod -R 777 /opt/conda/bin && \
    mkdir -p /.local && chmod -R 777 /.local && \
    mkdir -p /.cache && chmod -R 777 /.cache && \
    mkdir -p /home/jovyan/.cache && chmod -R 777 /home/jovyan/.cache && \
    mkdir -p /home/jovyan/.local && chmod -R 777 /home/jovyan/.local

# Create working directory and ensure proper permissions
RUN mkdir -p /home/jovyan/jupyter-work-dir && \
    chown -R jovyan:users /home/jovyan/jupyter-work-dir && \
    chmod -R 777 /home/jovyan/jupyter-work-dir

# Create additional directories that might be needed
RUN mkdir -p /tmp/rom-pipeline-outputs && \
    chmod -R 777 /tmp/rom-pipeline-outputs

# Copy requirements.txt to a permanent location for reference
COPY requirements.txt /opt/conda/requirements.txt

# Switch back to non-root user for better security
USER $NB_UID

# Set working directory
WORKDIR /home/$NB_USER/jupyter-work-dir
