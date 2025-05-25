# 🚀 Smart Data Processing Pipeline

An intelligent, flexible data processing pipeline with automatic input detection, chaining capabilities, and enterprise-level control features.

## 📋 Table of Contents

- [Quick Start for New Developers](#quick-start-for-new-developers)
- [Core Concepts](#core-concepts)
- [Architecture](#architecture)
- [Installation & Setup](#installation--setup)
- [Environment Variables Reference](#environment-variables-reference)
- [Pipeline Nodes](#pipeline-nodes)
- [Usage Examples](#usage-examples)
- [Development Workflow](#development-workflow)
- [File Structure](#file-structure)
- [Debugging & Troubleshooting](#debugging--troubleshooting)
- [Advanced Features](#advanced-features)

## 🚀 Quick Start for New Developers

### What This Pipeline Does

This is a **smart data cleaning pipeline** that automatically processes your data through multiple transformations:
- **Remove duplicates** from your dataset
- **Detect and handle outliers** using various statistical methods
- **Clean missing values** with different strategies

### 5-Minute Setup

1. **Get the Files**: You need these 4 Python scripts:
   - `load_data_from_s3.py` - Loads CSV data from S3/MinIO
   - `remove_duplicates.py` - Removes duplicate rows
   - `remove_outliers.py` - Handles outliers (IQR, Z-score, Isolation Forest, etc.)
   - `clean_null_values.py` - Fills or removes missing values

2. **Test Locally First**:
   ```bash
   # Put your CSV file in ./pipeline_output/raw_data.csv
   export TEST_MODE=local
   python load_data_local.py  # You'll need to create this for local testing
   python remove_duplicates.py
   python remove_outliers.py
   python clean_null_values.py
   ```

3. **Use with S3/MinIO**:
   ```bash
   export TEST_MODE=s3
   export MINIO_ENDPOINT="http://your-minio:9000"
   export MINIO_ACCESS_KEY="your-key"
   export MINIO_SECRET_KEY="your-secret"
   export INPUT_BUCKET="your-bucket"
   export INPUT_CSV="your-data.csv"
   
   python load_data_from_s3.py
   python remove_duplicates.py
   python remove_outliers.py
   python clean_null_values.py
   ```

### Understanding the "Smart" Features

**The pipeline is "smart" because:**
- 🔍 **Auto-detects input**: Automatically finds the best available data to process
- 🔄 **Chains transformations**: Each step uses the output of the previous step
- 🎯 **Flexible routing**: You can force specific inputs or run steps independently
- 📊 **Rich outputs**: Saves data + detailed statistics + visualization data

## 🧠 Core Concepts

### 1. Input Detection Logic

The pipeline follows this priority order to find input data:
```
1. Manual Override (INPUT_KEY or INPUT_PATH)
2. Most processed data available:
   - nulls_cleaned_data.pkl
   - outliers_removed_data.pkl  
   - deduplicated_data.pkl
   - input_data.pkl (raw data)
```

**Example**: If you run `remove_outliers.py` and it finds `deduplicated_data.pkl`, it will automatically use that instead of raw data.

### 2. Chaining vs Independent Processing

**Chaining Enabled** (`CHAIN_TRANSFORMATIONS=true`):
```
Raw Data → Remove Duplicates → Remove Outliers → Clean Nulls
```

**Chaining Disabled** (`CHAIN_TRANSFORMATIONS=false`):
```
Raw Data → Remove Duplicates
Raw Data → Remove Outliers  
Raw Data → Clean Nulls
```

### 3. Raw Data Updates

Set `UPDATE_RAW_DATA=true` to replace the raw data file with cleaned data:
```bash
# This will overwrite input_data.pkl with deduplicated data
export UPDATE_RAW_DATA=true
python remove_duplicates.py
```

## 🏗️ Architecture

### Data Flow Diagram
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CSV File      │───▶│  Data Loader     │───▶│  input_data.pkl │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                              ┌─────────────────────────┼─────────────────────────┐
                              ▼                         ▼                         ▼
                    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
                    │ Remove Duplicates│    │ Remove Outliers  │    │ Clean Null Values│
                    │                  │    │                  │    │                  │
                    └─────────┬────────┘    └─────────┬────────┘    └─────────┬────────┘
                              ▼                       ▼                       ▼
                    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
                    │deduplicated_data │    │outliers_removed  │    │nulls_cleaned_data│
                    │      .pkl        │    │    _data.pkl     │    │      .pkl        │
                    └──────────────────┘    └──────────────────┘    └──────────────────┘
```

### Smart Input Detection
```python
# Each node automatically checks for the best input in this order:
def auto_detect_best_input():
    possible_inputs = [
        "nulls_cleaned_data.pkl",      # Most processed
        "outliers_removed_data.pkl",   # Partially processed
        "deduplicated_data.pkl",       # Basic processing
        "input_data.pkl"               # Raw data
    ]
    # Returns the first one found
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.7+
- Access to S3/MinIO (for production) or local file system (for testing)

### Dependencies
**The scripts auto-install dependencies**, but they need:
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `boto3` - S3 communication
- `scikit-learn` - Machine learning (for outlier detection)

### Environment Setup

Create a `.env` file or set environment variables:
```bash
# S3/MinIO Configuration
export MINIO_ENDPOINT="http://minio.example.com:9000"
export MINIO_ACCESS_KEY="your-access-key"
export MINIO_SECRET_KEY="your-secret-key"
export INPUT_BUCKET="your-bucket"
export OUTPUT_BUCKET="your-bucket"

# Pipeline Behavior
export TEST_MODE="s3"                    # 's3' or 'local'
export CHAIN_TRANSFORMATIONS="true"      # Chain steps together
export UPDATE_RAW_DATA="false"          # Don't overwrite raw data
```

## 🔧 Environment Variables Reference

### Essential Variables

| Variable | Values | Default | When to Use |
|----------|--------|---------|-------------|
| `TEST_MODE` | `local`, `s3` | `local` | Set to `s3` for production |
| `CHAIN_TRANSFORMATIONS` | `true`, `false` | `true` | Set to `false` for parallel processing |
| `UPDATE_RAW_DATA` | `true`, `false` | `false` | Set to `true` for iterative cleaning |

### S3/MinIO Configuration

| Variable | Example | Description |
|----------|---------|-------------|
| `MINIO_ENDPOINT` | `http://minio:9000` | Your MinIO/S3 endpoint |
| `MINIO_ACCESS_KEY` | `admin` | Access key for authentication |
| `MINIO_SECRET_KEY` | `password` | Secret key for authentication |
| `INPUT_BUCKET` | `data-bucket` | Bucket containing your data |
| `OUTPUT_BUCKET` | `results-bucket` | Bucket for processed data |
| `OUTPUT_PREFIX` | `processed-data` | S3 path prefix for outputs |

### Override Variables (Advanced)

| Variable | Example | Use Case |
|----------|---------|----------|
| `INPUT_SOURCE` | `deduplicated` | Force specific input type |
| `INPUT_KEY` | `data/input.pkl` | Override auto-detection |
| `INPUT_PATH` | `./data/input.pkl` | Override local file path |

### Transformation Parameters

**Remove Duplicates**:
- `DUPLICATE_SUBSET` - Columns to check (comma-separated)
- `KEEP_FIRST` - Keep `first` or `last` duplicate

**Remove Outliers**:
- `OUTLIER_METHOD` - `iqr`, `zscore`, `isolation_forest`, `modified_zscore`
- `OUTLIER_THRESHOLD` - Detection threshold (method-dependent)
- `OUTLIER_ACTION` - `remove` or `cap`
- `OUTLIER_COLUMNS` - Specific columns to check

**Clean Nulls**:
- `NULL_STRATEGY` - `drop_rows`, `drop_cols`, `fill_mean`, `fill_median`, `fill_mode`, `fill_zero`, `fill_forward`, `fill_backward`
- `NULL_THRESHOLD` - For `drop_cols`, percentage threshold
- `NULL_COLUMNS` - Specific columns to clean

## 🔄 Pipeline Nodes

### Data Loader (`load_data_from_s3.py`)

**What it does**: Converts CSV files to pickle format for faster processing

**Key features**:
- Loads from S3/MinIO
- Generates data summary and statistics
- Creates metadata files
- Handles different CSV formats automatically

**Outputs**:
- `input_data.pkl` - The main data file
- `data_metadata.json` - Column info, data types, statistics

### Remove Duplicates (`remove_duplicates.py`)

**What it does**: Identifies and removes duplicate rows

**Key features**:
- Can check all columns or specific subset
- Choose which duplicate to keep (first/last)
- Generates deduplication statistics

**Outputs**:
- `deduplicated_data.pkl` - Clean data
- `deduplication_stats.json` - How many duplicates found/removed
- `deduplication_plotly.json` - Visualization data

### Remove Outliers (`remove_outliers.py`)

**What it does**: Detects and handles outliers using various methods

**Methods available**:
- **IQR (Interquartile Range)**: Classic statistical method
- **Z-Score**: Standard deviation based
- **Modified Z-Score**: Median-based (more robust)
- **Isolation Forest**: Machine learning approach

**Actions**:
- **Remove**: Delete outlier rows
- **Cap**: Limit outliers to threshold values

**Outputs**:
- `outliers_removed_data.pkl` - Processed data
- `outlier_removal_stats.json` - Detection statistics
- `outlier_removal_plotly.json` - Visualization data

### Clean Null Values (`clean_null_values.py`)

**What it does**: Handles missing values in various ways

**Strategies available**:
- **Drop rows**: Remove rows with nulls
- **Drop columns**: Remove columns with too many nulls
- **Fill methods**: Mean, median, mode, zero, forward/backward fill

**Outputs**:
- `nulls_cleaned_data.pkl` - Clean data
- `null_cleaning_stats.json` - Cleaning statistics
- `null_cleaning_plotly.json` - Visualization data

## 📝 Usage Examples

### Example 1: First-Time Setup

```bash
# 1. Set up environment
export TEST_MODE=s3
export MINIO_ENDPOINT="http://localhost:9000"
export MINIO_ACCESS_KEY="minioadmin"
export MINIO_SECRET_KEY="minioadmin"
export INPUT_BUCKET="my-data-bucket"
export INPUT_CSV="my_dataset.csv"

# 2. Load your data
python load_data_from_s3.py

# 3. Run default pipeline (auto-chaining enabled)
python remove_duplicates.py
python remove_outliers.py
python clean_null_values.py
```

### Example 2: Custom Outlier Detection

```bash
# Use Isolation Forest for outlier detection
export OUTLIER_METHOD=isolation_forest
export OUTLIER_THRESHOLD=0.05  # 5% contamination rate
export OUTLIER_ACTION=remove

python remove_outliers.py
```

### Example 3: Conservative Data Cleaning

```bash
# Preserve data as much as possible
export OUTLIER_ACTION=cap         # Don't remove outliers, just cap them
export NULL_STRATEGY=fill_median  # Fill nulls instead of dropping
export NULL_THRESHOLD=0.8         # Only drop columns with >80% nulls

python remove_outliers.py
python clean_null_values.py
```

### Example 4: Parallel Processing Different Strategies

```bash
# Disable chaining to run all on raw data
export CHAIN_TRANSFORMATIONS=false

# Run different strategies in parallel
export OUTLIER_METHOD=iqr && python remove_outliers.py &
export OUTLIER_METHOD=zscore && python remove_outliers.py &
export OUTLIER_METHOD=isolation_forest && python remove_outliers.py &
wait
```

### Example 5: Iterative Cleaning

```bash
# Round 1: Basic cleanup
export UPDATE_RAW_DATA=true
python remove_duplicates.py  # This updates the raw data

# Round 2: Advanced cleaning on improved data
export UPDATE_RAW_DATA=false
export OUTLIER_METHOD=isolation_forest
python remove_outliers.py
python clean_null_values.py
```

## 👨‍💻 Development Workflow

### Local Development Process

1. **Prepare Test Data**:
   ```bash
   mkdir -p ./pipeline_output
   # Put your test CSV file as ./pipeline_output/raw_data.csv
   ```

2. **Test Locally**:
   ```bash
   export TEST_MODE=local
   python remove_duplicates.py
   ```

3. **Check Results**:
   ```bash
   ls -la ./pipeline_output/deduplicated/
   # Look at stats file
   cat ./pipeline_output/deduplicated/deduplication_stats.json
   ```

4. **Deploy to S3**:
   ```bash
   export TEST_MODE=s3
   # Set S3 credentials
   python load_data_from_s3.py
   python remove_duplicates.py
   ```

### Adding New Transformations

To add a new transformation node:

1. **Copy existing script** as template
2. **Modify the main processing function**
3. **Update environment variable handling**
4. **Ensure smart input detection works**
5. **Add appropriate statistics and visualizations**

Example structure:
```python
def main():
    # 1. Parse environment variables
    # 2. Determine input source (auto-detect or override)
    # 3. Load data
    # 4. Process data
    # 5. Generate statistics
    # 6. Save results (with optional raw data update)
```

### Testing Your Changes

```bash
# Test with small dataset first
export TEST_MODE=local
# ... run your modified script

# Check outputs
ls -la ./pipeline_output/your_transformation/
python -c "import json; print(json.load(open('./pipeline_output/your_transformation/stats.json')))"
```

## 📁 File Structure

### Local Mode Structure
```
pipeline_output/
├── raw_data.pkl                    # Your input data
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

### S3 Mode Structure
```
s3://your-bucket/your-prefix/
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

### Multi-Branch Structure (Advanced)
```
s3://your-bucket/pipeline-data/
├── input_data.pkl                    # Main input
├── iqr-branch/                       # Aggressive cleaning
│   ├── outliers_removed_data.pkl
│   ├── nulls_cleaned_data.pkl
│   └── *.json
├── isolation-branch/                 # ML-based cleaning
│   ├── outliers_removed_data.pkl
│   ├── nulls_cleaned_data.pkl
│   └── *.json
└── conservative-branch/              # Data-preserving cleaning
    ├── outliers_removed_data.pkl
    ├── nulls_cleaned_data.pkl
    └── *.json
```

## 🐛 Debugging & Troubleshooting

### Common Issues & Solutions

#### 1. "No input data found" Error

**Symptoms**: Script exits with "No input data found! Please run the data loader first."

**Cause**: The auto-detection can't find any input files

**Solutions**:
```bash
# Check if raw data exists
ls -la ./pipeline_output/raw_data.pkl  # Local mode
# or
aws s3 ls s3://your-bucket/your-prefix/input_data.pkl  # S3 mode

# Force specific input
export INPUT_SOURCE=raw
# or
export INPUT_KEY=specific/path/to/data.pkl
```

#### 2. S3 Connection Errors

**Symptoms**: Connection timeouts, authentication errors

**Debug steps**:
```bash
# Test S3 connection manually
python -c "
import boto3
client = boto3.client('s3', 
    endpoint_url='$MINIO_ENDPOINT',
    aws_access_key_id='$MINIO_ACCESS_KEY',
    aws_secret_access_key='$MINIO_SECRET_KEY'
)
print(client.list_buckets())
"

# Check environment variables
echo $MINIO_ENDPOINT
echo $MINIO_ACCESS_KEY
```

#### 3. Memory Issues with Large Datasets

**Symptoms**: Out of memory errors, slow processing

**Solutions**:
```bash
# Use more efficient methods
export OUTLIER_METHOD=iqr          # Faster than isolation_forest
export NULL_STRATEGY=fill_median   # Faster than fill_mode

# Process smaller chunks (modify script)
# Or use more efficient data types
```

#### 4. Wrong Input Source Selected

**Symptoms**: Pipeline using unexpected input data

**Debug**:
```bash
# Check what files exist
ls -la ./pipeline_output/*/
# or
aws s3 ls s3://your-bucket/your-prefix/ --recursive

# Force specific input
export INPUT_SOURCE=raw
# or disable auto-detection
export CHAIN_TRANSFORMATIONS=false
```

### Debug Mode

Enable detailed logging:
```bash
# Add this to your environment
export DEBUG=true

# Run with verbose output
python remove_duplicates.py 2>&1 | tee debug.log
```

### Monitoring Pipeline Health

Check processing statistics:
```bash
# View stats from last run
python -c "
import json
stats = json.load(open('./pipeline_output/null_cleaned/null_cleaning_stats.json'))
print(f'Processed: {stats[\"initial_rows\"]} → {stats[\"final_rows\"]} rows')
print(f'Removed: {stats[\"nulls_removed\"]} null values')
print(f'Processing time: {stats[\"timestamp\"]}')
"
```

## 🎯 Advanced Features

### Multi-Branch Processing

Create different processing strategies:
```bash
# Setup different branches
export OUTPUT_PREFIX=pipeline-data/aggressive-branch
export OUTLIER_METHOD=iqr
export OUTLIER_THRESHOLD=1.5
python remove_outliers.py

export OUTPUT_PREFIX=pipeline-data/conservative-branch  
export OUTLIER_METHOD=iqr
export OUTLIER_THRESHOLD=3.0
export OUTLIER_ACTION=cap
python remove_outliers.py
```

### Pipeline Orchestration with Airflow

Example DAG:
```python
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'smart_data_pipeline',
    default_args=default_args,
    description='Smart data processing pipeline',
    schedule_interval='@daily',
    catchup=False
)

load_data = BashOperator(
    task_id='load_data',
    bash_command='python load_data_from_s3.py',
    env={'INPUT_CSV': '{{ ds }}_data.csv'},  # Use date for daily processing
    dag=dag
)

remove_duplicates = BashOperator(
    task_id='remove_duplicates',
    bash_command='python remove_duplicates.py',
    dag=dag
)

remove_outliers = BashOperator(
    task_id='remove_outliers',
    bash_command='python remove_outliers.py',
    env={'OUTLIER_METHOD': 'iqr', 'OUTLIER_THRESHOLD': '2.0'},
    dag=dag
)

clean_nulls = BashOperator(
    task_id='clean_nulls',
    bash_command='python clean_null_values.py',
    env={'NULL_STRATEGY': 'fill_median'},
    dag=dag
)

# Set dependencies
load_data >> remove_duplicates >> remove_outliers >> clean_nulls
```

### Custom Processing Logic

You can extend the pipeline by modifying the processing functions:

```python
# In remove_outliers.py, you can add custom outlier detection:
def detect_outliers_custom(df, columns, threshold=2.0):
    """Your custom outlier detection logic"""
    outlier_indices = []
    # ... your logic here
    return outlier_indices, outlier_details

# Then use it in the main function:
if method == 'custom':
    outlier_indices, outlier_details = detect_outliers_custom(df, columns, threshold)
```

### Performance Optimization

For large datasets:
```bash
# Use efficient methods
export OUTLIER_METHOD=iqr              # O(n log n) vs O(n²) for isolation forest
export NULL_STRATEGY=fill_median       # Faster than mode calculation
export DUPLICATE_SUBSET=key_columns    # Check only important columns

# Parallel processing
export CHAIN_TRANSFORMATIONS=false
python remove_duplicates.py &
python remove_outliers.py &
python clean_null_values.py &
wait
```

## 📊 Understanding Output Files

### Statistics Files Structure

**Deduplication Stats**:
```json
{
  "initial_rows": 10000,
  "final_rows": 9500,
  "duplicates_found": 500,
  "removal_percentage": 5.0,
  "timestamp": "2024-01-01T12:00:00",
  "transformation": "remove_duplicates"
}
```

**Outlier Removal Stats**:
```json
{
  "initial_rows": 9500,
  "final_rows": 9200,
  "outliers_detected": 300,
  "method": "iqr",
  "threshold": 1.5,
  "outlier_details": {
    "column1": {
      "outlier_count": 150,
      "outlier_percentage": 1.58
    }
  }
}
```

### Visualization Data

The `*_plotly.json` files contain data for creating visualizations:
- Bar charts showing before/after comparisons
- Pie charts showing data composition
- Column-wise analysis charts

## 📞 Support & Contributing

### Getting Help

1. **Check the logs** - Each script outputs detailed information
2. **Review environment variables** - Most issues are configuration related
3. **Test with small datasets** - Isolate issues with minimal data
4. **Check file permissions** - Ensure read/write access to directories

### Contributing

To contribute improvements:
1. Fork the repository
2. Create a feature branch
3. Test your changes thoroughly
4. Submit a pull request with clear description

### Best Practices

- **Always test locally first** before deploying to production
- **Use version control** for your pipeline configurations
- **Monitor resource usage** with large datasets
- **Backup your data** before running transformations
- **Document custom configurations** for your team

---

**🎉 Happy Data Processing!**

*This pipeline is designed to be flexible and extensible. Don't hesitate to modify it for your specific needs!*