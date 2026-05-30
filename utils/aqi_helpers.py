def get_aqi_category(aqi):
    """
    Returns the AQI category based on the AQI value.

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