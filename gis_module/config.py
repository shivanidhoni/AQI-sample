# gis_module/config.py

import pandas as pd

# ==================================================
# DATA PATH
# ==================================================
DATA_PATH = "data/dehradun_master_dataset.csv"

# ==================================================
# COLUMN NAMES
# ==================================================
LAT_COL = "latitude"
LON_COL = "longitude"
ZONE_COL = "zone"
# ==================================================
# ZONE COORDINATES (RESTORE FOR AGENTS + MAP)
# ==================================================
zone_coords = {
    "Max Hospital": (30.3255, 78.0421),
    "Rajpur": (30.3820, 78.0850),
    "Clock Tower": (30.3256, 78.0432),
    "ISBT": (30.2872, 78.0535),
}

# ==================================================
# AQI COLUMN DETECTION
# ==================================================
AQI_CANDIDATES = [
    "aqi",
    "AQI",
    "eu_aqi",
    "pm25_aqi",
    "air_quality_index"
]


def detect_aqi_column(df: pd.DataFrame):
    """
    Smart AQI column detection (robust + safe)
    """

    for col in AQI_CANDIDATES:
        if col in df.columns:
            return col

    # fallback: try partial match
    for col in df.columns:
        if "aqi" in col.lower():
            return col

    raise ValueError(
        f"❌ No AQI column found. Tried: {AQI_CANDIDATES}\n"
        f"Available columns: {list(df.columns)}"
    )


# ==================================================
# AQI INTELLIGENCE SYSTEM (NEW ADDITION)
# ==================================================

AQI_LEVELS = [
    (0, 50, "Good", "#00E400"),
    (51, 100, "Moderate", "#FFFF00"),
    (101, 150, "Unhealthy for Sensitive", "#FF7E00"),
    (151, 200, "Unhealthy", "#FF0000"),
    (201, 300, "Very Unhealthy", "#8F3F97"),
    (301, 500, "Hazardous", "#7E0023"),
]


def get_aqi_info(aqi: float):
    """
    Returns full AQI intelligence:
    - category
    - color
    - risk level
    """

    for low, high, label, color in AQI_LEVELS:
        if low <= aqi <= high:
            return {
                "label": label,
                "color": color,
                "level": risk_score(label)
            }

    return {
        "label": "Unknown",
        "color": "#808080",
        "level": 0
    }


def risk_score(label: str):
    """
    Converts AQI label → numeric severity score
    Useful for heatmaps + ML features
    """

    mapping = {
        "Good": 1,
        "Moderate": 2,
        "Unhealthy for Sensitive": 3,
        "Unhealthy": 4,
        "Very Unhealthy": 5,
        "Hazardous": 6
    }

    return mapping.get(label, 0)


# ==================================================
# MAP SETTINGS
# ==================================================
MAP_START_LOCATION = [30.3165, 78.0322]  # Dehradun
MAP_ZOOM = 11

# ==================================================
# HEATMAP SETTINGS (ENHANCED)
# ==================================================
HEATMAP_RADIUS = 18   # increased for visibility
HEATMAP_BLUR = 12

# ==================================================
# ZONE INTELLIGENCE SETTINGS (NEW)
# ==================================================
TOP_ZONE_LIMIT = 10
SAFE_ZONE_LIMIT = 5
