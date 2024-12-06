import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

# App Title
st.title("OData Account Reactions Viewer")

# Sidebar for credentials
st.sidebar.header("OData Connection Details")
odata_url = st.sidebar.text_input("OData Endpoint URL", "https://example.com/odata/EntitySet")
username = st.sidebar.text_input("Username", type="default")
password = st.sidebar.text_input("Password", type="password")

# Fetch Data from OData
@st.cache_data
def fetch_odata_data(url, user, pwd):
    try:
        # Make the GET request to the OData endpoint
        response = requests.get(url, auth=HTTPBasicAuth(user, pwd))
        response.raise_for_status()  # Raise HTTPError for bad responses
        # Parse JSON response into a Pandas DataFrame
        data = response.json()
        df = pd.json_normalize(data['value'])  # OData typically uses a "value" key for the main dataset

        # Select only the required columns: "Account Name" and "Reactions"
        if "Account Name" in df.columns and "Reactions" in df.columns:
            df = df[["Account Name", "Reactions"]]
        else:
            st.error("The required fields 'Account Name' and 'Reactions' are not found in the dataset.")
            return pd.DataFrame()

        # Ensure "Reactions" is numeric
        df["Reactions"] = pd.to_numeric(df["Reactions"], errors="coerce")
        df = df.dropna()  # Drop rows with missing values
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()  # Return empty DataFrame in case of error

# Fetch and Display Data
if st.sidebar.button("Fetch Data"):
    if odata_url and username and password:
        st.info("Fetching data...")
        data = fetch_odata_data(odata_url, username, password)
        if not data.empty:
            st.success("Data fetched successfully!")
            st.dataframe(data)  # Display data in a table

            # Plot the bar chart
            st.header("Reactions per Account")
            st.bar_chart(data.set_index("Account Name")["Reactions"])
        else:
            st.warning("No data available.")
    else:
        st.warning("Please provide OData URL, username, and password.")
