#!/usr/bin/env python3

"""
Get FMC user token with REST API

Returns:
    Token: Generated access token

Output File Format:
    .env file: saves the token to the .env file under FMC_TOKEN
"""

__author__ = "Sasa Kovacic"
__email__ = "sasa.kovacic@storm.hr"
__version__ = "1.0"


import os
import requests
import base64
from dotenv import load_dotenv

# Get the path to the root directory (assuming scripts are in a 'scripts' subfolder)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables from the .env file in the root directory
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path)

hostname = os.getenv('FMC_HOST')
username = os.getenv('FMC_USERNAME')
password = os.getenv('FMC_PASSWORD')

protocol = "https"

# Suppress any SSL warnings
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

# Function to generate auth token
def generate_auth_token(protocol, hostname, username, password):
    url = f"{protocol}://{hostname}/api/fmc_platform/v1/auth/generatetoken"
    
    # Encode the credentials
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    
    # Define the headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {encoded_credentials}'
    }
    
    try:
        # Make the POST request with SSL verification disabled
        response = requests.post(url, headers=headers, verify=False)
        
        # Check if the request was successful
        if response.status_code == 204:
            # Extract the token from the response headers
            auth_token = response.headers.get('X-auth-access-token')
            return auth_token
        else:
            print(f"Failed to generate token: {response.status_code}")
            print(response.text)
            return None
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

# Function to update or add the token in the .env file
def save_token_to_env(token):
    try:
        # Read the current contents of the .env file
        with open(dotenv_path, 'r') as env_file:
            lines = env_file.readlines()

        # Check if TOKEN exists, and replace it if necessary
        token_updated = False
        with open(dotenv_path, 'w') as env_file:
            for line in lines:
                if line.startswith("FMC_TOKEN="):
                    # Replace the existing token
                    env_file.write(f"FMC_TOKEN='{token}'\n")
                    token_updated = True
                else:
                    # Write other lines unchanged
                    env_file.write(line)
            
            # If TOKEN was not found, append it
            if not token_updated:
                env_file.write(f"FMC_TOKEN='{token}'\n")

        print(f"Token successfully saved to .env")
    except Exception as e:
        print(f"An error occurred while saving the token: {e}")

if __name__ == "__main__":
    # Step 1: Generate auth token
    token = generate_auth_token(protocol, hostname, username, password)

    if token:
        print(f"Auth Token: {token}")

        # Step 2: Save the token to the .env file in the project root
        save_token_to_env(token)
    else:
        print("Failed to retrieve auth token.")
