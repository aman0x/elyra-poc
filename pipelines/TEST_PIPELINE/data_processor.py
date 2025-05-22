#!/usr/bin/env python3
# data_processor.py

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

# Create a function to generate sample data
def generate_sample_data():
    # Create date range for the past 30 days
    dates = pd.date_range(end=datetime.now(), periods=30).tolist()
    dates = [d.strftime("%Y-%m-%d") for d in dates]
    
    # Generate random metrics
    temperature = np.random.normal(25, 5, 30).tolist()
    humidity = np.random.normal(60, 10, 30).tolist()
    pressure = np.random.normal(1013, 5, 30).tolist()
    wind_speed = np.random.normal(15, 7, 30).tolist()
    
    # Create a DataFrame
    df = pd.DataFrame({
        'date': dates,
        'temperature': temperature,
        'humidity': humidity,
        'pressure': pressure,
        'wind_speed': wind_speed
    })
    
    return df

# Process the data
def process_data(df):
    # Add some derived metrics
    df['feels_like'] = df['temperature'] - 0.4 * (df['humidity'] / 100 * 10)
    df['wind_chill'] = df['temperature'] - (df['wind_speed'] / 10)
    
    # Calculate rolling averages
    df['temp_7day_avg'] = df['temperature'].rolling(7, min_periods=1).mean()
    df['humidity_7day_avg'] = df['humidity'].rolling(7, min_periods=1).mean()
    
    # Round values for readability
    for col in df.columns:
        if col != 'date':
            df[col] = df[col].round(2)
    
    return df

def main():
    print("Generating and processing weather data...")
    
    # Generate sample data
    df = generate_sample_data()
    
    # Process the data
    processed_df = process_data(df)
    
    # Create output directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Save as CSV
    csv_path = 'data/processed_weather.csv'
    processed_df.to_csv(csv_path, index=False)
    
    # Also save as JSON for easy reading
    json_path = 'data/processed_weather.json'
    with open(json_path, 'w') as f:
        f.write(processed_df.to_json(orient='records'))
    
    print(f"Data processing complete. Files saved to {csv_path} and {json_path}")
    
    # Return the path for the next node in the pipeline
    return {
        'csv_path': csv_path,
        'json_path': json_path,
        'row_count': len(processed_df)
    }

if __name__ == "__main__":
    results = main()
    print(f"Results: {json.dumps(results)}")