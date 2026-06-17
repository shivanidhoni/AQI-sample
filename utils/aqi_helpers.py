# utils/aqihelpers.py

"""
VayuDrishti - AQI Helper Utilities
Used in:
- Report Generator
- Alert System
- GIS Map
"""

# =============================================================================
# AQI CATEGORY
# =============================================================================
def aqi_category(aqi):
    """
    Returns AQI category based on AQI value.
    """

    try:
        aqi = float(aqi)
    except (TypeError, ValueError):
        return "Unknown"

    if aqi <= 50:
        return "Good"

    if aqi <= 100:
        return "Moderate"

    if aqi <= 150:
        return "Unhealthy for Sensitive Groups"

    if aqi <= 200:
        return "Unhealthy"

    if aqi <= 300:
        return "Very Unhealthy"

    return "Hazardous"


# =============================================================================
# AQI COLOR (for charts / UI)
# =============================================================================
def aqi_color(aqi):
    """
    Returns color code based on AQI level.
    """

    try:
        aqi = float(aqi)
    except (TypeError, ValueError):
        return "#94a3b8"

    if aqi <= 50:
        return "#16a34a"   # green
    if aqi <= 100:
        return "#ca8a04"   # yellow
    if aqi <= 150:
        return "#ea580c"   # orange
    if aqi <= 200:
        return "#dc2626"   # red
    if aqi <= 300:
        return "#9333ea"   # purple

    return "#7f1d1d"       # maroon (hazardous)


# =============================================================================
# BACKGROUND COLOR (cards / UI blocks)
# =============================================================================
def aqi_bg_color(aqi):
    """
    Returns background color for UI cards.
    """

    try:
        aqi = float(aqi)
    except (TypeError, ValueError):
        return "#f8fafc"

    if aqi <= 50:
        return "#f0fdf4"
    if aqi <= 100:
        return "#fefce8"
    if aqi <= 150:
        return "#fff7ed"
    if aqi <= 200:
        return "#fef2f2"
    if aqi <= 300:
        return "#faf5ff"

    return "#fdf2f8"


# =============================================================================
# HEALTH MESSAGE (used in alerts + report)
# =============================================================================
def health_message(aqi):
    """
    Returns health advisory based on AQI level.
    """

    try:
        aqi = float(aqi)
    except (TypeError, ValueError):
        return "No data available."

    if aqi <= 50:
        return "Air quality is good. Safe for outdoor activities."

    if aqi <= 100:
        return "Air is acceptable. Sensitive people should limit long exposure."

    if aqi <= 150:
        return "Sensitive groups may face health issues."

    if aqi <= 200:
        return "Everyone may experience health effects. Limit outdoor activity."

    if aqi <= 300:
        return "Serious health risk. Avoid outdoor exposure."

    return "Emergency condition. Stay indoors and avoid all outdoor activity."