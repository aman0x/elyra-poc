# Airflow DAG Verification and Troubleshooting Guide for Kubernetes

This guide explains how to verify that your DAGs are correctly imported from Git into Airflow, how to check if the code is correct, and how to make sure the DAGs appear in the Airflow UI.

## Prerequisites

- A Kubernetes cluster with Airflow deployed
- `kubectl` command-line tool configured to access your cluster
- Airflow set up with git-sync to pull DAGs from a repository

## 1. Verify DAGs are Properly Imported from Git

### Check the git-sync logs

```bash
# Get the name of your current webserver pod
export WEBSERVER_POD=$(kubectl get pods -n airflow-elyra -l app=airflow-webserver -o jsonpath='{.items[0].metadata.name}')

# Check the git-sync container logs
kubectl logs -n airflow-elyra $WEBSERVER_POD -c git-sync | tail -20
```

Look for messages like:
- `Syncing repository...`
- `Fast-forward` or `Already up to date`
- `DAGs synchronized successfully`

If you see error messages or if files aren't being synced, check your git-sync configuration.

### Check if DAG files exist in the DAGs directory

```bash
# List DAG files in the directory
kubectl exec -n airflow-elyra $WEBSERVER_POD -c airflow-webserver -- ls -la /opt/airflow/dags
```

This should show your DAG files with `.py` extensions.

## 2. Check if the DAG Code is Correct

### View the DAG file content

```bash
# Check the DAG file contents (replace YOUR_DAG_FILE.py with your actual file name)
kubectl exec -n airflow-elyra $WEBSERVER_POD -c airflow-webserver -- cat /opt/airflow/dags/YOUR_DAG_FILE.py
```

### Verify Airflow can recognize the DAG

```bash
# Check if the DAG is recognized by Airflow (replace YOUR_DAG_ID with your actual DAG ID)
kubectl exec -n airflow-elyra $WEBSERVER_POD -c airflow-webserver -- airflow dags list | grep YOUR_DAG_ID
```

If Airflow can recognize your DAG, it means the DAG file syntax is correct.

### Check for common issues

1. **Service account**: Make sure your KubernetesPodOperator has `service_account_name="airflow"` (or appropriate service account)
2. **MinIO credentials**: Verify environment variables are correctly set (`MINIO_ENDPOINT`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
3. **Task dependencies**: Check that dependencies between tasks are properly defined
4. **Script paths**: Ensure that any scripts referenced in the DAG actually exist in the correct locations

## 3. Make DAGs Appear in the Airflow UI

If your DAG is not visible in the Airflow UI despite being recognized by Airflow, follow these steps:

### Ensure the DAG is not paused

```bash
# Unpause the DAG (replace YOUR_DAG_ID with your actual DAG ID)
kubectl exec -n airflow-elyra $WEBSERVER_POD -c airflow-webserver -- airflow unpause YOUR_DAG_ID
```

### Restart Airflow components to refresh the UI

```bash
# Restart the scheduler
kubectl rollout restart deployment airflow-scheduler -n airflow-elyra

# Restart the webserver
kubectl rollout restart deployment airflow-webserver -n airflow-elyra

# Wait for pods to be ready
kubectl get pods -n airflow-elyra -w
```

### Access the Airflow UI

```bash
# Get the NodePort for the Airflow webserver
kubectl get svc -n airflow-elyra airflow-webserver

# Setup port-forwarding for easier access
kubectl port-forward svc/airflow-webserver -n airflow-elyra 8080:8080
```

Then access http://localhost:8080 in your browser.

## 4. Troubleshooting Task Execution Issues

If your DAG is visible but tasks aren't executing correctly:

### Check task logs

```bash
# Get logs for a specific task (adjust namespace, DAG ID, task ID, and execution date)
kubectl exec -n airflow-elyra $WEBSERVER_POD -c airflow-webserver -- airflow tasks logs YOUR_DAG_ID TASK_ID EXECUTION_DATE
```

### Check for pod creation

If using KubernetesPodOperator:

```bash
# Check for pods created by your task
kubectl get pods -n airflow-elyra
```

### Check data sharing between tasks

For tasks that need to share data:
- Make sure data is stored in a shared location (like MinIO)
- Verify that upload and download functions are working correctly
- Check that environment variables for storage access are correctly set

### Manually trigger a DAG run

```bash
# Trigger a DAG run
kubectl exec -n airflow-elyra $WEBSERVER_POD -c airflow-webserver -- airflow trigger_dag YOUR_DAG_ID
```

### Clear previous DAG runs

```bash
# Clear previous runs of a DAG
kubectl exec -n airflow-elyra $WEBSERVER_POD -c airflow-webserver -- airflow clear -f YOUR_DAG_ID
```

## 5. Checking Data and Results

If your tasks deal with data processing and storage:

### Verify data in MinIO

```bash
# Run a pod with MinIO client
kubectl run minio-client -n airflow-elyra --rm -i --tty --image=minio/mc -- sh

# Inside the pod, run:
mc alias set myminio http://minio.minio-system.svc.cluster.local:9000 minio minio123
mc ls myminio/YOUR_BUCKET/YOUR_PREFIX/
```

### Download and view results

```bash
# Inside the MinIO client pod:
mc cp myminio/YOUR_BUCKET/YOUR_PREFIX/YOUR_FILE.html .
cat YOUR_FILE.html
```

## Common Issues and Solutions

1. **DAG not visible in UI but recognized by Airflow**
   - Restart the webserver and scheduler
   - Clear browser cache or try incognito mode
   - Check if the DAG is paused

2. **KubernetesPodOperator not creating pods**
   - Verify service account has proper permissions
   - Check for RBAC issues

3. **Tasks cannot share data**
   - Use a shared storage solution like MinIO
   - Verify the storage client code is in both tasks
   - Check credentials and connection details

4. **Git-sync not updating DAGs**
   - Verify Git repository URL and branch
   - Check for authentication issues
   - Look for file path issues in the sync script

5. **Syntax errors in DAGs**
   - Check scheduler logs for parsing errors
   - Verify Python syntax is correct
   - Look for import errors or missing dependencies

By following this guide, you should be able to verify that your DAGs are correctly imported, diagnose issues with their execution, and ensure they appear in the Airflow UI.