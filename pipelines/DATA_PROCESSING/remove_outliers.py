#!/usr/bin/env python
"""
Remove Outliers Transformation Node with Local Testing Support
============================================================
This node removes outlier values from the dataset using various methods.

Parameters (via environment variables):
- TEST_MODE: Set to 'local' for local file operations, otherwise uses S3
- For S3 mode: Same as original (MINIO_ENDPOINT, etc.)
- For Local mode:
  - INPUT_PATH: Local path to input pickle file
  - OUTPUT_PATH: Local directory for outputs
  - OUTLIER_METHOD: Method to detect outliers - 'iqr', 'zscore', 'isolation_forest', 'modified_zscore' (default: 'iqr')
  - OUTLIER_THRESHOLD: Threshold for outlier detection (default varies by method)
  - OUTLIER_COLUMNS: Comma-separated column names to check (optional - numeric columns if not specified)
  - OUTLIER_ACTION: Action to take - 'remove', 'cap' (default: 'remove')
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
        # Original S3 save logic
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
        outlier_percentages = []
        
        for col, details in stats['outlier_details'].items():
            if col != 'isolation_forest':  # Skip isolation forest summary
                col_names.append(col)
                outlier_counts.append(details.get('outlier_count', 0))
                outlier_percentages.append(details.get('outlier_percentage', 0))
        
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
    print("🚀 Starting Remove Outliers Transformation Node")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check test mode
    test_mode = os.getenv('TEST_MODE', 'local')
    
    if test_mode == 'local':
        print("🧪 Running in LOCAL TEST MODE")
        
        # Local mode parameters - INDEPENDENT INPUT PATH
        input_path = os.getenv('INPUT_PATH', './pipeline_output/raw_data.pkl')
        output_path = os.getenv('OUTPUT_PATH', './pipeline_output/outliers_removed')
        
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
    method = os.getenv('OUTLIER_METHOD', 'iqr')
    threshold = os.getenv('OUTLIER_THRESHOLD')
    if threshold:
        threshold = float(threshold)
    outlier_columns = os.getenv('OUTLIER_COLUMNS', '')
    action = os.getenv('OUTLIER_ACTION', 'remove')
    
    # Parse columns
    columns = [col.strip() for col in outlier_columns.split(',') if col.strip()] if outlier_columns else None
    
    print(f"  - Method: {method}")
    print(f"  - Threshold: {threshold if threshold else 'Default'}")
    print(f"  - Action: {action}")
    print(f"  - Columns: {columns if columns else 'All numeric columns'}")
    
    try:
        # Load data
        if test_mode == 'local':
            df = load_data('local', input_path=input_path)
        else:
            s3_client = create_s3_client(endpoint, access_key, secret_key)
            df = load_data('s3', s3_client=s3_client, bucket=input_bucket, key=input_key)
        
        print(f"✅ Successfully loaded data! Shape: {df.shape}")
        
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
        
        # Save results
        print(f"\n💾 Saving results...")
        if test_mode == 'local':
            save_results('local', df_cleaned, stats, plotly_data, output_path=output_path)
            
            # Update config for next node
            config_path = os.path.join(os.path.dirname(output_path), 'test_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                config['outliers_removed_data_path'] = os.path.join(output_path, 'outliers_removed_data.pkl')
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
            
        else:
            s3_client = create_s3_client(endpoint, access_key, secret_key)
            save_results('s3', df_cleaned, stats, plotly_data, 
                        s3_client=s3_client, bucket=output_bucket, prefix=output_prefix)
        
        print(f"\n✅ Remove Outliers Node completed successfully!")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Remove Outliers Node failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())