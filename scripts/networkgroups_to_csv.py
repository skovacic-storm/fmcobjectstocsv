#!/usr/bin/env python3

"""
Converts fmc_networkgroups.json file to fmc_networkgroups.csv


Args:
    input_file (str): /export/fmc_networkgroups.json
    output_file (str): /export/fmc_networkgroups.csv

Returns:
    None: This script doesn't return a value, but creates an output file.

Input File Format:
    JSON file: fmc_networkgroups.json, file exported from FMC

Output File Format:
    CSV file: fmc_networkgroups.csv, CSV file with processed data
"""

__author__ = "Sasa Kovacic"
__email__ = "sasa.kovacic@storm.hr"
__version__ = "1.0"


import pandas as pd
import json

json_file = 'export/fmc_networkgroups.json'
csv_file = 'export/fmc_networkgroups.csv'

# Load the JSON data
with open(json_file) as json_file:
    data = json.load(json_file)

# Initialize lists to store extracted values
names = []
values = []
types = []
overrides = []
descriptions = []
links = []

# Extract the desired fields from each item
for item in data['items']:
    # Extract name, value, type, and other fields
    names.append(item.get('name', ''))
    types.append(item.get('type', ''))
    overrides.append(item.get('overridable', ''))
    descriptions.append(item.get('description', ''))
    
    # For literals (if available), concatenate all values
    literal_values = [literal['value'] for literal in item.get('literals', [])]
    object_values = [obj['name'] for obj in item.get('objects', [])]
    values.append(', '.join(literal_values + object_values))
    
    # Extract the 'self' link
    links.append(item.get('links', {}).get('self', ''))

# Create a DataFrame from the extracted data
df = pd.DataFrame({
    'Object Name': names,
    'Value': values,
    'Type': types,
    'Override': overrides,
    'Object Description': descriptions,
    'Link': links
})

# Export DataFrame to CSV
df.to_csv(csv_file, index=False)

print(f"Data has been exported to {csv_file}")
