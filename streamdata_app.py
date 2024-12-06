import streamlit as st
import requests
from requests.auth import HTTPBasicAuth

# App Title
st.title("OData Debugging App")

# Sidebar for credentials
st.sidebar.header("OData Connection Details")
odata_url = st.sidebar.text_input("OData Endpoint URL", "https://sandbox.eu.adverity.com/api/internal/platform/v1/odata/")
username = st.sidebar.text_input("Username", type="default")
password = st.sidebar.text_input("Password", type="password")

# Fetch Data from OData
@st.cache_data
def fetch_odata_data(url, user, pwd):
    try:
        # Make the GET request to the OData endpoint
        response = requests.get(url, auth=HTTPBasicAuth(user, pwd))
        response.raise_for_status()  # Raise HTTPError for bad responses
        # Return raw JSON response
        return response.json()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return {}

# Fetch and Display Raw Data
if st.sidebar.button("Fetch Data"):
    if odata_url and username and password:
        st.info("Fetching data...")
        data = fetch_odata_data(odata_url, username, password)
        if data:
            st.success("Data fetched successfully!")
            st.json(data)  # Display raw JSON response for debugging

            # Check if "value" key exists
            if "value" in data:
                st.write("Value Contents:")
                st.write(data["value"])  # Display the contents of "value"
            else:
                st.warning("No 'value' key found in the response.")
        else:
            st.warning("No data available.")
    else:
        st.warning("Please provide OData URL, username, and password.")
