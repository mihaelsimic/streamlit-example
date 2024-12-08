import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

st.title("Dynamische OData-Datenanzeige und Visualisierung")

st.sidebar.header("Data Shares Odata details")
base_url = st.sidebar.text_input(
    "OData URL",
    "https://sandbox.eu.adverity.com/api/"
)
username = st.sidebar.text_input("username", type="default")
password = st.sidebar.text_input("password", type="password")

# Add /Query to the url to receive actual data and not query info when url is copied from data shares url
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
            st.error("Couldn't find any 'value'-key.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error while pulling data: {e}")
        return pd.DataFrame() # return empty frame

if st.sidebar.button("Pulling data"):
    if base_url and username and password:
        st.info(f"Data is being pulled from {odata_url}")
        data = fetch_odata_data(odata_url, username, password)
        if not data.empty:
            st.success("Data was pulled successfully!")

            st.dataframe(data)
            
            st.header("Visualize")
            available_columns = data.columns.tolist()

            x_axis = st.selectbox("Choose X-Achse", available_columns)
            y_axis = st.selectbox("Choose Y-Achse", available_columns)

            chart_type = st.selectbox("Wählen Sie den Diagrammtyp", ["Bar Chart", "Line Chart", "Dot Chart"])

            if st.button("Display visualization"):
                if chart_type == "Bar Chart":
                    st.bar_chart(data.set_index(x_axis)[y_axis])
                elif chart_type == "Line Chart":
                    st.line_chart(data.set_index(x_axis)[y_axis])
                elif chart_type == "Dot Chart":
                    st.write("Chart is getting created ...")
                    st.altair_chart(
                        data[[x_axis, y_axis]].dropna().rename(columns={x_axis: "x", y_axis: "y"}).reset_index().pipe(
                            lambda df: df.plot.scatter(x="x", y="y")
                        ),
                        use_container_width=True
                    )
        else:
            st.warning("No data available.")
    else:
        st.warning("Please provide Data Share URL, username & password.")
