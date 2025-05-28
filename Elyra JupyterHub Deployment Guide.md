# Elyra JupyterHub Deployment Guide

This guide walks you through deploying the improved JupyterHub configuration with your custom Elyra image.

## Prerequisites

- Kubernetes cluster with kubectl configured
- Helm 3 installed
- Access to your container registry (ghcr.io)

## Deployment Steps

### 1. Install or Upgrade JupyterHub

If you're installing for the first time:

```bash
# Create namespace if it doesn't exist
kubectl create namespace elyra-system

# Add JupyterHub Helm repository if not already added
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm repo update

# Install JupyterHub with the improved configuration
helm install jupyterhub jupyterhub/jupyterhub \
  --namespace elyra-system \
  --values jupyterhub-elyra-config.yaml
```

If you're upgrading an existing installation:

```bash
# Update JupyterHub with the improved configuration
helm upgrade jupyterhub jupyterhub/jupyterhub \
  --namespace elyra-system \
  --values jupyterhub-elyra-config.yaml
```

### 2. Verify the Deployment

Check that all pods are running:

```bash
kubectl get pods -n elyra-system
```

You should see pods for the hub, proxy, and user-scheduler components.

### 3. Access JupyterHub

For local development access:

```bash
kubectl port-forward -n elyra-system service/proxy-public 8080:http
```

Then visit http://localhost:8080 in your browser and log in with your GitHub credentials.

For cluster access, get the NodePort:

```bash
kubectl get service -n elyra-system proxy-public
```

### 4. Test User Profiles

After logging in, you can select different resource profiles from the server options page:
- Default (2 CPU, 4GB RAM)
- Minimal (0.5 CPU, 1GB RAM)
- Performance (4 CPU, 8GB RAM)

### 5. Verify Airflow Catalog Setup

Once logged in, run the following in a terminal to verify the Airflow catalog was created:

```bash
elyra-metadata list component-catalogs
```

You should see the "Apache Airflow 1.10.15 Components" catalog listed.

## Troubleshooting

### Pod Startup Issues

If user pods fail to start:

```bash
# Check pod status
kubectl get pods -n elyra-system

# Check pod logs
kubectl logs -n elyra-system <pod-name>
```

### Authentication Issues

If GitHub authentication fails:
- Verify the OAuth callback URL matches your access URL
- Check that your GitHub username is in the allowed_users list

### Storage Issues

If persistent volume claims fail:
- Verify your cluster has a storage class named "standard"
- Check PVC status: `kubectl get pvc -n elyra-system`

### Resource Constraints

If pods are pending due to insufficient resources:
- Try the "Minimal" profile
- Check node capacity: `kubectl describe nodes`

## Maintenance

### Updating the Custom Elyra Image

When you build a new version of your custom Elyra image:

1. Push the new image to your registry
2. Update the tag in the configuration file
3. Run the helm upgrade command

### Backing Up User Data

To back up user data:

```bash
kubectl get pvc -n elyra-system
# For each PVC:
kubectl exec -n elyra-system <some-pod> -- tar czf /tmp/backup.tar.gz /home/jovyan
kubectl cp -n elyra-system <some-pod>:/tmp/backup.tar.gz ./backup.tar.gz
```
