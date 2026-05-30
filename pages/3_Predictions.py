import streamlit as st
import pandas as pd
import plotly.express as px

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="AQI Insights",
    page_icon="📊",
    layout="wide"
)

st.title("📊 VayuDrishti - AQI Insights")

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
# SIDEBAR FILTER
# ==================================================

st.sidebar.header("🔍 Filters")

selected_zones = st.sidebar.multiselect(
    "Select Zones",
    sorted(df["zone"].unique()),
    default=sorted(df["zone"].unique())
)

filtered = df[df["zone"].isin(selected_zones)]

# ==================================================
# KPI CARDS
# ==================================================

st.subheader("📈 AQI Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Average EU AQI",
    f"{filtered['eu_aqi'].mean():.1f}"
)

col2.metric(
    "Maximum AQI",
    f"{filtered['eu_aqi'].max():.1f}"
)

col3.metric(
    "Minimum AQI",
    f"{filtered['eu_aqi'].min():.1f}"
)

col4.metric(
    "Zones",
    filtered["zone"].nunique()
)

st.divider()

# ==================================================
# ZONE AQI RANKING
# ==================================================

zone_avg = (
    filtered.groupby("zone")["eu_aqi"]
    .mean()
    .sort_values(ascending=False)
)

st.subheader("🏭 Average AQI by Zone")

fig = px.bar(
    x=zone_avg.index,
    y=zone_avg.values,
    color=zone_avg.values,
    labels={
        "x": "Zone",
        "y": "Average EU AQI"
    },
    template="plotly_dark",
    title="Zone-wise Average AQI"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()

# ==================================================
# TOP 5 POLLUTED ZONES
# ==================================================

st.subheader("🔴 Top 5 Polluted Zones")

top5 = (
    zone_avg.head(5)
    .reset_index()
)

top5.columns = [
    "Zone",
    "Average AQI"
]

st.dataframe(
    top5,
    use_container_width=True
)

# ==================================================
# TOP 5 CLEANEST ZONES
# ==================================================

st.subheader("🟢 Top 5 Cleanest Zones")

clean5 = (
    zone_avg.tail(5)
    .sort_values()
    .reset_index()
)

clean5.columns = [
    "Zone",
    "Average AQI"
]

st.dataframe(
    clean5,
    use_container_width=True
)

st.divider()

# ==================================================
# AQI DISTRIBUTION
# ==================================================

st.subheader("📉 AQI Distribution")

hist = px.histogram(
    filtered,
    x="eu_aqi",
    nbins=30,
    title="Distribution of EU AQI Values",
    template="plotly_dark"
)

st.plotly_chart(
    hist,
    use_container_width=True
)

# ==================================================
# ZONE SUMMARY TABLE
# ==================================================

st.subheader("📋 Zone Summary")

summary = (
    filtered.groupby("zone")
    .agg({
        "eu_aqi": "mean",
        "pm25": "mean",
        "pm10": "mean",
        "traffic_congestion": "mean"
    })
    .round(2)
    .reset_index()
)

st.dataframe(
    summary,
    use_container_width=True
)