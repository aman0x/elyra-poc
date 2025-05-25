#!/usr/bin/env python
"""
Local Data Loader Node for JupyterLab Testing
=============================================
This node loads data from local filesystem for testing in JupyterLab only.
DO NOT include this in Airflow DAG - it won't work in containerized environment.

Parameters (via environment variables):
- INPUT_FILE: Path to local CSV/Excel/Pickle file (default: 'sxmlready_encoded_all.csv')
- OUTPUT_PATH: Local directory to save outputs (default: './pipeline_output')
- TEST_MODE: Set to 'local' to enable local file operations

Output:
- Saves data as pickle file locally
- Saves metadata JSON locally
- Creates a test_config.json for downstream nodes
"""

import os
import sys
import pandas as pd
import pickle
import json
from datetime import datetime


def load_local_data(file_path):
    """Load data from local file"""
    print(f"📥 Loading data from local file: {file_path}")
    
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.pkl'):
            df = pd.read_pickle(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
        
        print(f"✅ Successfully loaded data!")
        return df
        
    except Exception as e:
        print(f"❌ Error loading data: {str(e)}")
        raise


def save_data_locally(df, output_path):
    """Save DataFrame to local file system"""
    try:
        # Create output directory
        os.makedirs(output_path, exist_ok=True)
        
        # Save pickle
        pickle_path = os.path.join(output_path, 'raw_data.pkl')
        with open(pickle_path, 'wb') as f:
            pickle.dump(df, f)
        print(f"💾 Data saved to: {pickle_path}")
        
        # Save metadata
        metadata = {
            'output_file': pickle_path,
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'timestamp': datetime.now().isoformat(),
            'test_mode': 'local'
        }
        
        metadata_path = os.path.join(output_path, 'raw_data_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"📝 Metadata saved to: {metadata_path}")
        
        # Create config for downstream nodes
        config = {
            'test_mode': 'local',
            'data_path': pickle_path,
            'metadata_path': metadata_path,
            'output_base': output_path
        }
        
        config_path = os.path.join(output_path, 'test_config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"🔧 Test config saved to: {config_path}")
        
        return pickle_path, metadata_path
        
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
    print("🚀 Starting Local Data Loader Node (TEST MODE)")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("⚠️  This node is for JupyterLab testing only!")
    
    # Get parameters from environment variables
    input_file = os.getenv('INPUT_FILE', 'sxmlready_encoded_all.csv')
    output_path = os.getenv('OUTPUT_PATH', './pipeline_output')
    test_mode = os.getenv('TEST_MODE', 'local')
    
    if test_mode != 'local':
        print("❌ This node only works in local test mode!")
        print("   Set TEST_MODE=local to use this node")
        return 1
    
    print(f"\n📌 Configuration:")
    print(f"  - Input File: {input_file}")
    print(f"  - Output Path: {output_path}")
    print(f"  - Test Mode: {test_mode}")
    
    # Check if file exists
    if not os.path.exists(input_file):
        print(f"\n❌ Input file not found: {input_file}")
        print("\nAvailable files in current directory:")
        for file in os.listdir('.'):
            if file.endswith(('.csv', '.xlsx', '.pkl')):
                print(f"  - {file}")
        return 1
    
    try:
        # Load data
        df = load_local_data(input_file)
        
        # Print summary
        print_data_summary(df)
        
        # Save data locally
        data_path, metadata_path = save_data_locally(df, output_path)
        
        print(f"\n✅ Local Data Loader Node completed successfully!")
        print(f"\n🎯 Next Steps:")
        print(f"1. Set TEST_MODE=local in all downstream nodes")
        print(f"2. Set INPUT_PATH={data_path} in the next node")
        print(f"3. Set OUTPUT_PATH={output_path}/[transformation_name] in each node")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Local Data Loader Node failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())