import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from gis_module.preprocessing import clean_data
from utils.data_loader import load_data  # <--- Linked to your function

# 1. High-Performance Data Loading
@st.cache_data
def get_ready_data():
    """Fetches, cleans, and prepares the dataset for analysis."""
    raw_df = load_data() 
    df = clean_data(raw_df)
    df["datetime"] = pd.to_datetime(df["datetime"])
    # Ensure hour/day columns exist for the charts
    df["hour"] = df["datetime"].dt.hour
    return df

def render_analytics(df):
    # Page Config (Must be first Streamlit command if not set in main)
    # st.set_page_config(page_title="VayuDrishti Analytics", layout="wide")

   

    # --- Sidebar Configuration ---
    st.sidebar.header("🛠 Analytics Configuration")
    
    # Zone Filter
    all_zones = ["Global (All Zones)"] + sorted(df["zone"].unique().tolist())
    selected_zone = st.sidebar.selectbox("Geographic Focus", all_zones)
    
    # Parameter Multi-select
    available_params = [
        "eu_aqi", "us_aqi", "pm25", "pm10", "co", "no2", "so2", "o3", 
        "traffic_flow_speed", "traffic_congestion", "wind_speed", 
        "humidity", "aerosol"
    ]
    selected_params = st.sidebar.multiselect(
        "Analysis Parameters",
        options=available_params,
        default=["eu_aqi", "pm25", "pm10", "no2"]
    )

    # Date Range Filter
    min_date = df["datetime"].min().date()
    max_date = df["datetime"].max().date()
    date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])

    # --- Data Processing ---
    # Filter by Zone
    if selected_zone == "Global (All Zones)":
        mask = (df["datetime"].dt.date >= date_range[0]) & (df["datetime"].dt.date <= date_range[1])
        plot_df = df[mask]
    else:
        mask = (df["zone"] == selected_zone) & (df["datetime"].dt.date >= date_range[0]) & (df["datetime"].dt.date <= date_range[1])
        plot_df = df[mask]

    # --- UI Header ---
    st.title("📊 VayuDrishti | Deep Analytics")
    st.info(f"Viewing data for **{selected_zone}** from **{date_range[0]}** to **{date_range[1]}**")

    # --- 1. Top Level KPIs ---
    if selected_params:
        st.subheader("📌 Average Concentrations")
        kpi_cols = st.columns(len(selected_params[:6]))
        for i, p in enumerate(selected_params[:6]):
            avg_val = plot_df[p].mean()
            kpi_cols[i].metric(label=p.replace("_", " ").upper(), value=f"{avg_val:.2f}")
    
    st.divider()

    # --- 2. Interactive Time-Series ---
    st.subheader("📈 Environmental Trend Analysis")
    if selected_params:
        # Resample to Hourly to prevent visual clutter
        ts_df = plot_df.set_index("datetime").resample("h")[selected_params].mean().reset_index()
        
        fig_ts = px.line(
            ts_df, x="datetime", y=selected_params,
            template="plotly_dark",
            labels={"value": "Level", "datetime": "Time"},
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_ts.update_layout(
            hovermode="x unified",
            xaxis_rangeslider_visible=True, # Pro-feature
            legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1)
        )
        st.plotly_chart(fig_ts, use_container_width=True)

    # --- 3. Patterns & Correlations ---
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("🕒 Diurnal (Hourly) Cycle")
        if selected_params:
            focus_p = st.selectbox("Select parameter for hourly breakdown:", selected_params)
            h_df = plot_df.groupby("hour")[focus_p].mean().reset_index()
            fig_h = px.area(h_df, x="hour", y=focus_p, color_discrete_sequence=["#00d4ff"])
            st.plotly_chart(fig_h, use_container_width=True)

    with col_b:
        st.subheader("🔗 Relationship Heatmap")
        if len(selected_params) > 1:
            fig_corr = px.imshow(
                plot_df[selected_params].corr(),
                text_auto=".2f",
                color_continuous_scale="RdBu_r"
            )
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.write("Add more parameters to see correlation.")

    # --- 4. Comparative Bar Chart ---
    st.divider()
    st.subheader("🌍 Zone-wise Comparison")
    if selected_params:
        comp_p = st.selectbox("Rank Zones by:", selected_params)
        rank_df = df.groupby("zone")[comp_p].mean().sort_values().reset_index()
        fig_rank = px.bar(rank_df, x=comp_p, y="zone", orientation='h', color=comp_p, color_continuous_scale="Plasma")
        st.plotly_chart(fig_rank, use_container_width=True)

# Run page
if __name__ == "__main__":
    render_analytics()