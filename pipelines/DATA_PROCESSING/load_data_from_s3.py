#!/usr/bin/env python
"""
S3 Data Loader Node - CSV to Pickle Converter for Pipeline
========================================================
This node loads CSV data from S3 and converts it to pickle format for downstream transformations.

Parameters (via environment variables):
- MINIO_ENDPOINT: MinIO endpoint URL (default: http://minio.minio-system.svc.cluster.local:9000)
- MINIO_ACCESS_KEY: Access key (default: minio)
- MINIO_SECRET_KEY: Secret key (default: minio123)
- INPUT_BUCKET: S3 bucket containing CSV data (default: customer-bucket)
- INPUT_CSV: CSV file name to load (default: sxmlready_encoded_all.csv)
- OUTPUT_BUCKET: S3 bucket for output (defaults to INPUT_BUCKET)
- OUTPUT_PREFIX: S3 prefix for output files (default: pipeline-data)
- OUTPUT_FILENAME: Output pickle filename (default: input_data.pkl)

Output:
- Saves data as pickle file in S3
- Saves metadata JSON in S3
- Ready for downstream transformation nodes
"""

import os
import sys
import subprocess

# Install required packages FIRST
print("Installing required packages...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "boto3", "pandas"])

# NOW import after installation
import pandas as pd
import boto3
from botocore.client import Config
import io
import pickle
import json
from datetime import datetime

def create_s3_client():
    """Create S3 client for MinIO"""
    endpoint = os.getenv('MINIO_ENDPOINT', 'http://minio.minio-system.svc.cluster.local:9000')
    access_key = os.getenv('MINIO_ACCESS_KEY', 'minio')
    secret_key = os.getenv('MINIO_SECRET_KEY', 'minio123')
    
    print(f"🔗 Connecting to: {endpoint}")
    print(f"🔑 Using access key: {access_key}")
    
    return boto3.client(
        's3',
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )

def load_csv_from_s3(s3_client, bucket, csv_key):
    """Load CSV data from S3"""
    print(f"📥 Loading CSV from s3://{bucket}/{csv_key}")
    
    try:
        # Get the CSV file from S3
        csv_obj = s3_client.get_object(Bucket=bucket, Key=csv_key)
        
        # Read CSV into DataFrame
        df = pd.read_csv(io.StringIO(csv_obj['Body'].read().decode('utf-8')))
        
        print(f"✅ Successfully loaded CSV! Shape: {df.shape}")
        return df
        
    except Exception as e:
        print(f"❌ Error loading CSV: {str(e)}")
        raise

def save_data_to_s3(s3_client, df, bucket, output_prefix, output_filename):
    """Save DataFrame as pickle to S3"""
    try:
        # Define S3 paths
        pickle_key = f"{output_prefix}/{output_filename}"
        metadata_key = f"{output_prefix}/data_metadata.json"
        
        # Save DataFrame as pickle
        pickle_buffer = io.BytesIO()
        pickle.dump(df, pickle_buffer)
        pickle_buffer.seek(0)
        
        s3_client.put_object(
            Bucket=bucket,
            Key=pickle_key,
            Body=pickle_buffer.getvalue()
        )
        print(f"💾 Data saved to: s3://{bucket}/{pickle_key}")
        
        # Save metadata
        metadata = {
            'output_file': f"s3://{bucket}/{pickle_key}",
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'timestamp': datetime.now().isoformat(),
            'source': 'S3 CSV Loader',
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2
        }
        
        s3_client.put_object(
            Bucket=bucket,
            Key=metadata_key,
            Body=json.dumps(metadata, indent=2)
        )
        print(f"📝 Metadata saved to: s3://{bucket}/{metadata_key}")
        
        return pickle_key, metadata_key
        
    except Exception as e:
        print(f"❌ Error saving data: {str(e)}")
        raise

def print_data_summary(df):
    """Print summary of loaded data"""
    print("\n" + "="*50)
    print("📊 DATA SUMMARY")
    print("="*50)
    print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    print("\n📋 Column Information:")
    dtype_counts = df.dtypes.value_counts()
    for dtype, count in dtype_counts.items():
        print(f"  - {dtype}: {count} columns")
    
    print("\n❓ Missing Values:")
    missing = df.isnull().sum()
    if missing.sum() > 0:
        missing_pct = (missing / len(df) * 100).round(2)
        missing_summary = pd.DataFrame({
            'Missing': missing[missing > 0],
            'Percentage': missing_pct[missing > 0]
        })
        print("Top columns with missing values:")
        print(missing_summary.head(10))
        print(f"Total missing values: {missing.sum():,}")
    else:
        print("No missing values found!")
    
    print("\n🔍 First 5 rows:")
    print(df.head())
    
    print("\n📈 Numeric columns summary:")
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        print(f"Found {len(numeric_cols)} numeric columns")
        print(df[numeric_cols].describe())
    else:
        print("No numeric columns found")
    
    print("\n🏷️  Categorical columns:")
    cat_cols = df.select_dtypes(include=['object']).columns
    if len(cat_cols) > 0:
        print(f"Found {len(cat_cols)} categorical columns:")
        for col in cat_cols[:5]:  # Show first 5
            unique_count = df[col].nunique()
            print(f"  - {col}: {unique_count} unique values")
        if len(cat_cols) > 5:
            print(f"  ... and {len(cat_cols) - 5} more")
    
    print("\n" + "="*50)

def list_available_csvs(s3_client, bucket):
    """List available CSV files in the bucket"""
    try:
        objects = s3_client.list_objects_v2(Bucket=bucket)
        csv_files = []
        
        if 'Contents' in objects:
            for obj in objects['Contents']:
                if obj['Key'].endswith('.csv'):
                    size_mb = obj['Size'] / (1024*1024)
                    csv_files.append({
                        'key': obj['Key'],
                        'size_mb': size_mb,
                        'modified': obj['LastModified']
                    })
        
        return csv_files
    except Exception as e:
        print(f"❌ Error listing files: {str(e)}")
        return []

def main():
    """Main execution function"""
    print("🚀 Starting S3 Data Loader Node - CSV to Pickle Converter")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get parameters from environment variables
    input_bucket = os.getenv('INPUT_BUCKET', 'customer-bucket')
    input_csv = os.getenv('INPUT_CSV', 'sxmlready_encoded_all.csv')
    output_bucket = os.getenv('OUTPUT_BUCKET', input_bucket)
    output_prefix = os.getenv('OUTPUT_PREFIX', 'pipeline-data')
    output_filename = os.getenv('OUTPUT_FILENAME', 'input_data.pkl')
    
    print(f"\n📌 Configuration:")
    print(f"  - Input Bucket: {input_bucket}")
    print(f"  - Input CSV: {input_csv}")
    print(f"  - Output Bucket: {output_bucket}")
    print(f"  - Output Path: s3://{output_bucket}/{output_prefix}/{output_filename}")
    
    try:
        # Create S3 client
        s3_client = create_s3_client()
        
        # Check if specific CSV exists, if not show available options
        try:
            s3_client.head_object(Bucket=input_bucket, Key=input_csv)
            print(f"✅ Found target CSV: {input_csv}")
        except:
            print(f"❌ CSV file '{input_csv}' not found in bucket '{input_bucket}'")
            print("\n📋 Available CSV files:")
            csv_files = list_available_csvs(s3_client, input_bucket)
            
            if csv_files:
                for csv_file in csv_files:
                    print(f"  - {csv_file['key']} ({csv_file['size_mb']:.2f} MB)")
                print(f"\n💡 To use a different CSV, set INPUT_CSV environment variable")
                print(f"   Example: INPUT_CSV={csv_files[0]['key']}")
            else:
                print("  No CSV files found in the bucket")
            
            return 1
        
        # Load CSV data
        df = load_csv_from_s3(s3_client, input_bucket, input_csv)
        
        # Print data summary
        print_data_summary(df)
        
        # Save data as pickle to S3
        print(f"\n💾 Converting and saving data...")
        pickle_key, metadata_key = save_data_to_s3(
            s3_client, df, output_bucket, output_prefix, output_filename
        )
        
        print(f"\n✅ S3 Data Loader completed successfully!")
        print(f"\n🎯 Data ready for pipeline:")
        print(f"  📁 Pickle file: s3://{output_bucket}/{pickle_key}")
        print(f"  📄 Metadata: s3://{output_bucket}/{metadata_key}")
        print(f"\n🔄 Your downstream transformation nodes can now use:")
        print(f"  INPUT_BUCKET={output_bucket}")
        print(f"  INPUT_KEY={pickle_key}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ S3 Data Loader failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())