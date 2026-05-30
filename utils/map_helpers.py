"""
Map Helper Functions
VayuDrishti - Dehradun Air Quality Monitoring System
"""

# ==================================================
# AQI COLOR SCALE
# ==================================================

def get_color(aqi):
    """
    Returns AQI color based on AQI value.

    Parameters:
        aqi (float): AQI value

    Returns:
        str: Hex color code
    """

    if aqi <= 50:
        return "#00E400"      # Green

    if aqi <= 100:
        return "#FFFF00"      # Yellow

    if aqi <= 150:
        return "#FF7E00"      # Orange

    if aqi <= 200:
        return "#FF0000"      # Red

    if aqi <= 300:
        return "#8F3F97"      # Purple

    return "#7E0023"          # Maroon


# ==================================================
# AQI CATEGORY
# ==================================================

def get_aqi_category(aqi):
    """
    Returns AQI category.

    Parameters:
        aqi (float): AQI value

    Returns:
        str: AQI category
    """

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


# ==================================================
# MARKER SIZE
# ==================================================

def get_marker_radius(aqi):
    """
    Returns marker size according to AQI.

    Parameters:
        aqi (float)

    Returns:
        int
    """

    return max(8, min(aqi / 10, 25))


# ==================================================
# AQI LEGEND HTML
# ==================================================

def get_aqi_legend():
    """
    Returns AQI legend HTML for Folium map.
    """

    return """
    <div style="
        position: fixed;
        bottom: 40px;
        left: 40px;
        width: 220px;
        background-color: white;
        padding: 12px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px grey;
        z-index:9999;
        font-size:14px;
    ">

    <b>🌍 AQI Legend</b><br><br>

    <span style="color:#00E400;">●</span> Good (0–50)<br>
    <span style="color:#FFFF00;">●</span> Moderate (51–100)<br>
    <span style="color:#FF7E00;">●</span> Sensitive (101–150)<br>
    <span style="color:#FF0000;">●</span> Unhealthy (151–200)<br>
    <span style="color:#8F3F97;">●</span> Very Unhealthy (201–300)<br>
    <span style="color:#7E0023;">●</span> Hazardous (300+)

    </div>
    """