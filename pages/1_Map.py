import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="GIS AQI Map",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ VayuDrishti - Dehradun GIS AQI Map")

st.markdown("""
Interactive GIS visualization of air quality across Dehradun.
Hover over markers for quick details and click markers for complete statistics.
""")

# ==================================================
# LOAD DATA
# ==================================================

@st.cache_data
def load_data():
    df = pd.read_excel(
        "data/dehradun_master_dataset_cleaned.xlsx"
    )

    df["datetime"] = pd.to_datetime(df["datetime"])

    return df

df = load_data()

# ==================================================
# SIDEBAR FILTERS
# ==================================================

st.sidebar.header("🔍 Map Filters")

selected_zones = st.sidebar.multiselect(
    "Select Zones",
    sorted(df["zone"].unique()),
    default=sorted(df["zone"].unique())
)

filtered_df = df[df["zone"].isin(selected_zones)]

# ==================================================
# AQI HELPERS
# ==================================================

def get_color(aqi):

    if aqi <= 50:
        return "#00E400"

    elif aqi <= 100:
        return "#FFFF00"

    elif aqi <= 150:
        return "#FF7E00"

    elif aqi <= 200:
        return "#FF0000"

    elif aqi <= 300:
        return "#8F3F97"

    else:
        return "#7E0023"


def get_aqi_category(aqi):

    if aqi <= 50:
        return "Good"

    elif aqi <= 100:
        return "Moderate"

    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"

    elif aqi <= 200:
        return "Unhealthy"

    elif aqi <= 300:
        return "Very Unhealthy"

    else:
        return "Hazardous"

# ==================================================
# KPI CARDS
# ==================================================

st.subheader("📊 Air Quality Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Average EU AQI",
    f"{filtered_df['eu_aqi'].mean():.1f}"
)

c2.metric(
    "Average PM2.5",
    f"{filtered_df['pm25'].mean():.1f}"
)

c3.metric(
    "Average PM10",
    f"{filtered_df['pm10'].mean():.1f}"
)

c4.metric(
    "Total Zones",
    filtered_df["zone"].nunique()
)

st.divider()

# ==================================================
# ZONE SUMMARY
# ==================================================

zone_data = (
    filtered_df.groupby(
        ["zone", "latitude", "longitude"]
    )
    .agg({
        "eu_aqi": "mean",
        "pm25": "mean",
        "pm10": "mean",
        "traffic_congestion": "mean",
        "wind_speed": "mean",
        "humidity": "mean"
    })
    .reset_index()
)

# ==================================================
# CREATE MAP
# ==================================================

m = folium.Map(
    location=[30.3165, 78.0322],
    zoom_start=11,
    tiles="CartoDB Positron"
)

# ==================================================
# MARKERS
# ==================================================

for _, row in zone_data.iterrows():

    aqi = row["eu_aqi"]

    popup_html = f"""
    <div style="width:250px">

    <h4>{row['zone']}</h4>

    <hr>

    <b>EU AQI:</b> {aqi:.1f}<br>
    <b>Category:</b> {get_aqi_category(aqi)}<br><br>

    <b>PM2.5:</b> {row['pm25']:.1f}<br>
    <b>PM10:</b> {row['pm10']:.1f}<br>
    <b>Traffic:</b> {row['traffic_congestion']:.1f}<br>
    <b>Wind Speed:</b> {row['wind_speed']:.1f}<br>
    <b>Humidity:</b> {row['humidity']:.1f}

    </div>
    """

    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=max(8, min(aqi / 10, 25)),
        color=get_color(aqi),
        fill=True,
        fill_color=get_color(aqi),
        fill_opacity=0.85,
        weight=2,
        tooltip=f"{row['zone']} | AQI: {aqi:.1f}",
        popup=folium.Popup(
            popup_html,
            max_width=300
        )
    ).add_to(m)

# ==================================================
# AQI LEGEND
# ==================================================

legend_html = """
<div style="
position: fixed;
bottom: 40px;
left: 40px;
width: 200px;
background-color: white;
padding: 12px;
border-radius: 10px;
box-shadow: 2px 2px 10px grey;
z-index:9999;
font-size:14px;
">

<b>🌍 AQI Legend</b><br><br>

<span style="color:#00E400;">●</span> Good (0-50)<br>
<span style="color:#FFFF00;">●</span> Moderate (51-100)<br>
<span style="color:#FF7E00;">●</span> Sensitive (101-150)<br>
<span style="color:#FF0000;">●</span> Unhealthy (151-200)<br>
<span style="color:#8F3F97;">●</span> Very Unhealthy (201-300)<br>
<span style="color:#7E0023;">●</span> Hazardous (300+)

</div>
"""

m.get_root().html.add_child(
    folium.Element(legend_html)
)

# ==================================================
# DISPLAY MAP
# ==================================================

st.subheader("🌍 Interactive GIS AQI Map")

st_folium(
    m,
    height=700,
    use_container_width=True
)

# ==================================================
# ZONE STATISTICS TABLE
# ==================================================

st.divider()

st.subheader("📋 Zone Statistics")

display_table = zone_data.sort_values(
    by="eu_aqi",
    ascending=False
)

st.dataframe(
    display_table,
    use_container_width=True
)