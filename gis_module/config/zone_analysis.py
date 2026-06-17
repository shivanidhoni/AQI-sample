import pandas as pd
import numpy as np
from gis_module.config import ZONE_COL, AQI_COL

def zone_summary(df: pd.DataFrame):
    """
    Advanced zone intelligence report
    """

    grouped = df.groupby(ZONE_COL).agg(
        avg_aqi=(AQI_COL, "mean"),
        max_aqi=(AQI_COL, "max"),
        min_aqi=(AQI_COL, "min"),
        pm25=("pm25", "mean"),
        pm10=("pm10", "mean"),
        records=(AQI_COL, "count")
    ).reset_index()

    # Risk level
    def risk_level(aqi):
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Poor"
        elif aqi <= 200:
            return "Unhealthy"
        return "Severe"

    grouped["risk_level"] = grouped["avg_aqi"].apply(risk_level)

    # Pollution score (for ranking)
    grouped["pollution_score"] = (
        grouped["avg_aqi"] * 0.6 +
        grouped["pm25"] * 0.3 +
        grouped["pm10"] * 0.1
    )

    grouped = grouped.sort_values("pollution_score", ascending=False)

    return grouped


def top_polluted_zones(df, top_n=10):
    summary = zone_summary(df)
    return summary.head(top_n)


def safe_zones(df, top_n=5):
    summary = zone_summary(df)
    return summary.tail(top_n)