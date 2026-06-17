import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


class AQIEstimatorAgent:

    def __init__(self):

        self.pm25_breakpoints = [
            (0.0, 12.0, 0.0, 50.0),
            (12.1, 35.4, 51.0, 100.0),
            (35.5, 55.4, 101.0, 150.0),
            (55.5, 150.4, 151.0, 200.0),
            (150.5, 250.4, 201.0, 300.0),
            (250.5, 350.4, 301.0, 400.0),
            (350.5, 500.4, 401.0, 500.0)
        ]

        self.pm10_breakpoints = [
            (0.0, 54.0, 0.0, 50.0),
            (55.0, 154.0, 51.0, 100.0),
            (155.0, 254.0, 101.0, 150.0),
            (255.0, 354.0, 151.0, 200.0),
            (355.0, 424.0, 201.0, 300.0),
            (425.0, 504.0, 301.0, 400.0),
            (505.0, 604.0, 401.0, 500.0)
        ]

    def _interpolate(self, cp: float, breakpoints) -> float:

        for bp_lo, bp_hi, aqi_lo, aqi_hi in breakpoints:

            if bp_lo <= cp <= bp_hi:

                return (
                    ((aqi_hi - aqi_lo) / (bp_hi - bp_lo))
                    * (cp - bp_lo)
                    + aqi_lo
                )

        return 500.0

    def compute_health_category(self, aqi: float) -> Tuple[str, str]:

        if aqi <= 50:
            return (
                "Good",
                "Air quality is satisfactory."
            )

        elif aqi <= 100:
            return (
                "Moderate",
                "Air quality is acceptable."
            )

        elif aqi <= 150:
            return (
                "Unhealthy for Sensitive Groups",
                "Sensitive groups may experience health effects."
            )

        elif aqi <= 200:
            return (
                "Unhealthy",
                "Everyone may begin to experience health effects."
            )

        elif aqi <= 300:
            return (
                "Very Unhealthy",
                "Health alert."
            )

        return (
            "Hazardous",
            "Emergency conditions."
        )

    def execute_estimation_cycle(
        self,
        telemetry_data: Dict[str, float]
    ) -> Dict[str, Any]:

        pm25 = float(telemetry_data.get("pm2_5", 0))
        pm10 = float(telemetry_data.get("pm10", 0))

        pm25_aqi = self._interpolate(pm25, self.pm25_breakpoints)
        pm10_aqi = self._interpolate(pm10, self.pm10_breakpoints)

        final_aqi = round(max(pm25_aqi, pm10_aqi), 1)

        category, advisory = self.compute_health_category(final_aqi)

        return {
            "scalar_aqi": final_aqi,
            "category_label": category,
            "health_advisory": advisory,
            "dominant_driver": (
                "PM2.5"
                if pm25_aqi >= pm10_aqi
                else "PM10"
            )
        }