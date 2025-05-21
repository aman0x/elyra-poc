#!/usr/bin/env python3
import sys
import re
import os

def patch_dag_file(dag_file_path):
    """
    Robustly patch the Airflow DAG file to force usage of the improved bootstrapper
    and prevent permission errors.
    """
    print(f"Patching DAG file: {dag_file_path}")
    
    with open(dag_file_path, "r") as f:
        content = f.read()
    
    # 1. Replace the bootstrapper download URL with a no-op command
    pattern = r"(echo 'Downloading https://raw\.githubusercontent\.com/elyra-ai/elyra/v3\.15\.0/elyra/airflow/bootstrapper\.py' && curl --fail -H 'Cache-Control: no-cache' -L https://raw\.githubusercontent\.com/elyra-ai/elyra/v3\.15\.0/elyra/airflow/bootstrapper\.py --output )bootstrapper\.py"
    replacement = r"\1improved_bootstrapper.py && cp /opt/conda/bin/improved_bootstrapper.py ."
    content = re.sub(pattern, replacement, content)
    
    # 2. Replace the requirements-elyra.txt download with a no-op command
    pattern = r"(echo 'Downloading https://raw\.githubusercontent\.com/elyra-ai/elyra/v3\.15\.0/etc/generic/requirements-elyra\.txt' && curl --fail -H 'Cache-Control: no-cache' -L https://raw\.githubusercontent\.com/elyra-ai/elyra/v3\.15\.0/etc/generic/requirements-elyra\.txt --output )requirements-elyra\.txt"
    replacement = r"\1requirements-elyra.txt && echo '# Empty file to prevent package installation' > requirements-elyra.txt"
    content = re.sub(pattern, replacement, content)
    
    # 3. Replace the pip install command with a no-op
    pattern = r"(python3 -m pip install packaging && python3 -m pip freeze > requirements-current\.txt)"
    replacement = r"echo 'Skipping pip install' && touch requirements-current.txt"
    content = re.sub(pattern, replacement, content)
    
    # 4. Replace bootstrapper.py with improved_bootstrapper.py
    pattern = r"(python3 )bootstrapper\.py"
    replacement = r"\1improved_bootstrapper.py"
    content = re.sub(pattern, replacement, content)
    
    # Write the patched content back
    with open(dag_file_path, "w") as f:
        f.write(content)
    
    print(f"Successfully patched {dag_file_path}")
    print("Changes made:")
    print("1. Replaced bootstrapper download with improved_bootstrapper.py")
    print("2. Created empty requirements-elyra.txt to prevent package installation")
    print("3. Skipped pip install commands")
    print("4. Used improved_bootstrapper.py instead of bootstrapper.py")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python robust_dag_patcher.py <dag_file_path>")
        sys.exit(1)
    
    dag_file_path = sys.argv[1]
    if not os.path.exists(dag_file_path):
        print(f"Error: DAG file {dag_file_path} does not exist")
        sys.exit(1)
        
    patch_dag_file(dag_file_path)
