import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import altair as alt

# App Title
st.title("Dynamic OData Data Viewer and Visualization")

# Sidebar for connection details
st.sidebar.header("OData Connection Details")
base_url = st.sidebar.text_input(
    "OData Endpoint Base URL",
    "https://sandbox.eu.adverity.com/api/internal/platform/v1/odata/4fad6efa-8c3b-4f07-a36a-54eacfe79b41/odata"
)
username = st.sidebar.text_input("Username", type="default")
password = st.sidebar.text_input("Password", type="password")

# Automatically append '/Query' (with uppercase 'Q') to the base URL
odata_url = f"{base_url.rstrip('/')}/Query"

# Fetch data from OData
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
        return pd.DataFrame()  # Return an empty DataFrame in case of an error

# Fetch and display data
if st.sidebar.button("Fetch Data"):
    if base_url and username and password:
        st.info(f"Fetching data from: {odata_url} ...")
        data = fetch_odata_data(odata_url, username, password)
        if not data.empty:
            st.success("Data fetched successfully!")
            # Display the data as a table
            st.dataframe(data)

            # Visualization options
            st.header("Visualizations")
            available_columns = data.columns.tolist()

            # Default selection for X-axis and Y-axis
            x_axis = st.selectbox("Select the X-axis", available_columns, index=0, key="x_axis")
            y_axis_default_index = 1 if len(available_columns) > 1 else 0  # Default to the 2nd column if available
            y_axis = st.selectbox("Select the Y-axis", available_columns, index=y_axis_default_index, key="y_axis")

            # Allow users to select the chart type
            chart_type = st.selectbox(
                "Select the Chart Type", ["Bar Chart", "Line Chart", "Scatter Plot"], key="chart_type"
            )

            # Button to show the chart
            if st.button("Show Chart"):
                # Render the selected chart type
                if chart_type == "Bar Chart":
                    chart_data = data[[x_axis, y_axis]].dropna()
                    st.ba
