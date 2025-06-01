import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="COVID-19 Global Dashboard", layout="wide")

st.title("COVID-19 Global Insights Dashboard")

# Sidebar input
st.sidebar.header("Choose a Country to View Stats")
api_url = "https://disease.sh/v3/covid-19/countries"

@st.cache_data(ttl=300)
def fetch_data():
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error("❌ Failed to fetch data. Please try again later.")
        return []

data = fetch_data()

if data:
    # Convert JSON to DataFrame
    df = pd.DataFrame(data)
    country_list = df['country'].sort_values().tolist()

    # User selects country
    selected_country = st.sidebar.selectbox("Select a Country", country_list)

    country_data = df[df['country'] == selected_country].squeeze()

    # Show country summary
    st.subheader(f"COVID-19 Stats for {selected_country}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cases", f"{country_data['cases']:,}")
    col2.metric("Total Deaths", f"{country_data['deaths']:,}")
    col3.metric("Recovered", f"{country_data['recovered']:,}")

    st.markdown("---")

    # Bar Chart: Active, Critical, Tests
    st.subheader("Case Breakdown")
    breakdown_data = {
        "Active": country_data["active"],
        "Critical": country_data["critical"],
        "Tests": country_data["tests"],
    }
    breakdown_df = pd.DataFrame.from_dict(breakdown_data, orient='index', columns=["Count"])
    breakdown_df.reset_index(inplace=True)
    breakdown_df.columns = ["Type", "Count"]

    fig = px.bar(breakdown_df, x="Type", y="Count", color="Type", title="COVID-19 Breakdown")
    st.plotly_chart(fig, use_container_width=True)

    # Optional: World map of cases
    st.subheader("🗺️ Global Case Map")
    df_map = df[["country", "cases", "countryInfo"]].copy()
    df_map["lat"] = df_map["countryInfo"].apply(lambda x: x.get("lat"))
    df_map["long"] = df_map["countryInfo"].apply(lambda x: x.get("long"))

    map_fig = px.scatter_geo(df_map,
                             lat="lat",
                             lon="long",
                             hover_name="country",
                             size="cases",
                             projection="natural earth",
                             title="Global COVID-19 Cases Distribution")
    st.plotly_chart(map_fig, use_container_width=True)

    st.caption("Data Source: disease.sh (public COVID-19 API)")
else:
    st.warning("No data available.")
