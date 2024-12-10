import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import altair as alt

st.title("Data Shares Mini App")

st.sidebar.header("Data Share credentials")
base_url = st.sidebar.text_input(
    "URL",
    "https://sandbox.eu.adverity.com/api/internal/platform/v1/odata/4fad6efa-8c3b-4f07-a36a-54eacfe79b41/odata"
)
username = st.sidebar.text_input("Username", type="default")
password = st.sidebar.text_input("Password", type="password")

odata_url = f"{base_url.rstrip('/')}/Query"

@st.cache_data
def fetch_odata_data(url, user, pwd):
    try:
        
        response = requests.get(url, auth=HTTPBasicAuth(user, pwd))
        response.raise_for_status() 

        data = response.json()
        if "value" in data:
            df = pd.json_normalize(data["value"]) 
            return df
        else:
            st.error("No 'value' key found in the response.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame() 

if st.sidebar.button("Fetch Data"):
    if base_url and username and password:
        st.info(f"Pulling data from Adverity: {odata_url} ...")
        data = fetch_odata_data(odata_url, username, password)
        if not data.empty:
            st.success("Data pulled successfully!")
            
            st.dataframe(data)

            st.header("Visualizations")
            available_columns = data.columns.tolist()

            x_axis = st.selectbox("Select the X-axis", available_columns, index=0)
            y_axis_default_index = 1 if len(available_columns) > 1 else 0  
            y_axis = st.selectbox("Select the Y-axis", available_columns, index=y_axis_default_index)

            if pd.api.types.is_numeric_dtype(data[y_axis]):

                st.subheader("Bar Chart")
                bar_chart_data = data[[x_axis, y_axis]].dropna()
                st.bar_chart(bar_chart_data.set_index(x_axis)[y_axis])

                st.subheader("Line Chart")
                line_chart_data = data[[x_axis, y_axis]].dropna()
                st.line_chart(line_chart_data.set_index(x_axis)[y_axis])

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
        st.warning("Please provide the URL, username, and password.")
