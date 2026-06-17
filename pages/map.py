import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap

from gis_module.preprocessing import clean_data
from gis_module.config import LAT_COL, LON_COL, ZONE_COL


def get_color(aqi):
    if aqi <= 50: return "#00E400"
    if aqi <= 100: return "#FFFF00"
    if aqi <= 150: return "#FF7E00"
    if aqi <= 200: return "#FF0000"
    if aqi <= 300: return "#8F3F97"
    return "#D1476E"


# =========================
# CACHE (VERY IMPORTANT)
# =========================
@st.cache_data(show_spinner=False)
def preprocess(df, zone, hour):

    df = clean_data(df)

    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
        df["hour"] = df["datetime"].dt.hour

    aqi_col = next((c for c in df.columns if "aqi" in c.lower()), "eu_aqi")

    # FILTER ZONE
    if zone != "All":
        df = df[df[ZONE_COL] == zone]

    # FILTER HOUR
    if hour is not None and "hour" in df.columns:
        df = df[df["hour"] == hour]

    # LIMIT DATA (CRITICAL FOR SPEED)
    if len(df) > 5000:
        df = df.sample(5000, random_state=42)

    return df, aqi_col


def render_map(df: pd.DataFrame):

    st.title("🗺️ VayuDrishti – Live AQI GIS Explorer")

    # -----------------------------
    # SIDEBAR
    # -----------------------------
    st.sidebar.header("🎛️ GIS Filters")

    zones = df[ZONE_COL].dropna().unique().tolist() if ZONE_COL in df.columns else []
    selected_zone = st.sidebar.selectbox("Select Zone", ["All"] + zones)

    selected_hour = st.sidebar.slider("Select Hour", 0, 23, 12)

    show_heatmap = st.sidebar.toggle("Heatmap Layer", value=True)
    show_points = st.sidebar.toggle("Point Layer", value=True)

    # -----------------------------
    # PREPROCESS (FAST)
    # -----------------------------
    filtered, aqi_col = preprocess(df, selected_zone, selected_hour)

    # -----------------------------
    # BASE MAP
    # -----------------------------
    m = folium.Map(
        location=[30.3165, 78.0322],
        zoom_start=11,
        tiles="CartoDB positron"
    )

    # -----------------------------
    # HEATMAP (OPTIMIZED)
    # -----------------------------
    if show_heatmap and aqi_col in filtered.columns:

        heat_df = filtered[[LAT_COL, LON_COL, aqi_col]].dropna()

        # reduce heatmap points if too many
        if len(heat_df) > 5000:
            heat_df = heat_df.sample(5000, random_state=42)

        heat_data = heat_df.values.tolist()

        HeatMap(
            heat_data,
            radius=15,
            blur=10
        ).add_to(m)

    # -----------------------------
    # POINTS (FAST LOOP)
    # -----------------------------
    if show_points:

        for row in filtered.itertuples(index=False):

            aqi = getattr(row, aqi_col, 0)

            popup = f"""
            <div style="width:250px">
                <h4>📍 {getattr(row, ZONE_COL, 'Zone')}</h4>
                <b>AQI:</b> {aqi}<br>
                <b>PM2.5:</b> {getattr(row, 'pm25', 'N/A')}<br>
                <b>PM10:</b> {getattr(row, 'pm10', 'N/A')}<br>
                <b>Time:</b> {getattr(row, 'datetime', 'N/A')}
            </div>
            """

            folium.CircleMarker(
                location=[getattr(row, LAT_COL), getattr(row, LON_COL)],
                radius=4,
                color=get_color(aqi),
                fill=True,
                fill_opacity=0.8,
                popup=folium.Popup(popup, max_width=300),
                tooltip=f"AQI: {aqi}"
            ).add_to(m)

    # -----------------------------
    # RENDER MAP
    # -----------------------------
    st.subheader("🌍 Live Interactive Map")
    st_folium(m, height=650, use_container_width=True)

    # -----------------------------
    # DATA VIEW (LIMITED FOR SPEED)
    # -----------------------------
    st.subheader("📊 Live Data (Filtered View)")

    st.dataframe(
        filtered.sort_values(aqi_col, ascending=False).head(1000),
        use_container_width=True
    )