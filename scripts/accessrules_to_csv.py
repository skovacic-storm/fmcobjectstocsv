#!/usr/bin/env python3

"""
Converts fmc_accessrules.json file to fmc_accessrules.csv


Args:
    input_file (str): /export/fmc_accessrules.json
    output_file (str): /export/fmc_accessrules.csv

Returns:
    None: This script doesn't return a value, but creates an output file.

Input File Format:
    JSON file: fmc_accessrules.json, file exported from FMC

Output File Format:
    CSV file: fmc_accessrules.csv, CSV file with processed data
"""

__author__ = "Sasa Kovacic"
__email__ = "sasa.kovacic@storm.hr"
__version__ = "1.0"


import json
import pandas as pd

json_file = 'export/fmc_accessrules.json'
csv_file = 'export/fmc_accessrules.csv'

# Load the JSON data
with open(json_file) as json_file:
    data = json.load(json_file)

# Initialize lists to store extracted values
names = []
actions = []
sourceZones = []
destinationZones = []
sourceNetworks = []
destinationNetworks = []
sourcePorts = []
destinationPorts = []
comments = []
indices = []
links = []
    
# Helper function to safely extract protocol:port or protocol:name
def extract_protocol_name(obj, port_type='name'):
    protocol = obj.get('protocol', '')

    # Check if protocol is a digit and convert it to TCP or UDP
    if protocol.isdigit():
        protocol = 'TCP' if protocol == '6' else 'UDP' if protocol == '17' else protocol

    port_or_name = obj.get(port_type, '')
    return f"{protocol}:{port_or_name}"

# Helper function to safely extract network name or literal value
def extract_network_name(obj, network_type='name'):
    return obj.get(network_type, '')


# Extract desired key-value pairs from each item
for index, item in enumerate(data['items']):
    # Start index, extract name and action
    indices.append(index + 1)  # Start index from 1
    names.append(item['name'])
    actions.append(item['action'])
    
    # Extract source zones
    source_zone_names = [obj['name'] for obj in item.get('sourceZones', {}).get('objects', [])]
    sourceZones.append(','.join(source_zone_names))
    
    # Extract destination zones
    destination_zone_names = [obj['name'] for obj in item.get('destinationZones', {}).get('objects', [])]
    destinationZones.append(','.join(destination_zone_names))
    
    # Extract source networks (from both objects and literals)
    source_networks = []

    # Check for 'objects' in sourceNetworks
    if 'objects' in item.get('sourceNetworks', {}):
        source_networks += [extract_network_name(obj, 'name') for obj in item['sourceNetworks']['objects']]

    # Check for 'literals' in sourceNetworks
    if 'literals' in item.get('sourceNetworks', {}):
        source_networks += [extract_network_name(literal, 'value') for literal in item['sourceNetworks']['literals']]

    sourceNetworks.append(','.join(source_networks) if source_networks else '')

    # Extract destination networks (from both objects and literals)
    destination_networks = []

    # Check for 'objects' in destinationNetworks
    if 'objects' in item.get('destinationNetworks', {}):
        destination_networks += [extract_network_name(obj, 'name') for obj in item['destinationNetworks']['objects']]

    # Check for 'literals' in destinationNetworks
    if 'literals' in item.get('destinationNetworks', {}):
        destination_networks += [extract_network_name(literal, 'value') for literal in item['destinationNetworks']['literals']]
    destinationNetworks.append(','.join(destination_networks) if destination_networks else '')

    # Extract source ports (from both objects and literals)
    source_ports = []

    # Check for 'objects' in sourcePorts
    if 'objects' in item.get('sourcePorts', {}):
        source_ports += [extract_protocol_name(obj, 'name') for obj in item['sourcePorts']['objects']]

    # Check for 'literals' in sourcePorts
    if 'literals' in item.get('sourcePorts', {}):
        source_ports += [extract_protocol_name(literal, 'port') for literal in item['sourcePorts']['literals']]

    sourcePorts.append(','.join(source_ports) if source_ports else '')

    # Extract destination ports (from both objects and literals)
    destination_ports = []

    # Check for 'objects' in destinationPorts
    if 'objects' in item.get('destinationPorts', {}):
        destination_ports += [extract_protocol_name(obj, 'name') for obj in item['destinationPorts']['objects']]

    # Check for 'literals' in destinationPorts
    if 'literals' in item.get('destinationPorts', {}):
        destination_ports += [extract_protocol_name(literal, 'port') for literal in item['destinationPorts']['literals']]

    destinationPorts.append(','.join(destination_ports) if destination_ports else '')

    # Extract comments (ensure it exists)
    if item.get('commentHistoryList'):
        # List to hold formatted comments
        formatted_comments = []
        
        # Loop through each comment in the commentHistoryList
        for comment_entry in item['commentHistoryList']:
            # Extract the date and comment
            date = comment_entry.get('date', '')[0:19]
            comment_text = comment_entry.get('comment', '').replace('\n', ' ')
            
            # Format as "date: comment"
            formatted_comments.append(f"{date}: {comment_text}")
        
        # Join all formatted comments with a separator (e.g., " | " or any other delimiter)
        comments.append(' | '.join(formatted_comments))
    else:
        comments.append('')  # Add an empty value if no comments are present
        
    # Extract links (ensure it exists)
    if item.get('links'):
        links.append(item['links']['self'])
    else:
        links.append('')

# Ensure all lists are the same length
max_length = max(len(names), len(actions), len(sourceZones), len(destinationZones), len(sourceNetworks),
                 len(destinationNetworks), len(sourcePorts), len(destinationPorts), len(comments), len(indices))

def pad_list(lst, max_length):
    return lst + [''] * (max_length - len(lst))

names = pad_list(names, max_length)
actions = pad_list(actions, max_length)
sourceZones = pad_list(sourceZones, max_length)
destinationZones = pad_list(destinationZones, max_length)
sourceNetworks = pad_list(sourceNetworks, max_length)
destinationNetworks = pad_list(destinationNetworks, max_length)
sourcePorts = pad_list(sourcePorts, max_length)
destinationPorts = pad_list(destinationPorts, max_length)
comments = pad_list(comments, max_length)
indices = pad_list(indices, max_length)
links = pad_list(links, max_length)

# Create DataFrame from extracted data
df = pd.DataFrame({
    'Index': indices,
    'Name': names,
    'Action': actions,
    'SourceZone': sourceZones,
    'DestinationZone': destinationZones,
    'SourceNetwork': sourceNetworks,
    'DestinationNetwork': destinationNetworks,
    'SourcePort': sourcePorts,
    'DestinationPort': destinationPorts,
    'Comment': comments,
    'Link': links
})

# Export DataFrame to CSV
df.to_csv(csv_file, index=False)

print(f"Data has been exported to {csv_file}")
