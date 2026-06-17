import streamlit as st
import pandas as pd
import os

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(
    page_title="VayuDrishti",
    page_icon="🌬️",
    layout="wide"
)

# =====================================
# CUSTOM CSS
# =====================================
st.markdown("""
<style>

.stApp{
    background: linear-gradient(135deg,#eef6ff,#ffffff);
}

/* Header */
.main-title{
    text-align:center;
    font-size:48px;
    font-weight:800;
    color:#0F4C81;
    margin-bottom:0;
}

.sub-title{
    text-align:center;
    font-size:18px;
    color:#555555;
    margin-top:-10px;
    margin-bottom:25px;
}

/* Cards */
.card{
    background:white;
    padding:25px;
    border-radius:20px;
    text-align:center;
    box-shadow:0px 4px 15px rgba(0,0,0,0.12);
    transition:0.3s;
}

.card:hover{
    transform:translateY(-4px);
}

/* AQI Status */
.status-box{
    background:white;
    padding:15px;
    border-radius:15px;
    text-align:center;
    font-size:22px;
    font-weight:600;
    box-shadow:0px 4px 12px rgba(0,0,0,0.08);
    margin-top:10px;
    margin-bottom:20px;
}

/* Section title */
.section-title{
    font-size:26px;
    font-weight:700;
    color:#0F4C81;
    margin-top:20px;
    margin-bottom:10px;
}

/* Dropdown */
div[data-baseweb="select"] > div{
    border-radius:12px;
}

/* Dataframe */
[data-testid="stDataFrame"]{
    border-radius:15px;
}

</style>
""", unsafe_allow_html=True)

# =====================================
# LOAD DATA
# =====================================
@st.cache_data
def load_data():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))

        file_path = os.path.join(
            base_dir,
            "dehradun_master_dataset_cleaned.xlsx"
        )

        df = pd.read_excel(file_path)

        df.columns = df.columns.str.strip()

        if "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(
                df["datetime"],
                errors="coerce"
            )

        if "zone" in df.columns:
            df["zone"] = (
                df["zone"]
                .astype(str)
                .str.strip()
            )

        return df

    except Exception as e:
        st.error(f"❌ Error loading dataset: {e}")
        return pd.DataFrame()

# =====================================
# LOAD DATASET
# =====================================
df = load_data()

if df.empty:
    st.warning("Dataset could not be loaded.")
    st.stop()

# =====================================
# HEADER
# =====================================
st.markdown(
    """
    <div class="main-title">
        🌬️ VayuDrishti
    </div>

    <div class="sub-title">
        Real-Time Zone-wise Air Quality Monitoring Dashboard
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# =====================================
# ZONE SELECTION
# =====================================
zones = sorted(df["zone"].dropna().unique())

selected_zone = st.selectbox(
    "🌍 Select Monitoring Zone",
    zones
)

# =====================================
# FILTER DATA
# =====================================
zone_df = df[df["zone"] == selected_zone].copy()

if zone_df.empty:
    st.warning("No data available for selected zone.")
    st.stop()

zone_df = zone_df.dropna(subset=["datetime"])

latest = (
    zone_df
    .sort_values("datetime", ascending=False)
    .iloc[0]
)

aqi = round(float(latest.get("eu_aqi", 0)), 2)
pm25 = round(float(latest.get("pm25", 0)), 2)

# =====================================
# AQI STATUS
# =====================================
if aqi <= 50:
    status = "🟢 Good"
elif aqi <= 100:
    status = "🟡 Moderate"
elif aqi <= 150:
    status = "🟠 Unhealthy for Sensitive Groups"
elif aqi <= 200:
    status = "🔴 Unhealthy"
else:
    status = "🟣 Very Unhealthy"

# =====================================
# LIVE METRICS
# =====================================
st.success(f"Live Air Quality Data for {selected_zone}")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
        <div class="card">
            <h3>🌫 AQI</h3>
            <h1>{aqi}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="card">
            <h3>💨 PM2.5</h3>
            <h1>{pm25}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

# =====================================
# AQI STATUS BOX
# =====================================
st.markdown(
    f"""
    <div class="status-box">
        Air Quality Status: {status}
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================
# CHART DATA
# =====================================
chart_df = zone_df.sort_values("datetime")

# =====================================
# AQI TREND
# =====================================
st.markdown(
    '<div class="section-title">📈 AQI Trend</div>',
    unsafe_allow_html=True
)

st.line_chart(
    chart_df.set_index("datetime")["eu_aqi"]
)

# =====================================
# PM2.5 TREND
# =====================================
st.markdown(
    '<div class="section-title">💨 PM2.5 Trend</div>',
    unsafe_allow_html=True
)

st.line_chart(
    chart_df.set_index("datetime")["pm25"]
)

# =====================================
# RECENT HISTORY
# =====================================
st.markdown(
    '<div class="section-title">📊 Recent AQI History</div>',
    unsafe_allow_html=True
)

history_df = (
    zone_df[
        ["datetime", "eu_aqi", "pm25"]
    ]
    .sort_values(
        "datetime",
        ascending=False
    )
    .head(20)
)

st.dataframe(
    history_df,
    use_container_width=True
)

# =====================================
# FOOTER
# =====================================
st.divider()

st.markdown(
    """
    <center>
        <b>🌬️ VayuDrishti</b><br>
        AI-Powered Air Quality Monitoring System
    </center>
    """,
    unsafe_allow_html=True
)