import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

# App Title
st.title("OData Integration Example")

# Sidebar for credentials
st.sidebar.header("OData Connection Details")
odata_url = st.sidebar.text_input("OData Endpoint URL", "https://sandbox.eu.adverity.com/api/")
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
            # Allow user to choose a chart to plot
            if st.checkbox("Show Chart"):
                chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Line Chart"])
                column_to_plot = st.selectbox("Select Column to Plot", data.columns)
                if chart_type == "Bar Chart":
                    st.bar_chart(data[column_to_plot])
                elif chart_type == "Line Chart":
                    st.line_chart(data[column_to_plot])
        else:
            st.warning("No data available.")
    else:
        st.warning("Please provide OData URL, username, and password.")

