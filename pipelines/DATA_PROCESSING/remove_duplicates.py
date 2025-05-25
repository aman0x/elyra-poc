#!/usr/bin/env python
"""
Smart Remove Duplicates Transformation Node
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
  - DUPLICATE_SUBSET: Comma-separated column names to check for duplicates (optional - all columns if not specified)
  - KEEP_FIRST: Which duplicate to keep - 'first' or 'last' (default: 'first')

Output:
- Saves deduplicated data as pickle file in S3/local
- Saves deduplication statistics JSON in S3/local
- Saves plotly visualization data JSON in S3/local
- Optionally updates raw data file for downstream steps
"""

import os
import sys
import subprocess
from datetime import datetime

# Install required packages FIRST
print("Installing required packages...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "boto3", "pandas"])

# NOW import the packages after installation
import pandas as pd
import boto3
from botocore.client import Config
import io
import pickle
import json


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
    
    # Priority order: most processed to least processed (excludes self)
    possible_inputs = [
        (f"{prefix}/nulls_cleaned_data.pkl", "null_cleaned"),
        (f"{prefix}/outliers_removed_data.pkl", "outliers_removed"),
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
    
    # Priority order: most processed to least processed (excludes self)
    possible_inputs = [
        (f"{base_path}/null_cleaned/nulls_cleaned_data.pkl", "null_cleaned"),
        (f"{base_path}/outliers_removed/outliers_removed_data.pkl", "outliers_removed"),
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
        pickle_path = os.path.join(output_path, 'deduplicated_data.pkl')
        with open(pickle_path, 'wb') as f:
            pickle.dump(df, f)
        print(f"💾 Data saved to: {pickle_path}")
        
        # Save stats
        stats_path = os.path.join(output_path, 'deduplication_stats.json')
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"📊 Stats saved to: {stats_path}")
        
        # Save plotly data
        plotly_path = os.path.join(output_path, 'deduplication_plotly.json')
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
        pickle_key = f"{prefix}/deduplicated_data.pkl"
        stats_key = f"{prefix}/deduplication_stats.json"
        plotly_key = f"{prefix}/deduplication_plotly.json"
        
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


def remove_duplicates(df, subset=None, keep='first'):
    """Remove duplicate rows from DataFrame"""
    initial_shape = df.shape
    initial_duplicates = df.duplicated(subset=subset).sum()
    
    # Remove duplicates
    df_cleaned = df.drop_duplicates(subset=subset, keep=keep)
    
    final_shape = df_cleaned.shape
    removed_count = initial_shape[0] - final_shape[0]
    
    stats = {
        'initial_rows': initial_shape[0],
        'initial_columns': initial_shape[1],
        'initial_duplicates': int(initial_duplicates),
        'final_rows': final_shape[0],
        'final_columns': final_shape[1],
        'removed_rows': removed_count,
        'removal_percentage': (removed_count / initial_shape[0] * 100) if initial_shape[0] > 0 else 0
    }
    
    return df_cleaned, stats


def create_plotly_data(stats):
    """Create Plotly-compatible visualization data"""
    plotly_data = {
        'bar_chart': {
            'data': [{
                'x': ['Original', 'After Deduplication'],
                'y': [stats['initial_rows'], stats['final_rows']],
                'type': 'bar',
                'marker': {
                    'color': ['#3498db', '#2ecc71']
                },
                'text': [f"{stats['initial_rows']:,}", f"{stats['final_rows']:,}"],
                'textposition': 'outside'
            }],
            'layout': {
                'title': 'Dataset Size Comparison',
                'yaxis': {'title': 'Number of Rows'},
                'showlegend': False
            }
        },
        'pie_chart': {
            'data': [{
                'values': [stats['final_rows'], stats['removed_rows']] if stats['removed_rows'] > 0 else [stats['final_rows']],
                'labels': ['Unique Rows', 'Duplicates Removed'] if stats['removed_rows'] > 0 else ['All Unique Rows'],
                'type': 'pie',
                'marker': {
                    'colors': ['#2ecc71', '#e74c3c'] if stats['removed_rows'] > 0 else ['#2ecc71']
                },
                'hole': 0.3
            }],
            'layout': {
                'title': 'Data Composition'
            }
        },
        'summary': {
            'transformation': 'remove_duplicates',
            'metrics': stats
        }
    }
    
    return plotly_data


def main():
    """Main execution function"""
    print("🚀 Starting Smart Remove Duplicates Transformation Node")
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
        
        output_path = os.getenv('OUTPUT_PATH', './pipeline_output/deduplicated')
        
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
    duplicate_subset = os.getenv('DUPLICATE_SUBSET', '')
    keep_first = os.getenv('KEEP_FIRST', 'first')
    subset_cols = [col.strip() for col in duplicate_subset.split(',') if col.strip()] if duplicate_subset else None
    
    print(f"\n🎛️  Transformation Parameters:")
    print(f"  - Check Columns: {subset_cols if subset_cols else 'All columns'}")
    print(f"  - Keep: {keep_first}")
    
    try:
        # Load data
        if test_mode == 'local':
            df = load_data('local', input_path=input_path)
        else:
            df = load_data('s3', s3_client=s3_client, bucket=input_bucket, key=input_key)
        
        print(f"\n✅ Successfully loaded data! Shape: {df.shape}")
        
        # Remove duplicates
        print(f"\n🧹 Removing duplicates...")
        df_cleaned, stats = remove_duplicates(df, subset=subset_cols, keep=keep_first)
        
        # Print results
        print(f"\n📊 Results:")
        print(f"  - Original rows: {stats['initial_rows']:,}")
        print(f"  - Duplicates found: {stats['initial_duplicates']:,}")
        print(f"  - Rows removed: {stats['removed_rows']:,}")
        print(f"  - Final rows: {stats['final_rows']:,}")
        print(f"  - Removal rate: {stats['removal_percentage']:.2f}%")
        
        # Create Plotly data
        print(f"\n📈 Creating Plotly visualization data...")
        plotly_data = create_plotly_data(stats)
        
        # Add metadata
        stats['timestamp'] = datetime.now().isoformat()
        stats['transformation'] = 'remove_duplicates'
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
        
        print(f"\n✅ Smart Remove Duplicates Node completed successfully!")
        print(f"📊 Processed {source_type} data → deduplicated data")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Smart Remove Duplicates Node failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())