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
    # Core zones
    "ISBT": (30.288, 78.040),
    "Clock Tower": (30.325, 78.043),
    "Rajpur Road": (30.360, 78.070),
    "Prem Nagar": (30.340, 77.980),
    "Clement Town": (30.270, 78.020),

    # Added AQI Agent zones (expanded coverage)
    "Ballupur": (30.316, 78.013),
    "Saharanpur Chowk": (30.321, 78.028),
    "Nehru Colony": (30.291, 78.056),
    "Jakhan": (30.366, 78.079),
    "Dalanwala": (30.316, 78.050),
    "Patel Nagar": (30.304, 78.015),
    "Race Course": (30.310, 78.035),
    "Kaulagarh": (30.350, 78.020),
    "Vasant Vihar": (30.330, 78.015),
    "Mussoorie Diversion": (30.385, 78.090),
    "Raipur": (30.320, 78.110),
    "Mothrowala": (30.250, 78.000),
    "Shimla Bypass": (30.300, 77.970),
    "Bindal": (30.330, 78.030),
    "Harrawala": (30.220, 78.010),

    # NEW EXTENDED ZONES (for richer AQI agent coverage)
    "Cantonment": (30.340, 78.060),
    "Sahastradhara": (30.400, 78.095),
    "GMS Road": (30.315, 78.020),
    "Subhash Nagar": (30.290, 78.045),
    "Ajabpur Kalan": (30.295, 78.070),
    "Panditwari": (30.360, 78.085),
    "Badowala": (30.260, 78.020),
    "Chakrata Road": (30.310, 78.005),
    "Turner Road": (30.330, 78.048),
    "Rispana": (30.275, 78.030),
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
