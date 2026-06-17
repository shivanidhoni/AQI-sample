import streamlit as st
import os
import sys
import pandas as pd

# Add project root to Python path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

# GIS Configuration
from gis_module.config import zone_coords

# Agent Imports
from agents.collector import AQICollectorAgent
from agents.analysis import AQIAnalyzerAgent
from agents.estimator import AQIEstimatorAgent
from agents.explanation import AQIExplanationAgent


def render_aqiagents(df: pd.DataFrame):

    st.title("🤖 Autonomous AQI Multi-Agent System")
    st.caption("Multi-Agent workflow for AQI collection, analysis, estimation and explanation.")

    # ==================================================
    # ZONE MERGING (DATASET + CONFIG)
    # ==================================================
    dataset_zones = df["zone"].dropna().unique().tolist() if "zone" in df.columns else []
    config_zones = list(zone_coords.keys())

    available_zones = sorted(set(dataset_zones + config_zones))

    zone = st.selectbox(
        "Select Zone",
        available_zones
    )

    if st.button("Run AQI Agents", type="primary"):

        # ==================================================
        # SAFETY CHECK
        # ==================================================
        if zone not in zone_coords:
            st.error(f"Coordinates not defined for zone: {zone}")
            st.stop()

        lat, lon = zone_coords[zone]

        collector = AQICollectorAgent()
        analyzer = AQIAnalyzerAgent()
        estimator = AQIEstimatorAgent()
        explainer = AQIExplanationAgent()

        with st.status("Running Multi-Agent Pipeline...", expanded=True) as status:

            st.write("🛰️ Collector Agent fetching live AQI data...")

            payload = collector.execute_ingestion_cycle(lat, lon)

            if payload is None:
                status.update(label="Failed to collect AQI data", state="error")
                st.error("Could not fetch AQI data.")
                return

            telemetry = payload.to_dict()

            # ✅ TIME DISPLAY ADDED HERE (correct place)
            timestamp = telemetry.get("timestamp")
            if timestamp:
                st.caption(f"🕒 Last Updated: {timestamp}")

            st.write("📐 Estimator Agent calculating AQI...")
            estimation_output = estimator.execute_estimation_cycle(telemetry)

            st.write("🧬 Analyzer Agent detecting anomalies...")
            diagnostic_report = analyzer.execute_diagnostic_cycle(telemetry)

            st.write("📝 Explanation Agent generating report...")
            narrative = explainer.execute_explanation_cycle(
                zone_name=zone,
                estimation_payload=estimation_output,
                diagnostic_logs=diagnostic_report.anomaly_logs
            )

            status.update(label="Pipeline Completed", state="complete")

        st.divider()

        col1, col2 = st.columns([1, 2])

        with col1:

            st.metric(
                "AQI",
                estimation_output["scalar_aqi"],
                delta=f"Driver: {estimation_output['dominant_driver']}"
            )

            st.subheader(estimation_output["category_label"])

            if diagnostic_report.is_anomaly_detected:
                st.error(f"Primary Contributor: {diagnostic_report.primary_contributor}")
            else:
                st.success("No anomaly detected")

        with col2:
            st.markdown(narrative)

        with st.expander("Agent Logs"):

            st.json({
                "collector": telemetry,
                "estimator": estimation_output,
                "analyzer": {
                    "is_anomaly_detected": diagnostic_report.is_anomaly_detected,
                    "primary_contributor": diagnostic_report.primary_contributor,
                    "severity": diagnostic_report.severity_contribution_pct,
                    "anomalies": diagnostic_report.anomaly_logs,
                }
            })