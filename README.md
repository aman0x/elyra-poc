# Keyward Elyra PoC

This project demonstrates deploying Apache Airflow 1.10.15 on Kubernetes for integration with Elyra 3.15.0, including DAG management and runtime orchestration.

## Project Purpose
- Deploy Airflow on Kubernetes for Elyra pipeline execution
- Provide configuration and deployment guides
- Enable reproducible data workflows using Elyra and Airflow

## Repository Structure
- `AIRFLOW.md`: Airflow deployment and management guide
- `Airflow DAG Info.md`: DAG troubleshooting and verification
- `airflow-1.10.15-k8s.yaml`: Airflow deployment manifest
- `elyra-deployment.yaml`: Elyra deployment manifest
- `minio-deployment.yaml`: MinIO deployment manifest
- `pipelines/`: Example pipelines and DAGs
- `tests/`: Test DAGs and scripts

## Prerequisites
**Important: Fork & GitHub Token Setup**

To enable Airflow to fetch DAGs from your repository, you must:

- **Fork this repository** to your own GitHub account.
- **Create a GitHub Personal Access Token (classic)** with repo access ([GitHub token creation guide](https://github.com/settings/tokens?type=classic)).
- **Add your GitHub token** to the Airflow Runtime configuration as a secret or environment variable. This allows Airflow to synchronize DAGs from your forked repository securely.
- For a visual example, see the reference in `Airflow Runtime Example.png` in this repository.

- Kubernetes cluster (v1.18+ recommended)
- `kubectl` configured for your cluster
- Helm (for Helm-based deployments)
- Docker (for building custom images, if needed)

## Deployment Instructions

### Deploy Airflow with kubectl
1. Apply the Airflow deployment YAML:
   ```bash
   kubectl apply -f airflow-1.10.15-k8s.yaml
   ```
2. Monitor deployment status:
   ```bash
   kubectl get pods -n airflow-elyra
   ```
3. Access Airflow UI (port-forward or service exposure as needed).

### Deploy Airflow with Helm
1. Customize `airflow-3.0.1-values.yaml` as needed.
2. Install Airflow:
   ```bash
   helm install airflow -n airflow-elyra -f airflow-3.0.1-values.yaml apache-airflow/airflow
   ```

### Deploy Elyra and MinIO
- Apply `elyra-deployment.yaml` and `minio-deployment.yaml` using `kubectl apply -f ...`

## DAG Management
- DAGs are managed via git-sync or direct volume mounts.
- See `Airflow DAG Info.md` for troubleshooting and verification steps.

## Cleaning Up
To remove the Airflow deployment:
```bash
kubectl delete namespace airflow-elyra
kubectl get namespace airflow-elyra
```

## Troubleshooting
- Check pod logs for errors: `kubectl logs <pod> -n airflow-elyra`
- Ensure all required Kubernetes resources are created
- Verify DAG synchronization and Airflow webserver status

## Further Documentation
- [Apache Airflow Docs](https://airflow.apache.org/docs/)
- [Elyra Docs](https://elyra.readthedocs.io/)
- See `AIRFLOW.md` and `Airflow DAG Info.md` in this repo for detailed guides

### Additional Guides
- [MinIO Deployment and UI Access Guide](minio-deployment.md): Step-by-step instructions to deploy MinIO on Kubernetes, including manifest usage, service exposure, and accessing the MinIO web UI for bucket management.
- [Airflow Kubernetes Operator with S3 DAG Storage: Architecture Diagram](airflow-k8s-s3-diagram.md): Explains how Airflow components interact with S3/MinIO for DAG storage, including the use of sidecar containers and shared volumes.
- [Using a Custom Docker Image with Airflow KubernetesPodOperator](airflow-custom-image-diagram.md): Details on customizing Docker images for Airflow tasks, covering dependency installation, environment variables, credentials, and runtime configuration.

## Configuring Sub-paths for Elyra DAG Repositories

### Current Limitation
Elyra does not natively support specifying sub-paths (such as "your-org/your-repo/subfolder") in the repository configuration for Airflow runtimes. The repository field only accepts the format "your-git-org/your-dag-repo" without additional path components.

### Alternative Approaches
1. **Use Branches Instead of Sub-paths**: Organize different DAG sets or purposes using separate branches (e.g., a "tests" branch) in your repository.
2. **Create a Dedicated Repository**: Maintain a separate repository specifically for DAGs, structuring folders internally as needed.
3. **Modify Airflow Configuration**: Advanced users can:
   - Adjust git-sync container settings to sync a specific subdirectory
   - Configure Airflow to scan for DAGs in specific subfolders within the repository
4. **Use Folder Structure Within Repository**: While Elyra cannot target a sub-path, you can organize DAGs in folders inside your repo. Airflow can be configured to recursively scan these folders for DAGs.

If you require a very specific structure, consider customizing the Airflow Helm chart or deployment manifest to change git-sync settings or the DAG folder path in Airflow.

For more details or guidance on any of these approaches, see the Airflow and Elyra documentation or reach out for further assistance.

## Compatibility Notice

**Important:** Elyra 3.15.0 is only fully compatible with Apache Airflow 1.10.15. Using other versions of Airflow may result in unexpected behavior or incompatibility issues with Elyra pipelines. Please ensure you deploy the specified versions for reliable integration. Refer to the [Elyra documentation changelog](https://elyra.readthedocs.io/en/stable/getting_started/changelog.html) for details.<mcreference link="https://elyra.readthedocs.io/en/stable/getting_started/changelog.html" index="2">2</mcreference>