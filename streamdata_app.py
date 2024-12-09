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

            # Dropdowns for selecting fields
            x_axis = st.selectbox("Select the X-axis", available_columns, index=0)
            y_axis_default_index = 1 if len(available_columns) > 1 else 0  # Default to the 2nd column if available
            y_axis = st.selectbox("Select the Y-axis", available_columns, index=y_axis_default_index)

            # Ensure Y-axis column is numeric for valid visualizations
            if pd.api.types.is_numeric_dtype(data[y_axis]):
                # Bar Chart
                st.subheader("Bar Chart")
                bar_chart_data = data[[x_axis, y_axis]].dropna()
                st.bar_chart(bar_chart_data.set_index(x_axis)[y_axis])

                # Line Chart
                st.subheader("Line Chart")
                line_chart_data = data[[x_axis, y_axis]].dropna()
                st.line_chart(line_chart_data.set_index(x_axis)[y_axis])

                # Scatter Plot
                st.subheader("Scatter Plot")
                scatter = alt.Chart(data.dropna()).mark_circle(size=60).encode(
                    x=alt.X(x_axis, title=x_axis),
                    y=alt.Y(y_axis, title=y_axis),
                    tooltip=available_columns
                ).interactive()
                st.altair_chart(scatter, use_container_width=True)
            else:
                st.warning(f"The selected Y-axis column '{y_axis}' is not numeric. Please select a numeric column.")
        else:
            st.warning("No data available.")
    else:
        st.warning("Please provide the Base URL, username, and password.")
