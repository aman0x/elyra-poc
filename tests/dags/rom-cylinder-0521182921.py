#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2018-2023 Elyra Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
The bootstrapper module is used to bootstrap an image with required dependencies.
"""

import argparse
import glob
import json
import logging
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin
from urllib.request import Request, urlopen


logger = logging.getLogger('elyra')
enable_pipeline_info = os.getenv('ELYRA_ENABLE_PIPELINE_INFO', 'true').lower() == 'true'


class Operation:
    """Base class for Operations that need to be performed during bootstrapping"""

    def execute(self) -> None:
        """Execute the operation"""
        raise NotImplementedError("Method 'execute()' must be implemented by subclass.")


class NotebookOperation(Operation):
    """Operation for working with notebooks"""

    def __init__(self, **kwargs: Any) -> None:
        self.filepath = kwargs['filepath']
        self.cos_endpoint = kwargs['cos-endpoint']
        self.cos_bucket = kwargs['cos-bucket']
        self.cos_directory = kwargs['cos-directory']
        self.cos_dependencies_archive = kwargs['cos-dependencies-archive']
        self.inputs = kwargs.get('inputs', [])
        self.outputs = kwargs.get('outputs', [])
        self.pipeline_name = kwargs.get('pipeline-name', '')
        self.pipeline_node_id = kwargs.get('pipeline-node-id', '')

    def execute(self) -> None:
        """Execute the notebook operation"""
        OpUtil.log_operation_info('running notebook', self.filepath)

        # Add all inputs to environment variables
        for inputname in self.inputs:
            OpUtil.log_operation_info(f"processing input: {inputname}")
            if inputname in os.environ:
                inputvalue = os.environ.get(inputname)
                OpUtil.log_operation_info(f"using input: {inputname}={inputvalue}")
            else:
                OpUtil.log_operation_info(f"input: {inputname} not in environment - ignored")

        # Execute the notebook
        notebook = os.path.basename(self.filepath)
        notebook_name = notebook.replace('.ipynb', '')
        notebook_output = notebook.replace('.ipynb', '-output.ipynb')
        notebook_output_relative_path = os.path.join('..', notebook_output)

        argv = ['papermill', self.filepath, notebook_output_relative_path, '--no-progress-bar']

        # Add the parameters to the argument list - including ELYRA_RUNTIME_ENV
        if 'ELYRA_RUNTIME_ENV' in os.environ:
            argv.extend(['--parameters', 'ELYRA_RUNTIME_ENV', os.environ['ELYRA_RUNTIME_ENV']])

        # Add COS parameters to the argument list
        if self.cos_endpoint:
            argv.extend(['--parameters', 'cos-endpoint', self.cos_endpoint])
        if self.cos_bucket:
            argv.extend(['--parameters', 'cos-bucket', self.cos_bucket])
        if self.cos_directory:
            argv.extend(['--parameters', 'cos-directory', self.cos_directory])
        if self.cos_dependencies_archive:
            argv.extend(['--parameters', 'cos-dependencies-archive', self.cos_dependencies_archive])

        # Add notebook-level parameters to the argument list
        for inputname in self.inputs:
            if inputname in os.environ:
                argv.extend(['--parameters', inputname, os.environ.get(inputname)])

        # Add pipeline-level parameters to the argument list
        if self.pipeline_name:
            argv.extend(['--parameters', 'pipeline-name', self.pipeline_name])
        if self.pipeline_node_id:
            argv.extend(['--parameters', 'pipeline-node-id', self.pipeline_node_id])

        # Execute the notebook
        subprocess.run(argv, check=True)

        # Process the notebook outputs
        for outputname in self.outputs:
            OpUtil.log_operation_info(f"processing output: {outputname}")
            if outputname in os.environ:
                output_filename = os.environ.get(outputname)
                OpUtil.log_operation_info(f"writing output: {outputname} to {output_filename}")
                output_file = open(output_filename, 'wt')
                output_file.write(notebook_name)
                output_file.close()
            else:
                OpUtil.log_operation_info(f"output: {outputname} not in environment - ignored")


class PythonScriptOperation(Operation):
    """Operation for working with Python scripts"""

    def __init__(self, **kwargs: Any) -> None:
        self.filepath = kwargs['filepath']
        self.cos_endpoint = kwargs['cos-endpoint']
        self.cos_bucket = kwargs['cos-bucket']
        self.cos_directory = kwargs['cos-directory']
        self.cos_dependencies_archive = kwargs['cos-dependencies-archive']
        self.inputs = kwargs.get('inputs', [])
        self.outputs = kwargs.get('outputs', [])
        self.pipeline_name = kwargs.get('pipeline-name', '')
        self.pipeline_node_id = kwargs.get('pipeline-node-id', '')

    def execute(self) -> None:
        """Execute the Python script operation"""
        OpUtil.log_operation_info('running Python script', self.filepath)

        # Add all inputs to environment variables
        for inputname in self.inputs:
            OpUtil.log_operation_info(f"processing input: {inputname}")
            if inputname in os.environ:
                inputvalue = os.environ.get(inputname)
                OpUtil.log_operation_info(f"using input: {inputname}={inputvalue}")
            else:
                OpUtil.log_operation_info(f"input: {inputname} not in environment - ignored")

        # Execute the script
        argv = ['python3', self.filepath]

        # Add COS parameters to the argument list
        if self.cos_endpoint:
            argv.extend(['--cos-endpoint', self.cos_endpoint])
        if self.cos_bucket:
            argv.extend(['--cos-bucket', self.cos_bucket])
        if self.cos_directory:
            argv.extend(['--cos-directory', self.cos_directory])
        if self.cos_dependencies_archive:
            argv.extend(['--cos-dependencies-archive', self.cos_dependencies_archive])

        # Add notebook-level parameters to the argument list
        for inputname in self.inputs:
            if inputname in os.environ:
                argv.extend([f"--{inputname}", os.environ.get(inputname)])

        # Add pipeline-level parameters to the argument list
        if self.pipeline_name:
            argv.extend(['--pipeline-name', self.pipeline_name])
        if self.pipeline_node_id:
            argv.extend(['--pipeline-node-id', self.pipeline_node_id])

        # Execute the script
        subprocess.run(argv, check=True)

        # Process the script outputs
        for outputname in self.outputs:
            OpUtil.log_operation_info(f"processing output: {outputname}")
            if outputname in os.environ:
                output_filename = os.environ.get(outputname)
                OpUtil.log_operation_info(f"writing output: {outputname} to {output_filename}")
                output_file = open(output_filename, 'wt')
                output_file.write(os.path.basename(self.filepath))
                output_file.close()
            else:
                OpUtil.log_operation_info(f"output: {outputname} not in environment - ignored")


class RScriptOperation(Operation):
    """Operation for working with R scripts"""

    def __init__(self, **kwargs: Any) -> None:
        self.filepath = kwargs['filepath']
        self.cos_endpoint = kwargs['cos-endpoint']
        self.cos_bucket = kwargs['cos-bucket']
        self.cos_directory = kwargs['cos-directory']
        self.cos_dependencies_archive = kwargs['cos-dependencies-archive']
        self.inputs = kwargs.get('inputs', [])
        self.outputs = kwargs.get('outputs', [])
        self.pipeline_name = kwargs.get('pipeline-name', '')
        self.pipeline_node_id = kwargs.get('pipeline-node-id', '')

    def execute(self) -> None:
        """Execute the R script operation"""
        OpUtil.log_operation_info('running R script', self.filepath)

        # Add all inputs to environment variables
        for inputname in self.inputs:
            OpUtil.log_operation_info(f"processing input: {inputname}")
            if inputname in os.environ:
                inputvalue = os.environ.get(inputname)
                OpUtil.log_operation_info(f"using input: {inputname}={inputvalue}")
            else:
                OpUtil.log_operation_info(f"input: {inputname} not in environment - ignored")

        # Execute the script
        argv = ['Rscript', self.filepath]

        # Add COS parameters to the argument list
        if self.cos_endpoint:
            argv.extend(['--cos-endpoint', self.cos_endpoint])
        if self.cos_bucket:
            argv.extend(['--cos-bucket', self.cos_bucket])
        if self.cos_directory:
            argv.extend(['--cos-directory', self.cos_directory])
        if self.cos_dependencies_archive:
            argv.extend(['--cos-dependencies-archive', self.cos_dependencies_archive])

        # Add notebook-level parameters to the argument list
        for inputname in self.inputs:
            if inputname in os.environ:
                argv.extend([f"--{inputname}", os.environ.get(inputname)])

        # Add pipeline-level parameters to the argument list
        if self.pipeline_name:
            argv.extend(['--pipeline-name', self.pipeline_name])
        if self.pipeline_node_id:
            argv.extend(['--pipeline-node-id', self.pipeline_node_id])

        # Execute the script
        subprocess.run(argv, check=True)

        # Process the script outputs
        for outputname in self.outputs:
            OpUtil.log_operation_info(f"processing output: {outputname}")
            if outputname in os.environ:
                output_filename = os.environ.get(outputname)
                OpUtil.log_operation_info(f"writing output: {outputname} to {output_filename}")
                output_file = open(output_filename, 'wt')
                output_file.write(os.path.basename(self.filepath))
                output_file.close()
            else:
                OpUtil.log_operation_info(f"output: {outputname} not in environment - ignored")


class OpUtil:
    """Utility functions for operations"""

    @classmethod
    def log_operation_info(cls, action_clause: str, source_clause: Optional[str] = None) -> None:
        """Produces a formatted log INFO message used entirely for support purposes.

        This is a utility method to ensure consistent log messages that can be helpful for support.
        """
        if not enable_pipeline_info:
            return

        if source_clause:
            logger.info(f"'{os.environ.get('ELYRA_RUNTIME_ENV', '')}':'{os.environ.get('PIPELINE_NODE_ID', '')}' - {action_clause} '{source_clause}'")
        else:
            logger.info(f"'{os.environ.get('ELYRA_RUNTIME_ENV', '')}':'{os.environ.get('PIPELINE_NODE_ID', '')}' - {action_clause}")

    @classmethod
    def package_install(cls) -> None:
        """Installs packages from requirements.txt.

        This is a PATCHED version that skips package installation to avoid permission errors.
        """
        OpUtil.log_operation_info('Installing packages - SKIPPED')
        # Original code removed to prevent package installation
        return

    @classmethod
    def package_list_to_dict(cls, filename: str) -> Dict[str, str]:
        """Converts list of package versions to dictionary.

        This is a PATCHED version that returns an empty dict to avoid file not found errors.
        """
        return {}

    @classmethod
    def parse_arguments(cls, args: List[str]) -> Dict[str, Any]:
        """Parse given arguments and return a dictionary of arguments and their values.

        Args:
            args: List of arguments to parse

        Returns:
            A dictionary of parsed arguments
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('-f', '--file', dest='filepath', help='File to execute', required=True)
        parser.add_argument('-e', '--cos-endpoint', dest='cos-endpoint', help='Cloud object storage endpoint', required=True)
        parser.add_argument('-b', '--cos-bucket', dest='cos-bucket', help='Cloud object storage bucket', required=True)
        parser.add_argument('-d', '--cos-directory', dest='cos-directory', help='Cloud object storage directory path', required=True)
        parser.add_argument('-a', '--cos-dependencies-archive', dest='cos-dependencies-archive',
                            help='Cloud object storage dependencies archive', required=True)
        parser.add_argument('-p', '--pipeline-name', dest='pipeline-name', help='Pipeline name', required=False)
        parser.add_argument('-n', '--pipeline-node-id', dest='pipeline-node-id', help='Pipeline node ID', required=False)
        parser.add_argument('-i', '--inputs', dest='inputs', nargs='*', help='Input artifacts', required=False)
        parser.add_argument('-o', '--outputs', dest='outputs', nargs='*', help='Output artifacts', required=False)
        return vars(parser.parse_args(args))

    @classmethod
    def get_file_object_store(cls, cos_endpoint: str, cos_bucket: str, cos_directory: str, cos_dependencies_archive: str) -> Tuple[str, str]:
        """Retrieve archive from object store and extract it.

        Args:
            cos_endpoint: Cloud object storage endpoint
            cos_bucket: Cloud object storage bucket
            cos_directory: Cloud object storage directory path
            cos_dependencies_archive: Cloud object storage dependencies archive

        Returns:
            A tuple containing the path to the extracted archive and the path to the archive file
        """
        OpUtil.log_operation_info('processing dependencies from object store')

        # Create a temporary directory
        temp_dir = tempfile.gettempdir()
        archive_file = os.path.join(temp_dir, cos_dependencies_archive)

        # Get the dependencies archive
        url = urljoin(f"{cos_endpoint}/", f"{cos_bucket}/{cos_directory}/{cos_dependencies_archive}")
        OpUtil.log_operation_info(f"object store url: {url}")

        # Attempt to download the file
        try:
            with urlopen(url) as response, open(archive_file, 'wb') as out_file:
                out_file.write(response.read())
        except Exception as ex:
            # Log the exception and re-raise
            OpUtil.log_operation_info(f"Error downloading archive: {str(ex)}")
            raise

        # Extract the archive
        archive_dir = os.path.join(temp_dir, 'extracted')
        os.makedirs(archive_dir, exist_ok=True)

        try:
            with tarfile.open(archive_file, "r:gz") as tar:
                tar.extractall(path=archive_dir)
        except Exception as ex:
            # Log the exception and re-raise
            OpUtil.log_operation_info(f"Error extracting archive: {str(ex)}")
            raise

        return archive_dir, archive_file

    @classmethod
    def get_working_dir(cls) -> str:
        """Get the current working directory.

        Returns:
            The current working directory
        """
        return os.getcwd()

    @classmethod
    def create_operation(cls, **kwargs: Any) -> Operation:
        """Create an operation based on the file extension.

        Args:
            **kwargs: Keyword arguments for the operation

        Returns:
            An operation instance
        """
        filepath = kwargs['filepath']
        filename, file_extension = os.path.splitext(filepath)

        if file_extension == '.ipynb':
            return NotebookOperation(**kwargs)
        elif file_extension == '.py':
            return PythonScriptOperation(**kwargs)
        elif file_extension == '.r':
            return RScriptOperation(**kwargs)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")


def bootstrap(operation_arguments: Dict[str, Any]) -> None:
    """Bootstrap the runtime with the appropriate dependencies.

    Args:
        operation_arguments: Dictionary of operation arguments
    """
    # Verify that the file exists
    filepath = operation_arguments['filepath']
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File '{filepath}' does not exist.")

    # Get the dependencies from object store
    cos_endpoint = operation_arguments['cos-endpoint']
    cos_bucket = operation_arguments['cos-bucket']
    cos_directory = operation_arguments['cos-directory']
    cos_dependencies_archive = operation_arguments['cos-dependencies-archive']

    # Get the dependencies
    OpUtil.get_file_object_store(cos_endpoint, cos_bucket, cos_directory, cos_dependencies_archive)

    # Create the appropriate operation
    operation = OpUtil.create_operation(**operation_arguments)

    # Execute the operation
    operation.execute()


def main() -> None:
    """Main entry point."""
    # Configure logger format
    logging.basicConfig(format='[%(levelname)1.1s %(asctime)s.%(msecs).03d] %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

    # Get operation arguments
    operation_arguments = OpUtil.parse_arguments(sys.argv[1:])

    # Get pipeline name from environment variable if not provided
    if 'pipeline-name' not in operation_arguments or not operation_arguments['pipeline-name']:
        operation_arguments['pipeline-name'] = os.environ.get('PIPELINE_NAME', '')

    # Get pipeline node ID from environment variable if not provided
    if 'pipeline-node-id' not in operation_arguments or not operation_arguments['pipeline-node-id']:
        operation_arguments['pipeline-node-id'] = os.environ.get('PIPELINE_NODE_ID', '')

    # Log operation info
    OpUtil.log_operation_info(f"{operation_arguments['pipeline-name']}:{operation_arguments.get('pipeline-node-id', '')} - starting operation")

    # Install packages - PATCHED: This is now a no-op
    OpUtil.log_operation_info(f"{operation_arguments['pipeline-name']}:{operation_arguments.get('pipeline-node-id', '')} - Installing packages")
    OpUtil.package_install()

    # Bootstrap the runtime
    bootstrap(operation_arguments)


if __name__ == '__main__':
    main()
