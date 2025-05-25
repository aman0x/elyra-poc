#!/usr/bin/env python
"""
Clean Null Values Transformation Node with Local Testing Support - INDEPENDENT VERSION
====================================================================================
This node handles missing values in the dataset using various strategies.
Works independently from raw data, just like outliers and duplicates removal.

Parameters (via environment variables):
- TEST_MODE: Set to 'local' for local file operations, otherwise uses S3
- For S3 mode: Same as original (MINIO_ENDPOINT, etc.)
- For Local mode:
  - INPUT_PATH: Local path to input pickle file
  - OUTPUT_PATH: Local directory for outputs
  - NULL_STRATEGY: Strategy to handle nulls - 'drop_rows', 'drop_cols', 'fill_mean', 'fill_median', 'fill_mode', 'fill_zero', 'fill_forward', 'fill_backward' (default: 'fill_median')
  - NULL_THRESHOLD: For drop_cols strategy, threshold for dropping columns (default: 0.5)
  - NULL_COLUMNS: Comma-separated column names to clean (optional - all if not specified)
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
        # Original S3 save logic
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
        # Drop rows with any null values in specified columns
        df_cleaned = df_cleaned.dropna(subset=columns)
        
    elif strategy == 'drop_cols':
        # Drop columns with missing values above threshold
        cols_to_drop = []
        for col in columns:
            if col in df_cleaned.columns:
                missing_pct = df_cleaned[col].isnull().sum() / len(df_cleaned)
                if missing_pct > threshold:
                    cols_to_drop.append(col)
        
        df_cleaned = df_cleaned.drop(columns=cols_to_drop)
        print(f"🗑️  Dropped {len(cols_to_drop)} columns with >{threshold*100}% missing values")
        
    elif strategy == 'fill_mean':
        # Fill numeric columns with mean
        for col in columns:
            if col in df_cleaned.columns and pd.api.types.is_numeric_dtype(df_cleaned[col]):
                df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].mean())
                
    elif strategy == 'fill_median':
        # Fill numeric columns with median
        for col in columns:
            if col in df_cleaned.columns and pd.api.types.is_numeric_dtype(df_cleaned[col]):
                df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].median())
                
    elif strategy == 'fill_mode':
        # Fill all columns with mode
        for col in columns:
            if col in df_cleaned.columns and df_cleaned[col].isnull().any():
                mode_values = df_cleaned[col].mode()
                if not mode_values.empty:
                    df_cleaned[col] = df_cleaned[col].fillna(mode_values[0])
                    
    elif strategy == 'fill_zero':
        # Fill with zero
        for col in columns:
            if col in df_cleaned.columns:
                df_cleaned[col] = df_cleaned[col].fillna(0)
                
    elif strategy == 'fill_forward':
        # Forward fill
        for col in columns:
            if col in df_cleaned.columns:
                df_cleaned[col] = df_cleaned[col].fillna(method='ffill')
                
    elif strategy == 'fill_backward':
        # Backward fill
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
    # Get columns with most missing values before cleaning
    missing_before = stats['missing_before']
    sorted_cols = sorted(missing_before.items(), 
                        key=lambda x: x[1]['missing_percentage'], 
                        reverse=True)[:10]
    
    col_names = [col[0] for col in sorted_cols]
    missing_pcts_before = [col[1]['missing_percentage'] for col in sorted_cols]
    
    # Get missing percentages after cleaning for same columns
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
    print("🚀 Starting Clean Null Values Transformation Node")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check test mode
    test_mode = os.getenv('TEST_MODE', 'local')
    
    if test_mode == 'local':
        print("🧪 Running in LOCAL TEST MODE")
        
        # Local mode parameters - INDEPENDENT INPUT PATH (same as outliers/duplicates)
        input_path = os.getenv('INPUT_PATH', './pipeline_output/raw_data.pkl')
        output_path = os.getenv('OUTPUT_PATH', './pipeline_output/null_cleaned')
        
        # Check if input exists
        if not os.path.exists(input_path):
            print(f"❌ Input file not found: {input_path}")
            return 1
            
        print(f"\n📌 Local Configuration:")
        print(f"  - Input: {input_path}")
        print(f"  - Output: {output_path}")
        
    else:
        print("☁️  Running in S3 MODE")
        
        # S3 mode parameters - INDEPENDENT (same as outliers/duplicates)
        endpoint = os.getenv('MINIO_ENDPOINT', 'http://localhost:9000')
        access_key = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
        secret_key = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
        input_bucket = os.getenv('INPUT_BUCKET', 'pipeline-data')
        input_key = os.getenv('INPUT_KEY', 'pipeline-data/input_data.pkl')  # INDEPENDENT - SAME AS OTHERS
        output_prefix = os.getenv('OUTPUT_PREFIX', 'pipeline-data')
        output_bucket = os.getenv('OUTPUT_BUCKET', input_bucket)
        
        print(f"\n📌 S3 Configuration:")
        print(f"  - Endpoint: {endpoint}")
        print(f"  - Input: s3://{input_bucket}/{input_key}")
        print(f"  - Output: s3://{output_bucket}/{output_prefix}")
    
    # Common parameters
    strategy = os.getenv('NULL_STRATEGY', 'fill_median')
    threshold = float(os.getenv('NULL_THRESHOLD', '0.5'))
    null_columns = os.getenv('NULL_COLUMNS', '')
    
    # Parse columns
    columns = [col.strip() for col in null_columns.split(',') if col.strip()] if null_columns else None
    
    print(f"  - Strategy: {strategy}")
    if strategy == 'drop_cols':
        print(f"  - Threshold: {threshold}")
    print(f"  - Columns: {columns if columns else 'All columns'}")
    
    try:
        # Load data
        if test_mode == 'local':
            df = load_data('local', input_path=input_path)
        else:
            s3_client = create_s3_client(endpoint, access_key, secret_key)
            df = load_data('s3', s3_client=s3_client, bucket=input_bucket, key=input_key)
        
        print(f"✅ Successfully loaded data! Shape: {df.shape}")
        
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
        
        # Save results
        print(f"\n💾 Saving results...")
        if test_mode == 'local':
            save_results('local', df_cleaned, stats, plotly_data, output_path=output_path)
            
            # Update config for next node
            config_path = os.path.join(os.path.dirname(output_path), 'test_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                config['null_cleaned_data_path'] = os.path.join(output_path, 'nulls_cleaned_data.pkl')
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
            
        else:
            s3_client = create_s3_client(endpoint, access_key, secret_key)
            save_results('s3', df_cleaned, stats, plotly_data, 
                        s3_client=s3_client, bucket=output_bucket, prefix=output_prefix)
        
        print(f"\n✅ Clean Null Values Node completed successfully!")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Clean Null Values Node failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())