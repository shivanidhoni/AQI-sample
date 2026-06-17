import pandas as pd
import numpy as np

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Standardize column names
    df.rename(columns={
        "lat": "latitude",
        "long": "longitude",
        "lng": "longitude"
    }, inplace=True)

    # Remove invalid coordinates
    df = df[
        df["latitude"].between(-90, 90) &
        df["longitude"].between(-180, 180)
    ]

    df = df.dropna(subset=["latitude", "longitude", "zone"])

    # Ensure AQI exists
    if "eu_aqi" not in df.columns:
        raise ValueError("Missing AQI column: eu_aqi")

    # AQI category (VERY IMPORTANT for map intelligence)
    def categorize(aqi):
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Unhealthy for Sensitive"
        elif aqi <= 200:
            return "Unhealthy"
        elif aqi <= 300:
            return "Very Unhealthy"
        return "Hazardous"

    df["aqi_category"] = df["eu_aqi"].apply(categorize)

    # Risk score (for heatmaps)
    df["risk_score"] = np.log1p(df["eu_aqi"])

    return df