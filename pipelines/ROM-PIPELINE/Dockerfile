FROM jupyter/scipy-notebook:latest

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libopenmpi-dev \
    libhdf5-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install all Python packages needed for the ROM pipeline
RUN pip install --no-cache-dir \
    boto3 \
    botocore \
    numpy \
    scipy \
    matplotlib \
    pandas \
    h5py \
    plotly \
    dash \
    jupyterlab \
    ipykernel \
    scikit-learn \
    minio \
    pyyaml \
    tqdm

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

# Switch back to non-root user for better security
USER $NB_UID

# Ensure jupyter-work-dir is usable
RUN mkdir -p /home/$NB_USER/jupyter-work-dir/test && \
    touch /home/$NB_USER/jupyter-work-dir/test/testfile && \
    rm -rf /home/$NB_USER/jupyter-work-dir/test