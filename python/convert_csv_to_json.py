import pandas as pd
import json
import os

def convert_csv_to_json(csv_file_path, json_file_path):
    """Convert CSV file to JSON format"""
    
    # Read the CSV file
    df = pd.read_csv(csv_file_path)
    
    # Convert to list of dictionaries
    data = df.to_dict('records')
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
    
    # Write to JSON file
    with open(json_file_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Converted {len(data)} records from {csv_file_path} to {json_file_path}")
    return data

def create_sample_json(csv_file_path, json_file_path, sample_size=50):
    """Create a sample JSON file with limited records for testing"""
    
    # Read the CSV file
    df = pd.read_csv(csv_file_path)
    
    # Take a sample
    df_sample = df.head(sample_size)
    
    # Convert to list of dictionaries
    data = df_sample.to_dict('records')
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
    
    # Write to JSON file
    with open(json_file_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Created sample with {len(data)} records at {json_file_path}")
    return data

if __name__ == "__main__":
    # Paths
    csv_file = "nutrition_dataset.csv"  # Your CSV file
    json_file = "data/nutrition_dataset.json"  # Output JSON file
    sample_json_file = "data/nutrition_dataset_sample.json"  # Sample output
    
    # Convert full dataset
    if os.path.exists(csv_file):
        convert_csv_to_json(csv_file, json_file)
        
        # Also create a smaller sample for quick testing
        create_sample_json(csv_file, sample_json_file, 50)
    else:
        print(f"CSV file {csv_file} not found!")
        print("Please ensure the CSV file is in the same directory as this script.")