import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

# App Title
st.title("MicroApp powererd by Adverity Data Shares")

# Sidebar for credentials
st.sidebar.header("Data Shares Connection Details")
base_url = st.sidebar.text_input(
    "OData Endpoint Base URL",
    "Copy OData URL from Adverity Data Share"
)
username = st.sidebar.text_input("Username", type="default")
password = st.sidebar.text_input("Password", type="password")

# Append '/query' automatically to the base URL
odata_url = f"{base_url.rstrip('/')}/query"

# Fetch Data from OData
@st.cache_data
def fetch_odata_data(url, user, pwd):
    try:
        # Make the GET request to the OData endpoint
        response = requests.get(url, auth=HTTPBasicAuth(user, pwd))
        response.raise_for_status()  # Raise HTTPError for bad responses

        # Parse JSON response into a Pandas DataFrame
        data = response.json()
        if "value" in data:
            df = pd.json_normalize(data["value"])  # Normalize the "value" array into a DataFrame
            return df
        else:
            st.error("No 'value' key found in the response.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()  # Return empty DataFrame in case of error

# Fetch and Display Data
if st.sidebar.button("Fetch Data"):
    if base_url and username and password:
        st.info(f"Fetching data from: {odata_url} ...")
        data = fetch_odata_data(odata_url, username, password)
        if not data.empty:
            st.success("Data fetched successfully!")

            # Display the data as a table
            st.dataframe(data)

            # Plot the bar chart
            st.header("Reactions per Account")
            if "Account Name" in data.columns and "Reactions" in data.columns:
                st.bar_chart(data.set_index("Account Name")["Reactions"])
            else:
                st.error("The required columns 'Account Name' and 'Reactions' are not available in the dataset.")
        else:
            st.warning("No data available.")
    else:
        st.warning("Please provide OData Base URL, username, and password.")
