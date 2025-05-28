# Airflow 2.11.0 Helm Installation Guide

This guide provides step-by-step instructions for deploying Apache Airflow 2.11.0 using Helm charts with the customized values.yaml file.

## Prerequisites

1. Kubernetes cluster running version 1.19+
2. Helm 3.0+ installed on your local machine
3. kubectl configured to communicate with your Kubernetes cluster
4. Sufficient permissions to create resources in the target namespace

## Installation Steps

### 1. Create the Namespace (if it doesn't exist)

```bash
kubectl create namespace airflow-elyra
```

### 2. Add the Apache Airflow Helm Repository

```bash
helm repo add apache-airflow https://airflow.apache.org
helm repo update
```

### 3. Install Airflow Using the Custom Values File

```bash
helm install airflow apache-airflow/airflow \
  --namespace airflow-elyra \
  --version 1.16.0 \
  --values airflow-2.11.0-values.yaml
```

### 4. Monitor the Deployment

```bash
kubectl get pods -n airflow-elyra
```

Wait until all pods are in the "Running" state. This may take a few minutes.

### 5. Access the Airflow Web UI

#### If using NodePort (as configured in the values.yaml):

```bash
# Get the NodePort assigned to the Airflow webserver service
kubectl get svc -n airflow-elyra airflow-webserver -o jsonpath='{.spec.ports[0].nodePort}'
```

Then access the Airflow UI at `http://<node-ip>:<node-port>`

#### If using Ingress (as configured in the values.yaml):

Access the Airflow UI at the hostname configured in your ingress.

### 6. Login to Airflow

Use the credentials configured in the values.yaml file:
- Username: admin
- Password: admin

## Verification Steps

1. Verify that the git-sync is working correctly:

```bash
kubectl logs -n airflow-elyra -l component=dag-processor -c git-sync
```

2. Verify that the KubernetesExecutor is configured correctly:

```bash
kubectl exec -it -n airflow-elyra deployment/airflow-webserver -- airflow config get-value core executor
```

3. Check that DAGs are being loaded:

```bash
kubectl exec -it -n airflow-elyra deployment/airflow-webserver -- airflow dags list
```

## Troubleshooting

### Common Issues

1. **Pods stuck in Pending state**:
   - Check for resource constraints: `kubectl describe pod <pod-name> -n airflow-elyra`

2. **Database connection issues**:
   - Verify PostgreSQL is running: `kubectl get pods -n airflow-elyra -l app=postgresql`
   - Check connection details in the values.yaml file

3. **Git-sync not working**:
   - Check git-sync logs: `kubectl logs -n airflow-elyra -l component=dag-processor -c git-sync`
   - Verify repository URL and credentials

4. **KubernetesExecutor issues**:
   - Ensure RBAC is properly configured
   - Check scheduler logs: `kubectl logs -n airflow-elyra -l component=scheduler`

## Upgrading in the Future

To upgrade Airflow in the future, use the following command:

```bash
helm upgrade airflow apache-airflow/airflow \
  --namespace airflow-elyra \
  --values airflow-2.11.0-values.yaml
```

## Uninstalling

If needed, you can uninstall Airflow using:

```bash
helm uninstall airflow -n airflow-elyra
```

Note: This will not delete persistent volumes. To delete them as well:

```bash
kubectl delete pvc --all -n airflow-elyra
```
