import streamlit as st
import os
import pandas as pd
import subprocess
import platform

from PIL import Image


# ----- Settings -----
icon = Image.open("images/flavicon.ico")

st.set_page_config(
    page_title="fmc objects to csv converter",
    page_icon=icon,
    layout="centered", # centered | wide
    initial_sidebar_state="expanded", # auto | collapsed | expanded
    menu_items={
        #"Get Help": "https://streamlit.io",
        "Report a bug": "mailto:sasa.kovacic@storm.hr",
        #"About": "About Streamlit App"
    }
)

hide_streamlit_style = """
            <style>
            /* Show/Hide (show:hidden) Main Menu */
            #MainMenu {visibility: show;}
            /* Show/Hide (show:hidden) Footer */
            footer {visibility: show;}
            /* Show/Hide (show:hidden) Deploy Button */
            .stAppDeployButton {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

footer = """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        text-align: center;
    }
    </style>
    <div class="footer">
        <p>Storm Computers @2024 | v1.0</p>
    </div>
"""
st.markdown(footer, unsafe_allow_html=True) #Show footer

# Inject custom CSS
st.markdown(
    """
    <style>
    /* Set the padding of the top */
        .block-container {
            padding-top: 10px;
            }
    /* Set the width of the sidebar */
        section[data-testid="stSidebar"] {
            width: 506px !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------

# Get the absolute path of the export folder
current_dir = os.path.dirname(os.path.abspath(__file__))
if platform.system() == 'Windows':
    venv_python = os.path.join(current_dir, '.venv', 'Scripts', 'python') #path to venv python for Windows
else:
    venv_python = os.path.join(current_dir, '.venv', 'bin', 'python') #path to venv python for Linux/MacOS
export_folder = os.path.join(current_dir, 'export')
env_file_path = os.path.join(current_dir, '.env')

# Function to read environment variables from .env
def read_env_variables():
    env_dict = {}
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_dict[key.strip()] = value.strip().strip("'")
    return env_dict

# Function to update .env file
def update_env_variable(key, value):
    try:
        # Read existing contents
        env_contents = []
        updated = False
        
        if os.path.exists(env_file_path):
            with open(env_file_path, 'r') as file:
                env_contents = file.readlines()
        
        # Update or add new variable
        new_contents = []
        for line in env_contents:
            if line.strip() and not line.startswith('#'):
                current_key = line.split('=', 1)[0].strip()
                if current_key == key:
                    # Add single quotes around the value
                    new_contents.append(f"{key}='{value}'\n")
                    updated = True
                else:
                    new_contents.append(line)
            else:
                new_contents.append(line)
        
        if not updated:
            # Add single quotes around the value for new entries
            new_contents.append(f"{key}='{value}'\n")
        
        # Write back to file
        with open(env_file_path, 'w') as file:
            file.writelines(new_contents)
        
        return True
    except Exception as e:
        st.error(f"Error updating .env file: {str(e)}")
        return False

# Function to clear the value of multiple environment variables
def clear_env_values(keys):
    try:
        with open(env_file_path, 'r') as file:
            lines = file.readlines()

        with open(env_file_path, 'w') as file:
            for line in lines:
                if any(line.strip().startswith(f'{key}=') for key in keys):
                    key_name = line.split('=')[0]
                    file.write(f"{key_name}=''\n")
                else:
                    file.write(line)

        return True
    except Exception as e:
        st.error(f"Error clearing .env values: {str(e)}")
        return False


# Sidebar
env_vars = read_env_variables()
with st.sidebar:
    try:
        env_dict = {}
        if os.path.exists(env_file_path):
            # Read .env file
            with open(env_file_path, 'r') as env_file:
                for line in env_file:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        # Remove single quotes from value when storing in dict
                        value = value.strip().strip("'")
                        env_dict[key.strip()] = value
        
        # Add/Update Credentials Section
        st.subheader("fmc credentials")
        current_username = env_dict.get('FMC_USERNAME', '')
        current_password = env_dict.get('FMC_PASSWORD', '')
        
        new_username = st.text_input("Username", value=current_username, key="username_input")
        new_password = st.text_input("Password", value=current_password, type="password", key="password_input")
        
        col1, col2 = st.columns([6,2])
        with col1:        
            if st.button("Update token", help="Send credentials and update token", icon=":material/sync:"):
                username_updated = update_env_variable('FMC_USERNAME', new_username)
                password_updated = update_env_variable('FMC_PASSWORD', new_password)
                    
                if username_updated and password_updated:
                    result = subprocess.run([venv_python, 'scripts/get_token.py'], capture_output=True, text=True)
                    if result.returncode == 1:
                        st.success(f"Success: Token updated")
                    else:
                        st.error(f"Error: Check credentials and try again")
                    st.rerun()
        
        with col2:
            # Only show Log Out button if FMC_TOKEN is present and not empty
            if 'FMC_TOKEN' in env_vars and env_vars['FMC_TOKEN']:
                if st.button("Log Out", icon=":material/logout:"):
                    if clear_env_values(['FMC_TOKEN', 'FMC_USERNAME', 'FMC_PASSWORD']):
                        st.toast("Logged out successfully!")
                        st.rerun()
        
        # Display all variables
        #st.subheader("FMC connection Variables")
        with st.expander("FMC connection varibles:", icon=":material/unfold_more:"):
            if env_dict:
                # Convert to DataFrame with masked password
                env_items = []
                for key, value in env_dict.items():
                    masked_value = '••••••••' if 'PASSWORD' in key.upper() else value
                    env_items.append({'Variable': key, 'Value': masked_value})
                #   env_items.append({'Variable': key, 'Value': value})
                
                env_df = pd.DataFrame(env_items)
                st.dataframe(
                    env_df,
                    column_config={
                        "Variable": st.column_config.TextColumn("Variable Name"),
                        "Value": st.column_config.TextColumn("Value", width=260),
                    },
                    hide_index=True,
                )
            else:
                st.info(f".env file is empty or not found")
            
    except Exception as e:
        st.error(f"Error handling .env file: {str(e)}")


# Main page
st.subheader("fmc objects to *.csv* converter")
st.divider()

col1, col2, col3, col4 = st.columns(4, vertical_alignment="center")


with col1:
    st.markdown("**AccessRules**")
    get_accessrules_button = st.button(label="Get .csv", help="Export and convert AccessRules to csv", key="get_accessrules_csv", icon=":material/csv:")
        

with col2:
    st.markdown("**NetworkGroups**")
    get_networkgroups_button = st.button(label="Get .csv", help="Export and convert NetworkGroups to csv", key="get_networkgroups_csv", icon=":material/csv:")
        

with col3:
    st.markdown("**Networks**")
    get_networks_button = st.button(label="Get .csv", help="Export and convert Networks to csv", key="get_networks_csv", icon=":material/csv:")
        
        
with col4:
    st.markdown("**PortObjectGroups**")
    get_portobjectgroups_button = st.button(label="Get .csv", help="Export and convert PortObjectGroups to csv", key="get_portobjectgroups_csv", icon=":material/csv:")
        

with st.expander("get .json", icon=":material/unfold_more:"):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        export_accessrules_button = st.button(label="Export", help="Export AccessRules from FMC to JSON", key="get_accessrules", icon=":material/file_save:")
        convert_accessrules_button = st.button(label="Convert", help="Convert AccessRules JSON to CSV", key="convert_accessrules", icon=":material/csv:")
        
    with col2:
        export_networkgroups_button = st.button(label="Export", help="Export NetworkGroups from FMC to JSON", key="get_networkgroups", icon=":material/file_save:")
        convert_networkgroups_button = st.button(label="Convert", help="Convert NetworkGroups JSON to CSV", key="convert_networkgroups", icon=":material/csv:")
        
    with col3:
        export_networks_button = st.button(label="Export", help="Export Networks from FMC to JSON", key="get_networks", icon=":material/file_save:")
        convert_networks_button = st.button(label="Convert", help="Convert Networks JSON to CSV", key="convert_networks", icon=":material/csv:")
        
    with col4:
        export_portobjectgroups_button = st.button(label="Export", help="Export PortObjectGroups from FMC to JSON", key="get_portobjectgroups", icon=":material/file_save:")
        convert_portobjectgroups_button = st.button(label="Convert", help="Convert PortObjectGroups JSON to CSV", key="convert_portobjectgroups", icon=":material/csv:")

# Run scripts on button press
# accessrules
if export_accessrules_button:
    with st.spinner("Exporting AccessRules from FMC to JSON..."):
        result = subprocess.run([venv_python, 'scripts/get_accessrules.py'], capture_output=True, text=True)        
        st.toast(f'{result.stdout} ')

if convert_accessrules_button:
    with st.spinner("Converting AccessRules JSON to CSV..."):
        result = subprocess.run([venv_python, 'scripts/accessrules_to_csv.py'], capture_output=True, text=True)
        if result.stderr:
            st.toast(f"fmc_accessrules.json not found, run Export first")
        else:      
            st.toast(f'{result.stdout} ')
            
# --- single button ---
if get_accessrules_button:
    with st.spinner("Exporting AccessRules from FMC to JSON..."):
        export_result = subprocess.run([venv_python, 'scripts/get_accessrules.py'], capture_output=True, text=True)
        st.toast(f'{export_result.stdout}')

    if export_result.returncode == 0:  # Check if the export script ran successfully
        with st.spinner("Converting AccessRules JSON to CSV..."):
            convert_result = subprocess.run([venv_python, 'scripts/accessrules_to_csv.py'], capture_output=True, text=True)
            if convert_result.stderr:
                st.toast("fmc_accessrules.json not found, run Export first")
            else:
                st.toast(f'{convert_result.stdout}')
                
            # Delete the .json file after successful conversion
            os.remove("export/fmc_accessrules.json")
    else:
        st.toast("Export failed, conversion skipped")

# --------------------- 

# networkGroups
if get_networkgroups_button:
    with st.spinner("Exporting NetworkGroups from FMC to JSON..."):
        export_result = subprocess.run([venv_python, 'scripts/get_networkgroups.py'], capture_output=True, text=True)
        st.toast(f'{export_result.stdout}')

    if export_result.returncode == 0:  # Check if the export script ran successfully
        with st.spinner("Converting NetworkGroups JSON to CSV..."): 
            convert_result = subprocess.run([venv_python, 'scripts/networkgroups_to_csv.py'], capture_output=True, text=True)
            if convert_result.stderr:
                st.toast("fmc_networkgroups.json not found, run Export first")
            else:
                st.toast(f'{convert_result.stdout}')
                
                # Delete the .json file after successful conversion
                os.remove("export/fmc_networkgroups.json")
    else:
        st.toast("Export failed, conversion skipped")

# --- single button ---
if get_networkgroups_button:
    with st.spinner("Exporting NetworkGroups from FMC to JSON..."):
        export_result = subprocess.run([venv_python, 'scripts/get_networkgroups.py'], capture_output=True, text=True)
        st.toast(f'{export_result.stdout}')

    if export_result.returncode == 0:  # Check if the export script ran successfully
        with st.spinner("Converting NetworkGroups JSON to CSV..."): 
            convert_result = subprocess.run([venv_python, 'scripts/networkgroups_to_csv.py'], capture_output=True, text=True)
            if convert_result.stderr:
                st.toast("fmc_networkgroups.json not found, run Export first")
            else:
                st.toast(f'{convert_result.stdout}')
                
            # Delete the .json file after successful conversion
            os.remove("export/fmc_networkgroups.json")
                
    else:
        st.toast("Export failed, conversion skipped")
        
# ---------------------

# networks
if export_networks_button:
    with st.spinner("Exporting Networks from FMC to JSON..."):
        result = subprocess.run([venv_python, 'scripts/get_networks.py'], capture_output=True, text=True)        
        st.toast(f'{result.stdout} ')
    
if convert_networks_button:
    with st.spinner("Converting Networks JSON to CSV..."):
        result = subprocess.run([venv_python, 'scripts/networks_to_csv.py'], capture_output=True, text=True)        
        if result.stderr:
            st.toast(f"networks.json not found, run Export first")
        else:      
            st.toast(f'{result.stdout} ')

# --- single button ---
if get_networks_button:
    with st.spinner("Exporting Networks from FMC to JSON..."):
        export_result = subprocess.run([venv_python, 'scripts/get_networks.py'], capture_output=True, text=True)
        st.toast(f'{export_result.stdout}')

    if export_result.returncode == 0:  # Check if the export script ran successfully
        with st.spinner("Converting Networks JSON to CSV..."):
            convert_result = subprocess.run([venv_python, 'scripts/networks_to_csv.py'], capture_output=True, text=True)
            if convert_result.stderr:
                st.toast("fmc_networks.json not found, run Export first")
            else:
                st.toast(f'{convert_result.stdout}')
            
            # Delete the .json file after successful conversion
            os.remove("export/fmc_networks.json")
                              
    else:
        st.toast("Export failed, conversion skipped")
# ---------------------
            
# portobjectgroups
if export_portobjectgroups_button:
    with st.spinner("Exporting PortObjectGroups from FMC to JSON..."):
        result = subprocess.run([venv_python, 'scripts/get_portobjectgroups.py'], capture_output=True, text=True)        
        st.toast(f'{result.stdout} ')
        
if convert_portobjectgroups_button:
    with st.spinner("Converting PortObjectGroups JSON to CSV..."):
        result = subprocess.run([venv_python, 'scripts/portobjectgroups_to_csv.py'], capture_output=True, text=True)        
        if result.stderr:
            st.toast(f"portobjectgroups.json not found, run Export first")
        else:      
            st.toast(f'{result.stdout} ')

# --- single button ---
if get_portobjectgroups_button:
    with st.spinner("Exporting PortObjectGroups from FMC to JSON..."):
        export_result = subprocess.run([venv_python, 'scripts/get_portobjectgroups.py'], capture_output=True, text=True)
        st.toast(f'{export_result.stdout}')

    if export_result.returncode == 0:  # Check if the export script ran successfully
        with st.spinner("Converting PortObjectGroups JSON to CSV..."):
            convert_result = subprocess.run([venv_python, 'scripts/portobjectgroups_to_csv.py'], capture_output=True, text=True)
            if convert_result.stderr:
                st.toast("fmc_portobjectgroups.json not found, run Export first")
            else:
                st.toast(f'{convert_result.stdout}')
                
            # Delete the .json file after successful conversion
            os.remove("export/fmc_portobjectgroups.json")
                
    else:
        st.toast("Export failed, conversion skipped")
        
# ---------------------

# Show export folder
st.divider()

# Initialize session state for deletion confirmation
if 'delete_clicked' not in st.session_state:
    st.session_state.delete_clicked = False

def delete_all_files():
    try:
        files = [f for f in os.listdir(export_folder) if os.path.isfile(os.path.join(export_folder, f))]
        for file in files:
            file_path = os.path.join(export_folder, file)
            os.remove(file_path)
        st.success("All files have been deleted successfully!")
        st.session_state.delete_clicked = False
        st.rerun()
    except Exception as e:
        st.error(f"Error deleting files: {str(e)}")

try:
    # Check if export folder exists
    if not os.path.exists(export_folder):
        st.warning("Export folder does not exist. Creating one...")
        os.makedirs(export_folder)
    
    # Get list of files in export folder
    contents = [f for f in os.listdir(export_folder) if os.path.isfile(os.path.join(export_folder, f))]
    
    # Add delete functionality at the top
    if contents:
        delete_col1, delete_col2, delete_col3 = st.columns([1, 2, 1])
        with delete_col1:
            if st.button("Delete All Files", type="primary"):
                st.session_state.delete_clicked = True
        
        if st.session_state.delete_clicked:
            with delete_col2:
                st.warning("Warning: This action cannot be undone!")
            with delete_col3:
                if st.button("Confirm Delete"):
                    delete_all_files()
    
    # Files container with border
    with st.container(border=True):
        if not contents:
            st.info("The export folder is empty.")
        else:
            st.markdown("**Exported Files:**")
            for item in contents:
                full_path = os.path.join(export_folder, item)
                if os.path.isfile(full_path):
                    size = f"{os.path.getsize(full_path) / 1024:.2f} KB"
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.text(item)
                    with col2:
                        st.text(size)
                    with col3:
                        try:
                            with open(full_path, "rb") as f:
                                st.download_button(
                                    label="Download",
                                    data=f,
                                    file_name=item,
                                    mime="application/octet-stream"
                                )
                        except Exception as e:
                            st.error(f"Error creating download button: {str(e)}")

except Exception as e:
    st.error(f"Error: {str(e)}")