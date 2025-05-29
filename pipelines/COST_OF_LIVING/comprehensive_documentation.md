# Configuration-Driven Pipeline Architecture
## DAG Structure and Node Communication

### 🏗️ Architecture Overview

**Configuration-driven, stateless pipeline** where DAG executions are controlled by JSON config files stored in S3.

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Airflow DAG   │    │  Configuration   │    │   Kubernetes    │
│  (Orchestrator) │◄──►│    Store (S3)    │◄──►│     Pods        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Data Store    │
                       │      (S3)       │
                       └─────────────────┘
```

### 🔑 DAG Key Generation

**CodeIgniter Encryption Keys** generate unique DAG identifiers:

```php
// Generate DAG key using CodeIgniter
$config['encryption_key'] = 'your_32_character_key_here';
$this->load->library('encrypt');
$dag_key = substr(md5($this->encrypt->encode($unique_identifier)), 0, 8);
// Result: DAG_KEY = "a7b3c9d2"
```

### 📄 Configuration File Pattern

**Naming**: `{pipeline-name}-{dag-key}.json`

**Examples**:
- `cost-analysis-a7b3c9d2.json`
- `data-processing-f4e8b1c6.json`

**Structure**:
```json
{
  "node_1": {
    "data_url": "https://example.com/data.csv",
    "timeout": 30
  },
  "node_2": {
    "output_dir": "results",
    "chart_dpi": 300
  },
  "s3": {
    "bucket": "pipeline-bucket",
    "prefix": "cost-analysis"
  }
}
```

### 🔄 Node Communication Flow

**S3 Folder Structure**:
```
pipeline-bucket/
├── cost-analysis-a7b3c9d2.json          # Config file
├── cost-analysis-a7b3c9d2/              # Execution workspace
│   ├── data/                            # Node 1 outputs
│   ├── processed/                       # Node 2 outputs  
│   └── results/                         # Final outputs
```

**Communication Pattern**:
```
Node A → S3 → Node B → S3 → Node C
```

### 🚀 DAG Implementation

```python
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator

# DAG with CodeIgniter-generated key
dag_key = "a7b3c9d2"  # From CodeIgniter encryption

def get_standard_env_vars():
    return {
        "DAG_KEY": dag_key,
        "AWS_ACCESS_KEY_ID": "your_key",
        "AWS_SECRET_ACCESS_KEY": "your_secret",
        "S3_ENDPOINT": "s3.amazonaws.com"
    }

# Node definition
node_1 = KubernetesPodOperator(
    name="DATA_FETCHER",
    task_id="FETCH_DATA",
    env_vars=get_standard_env_vars(),
    # ... other settings
)
```

### 🔧 Node Script Pattern

```python
#!/usr/bin/env python3
import boto3
import json
import os

def get_config():
    """Load config from S3 using DAG_KEY"""
    dag_key = os.environ.get('DAG_KEY')
    config_file = f"cost-analysis-{dag_key}.json"
    
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket='pipeline-bucket', Key=config_file)
    return json.loads(obj['Body'].read())

def download_from_s3(bucket, key, local_path):
    """Download file from S3"""
    s3 = boto3.client('s3')
    s3.download_file(bucket, key, local_path)

def upload_to_s3(local_path, bucket, key):
    """Upload file to S3"""
    s3 = boto3.client('s3')
    s3.upload_file(local_path, bucket, key)

def main():
    dag_key = os.environ.get('DAG_KEY')
    config = get_config()
    
    # Process using config parameters
    my_params = config['my_node']
    
    # Download inputs from previous nodes
    download_from_s3('pipeline-bucket', f'cost-analysis-{dag_key}/data/input.csv', 'input.csv')
    
    # Process data
    results = process_data('input.csv', my_params)
    
    # Upload outputs for next nodes
    upload_to_s3('output.csv', 'pipeline-bucket', f'cost-analysis-{dag_key}/processed/output.csv')

if __name__ == "__main__":
    main()
```

### 📋 Workflow Steps

1. **Generate DAG Key** (CodeIgniter)
   ```php
   $dag_key = substr(md5($this->encrypt->encode($project_id)), 0, 8);
   ```

2. **Create Config File**
   ```bash
   aws s3 cp cost-analysis-a7b3c9d2.json s3://pipeline-bucket/
   ```

3. **Deploy DAG** (with DAG_KEY)
   ```python
   env_vars = {"DAG_KEY": "a7b3c9d2"}
   ```

4. **Execute Pipeline**
   ```bash
   curl -X POST airflow-host/api/v1/dags/cost-analysis/dagRuns
   ```

### 🔄 Configuration Updates

**Change data source without code changes**:

1. Update config file:
   ```json
   {
     "node_1": {
       "data_url": "https://new-source.com/data_v2.csv"
     }
   }
   ```

2. Upload to S3:
   ```bash
   aws s3 cp cost-analysis-a7b3c9d2.json s3://pipeline-bucket/
   ```

3. Trigger DAG (same command, different behavior)

### 🎯 Key Benefits

- **Zero code changes** for parameter updates
- **Unique DAG identification** via CodeIgniter encryption
- **Stateless nodes** communicate through S3
- **Version control** through config files
- **Kubernetes-native** deployment pattern