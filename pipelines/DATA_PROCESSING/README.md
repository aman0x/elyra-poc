# 🚀 Smart Data Processing Pipeline

An intelligent, flexible data processing pipeline with automatic input detection, chaining capabilities, and enterprise-level control features.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [Pipeline Nodes](#pipeline-nodes)
- [Usage Examples](#usage-examples)
- [Pipeline Configurations](#pipeline-configurations)
- [File Structure](#file-structure)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

## 🌟 Overview

The Smart Data Processing Pipeline is an enhanced data transformation system that automatically detects the best input sources, supports flexible chaining between transformations, and provides enterprise-level control over data processing workflows.

### Key Capabilities

- **🔍 Smart Input Detection**: Automatically finds the best available input data
- **🔄 Flexible Chaining**: Chain transformations or run them independently
- **📦 Raw Data Updates**: Update source data with transformed results
- **🎯 Force Input Sources**: Override automatic detection when needed
- **☁️ Dual Mode Support**: Works with both S3/MinIO and local file systems
- **📊 Rich Metadata**: Comprehensive statistics and visualization data
- **🔧 Environment Control**: Configure pipeline behavior via environment variables

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Loader   │───▶│  Smart Pipeline  │───▶│  Output Files   │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Pipeline Control │
                    │ - Auto-detection │
                    │ - Chaining       │
                    │ - Raw updates    │
                    └──────────────────┘
```

## 🛠️ Installation

### Prerequisites

- Python 3.7+
- pandas
- numpy
- boto3 (for S3/MinIO support)
- scikit-learn (for outlier detection)

### Setup

1. **Clone or download the pipeline scripts**
2. **Ensure all dependencies are installed** (scripts auto-install required packages)
3. **Configure your environment** (see Environment Variables section)

## 🚀 Quick Start

### Local Mode (for testing)

```bash
# 1. Load data locally
python load_data_local.py

# 2. Run transformations (will auto-chain)
python smart_remove_duplicates.py
python smart_remove_outliers.py  
python smart_clean_null_values.py
```

### S3/MinIO Mode (for production)

```bash
# 1. Set environment variables
export MINIO_ENDPOINT="http://your-minio-endpoint:9000"
export MINIO_ACCESS_KEY="your-access-key"
export MINIO_SECRET_KEY="your-secret-key"

# 2. Load data from S3
python load_data_from_s3.py

# 3. Run transformations
python smart_remove_duplicates.py
python smart_remove_outliers.py
python smart_clean_null_values.py
```

## 🔧 Environment Variables

### Pipeline Control Variables

| Variable | Values | Default | Description |
|----------|--------|---------|-------------|
| `INPUT_SOURCE` | `raw`, `deduplicated`, `outliers_removed`, `null_cleaned` | Auto-detect | Force specific input source |
| `CHAIN_TRANSFORMATIONS` | `true`, `false` | `true` | Use output from previous transformation |
| `UPDATE_RAW_DATA` | `true`, `false` | `false` | Update raw data file after transformation |
| `TEST_MODE` | `local`, `s3` | `local` | Run in local or S3 mode |

### S3/MinIO Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MINIO_ENDPOINT` | `http://localhost:9000` | MinIO/S3 endpoint URL |
| `MINIO_ACCESS_KEY` | `minioadmin` | Access key for authentication |
| `MINIO_SECRET_KEY` | `minioadmin` | Secret key for authentication |
| `INPUT_BUCKET` | `pipeline-data` | S3 bucket for input data |
| `OUTPUT_BUCKET` | Same as INPUT_BUCKET | S3 bucket for output data |
| `OUTPUT_PREFIX` | `pipeline-data` | S3 prefix for output files |

### Manual Overrides

| Variable | Description |
|----------|-------------|
| `INPUT_PATH` | Manual local file path (local mode) |
| `INPUT_KEY` | Manual S3 key (S3 mode) |
| `OUTPUT_PATH` | Manual local output directory |

## 🔄 Pipeline Nodes

### 1. Data Loaders

#### `load_data_from_s3.py`
- Loads CSV data from S3/MinIO
- Converts to pickle format
- Creates metadata files

#### `load_data_local.py`
- Loads data from local files (CSV, Excel, Pickle)
- For testing and development only

### 2. Smart Transformation Nodes

#### `smart_remove_duplicates.py`
**Purpose**: Remove duplicate rows from dataset

**Parameters**:
- `DUPLICATE_SUBSET`: Columns to check for duplicates
- `KEEP_FIRST`: Which duplicate to keep (`first` or `last`)

#### `smart_remove_outliers.py`
**Purpose**: Detect and remove/cap outliers

**Parameters**:
- `OUTLIER_METHOD`: Detection method (`iqr`, `zscore`, `isolation_forest`, `modified_zscore`)
- `OUTLIER_THRESHOLD`: Detection threshold
- `OUTLIER_COLUMNS`: Columns to check
- `OUTLIER_ACTION`: Action to take (`remove` or `cap`)

#### `smart_clean_null_values.py`
**Purpose**: Handle missing values in dataset

**Parameters**:
- `NULL_STRATEGY`: Handling strategy (`drop_rows`, `drop_cols`, `fill_mean`, `fill_median`, `fill_mode`, `fill_zero`, `fill_forward`, `fill_backward`)
- `NULL_THRESHOLD`: Threshold for dropping columns
- `NULL_COLUMNS`: Columns to clean

## 📝 Usage Examples

### Example 1: Basic Sequential Pipeline

```bash
# Default behavior - each step automatically uses the best available input
export CHAIN_TRANSFORMATIONS=true

# Pipeline flow:
# 1. remove_duplicates: raw_data.pkl → deduplicated_data.pkl
# 2. remove_outliers: deduplicated_data.pkl → outliers_removed_data.pkl  
# 3. clean_null_values: outliers_removed_data.pkl → nulls_cleaned_data.pkl

python smart_remove_duplicates.py
python smart_remove_outliers.py
python smart_clean_null_values.py
```

### Example 2: Parallel Processing

```bash
# All transformations work on raw data independently
export CHAIN_TRANSFORMATIONS=false

# All nodes process: raw_data.pkl → [transformation]_data.pkl
python smart_remove_duplicates.py &
python smart_remove_outliers.py &
python smart_clean_null_values.py &
wait
```

### Example 3: Custom Pipeline Flow

```bash
# Step 1: Remove duplicates from raw data
python smart_remove_duplicates.py

# Step 2: Clean nulls from deduplicated data (skip outlier removal)
export INPUT_SOURCE=deduplicated
python smart_clean_null_values.py

# Step 3: Remove outliers from null-cleaned data
export INPUT_SOURCE=null_cleaned
python smart_remove_outliers.py
```

### Example 4: Iterative Refinement

```bash
# Round 1: Basic cleaning + update raw data
export UPDATE_RAW_DATA=true
python smart_remove_duplicates.py

# Round 2: Advanced cleaning on refined data (now stored as raw data)
export UPDATE_RAW_DATA=false
export CHAIN_TRANSFORMATIONS=true
python smart_remove_outliers.py
python smart_clean_null_values.py
```

### Example 5: Production Configuration

```bash
# S3 Production Setup
export TEST_MODE=s3
export MINIO_ENDPOINT="https://your-production-minio.com"
export MINIO_ACCESS_KEY="prod-access-key"
export MINIO_SECRET_KEY="prod-secret-key"
export INPUT_BUCKET="production-data"
export OUTPUT_BUCKET="production-results"

# Quality-first pipeline
export CHAIN_TRANSFORMATIONS=true
export NULL_STRATEGY=fill_median
export OUTLIER_METHOD=iqr
export OUTLIER_THRESHOLD=2.0

python smart_remove_duplicates.py
python smart_clean_null_values.py
python smart_remove_outliers.py
```

## ⚙️ Pipeline Configurations

### Configuration A: Data Quality Focus

```bash
# Sequential processing for maximum data quality
export CHAIN_TRANSFORMATIONS=true
export NULL_STRATEGY=drop_rows
export OUTLIER_METHOD=isolation_forest
export DUPLICATE_SUBSET=""  # Check all columns
```

**Flow**: Raw → Remove Duplicates → Clean Nulls → Remove Outliers

### Configuration B: Data Volume Preservation

```bash
# Preserve as much data as possible
export CHAIN_TRANSFORMATIONS=true
export NULL_STRATEGY=fill_median
export OUTLIER_ACTION=cap
export UPDATE_RAW_DATA=true
```

**Flow**: Raw → Cap Outliers → Fill Nulls → Remove Duplicates → Update Raw

### Configuration C: Comparative Analysis

```bash
# Create multiple versions for comparison
export CHAIN_TRANSFORMATIONS=false

# Run all transformations on raw data
# Then choose best result for final processing
export INPUT_SOURCE=deduplicated  # Use best intermediate result
```

### Configuration D: Development/Testing

```bash
# Local development setup
export TEST_MODE=local
export INPUT_PATH="./test_data.csv"
export OUTPUT_PATH="./results"
export CHAIN_TRANSFORMATIONS=true
```

## 📁 File Structure

### Input Files
```
pipeline_output/
├── raw_data.pkl                    # Raw data (local mode)
└── test_config.json               # Configuration for local testing
```

### Output Files (per transformation)
```
pipeline_output/
├── deduplicated/
│   ├── deduplicated_data.pkl      # Processed data
│   ├── deduplication_stats.json   # Processing statistics
│   └── deduplication_plotly.json  # Visualization data
├── outliers_removed/
│   ├── outliers_removed_data.pkl
│   ├── outlier_removal_stats.json
│   └── outlier_removal_plotly.json
└── null_cleaned/
    ├── nulls_cleaned_data.pkl
    ├── null_cleaning_stats.json
    └── null_cleaning_plotly.json
```

### S3 Structure
```
s3://your-bucket/pipeline-data/
├── input_data.pkl                 # Raw data
├── deduplicated_data.pkl          # Transformation outputs
├── outliers_removed_data.pkl
├── nulls_cleaned_data.pkl
├── deduplication_stats.json       # Statistics files
├── outlier_removal_stats.json
├── null_cleaning_stats.json
├── deduplication_plotly.json      # Visualization data
├── outlier_removal_plotly.json
└── null_cleaning_plotly.json
```

## 🔧 Troubleshooting

### Common Issues

#### 1. "No input data found" Error

**Cause**: No raw data available or incorrect file paths

**Solution**:
```bash
# Check if raw data exists
ls -la ./pipeline_output/raw_data.pkl  # Local mode
# or run data loader first
python load_data_local.py
```

#### 2. S3 Connection Errors

**Cause**: Incorrect S3/MinIO configuration

**Solution**:
```bash
# Verify S3 settings
export MINIO_ENDPOINT="http://correct-endpoint:9000"
export MINIO_ACCESS_KEY="correct-key"
export MINIO_SECRET_KEY="correct-secret"

# Test connection manually
python -c "import boto3; boto3.client('s3', endpoint_url='$MINIO_ENDPOINT').list_buckets()"
```

#### 3. Forced Input Source Not Found

**Cause**: Specified INPUT_SOURCE doesn't exist

**Solution**:
```bash
# Let auto-detection find available inputs
unset INPUT_SOURCE
# or specify correct source
export INPUT_SOURCE=raw
```

#### 4. Memory Issues with Large Datasets

**Solutions**:
- Use more efficient data types
- Process in chunks
- Enable outlier capping instead of removal
- Use sampling for development

### Debug Mode

Enable verbose logging:

```bash
export DEBUG=true
python smart_remove_duplicates.py
```

## 🎯 Advanced Usage

### Custom Transformation Chains

```bash
# Create custom processing sequence
export CHAIN_TRANSFORMATIONS=true

# 1. Light cleaning first
export NULL_STRATEGY=fill_mean
python smart_clean_null_values.py

# 2. Remove outliers from clean data
export OUTLIER_METHOD=zscore
export OUTLIER_THRESHOLD=2.5
python smart_remove_outliers.py

# 3. Final deduplication
export DUPLICATE_SUBSET="important_column1,important_column2"
python smart_remove_duplicates.py
```

### Airflow Integration

```python
from airflow import DAG
from airflow.operators.bash_operator import BashOperator

# Sequential Pipeline DAG
with DAG('smart_data_pipeline', schedule_interval='@daily') as dag:
    
    load_data = BashOperator(
        task_id='load_data',
        bash_command='python load_data_from_s3.py',
        env={'INPUT_CSV': 'daily_data.csv'}
    )
    
    remove_duplicates = BashOperator(
        task_id='remove_duplicates',
        bash_command='python smart_remove_duplicates.py',
        env={'CHAIN_TRANSFORMATIONS': 'true'}
    )
    
    remove_outliers = BashOperator(
        task_id='remove_outliers', 
        bash_command='python smart_remove_outliers.py',
        env={'OUTLIER_METHOD': 'iqr', 'OUTLIER_THRESHOLD': '2.0'}
    )
    
    clean_nulls = BashOperator(
        task_id='clean_nulls',
        bash_command='python smart_clean_null_values.py',
        env={'NULL_STRATEGY': 'fill_median'}
    )
    
    load_data >> remove_duplicates >> remove_outliers >> clean_nulls
```

### Monitoring and Alerts

Monitor pipeline execution:

```bash
# Check processing statistics
python -c "
import json
with open('./pipeline_output/null_cleaned/null_cleaning_stats.json') as f:
    stats = json.load(f)
    print(f'Processed {stats[\"initial_rows\"]} → {stats[\"final_rows\"]} rows')
    print(f'Removed {stats[\"nulls_removed\"]} null values')
"
```

### Performance Optimization

```bash
# For large datasets
export OUTLIER_METHOD=iqr          # Faster than isolation_forest
export NULL_STRATEGY=fill_median   # Faster than fill_mode
export DUPLICATE_SUBSET=key_cols   # Check only important columns

# Parallel processing
export CHAIN_TRANSFORMATIONS=false
python smart_remove_duplicates.py &
python smart_remove_outliers.py &  
python smart_clean_null_values.py &
wait
```

## 📞 Support

For issues, questions, or contributions:

1. Check the troubleshooting section
2. Review environment variable configurations
3. Verify input data format and availability
4. Check file permissions and paths

## 📄 License

This project is provided as-is for educational and commercial use.

---

**🎉 Happy Data Processing!**