#!/usr/bin/env python
"""
Remove Duplicates Transformation Node for Elyra Pipeline
========================================================
This node removes duplicate rows from the dataset.

Parameters (via environment variables):
- MINIO_ENDPOINT: MinIO endpoint URL
- MINIO_ACCESS_KEY: Access key
- MINIO_SECRET_KEY: Secret key
- INPUT_BUCKET: S3 bucket containing input data
- INPUT_KEY: S3 key to the input pickle file
- OUTPUT_PREFIX: S3 prefix for output files
- OUTPUT_BUCKET: S3 bucket for output (defaults to INPUT_BUCKET)
- DUPLICATE_SUBSET: Comma-separated column names to check for duplicates (optional)
- KEEP_FIRST: Whether to keep first or last duplicate (default: 'first')

Output:
- Saves deduplicated data as pickle file to S3
- Saves transformation report as JSON to S3
- Generates comparison visualization
"""

import os
import sys
import subprocess

# Install required packages
print("Installing required packages...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "boto3", "pandas", "matplotlib", "seaborn"])

import pandas as pd
import boto3
from botocore.client import Config
import io
import pickle
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import base64


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


def load_data_from_s3(s3_client, bucket_name, pickle_key):
    """Load pickle data from S3/MinIO"""
    print(f"📥 Loading data from s3://{bucket_name}/{pickle_key}")
    
    try:
        # Get object from S3
        obj = s3_client.get_object(Bucket=bucket_name, Key=pickle_key)
        
        # Load pickle from object
        df = pickle.loads(obj['Body'].read())
        
        print(f"✅ Successfully loaded data!")
        print(f"   Shape: {df.shape}")
        return df
        
    except Exception as e:
        print(f"❌ Error loading data: {str(e)}")
        raise


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


def create_visualization(stats):
    """Create before/after visualization"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Bar chart of row counts
    labels = ['Original', 'After Deduplication']
    row_counts = [stats['initial_rows'], stats['final_rows']]
    colors = ['#3498db', '#2ecc71']
    
    bars = ax1.bar(labels, row_counts, color=colors)
    ax1.set_ylabel('Number of Rows')
    ax1.set_title('Dataset Size Comparison')
    
    # Add value labels on bars
    for bar, count in zip(bars, row_counts):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(count):,}', ha='center', va='bottom')
    
    # Add removed count annotation
    if stats['removed_rows'] > 0:
        ax1.annotate(f"-{stats['removed_rows']:,} rows\n({stats['removal_percentage']:.1f}%)",
                    xy=(0.5, (row_counts[0] + row_counts[1]) / 2),
                    xytext=(1.2, (row_counts[0] + row_counts[1]) / 2),
                    arrowprops=dict(arrowstyle='->', color='red', lw=2),
                    fontsize=12, color='red', weight='bold')
    
    # Pie chart of data composition
    if stats['removed_rows'] > 0:
        sizes = [stats['final_rows'], stats['removed_rows']]
        labels_pie = ['Unique Rows', 'Duplicates Removed']
        colors_pie = ['#2ecc71', '#e74c3c']
        explode = (0.05, 0.1)
        
        ax2.pie(sizes, explode=explode, labels=labels_pie, colors=colors_pie,
                autopct='%1.1f%%', shadow=True, startangle=90)
        ax2.set_title('Data Composition')
    else:
        ax2.text(0.5, 0.5, 'No Duplicates Found!', 
                ha='center', va='center', fontsize=20, 
                color='green', weight='bold', transform=ax2.transAxes)
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)
        ax2.axis('off')
    
    plt.suptitle('Duplicate Removal Results', fontsize=16, weight='bold')
    plt.tight_layout()
    
    # Save to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return buf.getvalue()


def save_results_to_s3(s3_client, df, stats, viz_data, bucket_name, output_prefix):
    """Save transformed data and results to S3"""
    try:
        # Define S3 paths
        pickle_key = f"{output_prefix}/deduplicated_data.pkl"
        stats_key = f"{output_prefix}/deduplication_stats.json"
        viz_key = f"{output_prefix}/deduplication_visualization.png"
        
        # Save DataFrame as pickle
        pickle_buffer = io.BytesIO()
        pickle.dump(df, pickle_buffer)
        pickle_buffer.seek(0)
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=pickle_key,
            Body=pickle_buffer.getvalue()
        )
        print(f"💾 Data saved to: s3://{bucket_name}/{pickle_key}")
        
        # Save statistics
        stats['timestamp'] = datetime.now().isoformat()
        stats['transformation'] = 'remove_duplicates'
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=stats_key,
            Body=json.dumps(stats, indent=2)
        )
        print(f"📊 Stats saved to: s3://{bucket_name}/{stats_key}")
        
        # Save visualization
        s3_client.put_object(
            Bucket=bucket_name,
            Key=viz_key,
            Body=viz_data,
            ContentType='image/png'
        )
        print(f"📈 Visualization saved to: s3://{bucket_name}/{viz_key}")
        
        return pickle_key, stats_key, viz_key
        
    except Exception as e:
        print(f"❌ Error saving results: {str(e)}")
        raise


def main():
    """Main execution function"""
    print("🚀 Starting Remove Duplicates Transformation Node")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get parameters from environment variables
    endpoint = os.getenv('MINIO_ENDPOINT', 'http://localhost:9000')
    access_key = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
    secret_key = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
    input_bucket = os.getenv('INPUT_BUCKET', 'pipeline-data')
    input_key = os.getenv('INPUT_KEY', 'pipeline-data/raw_data.pkl')
    output_prefix = os.getenv('OUTPUT_PREFIX', 'pipeline-data')
    output_bucket = os.getenv('OUTPUT_BUCKET', input_bucket)
    
    # Deduplication parameters
    duplicate_subset = os.getenv('DUPLICATE_SUBSET', '')
    keep_first = os.getenv('KEEP_FIRST', 'first')
    
    # Parse subset columns
    subset_cols = [col.strip() for col in duplicate_subset.split(',') if col.strip()] if duplicate_subset else None
    
    print(f"\n📌 Configuration:")
    print(f"  - Endpoint: {endpoint}")
    print(f"  - Input: s3://{input_bucket}/{input_key}")
    print(f"  - Output Prefix: {output_prefix}")
    print(f"  - Output Bucket: {output_bucket}")
    print(f"  - Check Columns: {subset_cols if subset_cols else 'All columns'}")
    print(f"  - Keep: {keep_first}")
    
    try:
        # Create S3 client
        s3_client = create_s3_client(endpoint, access_key, secret_key)
        
        # Load data from S3
        df = load_data_from_s3(s3_client, input_bucket, input_key)
        
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
        
        # Create visualization
        print(f"\n📈 Creating visualization...")
        viz_data = create_visualization(stats)
        
        # Save results to S3
        print(f"\n💾 Saving results...")
        data_key, stats_key, viz_key = save_results_to_s3(
            s3_client, df_cleaned, stats, viz_data, output_bucket, output_prefix
        )
        
        print(f"\n✅ Remove Duplicates Node completed successfully!")
        print(f"   - Cleaned data: s3://{output_bucket}/{data_key}")
        print(f"   - Statistics: s3://{output_bucket}/{stats_key}")
        print(f"   - Visualization: s3://{output_bucket}/{viz_key}")
        
        # Save output info for next node
        output_info = {
            'data_location': f"s3://{output_bucket}/{data_key}",
            'stats_location': f"s3://{output_bucket}/{stats_key}",
            'viz_location': f"s3://{output_bucket}/{viz_key}",
            'bucket': output_bucket,
            'data_key': data_key,
            'transformation': 'remove_duplicates',
            'rows_removed': stats['removed_rows']
        }
        
        with open('output_info.json', 'w') as f:
            json.dump(output_info, f)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Remove Duplicates Node failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())