FROM jupyter/scipy-notebook:python-3.11

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libopenmpi-dev \
    libhdf5-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a requirements.txt file with exact Elyra versions
# These versions are extracted directly from the error logs
RUN echo "# Elyra required packages with exact versions\n\
jinja2==3.0.3\n\
jupyter-core==4.11.2\n\
jupyter-client==7.3.1\n\
nbclient==0.6.3\n\
nbformat==5.4.0\n\
traitlets==5.1.1\n\
markupsafe==2.1.1\n\
pyzmq==24.0.1\n\
tornado==6.1\n\
prompt-toolkit==3.0.30\n\
requests==2.27.1\n\
urllib3==1.26.9\n\
ipykernel==6.13.0\n\
ipython==8.10.0\n\
papermill==2.3.4\n\
minio==7.1.8\n\
# Install both lxml 4.9.3 and lxml_html_clean to ensure compatibility\n\
lxml==4.9.3\n\
lxml_html_clean\n\
\n\
# ROM pipeline required packages\n\
boto3==1.28.40\n\
botocore==1.31.40\n\
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
tenacity==9.1.2\n\
textwrap3==0.9.2\n\
ansiwrap==0.8.4\n\
mistune==0.8.4\n\
nbconvert==6.5.1" > /tmp/requirements.txt

# Uninstall any conflicting packages first
RUN pip uninstall -y jupyter-core jupyter-client jinja2 nbclient nbformat nbconvert traitlets markupsafe pyzmq tornado prompt-toolkit requests urllib3 ipykernel ipython papermill minio lxml

# Install all Python packages with pinned versions
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    # Create a backup of installed packages
    pip freeze > /opt/conda/requirements-current.txt

# Create a patch for nbconvert to use lxml_html_clean if available
RUN echo 'import sys\n\
import os\n\
\n\
# Create a patch file for nbconvert to handle lxml.html.clean import error\n\
patch_file = "/opt/conda/lib/python3.11/site-packages/nbconvert_lxml_patch.py"\n\
with open(patch_file, "w") as f:\n\
    f.write("""\n\
# Patch for nbconvert to handle lxml.html.clean import error\n\
import sys\n\
from importlib.util import find_spec\n\
\n\
# Check if original module exists\n\
original_import = __import__\n\
\n\
def patched_import(name, globals=None, locals=None, fromlist=(), level=0):\n\
    try:\n\
        return original_import(name, globals, locals, fromlist, level)\n\
    except ImportError as e:\n\
        # Only handle lxml.html.clean import error\n\
        if name == "lxml.html.clean" or (name == "lxml.html" and "clean" in fromlist):\n\
            # Check if lxml_html_clean is available\n\
            if find_spec("lxml_html_clean"):\n\
                if name == "lxml.html.clean":\n\
                    return original_import("lxml_html_clean", globals, locals, fromlist, level)\n\
                elif "clean" in fromlist:\n\
                    # Import lxml_html_clean and add it to lxml.html\n\
                    lxml_html = original_import("lxml.html", globals, locals, [], level)\n\
                    lxml_html_clean = original_import("lxml_html_clean", globals, locals, fromlist, level)\n\
                    setattr(lxml_html, "clean", lxml_html_clean)\n\
                    return lxml_html\n\
        # Re-raise the original exception\n\
        raise e\n\
\n\
# Replace the built-in __import__ function\n\
sys.__import__ = patched_import\n\
sys.modules["builtins"].__import__ = patched_import\n\
""")\n\
\n\
# Create a sitecustomize.py file to load the patch at Python startup\n\
site_customize = "/opt/conda/lib/python3.11/site-packages/sitecustomize.py"\n\
with open(site_customize, "w") as f:\n\
    f.write("""\n\
# Load nbconvert lxml patch\n\
try:\n\
    exec(open("/opt/conda/lib/python3.11/site-packages/nbconvert_lxml_patch.py").read())\n\
except Exception as e:\n\
    print(f"Error loading nbconvert lxml patch: {e}")\n\
""")\n\
' > /tmp/create_patch.py && python3 /tmp/create_patch.py

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
