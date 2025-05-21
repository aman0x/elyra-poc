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
RUN pip install --no-cache-dir -r /tmp/requirements.txt

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

# Create a requirements-current.txt file to avoid bootstrapper errors
RUN touch /opt/conda/requirements-current.txt && \
    chmod 777 /opt/conda/requirements-current.txt

# Add environment validation script
RUN echo '#!/usr/bin/env python3\n\
import pkg_resources\n\
import sys\n\
import os\n\
\n\
def validate_environment():\n\
    # Check if pip can write to site-packages\n\
    site_packages = "/opt/conda/lib/python3.11/site-packages"\n\
    if not os.access(site_packages, os.W_OK):\n\
        print(f"ERROR: {site_packages} is not writable")\n\
        return False\n\
    \n\
    # Check if pip binary is writable\n\
    pip_path = "/opt/conda/bin/pip"\n\
    if not os.access(pip_path, os.W_OK):\n\
        print(f"ERROR: {pip_path} is not writable")\n\
        return False\n\
    \n\
    # Check if we can create files in /tmp\n\
    try:\n\
        with open("/tmp/test_write.txt", "w") as f:\n\
            f.write("test")\n\
        os.remove("/tmp/test_write.txt")\n\
    except Exception as e:\n\
        print(f"ERROR: Cannot write to /tmp: {e}")\n\
        return False\n\
    \n\
    # Check if we can install a package\n\
    try:\n\
        import subprocess\n\
        result = subprocess.run([sys.executable, "-m", "pip", "install", "--user", "six"], \n\
                               capture_output=True, text=True)\n\
        if result.returncode != 0:\n\
            print(f"ERROR: Cannot install packages: {result.stderr}")\n\
            return False\n\
    except Exception as e:\n\
        print(f"ERROR: Package installation test failed: {e}")\n\
        return False\n\
    \n\
    print("Environment validation passed!")\n\
    return True\n\
\n\
if __name__ == "__main__":\n\
    if not validate_environment():\n\
        sys.exit(1)\n\
' > /usr/local/bin/validate_env.py && \
    chmod +x /usr/local/bin/validate_env.py

# Copy requirements.txt to a permanent location for reference
COPY requirements.txt /opt/conda/requirements.txt

# Switch back to non-root user for better security
USER $NB_UID

# Validate the environment
RUN python /usr/local/bin/validate_env.py

# Set working directory
WORKDIR /home/$NB_USER/jupyter-work-dir
