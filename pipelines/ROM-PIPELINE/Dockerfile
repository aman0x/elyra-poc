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

# Install all Python packages with pinned versions
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

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
