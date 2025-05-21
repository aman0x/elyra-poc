#!/usr/bin/env python3
import sys
import re

def patch_dag_file(dag_file_path):
    with open(dag_file_path, "r") as f:
        content = f.read()
    
    # Replace bootstrapper.py with custom_bootstrapper.py
    pattern = r"(curl --fail -H .Cache-Control: no-cache. -L https://raw.githubusercontent.com/elyra-ai/elyra/v3.15.0/elyra/airflow/bootstrapper.py --output )bootstrapper.py"
    replacement = r"\1custom_bootstrapper.py && cp /opt/conda/bin/custom_bootstrapper.py ."
    content = re.sub(pattern, replacement, content)
    
    # Replace python3 bootstrapper.py with python3 custom_bootstrapper.py
    pattern = r"(python3 )bootstrapper.py"
    replacement = r"\1custom_bootstrapper.py"
    content = re.sub(pattern, replacement, content)
    
    with open(dag_file_path, "w") as f:
        f.write(content)
    
    print(f"Successfully patched {dag_file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python patch_dag.py <dag_file_path>")
        sys.exit(1)
    
    patch_dag_file(sys.argv[1])