#!/usr/bin/env python3
# data_visualizer.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
import sys

# Set style
sns.set_style('whitegrid')

def load_data(file_path):
    """Load data from CSV file"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    return pd.read_csv(file_path)

def create_temperature_plot(df, output_dir):
    """Create a temperature plot"""
    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df['temperature'], 'r-', label='Temperature')
    plt.plot(df['date'], df['temp_7day_avg'], 'b--', label='7-Day Average')
    plt.plot(df['date'], df['feels_like'], 'g-.', label='Feels Like')
    
    plt.title('Temperature Trends', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Temperature (°C)', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(f"{output_dir}/temperature_trends.png")
    plt.close()

def create_humidity_plot(df, output_dir):
    """Create a humidity plot"""
    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df['humidity'], 'b-', label='Humidity')
    plt.plot(df['date'], df['humidity_7day_avg'], 'r--', label='7-Day Average')
    
    plt.title('Humidity Trends', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Humidity (%)', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(f"{output_dir}/humidity_trends.png")
    plt.close()

def create_correlation_heatmap(df, output_dir):
    """Create a correlation heatmap"""
    # Select only numeric columns
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title('Correlation Between Weather Metrics', fontsize=16)
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(f"{output_dir}/correlation_heatmap.png")
    plt.close()

def create_scatter_plot(df, output_dir):
    """Create a scatter plot"""
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='temperature', y='humidity', data=df, hue='wind_speed', 
                   palette='viridis', size='pressure', sizes=(20, 200))
    
    plt.title('Temperature vs. Humidity (colored by wind speed)', fontsize=16)
    plt.xlabel('Temperature (°C)', fontsize=12)
    plt.ylabel('Humidity (%)', fontsize=12)
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(f"{output_dir}/temp_humidity_scatter.png")
    plt.close()

def main():
    # Check if a file path was passed from the previous task
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Default path if not provided
        file_path = 'data/processed_weather.csv'
    
    print(f"Loading data from {file_path}")
    
    # Load the data
    try:
        df = load_data(file_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return {
            'status': 'error',
            'message': f"Could not find data file: {file_path}"
        }
    
    # Create output directory if it doesn't exist
    output_dir = 'visualizations'
    os.makedirs(output_dir, exist_ok=True)
    
    print("Creating visualizations...")
    
    # Create various plots
    create_temperature_plot(df, output_dir)
    create_humidity_plot(df, output_dir)
    create_correlation_heatmap(df, output_dir)
    create_scatter_plot(df, output_dir)
    
    # List of generated files
    generated_files = [
        f"{output_dir}/temperature_trends.png",
        f"{output_dir}/humidity_trends.png",
        f"{output_dir}/correlation_heatmap.png",
        f"{output_dir}/temp_humidity_scatter.png"
    ]
    
    print(f"Visualization complete. Files saved to {output_dir}")
    
    return {
        'status': 'success',
        'visualization_files': generated_files,
        'row_count': len(df)
    }

if __name__ == "__main__":
    results = main()
    print(f"Results: {json.dumps(results)}")