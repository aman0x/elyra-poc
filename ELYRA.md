# Elyra Deployment - kubectl Command Guide

This guide provides the essential kubectl commands to deploy, verify, and interact with your Elyra deployment in Kubernetes.

## Deployment Commands

### 1. Deploy Elyra with Airflow Components

```bash
# Apply the Elyra deployment YAML
kubectl apply -f elyra-deployment.yaml

# New Elyta Deployment
helm install jupyterhub jupyterhub/jupyterhub --values jupyterhub-elyra-config.yaml --namespace elyra-system --create-namespace

# Watch the deployment status
kubectl get pods -n elyra-system -w
```

### 2. Verify Deployment Status

```bash
# New Elyra Deployment
kubectl port-forward -n elyra-system service/proxy-public 8080:http

# Check if all pods are running
kubectl get pods -n elyra-system

# Check details of the pod
kubectl describe pod -n elyra-system -l app=elyra

# Check logs of the init container
kubectl logs -n elyra-system $(kubectl get pods -n elyra-system -o name) -c init-catalogs

# Check logs of the main container
kubectl logs -n elyra-system $(kubectl get pods -n elyra-system -o name) -c elyra

# Get the NodePort service details
kubectl get svc -n elyra-system elyra
```

### 3. Access Elyra UI

```bash
# Using NodePort (replace with your actual port number from the service output)
# The URL format will be: http://<node-ip>:<nodeport>/?token=dGf7Hs9pKl2Mn6Qw3rT5yUi8oP1aZ0bX

# Or set up port forwarding for local access
kubectl port-forward -n elyra-system svc/elyra 8888:8888
# Then access: http://localhost:8888/?token=dGf7Hs9pKl2Mn6Qw3rT5yUi8oP1aZ0bX
```

### 4. Verify Airflow Component Catalog

Once logged into Elyra:
1. Click on the "Pipeline Components" tab in the left sidebar
2. You should see "Apache Airflow 1.10.15 Components" listed
3. You can use these components to create pipelines that will run on Airflow 1.10.x

### 5. Troubleshooting Commands

```bash
# Check persistent volume claims
kubectl get pvc -n elyra-system

# Check config maps
kubectl get configmaps -n elyra-system

# Execute a shell inside the Elyra pod for debugging
kubectl exec -it -n elyra-system $(kubectl get pods -n elyra-system -o name | head -1) -- /bin/bash

# Inside the pod, you can verify the component catalog:
elyra-metadata list component-catalogs
```

## FAQ & Known Warnings

- When starting Elyra, you may see log messages like:

  - `[W ...] Operator 'BranchPythonOperator' ... does not have an __init__ function. Skipping...`
  - `[W ...] Operator 'ShortCircuitOperator' ... does not have an __init__ function. Skipping...`
  - `[W ...] Operator 'LatestOnlyOperator' ... does not have an __init__ function. Skipping...`
  - `[W ...] Operator 'BaseBranchOperator' ... does not have an __init__ function. Skipping...`

- These warnings are expected and do not indicate a problem. Elyra will still function correctly and all required components will be available.

### 6. Delete the Deployment

```bash
# Delete all resources in the namespace
kubectl delete namespace elyra-system

# Verify the namespace is gone
kubectl get namespace elyra-system
```

## Important Notes

- This deployment is configured to work with Apache Airflow 1.10.x
- The Elyra access token is: `dGf7Hs9pKl2Mn6Qw3rT5yUi8oP1aZ0bX`
- The component catalog is automatically configured during deployment
- Persistent volumes maintain your work and configurations across pod restarts

## Next Steps

After deploying, configure an Airflow runtime in Elyra:
1. Go to the Runtimes tab in Elyra
2. Click "+" to add a new runtime
3. Select "Apache Airflow"
4. Configure with your Airflow 1.10.x server details