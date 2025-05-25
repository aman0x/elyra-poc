#!/usr/bin/env python
"""
Smart Remove Outliers Transformation Node
=========================================
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
  - OUTLIER_METHOD: Detection method - 'iqr', 'zscore', 'isolation_forest', 'modified_zscore' (default: 'iqr')
  - OUTLIER_THRESHOLD: Threshold for outlier detection (default varies by method)
  - OUTLIER_COLUMNS: Comma-separated column names to check (optional - numeric columns if not specified)
  - OUTLIER_ACTION: Action to take - 'remove', 'cap' (default: 'remove')

Output:
- Saves outlier-cleaned data as pickle file in S3/local
- Saves outlier removal statistics JSON in S3/local
- Saves plotly visualization data JSON in S3/local
- Optionally updates raw data file for downstream steps
"""

import os
import sys
import subprocess

# Install required packages
print("Installing required packages...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "boto3", "pandas", "numpy", "scikit-learn"])

import pandas as pd
import numpy as np
import boto3
from botocore.client import Config
import io
import pickle
import json
from datetime import datetime
from sklearn.ensemble import IsolationForest
from scipy import stats


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
    
    # Priority order: most processed to least processed (excludes self)
    possible_inputs = [
        (f"{base_path}/null_cleaned/nulls_cleaned_data.pkl", "null_cleaned"),
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
        pickle_path = os.path.join(output_path, 'outliers_removed_data.pkl')
        with open(pickle_path, 'wb') as f:
            pickle.dump(df, f)
        print(f"💾 Data saved to: {pickle_path}")
        
        # Save stats
        stats_path = os.path.join(output_path, 'outlier_removal_stats.json')
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"📊 Stats saved to: {stats_path}")
        
        # Save plotly data
        plotly_path = os.path.join(output_path, 'outlier_removal_plotly.json')
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
        pickle_key = f"{prefix}/outliers_removed_data.pkl"
        stats_key = f"{prefix}/outlier_removal_stats.json"
        plotly_key = f"{prefix}/outlier_removal_plotly.json"
        
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


def detect_outliers_iqr(df, columns, threshold=1.5):
    """Detect outliers using Interquartile Range method"""
    outlier_indices = set()
    outlier_details = {}
    
    for col in columns:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            
            col_outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)].index
            outlier_indices.update(col_outliers)
            
            outlier_details[col] = {
                'method': 'IQR',
                'threshold': threshold,
                'lower_bound': float(lower_bound),
                'upper_bound': float(upper_bound),
                'outlier_count': len(col_outliers),
                'outlier_percentage': len(col_outliers) / len(df) * 100
            }
    
    return list(outlier_indices), outlier_details


def detect_outliers_zscore(df, columns, threshold=3):
    """Detect outliers using Z-score method"""
    outlier_indices = set()
    outlier_details = {}
    
    for col in columns:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            z_scores = np.abs(stats.zscore(df[col].dropna()))
            col_outliers = df[col].dropna().index[z_scores > threshold]
            outlier_indices.update(col_outliers)
            
            outlier_details[col] = {
                'method': 'Z-Score',
                'threshold': threshold,
                'outlier_count': len(col_outliers),
                'outlier_percentage': len(col_outliers) / len(df) * 100,
                'max_zscore': float(np.max(z_scores)) if len(z_scores) > 0 else 0
            }
    
    return list(outlier_indices), outlier_details


def detect_outliers_modified_zscore(df, columns, threshold=3.5):
    """Detect outliers using Modified Z-score method (using median)"""
    outlier_indices = set()
    outlier_details = {}
    
    for col in columns:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            median = df[col].median()
            mad = np.median(np.abs(df[col] - median))
            
            if mad == 0:
                modified_z_scores = np.zeros(len(df[col]))
            else:
                modified_z_scores = 0.6745 * (df[col] - median) / mad
            
            col_outliers = df[np.abs(modified_z_scores) > threshold].index
            outlier_indices.update(col_outliers)
            
            outlier_details[col] = {
                'method': 'Modified Z-Score',
                'threshold': threshold,
                'outlier_count': len(col_outliers),
                'outlier_percentage': len(col_outliers) / len(df) * 100,
                'median': float(median),
                'mad': float(mad)
            }
    
    return list(outlier_indices), outlier_details


def detect_outliers_isolation_forest(df, columns, contamination=0.1):
    """Detect outliers using Isolation Forest method"""
    # Filter numeric columns
    numeric_cols = [col for col in columns if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]
    
    if not numeric_cols:
        return [], {}
    
    # Prepare data for Isolation Forest
    data_for_isolation = df[numeric_cols].dropna()
    
    if len(data_for_isolation) == 0:
        return [], {}
    
    # Apply Isolation Forest
    isolation_forest = IsolationForest(contamination=contamination, random_state=42)
    outlier_labels = isolation_forest.fit_predict(data_for_isolation)
    
    # Get outlier indices
    outlier_indices = data_for_isolation.index[outlier_labels == -1].tolist()
    
    outlier_details = {
        'isolation_forest': {
            'method': 'Isolation Forest',
            'contamination': contamination,
            'columns_used': numeric_cols,
            'outlier_count': len(outlier_indices),
            'outlier_percentage': len(outlier_indices) / len(df) * 100
        }
    }
    
    return outlier_indices, outlier_details


def cap_outliers(df, columns, method='iqr', threshold=1.5):
    """Cap outliers instead of removing them"""
    df_capped = df.copy()
    capping_details = {}
    
    for col in columns:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            if method == 'iqr':
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                # Cap the values
                df_capped[col] = df_capped[col].clip(lower=lower_bound, upper=upper_bound)
                
                capping_details[col] = {
                    'method': method,
                    'lower_bound': float(lower_bound),
                    'upper_bound': float(upper_bound),
                    'values_capped': int(((df[col] < lower_bound) | (df[col] > upper_bound)).sum())
                }
    
    return df_capped, capping_details


def remove_outliers(df, method='iqr', threshold=None, columns=None, action='remove'):
    """Remove or cap outliers from DataFrame using specified method"""
    initial_shape = df.shape
    
    # Get numeric columns if not specified
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Set default thresholds
    if threshold is None:
        if method == 'iqr':
            threshold = 1.5
        elif method == 'zscore':
            threshold = 3
        elif method == 'modified_zscore':
            threshold = 3.5
        elif method == 'isolation_forest':
            threshold = 0.1  # contamination parameter
    
    # Detect outliers
    if method == 'iqr':
        outlier_indices, outlier_details = detect_outliers_iqr(df, columns, threshold)
    elif method == 'zscore':
        outlier_indices, outlier_details = detect_outliers_zscore(df, columns, threshold)
    elif method == 'modified_zscore':
        outlier_indices, outlier_details = detect_outliers_modified_zscore(df, columns, threshold)
    elif method == 'isolation_forest':
        outlier_indices, outlier_details = detect_outliers_isolation_forest(df, columns, threshold)
    else:
        raise ValueError(f"Unknown outlier detection method: {method}")
    
    # Apply action
    if action == 'remove':
        df_cleaned = df.drop(index=outlier_indices)
        action_details = {'action': 'remove', 'outliers_removed': len(outlier_indices)}
    elif action == 'cap':
        df_cleaned, capping_details = cap_outliers(df, columns, method, threshold)
        action_details = {'action': 'cap', 'capping_details': capping_details}
        outlier_indices = []  # No rows removed when capping
    else:
        raise ValueError(f"Unknown action: {action}")
    
    final_shape = df_cleaned.shape
    
    stats = {
        'initial_rows': initial_shape[0],
        'initial_columns': initial_shape[1],
        'final_rows': final_shape[0],
        'final_columns': final_shape[1],
        'outliers_detected': len(outlier_indices),
        'rows_removed': initial_shape[0] - final_shape[0],
        'outlier_percentage': len(outlier_indices) / initial_shape[0] * 100 if initial_shape[0] > 0 else 0,
        'method': method,
        'threshold': threshold,
        'columns_processed': len(columns),
        'outlier_details': outlier_details,
        'action_details': action_details
    }
    
    return df_cleaned, stats


def create_plotly_data(stats):
    """Create Plotly-compatible visualization data"""
    # Overview comparison
    plotly_data = {
        'comparison_chart': {
            'data': [{
                'x': ['Original Rows', 'Final Rows', 'Outliers Detected'],
                'y': [stats['initial_rows'], stats['final_rows'], stats['outliers_detected']],
                'type': 'bar',
                'marker': {
                    'color': ['#3498db', '#2ecc71', '#e74c3c']
                },
                'text': [f"{stats['initial_rows']:,}", f"{stats['final_rows']:,}", f"{stats['outliers_detected']:,}"],
                'textposition': 'outside'
            }],
            'layout': {
                'title': 'Outlier Detection Results',
                'yaxis': {'title': 'Count'},
                'showlegend': False
            }
        },
        'pie_chart': {
            'data': [{
                'values': [stats['final_rows'], stats['outliers_detected']] if stats['outliers_detected'] > 0 else [stats['initial_rows']],
                'labels': ['Clean Data', 'Outliers Detected'] if stats['outliers_detected'] > 0 else ['All Clean'],
                'type': 'pie',
                'marker': {
                    'colors': ['#2ecc71', '#e74c3c'] if stats['outliers_detected'] > 0 else ['#2ecc71']
                },
                'hole': 0.3
            }],
            'layout': {
                'title': 'Data Composition After Outlier Detection'
            }
        },
        'summary': {
            'transformation': 'remove_outliers',
            'metrics': stats
        }
    }
    
    # Add column-wise outlier details if available
    if 'outlier_details' in stats and stats['outlier_details']:
        col_names = []
        outlier_counts = []
        
        for col, details in stats['outlier_details'].items():
            if col != 'isolation_forest':  # Skip isolation forest summary
                col_names.append(col)
                outlier_counts.append(details.get('outlier_count', 0))
        
        if col_names:
            plotly_data['outliers_by_column'] = {
                'data': [{
                    'x': col_names,
                    'y': outlier_counts,
                    'type': 'bar',
                    'marker': {'color': '#e74c3c'},
                    'name': 'Outlier Count'
                }],
                'layout': {
                    'title': 'Outliers by Column',
                    'xaxis': {'tickangle': -45},
                    'yaxis': {'title': 'Outlier Count'}
                }
            }
    
    return plotly_data


def main():
    """Main execution function"""
    print("🚀 Starting Smart Remove Outliers Transformation Node")
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
        
        output_path = os.getenv('OUTPUT_PATH', './pipeline_output/outliers_removed')
        
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
    method = os.getenv('OUTLIER_METHOD', 'iqr')
    threshold = os.getenv('OUTLIER_THRESHOLD')
    if threshold:
        threshold = float(threshold)
    outlier_columns = os.getenv('OUTLIER_COLUMNS', '')
    action = os.getenv('OUTLIER_ACTION', 'remove')
    
    # Parse columns
    columns = [col.strip() for col in outlier_columns.split(',') if col.strip()] if outlier_columns else None
    
    print(f"\n🎛️  Transformation Parameters:")
    print(f"  - Method: {method}")
    print(f"  - Threshold: {threshold if threshold else 'Default'}")
    print(f"  - Action: {action}")
    print(f"  - Columns: {columns if columns else 'All numeric columns'}")
    
    try:
        # Load data
        if test_mode == 'local':
            df = load_data('local', input_path=input_path)
        else:
            df = load_data('s3', s3_client=s3_client, bucket=input_bucket, key=input_key)
        
        print(f"\n✅ Successfully loaded data! Shape: {df.shape}")
        
        # Remove outliers
        print(f"\n🔍 Detecting outliers using '{method}' method...")
        df_cleaned, stats = remove_outliers(df, method=method, threshold=threshold, columns=columns, action=action)
        
        # Print results
        print(f"\n📊 Results:")
        print(f"  - Original rows: {stats['initial_rows']:,}")
        print(f"  - Final rows: {stats['final_rows']:,}")
        print(f"  - Outliers detected: {stats['outliers_detected']:,}")
        print(f"  - Rows removed: {stats['rows_removed']:,}")
        print(f"  - Outlier rate: {stats['outlier_percentage']:.2f}%")
        
        # Create Plotly visualization data
        print(f"\n📈 Creating Plotly visualization data...")
        plotly_data = create_plotly_data(stats)
        
        # Add metadata
        stats['timestamp'] = datetime.now().isoformat()
        stats['transformation'] = 'remove_outliers'
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
        
        print(f"\n✅ Smart Remove Outliers Node completed successfully!")
        print(f"📊 Processed {source_type} data → outliers_removed data")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Smart Remove Outliers Node failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())