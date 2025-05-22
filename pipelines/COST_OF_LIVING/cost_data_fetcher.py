#!/usr/bin/env python3
# cost_data_fetcher.py

import pandas as pd
import requests
import json
import os
from datetime import datetime

def upload_to_minio(local_file_path, bucket_name, object_name):
    """Upload file to MinIO"""
    from minio import Minio
    import os
    
    print(f"Uploading {local_file_path} to MinIO bucket {bucket_name}, object {object_name}")
    
    # MinIO connection details from environment variables
    minio_endpoint = os.environ.get('MINIO_ENDPOINT', 'minio.minio-system.svc.cluster.local:9000')
    minio_access_key = os.environ.get('AWS_ACCESS_KEY_ID', 'minio')
    minio_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY', 'minio123')
    use_ssl = False  # Change to True if MinIO is configured with SSL
    
    # Create client
    client = Minio(
        minio_endpoint,
        access_key=minio_access_key,
        secret_key=minio_secret_key,
        secure=use_ssl
    )
    
    # Ensure bucket exists
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
    
    # Upload file
    client.fput_object(bucket_name, object_name, local_file_path)
    print(f"Successfully uploaded {local_file_path} to MinIO")
    return True

def fetch_numbeo_dataset():
    """
    Fetch cost of living dataset from Kaggle/GitHub public dataset
    We'll use a publicly available dataset about cost of living
    """
    print("Fetching cost of living dataset...")
    
    # URL for the dataset (GitHub hosted CSV of Numbeo data)
    url = "https://raw.githubusercontent.com/datasets/worldwide-cost-of-living/main/data/worldwide-cost-of-living.csv"
    
    try:
        # If the above URL doesn't work, we'll use this alternative dataset
        # This is a backup in case the primary dataset is unavailable
        alt_url = "https://raw.githubusercontent.com/Ovi/DummyJSON/master/src/data/cities.json"
        
        try:
            # Try primary dataset first
            df = pd.read_csv(url)
            print(f"Successfully loaded dataset with {len(df)} records")
            
        except Exception as e:
            print(f"Error loading primary dataset: {e}")
            print("Using backup dataset...")
            
            # Fetch the JSON data from alternative source
            response = requests.get(alt_url)
            data = response.json()
            
            # Convert to DataFrame
            df = pd.json_normalize(data['cities'])
            df['timestamp'] = datetime.now().strftime("%Y-%m-%d")
            
            print(f"Successfully loaded alternative dataset with {len(df)} records")
    
    except Exception as e:
        print(f"Error loading datasets: {e}")
        
        # Generate sample data if both sources fail
        print("Generating sample data...")
        cities = ['New York', 'London', 'Tokyo', 'Paris', 'Singapore', 'Hong Kong', 
                  'Zurich', 'Shanghai', 'Sydney', 'Dubai']
        
        cost_index = [100, 95, 83, 87, 91, 93, 106, 66, 80, 72]
        rent_index = [100, 78, 51, 53, 73, 86, 68, 49, 62, 63]
        groceries_index = [100, 69, 94, 84, 81, 85, 126, 63, 84, 62]
        restaurant_index = [100, 89, 61, 89, 80, 77, 123, 52, 77, 75]
        
        # Create DataFrame
        df = pd.DataFrame({
            'city': cities,
            'cost_index': cost_index,
            'rent_index': rent_index, 
            'groceries_index': groceries_index,
            'restaurant_index': restaurant_index,
            'timestamp': datetime.now().strftime("%Y-%m-%d")
        })
        
        print(f"Generated sample dataset with {len(df)} cities")
    
    # Create output directory
    os.makedirs('data', exist_ok=True)
    
    # Save to CSV
    csv_path = 'data/cost_of_living.csv'
    df.to_csv(csv_path, index=False)
    
    # Also save as JSON for easy reading
    json_path = 'data/cost_of_living.json'
    with open(json_path, 'w') as f:
        f.write(df.to_json(orient='records'))
    
    print(f"Data processing complete. Files saved to {csv_path} and {json_path}")
    
    # Upload files to MinIO
    pipeline_name = os.environ.get('ELYRA_RUN_NAME', 'cost-of-living-pipeline')
    bucket_name = 'elyra-airflow'
    
    # Upload both CSV and JSON files
    csv_object_name = f"{pipeline_name}/data/cost_of_living.csv"
    json_object_name = f"{pipeline_name}/data/cost_of_living.json"
    
    # Try to install minio if not available
    try:
        import minio
    except ImportError:
        print("Installing minio package...")
        import subprocess
        subprocess.check_call(["pip", "install", "minio"])
    
    upload_to_minio(csv_path, bucket_name, csv_object_name)
    upload_to_minio(json_path, bucket_name, json_object_name)
    
    return {
        'csv_path': csv_path,
        'json_path': json_path,
        'minio_bucket': bucket_name,
        'minio_csv_object': csv_object_name,
        'minio_json_object': json_object_name,
        'row_count': len(df),
        'columns': list(df.columns)
    }

if __name__ == "__main__":
    results = fetch_numbeo_dataset()
    print(f"Results: {json.dumps(results)}")