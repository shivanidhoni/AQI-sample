import streamlit as st
import pandas as pd

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="VayuDrishti",
    page_icon="🌬️",
    layout="wide"
)

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
# HOME PAGE
# ==================================================

st.title("🌬️ VayuDrishti - Dehradun Air Quality Monitoring System")

st.markdown("""
### Welcome to VayuDrishti

This dashboard provides:

- 🗺️ GIS AQI Mapping
- 📈 Air Quality Analytics
- 📊 AQI Insights
- 🚦 Traffic vs Pollution Analysis
- 💨 Pollutant Monitoring
- 🌍 Zone-wise Air Quality Assessment
""")

# ==================================================
# KPI CARDS
# ==================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Records",
    f"{len(df):,}"
)

col2.metric(
    "Zones",
    df["zone"].nunique()
)

col3.metric(
    "Average EU AQI",
    f"{df['eu_aqi'].mean():.1f}"
)

col4.metric(
    "Average PM2.5",
    f"{df['pm25'].mean():.1f}"
)

st.divider()

# ==================================================
# DATA PREVIEW
# ==================================================

st.subheader("📋 Dataset Preview")

st.dataframe(
    df.head(20),
    use_container_width=True
)

st.divider()

# ==================================================
# DATASET INFORMATION
# ==================================================

st.subheader("📊 Dataset Information")

info = pd.DataFrame({
    "Metric": [
        "Rows",
        "Columns",
        "Date Range Start",
        "Date Range End"
    ],
    "Value": [
        len(df),
        len(df.columns),
        str(df["datetime"].min()),
        str(df["datetime"].max())
    ]
})

st.dataframe(
    info,
    use_container_width=True
)