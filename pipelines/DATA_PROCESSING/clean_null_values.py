#!/usr/bin/env python
"""
Smart Clean Null Values Transformation Node
==========================================
Enhanced pipeline node with intelligent input selection and chaining capabilities.

Parameters (via environment variables):
- TEST_MODE: Set to 'local' for local file operations, otherwise uses S3
- For Local mode:
  - INPUT_PATH: Local path to input pickle file (optional - auto-detected if not set)
  - OUTPUT_PATH: Local directory for outputs
- For S3 mode:
  - MINIO_ENDPOINT: MinIO endpoint URL (default: http://localhost:9000)
  - MINIO_ACCESS_KEY: Access key (default: minioadmin)
  - MINIO_SECRET_KEY: Secret key (default: minioadmin)
  - INPUT_BUCKET: S3 bucket for input (default: pipeline-data)
  - INPUT_KEY: S3 key for input pickle file (optional - auto-detected if not set)
  - OUTPUT_BUCKET: S3 bucket for output (defaults to INPUT_BUCKET)
  - OUTPUT_PREFIX: S3 prefix for output files (default: pipeline-data)
- Pipeline Control:
  - INPUT_SOURCE: Force specific input - 'raw', 'deduplicated', 'outliers_removed', 'null_cleaned' (optional)
  - CHAIN_TRANSFORMATIONS: Use output from previous transformation (default: true)
  - UPDATE_RAW_DATA: Update raw data file after transformation (default: false)
- Transformation parameters:
  - NULL_STRATEGY: Strategy to handle nulls (default: 'fill_median')
  - NULL_THRESHOLD: For drop_cols strategy, threshold for dropping columns (default: 0.5)
  - NULL_COLUMNS: Comma-separated column names to clean (optional - all columns if not specified)

Output:
- Saves null-cleaned data as pickle file in S3/local
- Saves null cleaning statistics JSON in S3/local
- Saves plotly visualization data JSON in S3/local
- Optionally updates raw data file for downstream steps
"""

import os
import sys
import subprocess

# Install required packages
print("Installing required packages...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "boto3", "pandas", "numpy"])

import pandas as pd
import numpy as np
import boto3
from botocore.client import Config
import io
import pickle
import json
from datetime import datetime


def create_s3_client(endpoint, access_key, secret_key):
    """Create S3 client configured for MinIO"""
    return boto3.client(
        's3',
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )


def auto_detect_best_input_s3(s3_client, bucket, prefix):
    """Automatically detect the best input file in S3"""
    print("🔍 Auto-detecting best input source...")
    
    # Priority order: most processed to least processed
    possible_inputs = [
        (f"{prefix}/outliers_removed_data.pkl", "outliers_removed"),
        (f"{prefix}/deduplicated_data.pkl", "deduplicated"),
        (f"{prefix}/input_data.pkl", "raw")
    ]
    
    for key, source_type in possible_inputs:
        try:
            s3_client.head_object(Bucket=bucket, Key=key)
            print(f"✅ Found {source_type} data: s3://{bucket}/{key}")
            return key, source_type
        except:
            print(f"❌ Not found: s3://{bucket}/{key}")
            continue
    
    raise Exception("❌ No input data found! Please run the data loader first.")


def auto_detect_best_input_local(base_path="./pipeline_output"):
    """Automatically detect the best input file locally"""
    print("🔍 Auto-detecting best local input source...")
    
    # Priority order: most processed to least processed
    possible_inputs = [
        (f"{base_path}/outliers_removed/outliers_removed_data.pkl", "outliers_removed"),
        (f"{base_path}/deduplicated/deduplicated_data.pkl", "deduplicated"),
        (f"{base_path}/raw_data.pkl", "raw")
    ]
    
    for path, source_type in possible_inputs:
        if os.path.exists(path):
            print(f"✅ Found {source_type} data: {path}")
            return path, source_type
        else:
            print(f"❌ Not found: {path}")
    
    raise Exception("❌ No input data found! Please run the data loader first.")


def get_smart_input_s3(s3_client, bucket, prefix, override_source=None):
    """Get input source with smart detection or override"""
    
    if override_source:
        # Force specific input source
        source_mapping = {
            'raw': f"{prefix}/input_data.pkl",
            'deduplicated': f"{prefix}/deduplicated_data.pkl", 
            'outliers_removed': f"{prefix}/outliers_removed_data.pkl",
            'null_cleaned': f"{prefix}/nulls_cleaned_data.pkl"
        }
        
        if override_source in source_mapping:
            key = source_mapping[override_source]
            try:
                s3_client.head_object(Bucket=bucket, Key=key)
                print(f"🎯 Using forced input source: {override_source} -> s3://{bucket}/{key}")
                return key, override_source
            except:
                print(f"⚠️  Forced source '{override_source}' not found, falling back to auto-detection")
    
    # Auto-detect best input
    return auto_detect_best_input_s3(s3_client, bucket, prefix)


def get_smart_input_local(override_source=None, base_path="./pipeline_output"):
    """Get local input source with smart detection or override"""
    
    if override_source:
        # Force specific input source
        source_mapping = {
            'raw': f"{base_path}/raw_data.pkl",
            'deduplicated': f"{base_path}/deduplicated/deduplicated_data.pkl",
            'outliers_removed': f"{base_path}/outliers_removed/outliers_removed_data.pkl",
            'null_cleaned': f"{base_path}/null_cleaned/nulls_cleaned_data.pkl"
        }
        
        if override_source in source_mapping:
            path = source_mapping[override_source]
            if os.path.exists(path):
                print(f"🎯 Using forced input source: {override_source} -> {path}")
                return path, override_source
            else:
                print(f"⚠️  Forced source '{override_source}' not found, falling back to auto-detection")
    
    # Auto-detect best input
    return auto_detect_best_input_local(base_path)


def load_data(test_mode, **kwargs):
    """Load data from S3 or local file"""
    if test_mode == 'local':
        input_path = kwargs['input_path']
        print(f"📥 Loading data from local file: {input_path}")
        with open(input_path, 'rb') as f:
            return pickle.load(f)
    else:
        s3_client = kwargs['s3_client']
        bucket = kwargs['bucket']
        key = kwargs['key']
        print(f"📥 Loading data from s3://{bucket}/{key}")
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        return pickle.loads(obj['Body'].read())


def save_results_with_options(test_mode, df, stats, plotly_data, **kwargs):
    """Save results with optional raw data update"""
    
    # Normal save
    paths = save_results_normal(test_mode, df, stats, plotly_data, **kwargs)
    
    # Optional: Update raw data for downstream steps
    update_raw = os.getenv('UPDATE_RAW_DATA', 'false').lower() == 'true'
    if update_raw:
        print("\n🔄 Updating raw data for downstream transformations...")
        update_raw_data(test_mode, df, **kwargs)
    
    return paths


def save_results_normal(test_mode, df, stats, plotly_data, **kwargs):
    """Normal save results to S3 or local file"""
    if test_mode == 'local':
        output_path = kwargs['output_path']
        os.makedirs(output_path, exist_ok=True)
        
        # Save pickle
        pickle_path = os.path.join(output_path, 'nulls_cleaned_data.pkl')
        with open(pickle_path, 'wb') as f:
            pickle.dump(df, f)
        print(f"💾 Data saved to: {pickle_path}")
        
        # Save stats
        stats_path = os.path.join(output_path, 'null_cleaning_stats.json')
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"📊 Stats saved to: {stats_path}")
        
        # Save plotly data
        plotly_path = os.path.join(output_path, 'null_cleaning_plotly.json')
        with open(plotly_path, 'w') as f:
            json.dump(plotly_data, f, indent=2)
        print(f"📈 Plotly data saved to: {plotly_path}")
        
        return pickle_path, stats_path, plotly_path
        
    else:
        # S3 save logic
        s3_client = kwargs['s3_client']
        bucket = kwargs['bucket']
        prefix = kwargs['prefix']
        
        # Define S3 paths
        pickle_key = f"{prefix}/nulls_cleaned_data.pkl"
        stats_key = f"{prefix}/null_cleaning_stats.json"
        plotly_key = f"{prefix}/null_cleaning_plotly.json"
        
        # Save DataFrame
        pickle_buffer = io.BytesIO()
        pickle.dump(df, pickle_buffer)
        pickle_buffer.seek(0)
        s3_client.put_object(Bucket=bucket, Key=pickle_key, Body=pickle_buffer.getvalue())
        print(f"💾 Data saved to: s3://{bucket}/{pickle_key}")
        
        # Save stats
        s3_client.put_object(Bucket=bucket, Key=stats_key, Body=json.dumps(stats, indent=2))
        print(f"📊 Stats saved to: s3://{bucket}/{stats_key}")
        
        # Save plotly data
        s3_client.put_object(Bucket=bucket, Key=plotly_key, Body=json.dumps(plotly_data, indent=2))
        print(f"📈 Plotly data saved to: s3://{bucket}/{plotly_key}")
        
        return pickle_key, stats_key, plotly_key


def update_raw_data(test_mode, df, **kwargs):
    """Update raw data file with transformed data"""
    if test_mode == 'local':
        base_path = kwargs.get('base_path', './pipeline_output')
        raw_path = f"{base_path}/raw_data.pkl"
        
        # Backup original if it exists
        if os.path.exists(raw_path):
            backup_path = f"{base_path}/raw_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
            os.rename(raw_path, backup_path)
            print(f"📦 Backed up original raw data to: {backup_path}")
        
        # Save new raw data
        with open(raw_path, 'wb') as f:
            pickle.dump(df, f)
        print(f"🔄 Updated raw data: {raw_path}")
        
    else:
        # S3 update
        s3_client = kwargs['s3_client']
        bucket = kwargs['bucket']
        prefix = kwargs['prefix']
        raw_key = f"{prefix}/input_data.pkl"
        
        # Backup original
        backup_key = f"{prefix}/input_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        try:
            s3_client.copy_object(
                Bucket=bucket,
                CopySource={'Bucket': bucket, 'Key': raw_key},
                Key=backup_key
            )
            print(f"📦 Backed up original raw data to: s3://{bucket}/{backup_key}")
        except:
            print("⚠️  No original raw data to backup")
        
        # Save new raw data
        pickle_buffer = io.BytesIO()
        pickle.dump(df, pickle_buffer)
        pickle_buffer.seek(0)
        s3_client.put_object(Bucket=bucket, Key=raw_key, Body=pickle_buffer.getvalue())
        print(f"🔄 Updated raw data: s3://{bucket}/{raw_key}")


def analyze_missing_values(df, columns=None):
    """Analyze missing values in DataFrame"""
    if columns is None:
        columns = df.columns.tolist()
    
    missing_stats = {}
    
    for col in columns:
        if col in df.columns:
            missing_count = df[col].isnull().sum()
            missing_pct = missing_count / len(df) * 100
            
            missing_stats[col] = {
                'missing_count': int(missing_count),
                'missing_percentage': float(missing_pct),
                'dtype': str(df[col].dtype)
            }
    
    return missing_stats


def clean_null_values(df, strategy='fill_median', threshold=0.5, columns=None):
    """Clean null values from DataFrame using specified strategy"""
    initial_shape = df.shape
    initial_nulls = df.isnull().sum().sum()
    df_cleaned = df.copy()
    
    # Get initial missing value stats
    missing_before = analyze_missing_values(df, columns)
    
    if columns is None:
        columns = df.columns.tolist()
    
    # Apply cleaning strategy
    if strategy == 'drop_rows':
        df_cleaned = df_cleaned.dropna(subset=columns)
    elif strategy == 'drop_cols':
        cols_to_drop = []
        for col in columns:
            if col in df_cleaned.columns:
                missing_pct = df_cleaned[col].isnull().sum() / len(df_cleaned)
                if missing_pct > threshold:
                    cols_to_drop.append(col)
        df_cleaned = df_cleaned.drop(columns=cols_to_drop)
        print(f"🗑️  Dropped {len(cols_to_drop)} columns with >{threshold*100}% missing values")
    elif strategy == 'fill_mean':
        for col in columns:
            if col in df_cleaned.columns and pd.api.types.is_numeric_dtype(df_cleaned[col]):
                df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].mean())
    elif strategy == 'fill_median':
        for col in columns:
            if col in df_cleaned.columns and pd.api.types.is_numeric_dtype(df_cleaned[col]):
                df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].median())
    elif strategy == 'fill_mode':
        for col in columns:
            if col in df_cleaned.columns and df_cleaned[col].isnull().any():
                mode_values = df_cleaned[col].mode()
                if not mode_values.empty:
                    df_cleaned[col] = df_cleaned[col].fillna(mode_values[0])
    elif strategy == 'fill_zero':
        for col in columns:
            if col in df_cleaned.columns:
                df_cleaned[col] = df_cleaned[col].fillna(0)
    elif strategy == 'fill_forward':
        for col in columns:
            if col in df_cleaned.columns:
                df_cleaned[col] = df_cleaned[col].fillna(method='ffill')
    elif strategy == 'fill_backward':
        for col in columns:
            if col in df_cleaned.columns:
                df_cleaned[col] = df_cleaned[col].fillna(method='bfill')
    
    # Get final missing value stats
    missing_after = analyze_missing_values(df_cleaned, df_cleaned.columns.tolist())
    
    final_shape = df_cleaned.shape
    final_nulls = df_cleaned.isnull().sum().sum()
    
    stats = {
        'initial_rows': initial_shape[0],
        'initial_columns': initial_shape[1],
        'initial_nulls': int(initial_nulls),
        'final_rows': final_shape[0],
        'final_columns': final_shape[1],
        'final_nulls': int(final_nulls),
        'rows_removed': initial_shape[0] - final_shape[0],
        'columns_removed': initial_shape[1] - final_shape[1],
        'nulls_removed': int(initial_nulls - final_nulls),
        'strategy': strategy,
        'threshold': threshold if strategy == 'drop_cols' else None,
        'columns_processed': len(columns),
        'missing_before': missing_before,
        'missing_after': missing_after
    }
    
    return df_cleaned, stats


def create_plotly_data(stats):
    """Create Plotly-compatible visualization data"""
    missing_before = stats['missing_before']
    sorted_cols = sorted(missing_before.items(), 
                        key=lambda x: x[1]['missing_percentage'], 
                        reverse=True)[:10]
    
    col_names = [col[0] for col in sorted_cols]
    missing_pcts_before = [col[1]['missing_percentage'] for col in sorted_cols]
    
    missing_after = stats['missing_after']
    missing_pcts_after = [missing_after.get(col, {}).get('missing_percentage', 0) 
                         for col in col_names]
    
    plotly_data = {
        'comparison_chart': {
            'data': [
                {
                    'x': ['Rows', 'Columns', 'Total Nulls'],
                    'y': [stats['initial_rows'], stats['initial_columns'], stats['initial_nulls']],
                    'type': 'bar',
                    'name': 'Before',
                    'marker': {'color': '#3498db'}
                },
                {
                    'x': ['Rows', 'Columns', 'Total Nulls'],
                    'y': [stats['final_rows'], stats['final_columns'], stats['final_nulls']],
                    'type': 'bar',
                    'name': 'After',
                    'marker': {'color': '#2ecc71'}
                }
            ],
            'layout': {
                'title': 'Data Cleaning Results',
                'barmode': 'group',
                'yaxis': {'title': 'Count'}
            }
        },
        'missing_by_column': {
            'data': [
                {
                    'x': col_names,
                    'y': missing_pcts_before,
                    'type': 'bar',
                    'name': 'Before',
                    'marker': {'color': '#e74c3c'}
                },
                {
                    'x': col_names,
                    'y': missing_pcts_after,
                    'type': 'bar',
                    'name': 'After',
                    'marker': {'color': '#2ecc71'}
                }
            ],
            'layout': {
                'title': 'Missing Values by Column (Top 10)',
                'barmode': 'group',
                'xaxis': {'tickangle': -45},
                'yaxis': {'title': 'Missing %'}
            }
        },
        'pie_chart': {
            'data': [{
                'values': [stats['final_nulls'], stats['nulls_removed']] if stats['nulls_removed'] > 0 else [stats['initial_nulls']],
                'labels': ['Remaining Nulls', 'Nulls Cleaned'] if stats['nulls_removed'] > 0 else ['All Clean'],
                'type': 'pie',
                'marker': {
                    'colors': ['#f39c12', '#2ecc71'] if stats['nulls_removed'] > 0 else ['#2ecc71']
                },
                'hole': 0.3
            }],
            'layout': {
                'title': 'Null Value Handling'
            }
        },
        'summary': {
            'transformation': 'clean_null_values',
            'metrics': stats
        }
    }
    
    return plotly_data


def main():
    """Main execution function"""
    print("🚀 Starting Smart Clean Null Values Transformation Node")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check test mode
    test_mode = os.getenv('TEST_MODE', 'local')
    
    # Pipeline control parameters
    input_source_override = os.getenv('INPUT_SOURCE')  # raw, deduplicated, outliers_removed, null_cleaned
    chain_transformations = os.getenv('CHAIN_TRANSFORMATIONS', 'true').lower() == 'true'
    update_raw = os.getenv('UPDATE_RAW_DATA', 'false').lower() == 'true'
    
    print(f"\n🔧 Pipeline Configuration:")
    print(f"  - Input Source Override: {input_source_override or 'Auto-detect'}")
    print(f"  - Chain Transformations: {chain_transformations}")
    print(f"  - Update Raw Data: {update_raw}")
    
    if test_mode == 'local':
        print("\n🧪 Running in LOCAL MODE")
        
        # Smart input selection for local mode
        override_path = os.getenv('INPUT_PATH')
        if override_path:
            input_path = override_path
            source_type = "manual_override"
            print(f"🎯 Using manual input path: {input_path}")
        else:
            if chain_transformations:
                input_path, source_type = get_smart_input_local(input_source_override)
            else:
                input_path = "./pipeline_output/raw_data.pkl"
                source_type = "raw"
                print(f"🎯 Using raw data (chaining disabled): {input_path}")
        
        output_path = os.getenv('OUTPUT_PATH', './pipeline_output/null_cleaned')
        
        # Check if input exists
        if not os.path.exists(input_path):
            print(f"❌ Input file not found: {input_path}")
            return 1
            
        print(f"\n📌 Local Configuration:")
        print(f"  - Input: {input_path} ({source_type})")
        print(f"  - Output: {output_path}")
        
    else:
        print("\n☁️  Running in S3 MODE")
        
        # S3 parameters
        endpoint = os.getenv('MINIO_ENDPOINT', 'http://localhost:9000')
        access_key = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
        secret_key = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
        input_bucket = os.getenv('INPUT_BUCKET', 'pipeline-data')
        output_prefix = os.getenv('OUTPUT_PREFIX', 'pipeline-data')
        output_bucket = os.getenv('OUTPUT_BUCKET', input_bucket)
        
        # Create S3 client
        s3_client = create_s3_client(endpoint, access_key, secret_key)
        
        # Smart input selection for S3 mode
        override_key = os.getenv('INPUT_KEY')
        if override_key:
            input_key = override_key
            source_type = "manual_override"
            print(f"🎯 Using manual input key: {input_key}")
        else:
            if chain_transformations:
                input_key, source_type = get_smart_input_s3(s3_client, input_bucket, output_prefix, input_source_override)
            else:
                input_key = f"{output_prefix}/input_data.pkl"
                source_type = "raw"
                print(f"🎯 Using raw data (chaining disabled): {input_key}")
        
        print(f"\n📌 S3 Configuration:")
        print(f"  - Endpoint: {endpoint}")
        print(f"  - Input: s3://{input_bucket}/{input_key} ({source_type})")
        print(f"  - Output: s3://{output_bucket}/{output_prefix}")
    
    # Transformation parameters
    strategy = os.getenv('NULL_STRATEGY', 'fill_median')
    threshold = float(os.getenv('NULL_THRESHOLD', '0.5'))
    null_columns = os.getenv('NULL_COLUMNS', '')
    
    # Parse columns
    columns = [col.strip() for col in null_columns.split(',') if col.strip()] if null_columns else None
    
    print(f"\n🎛️  Transformation Parameters:")
    print(f"  - Strategy: {strategy}")
    if strategy == 'drop_cols':
        print(f"  - Threshold: {threshold}")
    print(f"  - Columns: {columns if columns else 'All columns'}")
    
    try:
        # Load data
        if test_mode == 'local':
            df = load_data('local', input_path=input_path)
        else:
            df = load_data('s3', s3_client=s3_client, bucket=input_bucket, key=input_key)
        
        print(f"\n✅ Successfully loaded data! Shape: {df.shape}")
        
        # Clean null values
        print(f"\n🧹 Cleaning null values using '{strategy}' strategy...")
        df_cleaned, stats = clean_null_values(df, strategy=strategy, threshold=threshold, columns=columns)
        
        # Print results
        print(f"\n📊 Results:")
        print(f"  - Initial shape: {stats['initial_rows']} rows × {stats['initial_columns']} columns")
        print(f"  - Final shape: {stats['final_rows']} rows × {stats['final_columns']} columns")
        print(f"  - Initial nulls: {stats['initial_nulls']:,}")
        print(f"  - Final nulls: {stats['final_nulls']:,}")
        print(f"  - Nulls removed: {stats['nulls_removed']:,}")
        print(f"  - Rows removed: {stats['rows_removed']:,}")
        print(f"  - Columns removed: {stats['columns_removed']:,}")
        
        # Create Plotly visualization data
        print(f"\n📈 Creating Plotly visualization data...")
        plotly_data = create_plotly_data(stats)
        
        # Add metadata
        stats['timestamp'] = datetime.now().isoformat()
        stats['transformation'] = 'clean_null_values'
        stats['test_mode'] = test_mode
        stats['input_source_type'] = source_type
        stats['pipeline_config'] = {
            'input_source_override': input_source_override,
            'chain_transformations': chain_transformations,
            'update_raw_data': update_raw
        }
        
        # Save results with options
        print(f"\n💾 Saving results...")
        if test_mode == 'local':
            save_results_with_options('local', df_cleaned, stats, plotly_data, 
                                    output_path=output_path, base_path='./pipeline_output')
        else:
            save_results_with_options('s3', df_cleaned, stats, plotly_data, 
                                    s3_client=s3_client, bucket=output_bucket, prefix=output_prefix)
        
        print(f"\n✅ Smart Clean Null Values Node completed successfully!")
        print(f"📊 Processed {source_type} data → nulls_cleaned data")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Smart Clean Null Values Node failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())