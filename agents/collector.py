import logging
import requests
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelemetryPayload:
    def __init__(self, zone_data: Dict[str, Any]):
        self.pm25 = float(zone_data.get("pm2_5") or 0.0)
        self.pm10 = float(zone_data.get("pm10") or 0.0)
        self.no2 = float(zone_data.get("no2") or 0.0)
        self.co = float(zone_data.get("co") or 0.0)
        self.o3 = float(zone_data.get("o3") or 0.0)

        # ✅ NEW: timestamp field
        self.timestamp = zone_data.get("time")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pm2_5": self.pm25,
            "pm10": self.pm10,
            "no2": self.no2,
            "co": self.co,
            "o3": self.o3,
            "timestamp": self.timestamp  # ✅ added here
        }


class AQICollectorAgent:
    def __init__(self, timeout_seconds: int = 12):
        self.base_endpoint = "https://air-quality-api.open-meteo.com/v1/air-quality"
        self.timeout = timeout_seconds

    def execute_ingestion_cycle(
        self,
        lat: float,
        lon: float
    ) -> Optional[TelemetryPayload]:

        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "pm10,pm2_5,nitrogen_dioxide,carbon_monoxide,ozone",
        }

        try:
            response = requests.get(
                self.base_endpoint,
                params=params,
                timeout=self.timeout,
            )

            response.raise_for_status()

            data = response.json()
            current = data.get("current")

            if not current:
                logger.error("No 'current' data found in API response.")
                return None

            return TelemetryPayload(
                {
                    "pm2_5": current.get("pm2_5"),
                    "pm10": current.get("pm10"),
                    "no2": current.get("nitrogen_dioxide"),
                    "co": current.get("carbon_monoxide"),
                    "o3": current.get("ozone"),

                    # ✅ IMPORTANT: time from API
                    "time": current.get("time")
                }
            )

        except requests.exceptions.Timeout:
            logger.error("Request timed out.")
            return None

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            return None

        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return None