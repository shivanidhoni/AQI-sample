import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Analytics",
    page_icon="📈",
    layout="wide"
)

st.title("📈 VayuDrishti - Air Quality Analytics")

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

st.sidebar.header("🔍 Analytics Filters")

selected_zones = st.sidebar.multiselect(
    "Select Zones",
    sorted(df["zone"].unique()),
    default=sorted(df["zone"].unique())
)

selected_pollutant = st.sidebar.selectbox(
    "Select Pollutant",
    [
        "eu_aqi",
        "us_aqi",
        "pm25",
        "pm10",
        "co",
        "no2",
        "so2",
        "o3"
    ]
)

# Date Filter
start_date = df["datetime"].min().date()
end_date = df["datetime"].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(start_date, end_date)
)

# ==================================================
# FILTER DATA
# ==================================================

filtered = df[df["zone"].isin(selected_zones)]

if len(date_range) == 2:
    filtered = filtered[
        (filtered["datetime"].dt.date >= date_range[0]) &
        (filtered["datetime"].dt.date <= date_range[1])
    ]

# ==================================================
# KPI CARDS
# ==================================================

st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Average EU AQI",
    f"{filtered['eu_aqi'].mean():.1f}"
)

col2.metric(
    "Average PM2.5",
    f"{filtered['pm25'].mean():.1f}"
)

col3.metric(
    "Average PM10",
    f"{filtered['pm10'].mean():.1f}"
)

col4.metric(
    "Average Traffic",
    f"{filtered['traffic_congestion'].mean():.1f}"
)

st.divider()

# ==================================================
# TREND ANALYSIS
# ==================================================

st.subheader(
    f"📈 {selected_pollutant.upper()} Trend Analysis"
)

trend = (
    filtered.groupby(
        [pd.Grouper(key="datetime", freq="D"), "zone"]
    )[selected_pollutant]
    .mean()
    .reset_index()
)

fig = px.line(
    trend,
    x="datetime",
    y=selected_pollutant,
    color="zone",
    markers=True,
    title=f"{selected_pollutant.upper()} Trend by Zone",
    template="plotly_dark"
)

fig.update_layout(
    height=500,
    hovermode="x unified"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()

# ==================================================
# TRAFFIC VS AQI
# ==================================================

st.subheader("🚦 Traffic Congestion vs EU AQI")

scatter = px.scatter(
    filtered,
    x="traffic_congestion",
    y="eu_aqi",
    color="zone",
    size="pm25",
    hover_data=[
        "pm10",
        "co",
        "no2",
        "so2",
        "o3"
    ],
    title="Traffic Impact on Air Quality",
    template="plotly_dark"
)

scatter.update_layout(height=550)

st.plotly_chart(
    scatter,
    use_container_width=True
)

st.divider()

# ==================================================
# HEATMAP
# ==================================================

st.subheader("🔥 AQI Heatmap (Weekday vs Hour)")

weekday_labels = {
    0: "Mon",
    1: "Tue",
    2: "Wed",
    3: "Thu",
    4: "Fri",
    5: "Sat",
    6: "Sun"
}

pivot = filtered.pivot_table(
    values="eu_aqi",
    index="weekday",
    columns="hour",
    aggfunc="mean"
)

pivot.index = [
    weekday_labels.get(i, i)
    for i in pivot.index
]

heatmap = go.Figure(
    data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale="RdYlGn_r"
    )
)

heatmap.update_layout(
    title="Pollution Pattern by Hour and Weekday",
    template="plotly_dark",
    height=500,
    xaxis_title="Hour",
    yaxis_title="Weekday"
)

st.plotly_chart(
    heatmap,
    use_container_width=True
)

st.divider()

# ==================================================
# RADAR CHART
# ==================================================

st.subheader("🕸️ Zone Pollutant Comparison")

radar_data = (
    filtered.groupby("zone")[
        ["pm25", "pm10", "co", "no2", "so2", "o3"]
    ]
    .mean()
)

fig_radar = go.Figure()

for zone in radar_data.index:

    fig_radar.add_trace(
        go.Scatterpolar(
            r=radar_data.loc[zone].values,
            theta=radar_data.columns,
            fill="toself",
            name=zone
        )
    )

fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True
        )
    ),
    showlegend=True,
    template="plotly_dark",
    height=600
)

st.plotly_chart(
    fig_radar,
    use_container_width=True
)

st.divider()

# ==================================================
# TOP POLLUTED ZONES
# ==================================================

st.subheader("🏭 Top Polluted Zones")

zone_rank = (
    filtered.groupby("zone")["eu_aqi"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

bar = px.bar(
    zone_rank,
    x="zone",
    y="eu_aqi",
    color="eu_aqi",
    title="Average EU AQI by Zone",
    template="plotly_dark"
)

st.plotly_chart(
    bar,
    use_container_width=True
)

st.divider()

# ==================================================
# DATA TABLE
# ==================================================

st.subheader("📋 Filtered Dataset")

st.dataframe(
    filtered,
    use_container_width=True,
    height=400
)