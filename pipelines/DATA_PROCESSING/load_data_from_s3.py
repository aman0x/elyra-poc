#!/usr/bin/env python
"""
Data Loader Node for Elyra Pipeline
===================================
This node loads data from S3/MinIO and saves it back to S3 for downstream processing.

Parameters (via environment variables):
- MINIO_ENDPOINT: MinIO endpoint URL
- MINIO_ACCESS_KEY: Access key
- MINIO_SECRET_KEY: Secret key
- INPUT_BUCKET: S3 bucket name for input
- INPUT_KEY: S3 object key (path to file)
- OUTPUT_PREFIX: S3 prefix for output files
- OUTPUT_BUCKET: S3 bucket for output (defaults to INPUT_BUCKET)

Output:
- Saves data as pickle file to S3
- Saves metadata JSON to S3
- Creates local output_info.json with S3 locations
"""

import os
import sys
import subprocess

# Install required packages
print("Installing required packages...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "boto3", "pandas"])

import pandas as pd
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


def load_data_from_s3(s3_client, bucket_name, file_key):
    """Load CSV data from S3/MinIO"""
    print(f"📥 Loading data from s3://{bucket_name}/{file_key}")
    
    try:
        # Get object from S3
        obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        
        # Read CSV from object
        df = pd.read_csv(io.StringIO(obj['Body'].read().decode('utf-8')))
        
        print(f"✅ Successfully loaded data!")
        return df
        
    except Exception as e:
        print(f"❌ Error loading data: {str(e)}")
        raise


def save_data_to_minio(df, s3_client, bucket_name, output_prefix):
    """Save DataFrame to MinIO/S3 as pickle and metadata"""
    try:
        # Define S3 paths
        pickle_key = f"{output_prefix}/raw_data.pkl"
        metadata_key = f"{output_prefix}/raw_data_metadata.json"
        
        # Save DataFrame as pickle to S3
        pickle_buffer = io.BytesIO()
        pickle.dump(df, pickle_buffer)
        pickle_buffer.seek(0)
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=pickle_key,
            Body=pickle_buffer.getvalue()
        )
        print(f"💾 Data saved to: s3://{bucket_name}/{pickle_key}")
        
        # Create and save metadata
        metadata = {
            'output_file': f"s3://{bucket_name}/{pickle_key}",
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'timestamp': datetime.now().isoformat(),
            'bucket': bucket_name,
            'pickle_key': pickle_key
        }
        
        metadata_json = json.dumps(metadata, indent=2)
        s3_client.put_object(
            Bucket=bucket_name,
            Key=metadata_key,
            Body=metadata_json
        )
        print(f"📝 Metadata saved to: s3://{bucket_name}/{metadata_key}")
        
        return pickle_key, metadata_key
        
    except Exception as e:
        print(f"❌ Error saving data to MinIO: {str(e)}")
        raise


def print_data_summary(df):
    """Print summary of loaded data"""
    print("\n" + "="*50)
    print("📊 DATA SUMMARY")
    print("="*50)
    print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    print("\n📋 Column Information:")
    print(df.dtypes.value_counts())
    
    print("\n❓ Missing Values:")
    missing = df.isnull().sum()
    if missing.sum() > 0:
        missing_pct = (missing / len(df) * 100).round(2)
        missing_summary = pd.DataFrame({
            'Missing': missing[missing > 0],
            'Percentage': missing_pct[missing > 0]
        })
        print(missing_summary)
    else:
        print("No missing values found!")
    
    print("\n🔍 First 5 rows:")
    print(df.head())
    
    print("\n📈 Numeric columns summary:")
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        print(df[numeric_cols].describe())
    else:
        print("No numeric columns found")
    
    print("\n" + "="*50)


def main():
    """Main execution function"""
    print("🚀 Starting Data Loader Node")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get parameters from environment variables
    endpoint = os.getenv('MINIO_ENDPOINT', 'http://localhost:9000')
    access_key = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
    secret_key = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
    bucket_name = os.getenv('INPUT_BUCKET', 'data-bucket')
    file_key = os.getenv('INPUT_KEY', 'raw-data/dataset.csv')
    output_prefix = os.getenv('OUTPUT_PREFIX', 'pipeline-data')
    
    # For Elyra: the output is saved back to the same bucket
    output_bucket = os.getenv('OUTPUT_BUCKET', bucket_name)
    
    print(f"\n📌 Configuration:")
    print(f"  - Endpoint: {endpoint}")
    print(f"  - Bucket: {bucket_name}")
    print(f"  - File: {file_key}")
    print(f"  - Output Prefix: {output_prefix}")
    print(f"  - Output Bucket: {output_bucket}")
    
    try:
        # Create S3 client
        s3_client = create_s3_client(endpoint, access_key, secret_key)
        
        # Load data from S3
        df = load_data_from_s3(s3_client, bucket_name, file_key)
        
        # Print summary
        print_data_summary(df)
        
        # Save data back to MinIO
        pickle_key, metadata_key = save_data_to_minio(df, s3_client, output_bucket, output_prefix)
        
        print(f"\n✅ Data Loader Node completed successfully!")
        print(f"   - Data location: s3://{output_bucket}/{pickle_key}")
        print(f"   - Metadata location: s3://{output_bucket}/{metadata_key}")
        
        # For Elyra: Save output info to a file that can be accessed by the runtime
        output_info = {
            'data_location': f"s3://{output_bucket}/{pickle_key}",
            'metadata_location': f"s3://{output_bucket}/{metadata_key}",
            'bucket': output_bucket,
            'data_key': pickle_key,
            'metadata_key': metadata_key
        }
        
        with open('output_info.json', 'w') as f:
            json.dump(output_info, f)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Data Loader Node failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())