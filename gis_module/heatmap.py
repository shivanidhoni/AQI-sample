from folium.plugins import HeatMap, MarkerCluster
import folium
import numpy as np

from gis_module.config import LAT_COL, LON_COL, ZONE_COL, HEATMAP_RADIUS, HEATMAP_BLUR


# ==============================
# AQI COLOR SYSTEM (IMPORTANT)
# ==============================
def get_aqi_color(aqi):
    if aqi <= 50:
        return "#00E400"   # Good
    elif aqi <= 100:
        return "#FFFF00"   # Moderate
    elif aqi <= 150:
        return "#FF7E00"   # Unhealthy for sensitive
    elif aqi <= 200:
        return "#FF0000"   # Unhealthy
    elif aqi <= 300:
        return "#8F3F97"   # Very Unhealthy
    return "#7E0023"       # Hazardous


def get_aqi_weight(aqi):
    """
    Makes heatmap smarter (pollution intensity boost)
    """
    return np.log1p(float(aqi)) if aqi is not None else 1


# ==============================
# MAIN FUNCTION
# ==============================
def add_heatmap(m, df, aqi_col=None):

    df = df.dropna(subset=[LAT_COL, LON_COL])

    # =========================
    # 1. INTELLIGENT HEATMAP
    # =========================
    heat_data = []

    if aqi_col and aqi_col in df.columns:
        for _, row in df.iterrows():
            heat_data.append([
                row[LAT_COL],
                row[LON_COL],
                get_aqi_weight(row[aqi_col])
            ])
    else:
        heat_data = df[[LAT_COL, LON_COL]].values.tolist()

    HeatMap(
        heat_data,
        radius=HEATMAP_RADIUS + 5,   # 🔥 more visible impact
        blur=HEATMAP_BLUR,
        max_zoom=12,
        min_opacity=0.4
    ).add_to(m)


    # =========================
    # 2. SMART MARKERS (CLUSTERED)
    # =========================
    cluster = MarkerCluster(name="AQI Zones").add_to(m)

    if ZONE_COL in df.columns and aqi_col in df.columns:

        for _, row in df.iterrows():

            aqi = row[aqi_col]

            popup_html = f"""
            <div style="width:220px">
                <h4>🌍 {row[ZONE_COL]}</h4>
                <hr>
                <b>☁ AQI:</b> {aqi}<br>
                <b>📍 Lat:</b> {row[LAT_COL]:.4f}<br>
                <b>📍 Lon:</b> {row[LON_COL]:.4f}<br>
                <b>🔥 Status:</b> 
                <span style="color:{get_aqi_color(aqi)}; font-weight:bold;">
                    {"Good" if aqi<=50 else "Moderate" if aqi<=100 else "Unhealthy"}
                </span>
            </div>
            """

            folium.CircleMarker(
                location=[row[LAT_COL], row[LON_COL]],

                radius=max(5, min(aqi / 15, 18)),  # dynamic sizing

                color=get_aqi_color(aqi),
                fill=True,
                fill_color=get_aqi_color(aqi),
                fill_opacity=0.75,

                popup=folium.Popup(popup_html, max_width=300),

                tooltip=f"{row[ZONE_COL]} | AQI: {aqi}"
            ).add_to(cluster)

    # =========================
    # 3. LAYER CONTROL (IMPORTANT)
    # =========================
    folium.LayerControl().add_to(m)

    return m