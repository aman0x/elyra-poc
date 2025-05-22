#!/usr/bin/env python3
# cost_data_visualizer.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import sys
import numpy as np
from datetime import datetime

# Set style
sns.set_style('whitegrid')

def download_from_minio(bucket_name, object_name, local_file_path):
    """Download file from MinIO"""
    from minio import Minio
    import os
    
    print(f"Downloading from MinIO bucket {bucket_name}, object {object_name} to {local_file_path}")
    
    # Create directories if needed
    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
    
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
    
    # Download file
    client.fget_object(bucket_name, object_name, local_file_path)
    print(f"Successfully downloaded to {local_file_path}")
    return True

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

def load_data(file_path):
    """Load data from CSV file"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    return pd.read_csv(file_path)

def create_html_report(df, output_dir):
    """Create an HTML report with visualizations"""
    # Create HTML file with visualizations
    html_path = f"{output_dir}/cost_of_living_report.html"
    
    # Generate plots and save them
    create_plots(df, output_dir)
    
    # List of generated image files
    image_files = [
        "cost_comparison.png",
        "cost_vs_rent.png", 
        "top_expensive_cities.png",
        "cost_distribution.png"
    ]
    
    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cost of Living Analysis</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; max-width: 1200px; margin: 0 auto; }}
            h1 {{ color: #2c3e50; text-align: center; }}
            .container {{ display: flex; flex-wrap: wrap; justify-content: center; }}
            .chart {{ margin: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-radius: 5px; overflow: hidden; }}
            .chart img {{ max-width: 100%; height: auto; display: block; }}
            .chart h3 {{ padding: 10px; margin: 0; background-color: #f8f9fa; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .timestamp {{ text-align: center; color: #666; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <h1>Cost of Living Analysis</h1>
        
        <div class="container">
    """
    
    # Add images to HTML
    for img_file in image_files:
        img_path = f"{img_file}"
        title = img_file.replace(".png", "").replace("_", " ").title()
        
        html_content += f"""
            <div class="chart">
                <h3>{title}</h3>
                <img src="{img_path}" alt="{title}">
            </div>
        """
    
    # Add table with top 10 most expensive cities
    if 'cost_index' in df.columns:
        top_cities = df.sort_values(by='cost_index', ascending=False).head(10)
    else:
        # If we don't have cost_index (backup dataset), use a different column
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            top_cities = df.sort_values(by=numeric_cols[0], ascending=False).head(10)
        else:
            top_cities = df.head(10)
    
    html_content += """
        </div>
        
        <h2>Top Most Expensive Cities</h2>
        <table>
            <tr>
    """
    
    # Add table headers
    for col in top_cities.columns:
        html_content += f"<th>{col}</th>"
    
    html_content += "</tr>"
    
    # Add table rows
    for _, row in top_cities.iterrows():
        html_content += "<tr>"
        for col in top_cities.columns:
            html_content += f"<td>{row[col]}</td>"
        html_content += "</tr>"
    
    # Finish HTML
    html_content += f"""
        </table>
        
        <p class="timestamp">Report generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </body>
    </html>
    """
    
    # Write HTML to file
    with open(html_path, 'w') as f:
        f.write(html_content)
    
    return html_path

def create_plots(df, output_dir):
    """Create various plots and save them to the output directory"""
    # Check what columns we have available
    if 'cost_index' in df.columns and 'city' in df.columns:
        # Sort data by cost index
        df = df.sort_values(by='cost_index', ascending=False)
        
        # 1. Cost Comparison Bar Chart
        plt.figure(figsize=(12, 8))
        bar_plot = sns.barplot(x='cost_index', y='city', data=df.head(15))
        plt.title('Cost of Living Index by City', fontsize=16)
        plt.xlabel('Cost Index', fontsize=12)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/cost_comparison.png")
        plt.close()
        
        # 2. Cost vs Rent Scatter Plot
        if 'rent_index' in df.columns:
            plt.figure(figsize=(10, 8))
            scatter = sns.scatterplot(x='cost_index', y='rent_index', data=df, s=100)
            
            # Add city labels to some points
            for i, row in df.head(10).iterrows():
                plt.text(row['cost_index']+1, row['rent_index']+1, row['city'], fontsize=9)
                
            plt.title('Cost of Living vs. Rent Index', fontsize=16)
            plt.xlabel('Cost of Living Index', fontsize=12)
            plt.ylabel('Rent Index', fontsize=12)
            plt.tight_layout()
            plt.savefig(f"{output_dir}/cost_vs_rent.png")
            plt.close()
        
        # 3. Top 10 Most Expensive Cities
        plt.figure(figsize=(12, 8))
        top_10 = df.head(10)
        
        if 'groceries_index' in df.columns and 'restaurant_index' in df.columns:
            # Create grouped bar chart
            bar_width = 0.25
            x = np.arange(len(top_10))
            
            plt.bar(x - bar_width, top_10['cost_index'], width=bar_width, label='Cost Index')
            plt.bar(x, top_10['groceries_index'], width=bar_width, label='Groceries Index')
            plt.bar(x + bar_width, top_10['restaurant_index'], width=bar_width, label='Restaurant Index')
            
            plt.xlabel('City', fontsize=12)
            plt.ylabel('Index Value', fontsize=12)
            plt.title('Cost Breakdown for Top 10 Most Expensive Cities', fontsize=16)
            plt.xticks(x, top_10['city'], rotation=45, ha='right')
            plt.legend()
        else:
            # Simpler bar chart if we don't have the detailed indices
            sns.barplot(x='city', y='cost_index', data=top_10)
            plt.xlabel('City', fontsize=12)
            plt.ylabel('Cost Index', fontsize=12)
            plt.title('Top 10 Most Expensive Cities', fontsize=16)
            plt.xticks(rotation=45, ha='right')
            
        plt.tight_layout()
        plt.savefig(f"{output_dir}/top_expensive_cities.png")
        plt.close()
        
        # 4. Cost Distribution Histogram
        plt.figure(figsize=(10, 6))
        sns.histplot(df['cost_index'], kde=True)
        plt.title('Distribution of Cost of Living Index', fontsize=16)
        plt.xlabel('Cost Index', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/cost_distribution.png")
        plt.close()
    else:
        # Fallback visualization if we don't have the expected columns
        # Identify numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 0:
            # Bar chart of first numeric column
            plt.figure(figsize=(12, 8))
            df_sorted = df.sort_values(by=numeric_cols[0], ascending=False).head(15)
            
            # Try to find a label column (non-numeric)
            label_cols = df.select_dtypes(exclude=[np.number]).columns
            if len(label_cols) > 0:
                label_col = label_cols[0]
                sns.barplot(x=numeric_cols[0], y=label_col, data=df_sorted)
                plt.title(f'{numeric_cols[0]} by {label_col}', fontsize=16)
            else:
                # Just plot the values
                sns.barplot(x=df_sorted.index, y=numeric_cols[0], data=df_sorted)
                plt.title(f'Top 15 by {numeric_cols[0]}', fontsize=16)
                
            plt.tight_layout()
            plt.savefig(f"{output_dir}/cost_comparison.png")
            plt.close()
            
            # Create placeholder images for the other plots
            for img_name in ['cost_vs_rent.png', 'top_expensive_cities.png', 'cost_distribution.png']:
                plt.figure(figsize=(10, 6))
                plt.text(0.5, 0.5, f"No data available for {img_name}", 
                         horizontalalignment='center', verticalalignment='center',
                         fontsize=14)
                plt.axis('off')
                plt.savefig(f"{output_dir}/{img_name}")
                plt.close()
        else:
            # Create placeholder images if we have no numeric columns
            for img_name in ['cost_comparison.png', 'cost_vs_rent.png', 
                             'top_expensive_cities.png', 'cost_distribution.png']:
                plt.figure(figsize=(10, 6))
                plt.text(0.5, 0.5, "No numeric data available", 
                         horizontalalignment='center', verticalalignment='center',
                         fontsize=14)
                plt.axis('off')
                plt.savefig(f"{output_dir}/{img_name}")
                plt.close()

def main():
    # Try to install minio if not available
    try:
        import minio
    except ImportError:
        print("Installing minio package...")
        import subprocess
        subprocess.check_call(["pip", "install", "minio"])
    
    # Get pipeline name from environment
    pipeline_name = os.environ.get('ELYRA_RUN_NAME', 'cost-of-living-pipeline')
    bucket_name = 'elyra-airflow'
    
    # Create local directories
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    
    # Local file paths
    csv_path = f"{data_dir}/cost_of_living.csv"
    
    # MinIO object names
    csv_object_name = f"{pipeline_name}/data/cost_of_living.csv"
    
    # Download the CSV file from MinIO
    try:
        download_from_minio(bucket_name, csv_object_name, csv_path)
    except Exception as e:
        print(f"Error downloading from MinIO: {e}")
        return {
            'status': 'error',
            'message': f"Could not download data from MinIO: {e}"
        }
    
    # Now continue with existing code to load and process the data
    try:
        # Load the data
        df = load_data(csv_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return {
            'status': 'error',
            'message': f"Could not find data file: {csv_path}"
        }
    
    # Create output directory if it doesn't exist
    output_dir = 'visualizations'
    os.makedirs(output_dir, exist_ok=True)
    
    print("Creating visualizations and HTML report...")
    
    # Create HTML report with embedded visualizations
    html_path = create_html_report(df, output_dir)
    
    # Upload HTML report and visualizations to MinIO
    try:
        # Upload HTML report
        report_object_name = f"{pipeline_name}/visualizations/cost_of_living_report.html"
        upload_to_minio(html_path, bucket_name, report_object_name)
        
        # Upload visualization images
        image_files = [
            "cost_comparison.png",
            "cost_vs_rent.png", 
            "top_expensive_cities.png",
            "cost_distribution.png"
        ]
        
        for img_file in image_files:
            img_path = f"{output_dir}/{img_file}"
            img_object_name = f"{pipeline_name}/visualizations/{img_file}"
            upload_to_minio(img_path, bucket_name, img_object_name)
            
        print(f"Successfully uploaded report and images to MinIO")
    except Exception as e:
        print(f"Warning: Could not upload to MinIO: {e}")
    
    print(f"Visualization complete. HTML report saved to {html_path}")
    
    return {
        'status': 'success',
        'html_report': html_path,
        'minio_report': f"{bucket_name}/{report_object_name}",
        'row_count': len(df)
    }

if __name__ == "__main__":
    results = main()
    print(f"Results: {json.dumps(results)}")