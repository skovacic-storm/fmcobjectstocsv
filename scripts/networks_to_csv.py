#!/usr/bin/env python3

"""
Converts fmc_networks.json file to fmc_networks.csv


Args:
    input_file (str): /export/fmc_networks.json
    output_file (str): /export/fmc_networks.csv

Returns:
    None: This script doesn't return a value, but creates an output file.

Input File Format:
    JSON file: fmc_networks.json, file exported from FMC

Output File Format:
    CSV file: fmc_networks.csv, CSV file with processed data
"""

__author__ = "Sasa Kovacic"
__email__ = "sasa.kovacic@storm.hr"
__version__ = "1.0"


import pandas as pd
import json

json_file = 'export/fmc_networks.json'
csv_file = 'export/fmc_networks.csv'

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
    # Extract each field, ensuring they exist
    names.append(item.get('name', ''))
    values.append(item.get('value', ''))
    types.append(item.get('type', ''))
    overrides.append(item.get('overridable', ''))
    descriptions.append(item.get('description', ''))
    
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
