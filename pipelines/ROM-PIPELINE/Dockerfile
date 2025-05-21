FROM jupyter/scipy-notebook:python-3.11

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libopenmpi-dev \
    libhdf5-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a requirements.txt file with exact Elyra versions
RUN echo "# Elyra required packages with exact versions\n\
jinja2==3.0.3\n\
jupyter-core==4.11.2\n\
jupyter-client==7.3.1\n\
nbclient==0.7.0\n\
nbformat==5.4.0\n\
nbconvert==6.5.1\n\
traitlets==5.2.2\n\
markupsafe==2.1.1\n\
pyzmq==24.0.1\n\
tornado==6.1\n\
prompt-toolkit==3.0.30\n\
requests==2.27.1\n\
urllib3==1.26.16\n\
\n\
# ROM pipeline required packages\n\
boto3==1.28.40\n\
botocore==1.31.40\n\
minio==7.2.15\n\
h5py==3.9.0\n\
numpy==1.24.3\n\
matplotlib==3.7.2\n\
scipy==1.11.3\n\
pandas==2.0.3\n\
scikit-learn==1.3.0\n\
plotly==5.15.0\n\
dash==3.0.4\n\
pyyaml==6.0.1\n\
tqdm==4.66.1\n\
papermill==2.3.4\n\
ipykernel==6.13.0\n\
ipython==8.10.0" > /tmp/requirements.txt

# Install all Python packages with pinned versions
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    # Create a backup of installed packages
    pip freeze > /opt/conda/requirements-current.txt

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

# Create empty requirements files to prevent bootstrapper errors
RUN touch /opt/conda/requirements-elyra.txt && \
    chmod 666 /opt/conda/requirements-elyra.txt

# Switch back to non-root user for better security
USER $NB_UID

# Set working directory
WORKDIR /home/$NB_USER/jupyter-work-dir
