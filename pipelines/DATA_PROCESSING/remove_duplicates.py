#!/usr/bin/env python
"""
Remove Duplicates Transformation Node with Local Testing Support - FIXED VERSION
==============================================================================
This node removes duplicate rows and supports both S3 and local file operations.

Parameters (via environment variables):
- TEST_MODE: Set to 'local' for local file operations, otherwise uses S3
- For S3 mode: Same as original (MINIO_ENDPOINT, etc.)
- For Local mode:
  - INPUT_PATH: Local path to input pickle file
  - OUTPUT_PATH: Local directory for outputs
  - DUPLICATE_SUBSET: Comma-separated column names (optional)
  - KEEP_FIRST: 'first' or 'last' (default: 'first')
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


def save_results(test_mode, df, stats, plotly_data, **kwargs):
    """Save results to S3 or local file"""
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
        # Original S3 save logic
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
    print("🚀 Starting Remove Duplicates Transformation Node")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check test mode
    test_mode = os.getenv('TEST_MODE', 'local')
    
    if test_mode == 'local':
        print("🧪 Running in LOCAL TEST MODE")
        
        # Local mode parameters - INDEPENDENT INPUT PATH
        input_path = os.getenv('INPUT_PATH', './pipeline_output/raw_data.pkl')
        output_path = os.getenv('OUTPUT_PATH', './pipeline_output/deduplicated')
        
        # Check if input exists
        if not os.path.exists(input_path):
            print(f"❌ Input file not found: {input_path}")
            return 1
            
        print(f"\n📌 Local Configuration:")
        print(f"  - Input: {input_path}")
        print(f"  - Output: {output_path}")
        
    else:
        print("☁️  Running in S3 MODE")
        
        # S3 mode parameters
        endpoint = os.getenv('MINIO_ENDPOINT', 'http://localhost:9000')
        access_key = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
        secret_key = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
        input_bucket = os.getenv('INPUT_BUCKET', 'pipeline-data')
        input_key = os.getenv('INPUT_KEY', 'pipeline-data/input_data.pkl')
        output_prefix = os.getenv('OUTPUT_PREFIX', 'pipeline-data')
        output_bucket = os.getenv('OUTPUT_BUCKET', input_bucket)
        
        print(f"\n📌 S3 Configuration:")
        print(f"  - Endpoint: {endpoint}")
        print(f"  - Input: s3://{input_bucket}/{input_key}")
        print(f"  - Output: s3://{output_bucket}/{output_prefix}")
    
    # Common parameters
    duplicate_subset = os.getenv('DUPLICATE_SUBSET', '')
    keep_first = os.getenv('KEEP_FIRST', 'first')
    subset_cols = [col.strip() for col in duplicate_subset.split(',') if col.strip()] if duplicate_subset else None
    
    print(f"  - Check Columns: {subset_cols if subset_cols else 'All columns'}")
    print(f"  - Keep: {keep_first}")
    
    try:
        # Load data
        if test_mode == 'local':
            df = load_data('local', input_path=input_path)
        else:
            s3_client = create_s3_client(endpoint, access_key, secret_key)
            df = load_data('s3', s3_client=s3_client, bucket=input_bucket, key=input_key)
        
        print(f"✅ Successfully loaded data! Shape: {df.shape}")
        
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
        
        # Save results
        print(f"\n💾 Saving results...")
        if test_mode == 'local':
            save_results('local', df_cleaned, stats, plotly_data, output_path=output_path)
            
            # Update config for next node
            config_path = os.path.join(os.path.dirname(output_path), 'test_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                config['deduplicated_data_path'] = os.path.join(output_path, 'deduplicated_data.pkl')
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
            
        else:
            save_results('s3', df_cleaned, stats, plotly_data, 
                        s3_client=s3_client, bucket=output_bucket, prefix=output_prefix)
        
        print(f"\n✅ Remove Duplicates Node completed successfully!")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Remove Duplicates Node failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())