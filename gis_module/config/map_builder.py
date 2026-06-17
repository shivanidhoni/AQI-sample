import folium
from folium.plugins import HeatMap, MarkerCluster
from gis_module.config import MAP_START_LOCATION, MAP_ZOOM


def get_color(aqi):
    if aqi <= 50:
        return "green"
    elif aqi <= 100:
        return "yellow"
    elif aqi <= 150:
        return "orange"
    elif aqi <= 200:
        return "red"
    elif aqi <= 300:
        return "purple"
    return "darkred"


def create_base_map():
    return folium.Map(
        location=MAP_START_LOCATION,
        zoom_start=MAP_ZOOM,
        tiles="CartoDB dark_matter"
    )


def add_heatmap(m, df):
    heat_data = df[["latitude", "longitude", "risk_score"]].dropna().values.tolist()
    HeatMap(heat_data, radius=18, blur=12).add_to(m)


def add_zone_markers(m, zone_df):
    cluster = MarkerCluster().add_to(m)

    for _, row in zone_df.iterrows():
        popup = f"""
        <b>Zone:</b> {row['zone']}<br>
        <b>AQI:</b> {row['avg_aqi']:.1f}<br>
        <b>PM2.5:</b> {row['pm25']:.1f}<br>
        <b>PM10:</b> {row['pm10']:.1f}<br>
        <b>Risk:</b> {row['risk_level']}<br>
        """

        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=8 + row["avg_aqi"] / 20,
            color=get_color(row["avg_aqi"]),
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(popup, max_width=300),
            tooltip=f"{row['zone']} ({row['risk_level']})"
        ).add_to(cluster)


def add_top_zones_overlay(m, zone_df):
    top = zone_df.head(5)

    html = "<h4>🔥 Most Polluted Zones</h4><ul>"
    for _, row in top.iterrows():
        html += f"<li>{row['zone']} - AQI {row['avg_aqi']:.1f}</li>"
    html += "</ul>"

    folium.Marker(
        location=MAP_START_LOCATION,
        popup=html,
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)


def save_map(m, filename="city_map.html"):
    m.save(filename)