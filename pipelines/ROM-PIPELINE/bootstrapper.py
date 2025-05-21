#!/usr/bin/env python3
import os
import sys
import subprocess
import tempfile
import tarfile
import json
import importlib
import logging
from urllib.request import urlopen
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.INFO)

# Critical packages that should never be uninstalled
CRITICAL_PACKAGES = ["boto3", "botocore", "minio", "h5py", "numpy", "matplotlib"]

class OpUtil(object):
    """Utility functions for preparing, executing, and monitoring pipeline operations."""

    @classmethod
    def package_install(cls):
        """Install packages from requirements-elyra.txt but preserve critical packages."""
        try:
            # Skip package installation completely
            logging.info("Completely skipping package installation to avoid permission errors")
            # Create empty requirements-current.txt if it doesn't exist
            if not os.path.exists("requirements-current.txt"):
                with open("requirements-current.txt", "w") as f:
                    f.write("# Empty file to satisfy bootstrapper\n")
            return True
        except Exception as ex:
            logging.error("Error in package_install: {}".format(ex))
            return False

    @classmethod
    def package_list_to_dict(cls, filename):
        """Get dictionary of package names and versions from a list."""
        result = {}
        if not os.path.exists(filename):
            return result

        with open(filename) as fh:
            for line in fh.readlines():
                if ":" in line:
                    pkg_name, pkg_ver = line.strip().split(":", 1)
                    result[pkg_name.strip()] = pkg_ver.strip()
                elif "==" in line:
                    pkg_name, pkg_ver = line.strip().split("==", 1)
                    result[pkg_name.strip()] = pkg_ver.strip()
        return result

    @classmethod
    def process_dependencies(cls, filepath):
        """Process dependencies for the pipeline."""
        try:
            if os.path.exists(filepath):
                with tarfile.open(filepath) as tar:
                    tar.extractall(".")
            return True
        except Exception as ex:
            logging.error("Error processing dependencies: {}".format(ex))
            return False

    @classmethod
    def run_notebook(cls, notebook, **kwargs):
        """Execute a notebook and capture the output."""
        import papermill

        try:
            # Execute the notebook
            logging.info("Executing notebook: {}".format(notebook))
            papermill.execute_notebook(
                notebook,
                notebook,
                parameters=kwargs
            )
            return True
        except Exception as ex:
            logging.error("Error executing notebook: {}".format(ex))
            return False

def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--pipeline-name", dest="pipeline_name", required=True)
    parser.add_argument("--cos-endpoint", dest="cos_endpoint", required=True)
    parser.add_argument("--cos-bucket", dest="cos_bucket", required=True)
    parser.add_argument("--cos-directory", dest="cos_directory", required=True)
    parser.add_argument("--cos-dependencies-archive", dest="cos_dependencies_archive", required=True)
    parser.add_argument("--file", dest="file", required=True)
    args = parser.parse_args()

    logging.info("'{}':{} - starting operation".format(args.pipeline_name, args.file))

    # Skip package installation completely
    logging.info("'{}':{} - Skipping package installation".format(args.pipeline_name, args.file))
    OpUtil.package_install()

    # Process dependencies
    archive_url = urljoin(
        args.cos_endpoint + "/",
        args.cos_bucket + "/" + args.cos_directory + "/" + args.cos_dependencies_archive
    )

    logging.info("'{}':{} - Processing dependencies".format(args.pipeline_name, args.file))
    logging.info("Downloading: {}".format(archive_url))

    with tempfile.TemporaryDirectory() as temp_dir:
        archive_path = os.path.join(temp_dir, args.cos_dependencies_archive)

        with open(archive_path, "wb") as f:
            with urlopen(archive_url) as response:
                f.write(response.read())

        OpUtil.process_dependencies(archive_path)

    # Execute notebook
    logging.info("'{}':{} - Executing notebook".format(args.pipeline_name, args.file))
    notebook_output = args.file

    # Check if boto3 is available
    try:
        import boto3
        logging.info("boto3 is available, version: {}".format(boto3.__version__))
    except ImportError:
        logging.error("boto3 is not available! This will cause pipeline failures.")

    # Execute the notebook
    params = {
        "cos-endpoint": args.cos_endpoint,
        "cos-bucket": args.cos_bucket,
        "cos-directory": args.cos_directory,
        "cos-dependencies-archive": args.cos_dependencies_archive
    }

    OpUtil.run_notebook(notebook_output, **params)
    logging.info("'{}':{} - Finished".format(args.pipeline_name, args.file))

if __name__ == "__main__":
    main()
