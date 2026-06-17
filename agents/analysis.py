import logging
from typing import Dict, Any, List, Optional

# Institutional level tracking setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AQIAnalysisAgent")

class DiagnosticReport:
    """
    Encapsulates the structured output of the Analyzer Node.
    Replaces child-like string arrays with explicit metric data matrices.
    """
    def __init__(self):
        self.is_anomaly_detected: bool = False
        self.anomaly_logs: List[Dict[str, Any]] = []
        self.primary_contributor: str = "None"
        self.severity_contribution_pct: float = 0.0

class AQIAnalyzerAgent:
    """
    Autonomous Diagnostic Worker. Analyzes multi-variable environmental telemetry,
    calculates critical parameter deviations, and identifies primary pollution drivers.
    """
    def __init__(self):
        # Industrial Standard Breakpoints (Safe Limits configured as per Central Pollution Control Guidelines)
        self.regulatory_thresholds = {
            "pm2_5": 35.0,  # µg/m³
            "pm10": 80.0,   # µg/m³
            "no2": 80.0,    # µg/m³ (Standard industrial boundary)
            "co": 400.0,    # µg/m³
            "o3": 100.0     # µg/m³
        }
        
        # Environmental Context Knowledge Matrix mapping drivers to architectural origins
        self.source_knowledge_base = {
            "pm2_5": "Fine particulate suspension heavily sourced from vehicle combustion and industrial chimneys.",
            "pm10": "Coarse suspension dust originating from macro-construction activities and road debris pulverization.",
            "no2": "High concentration vehicular emissions, primarily diesel exhaust plumes and structural fuel burning.",
            "co": "Incomplete carbon oxidation caused by high traffic idling congestion or localized open biomass burning.",
            "o3": "Secondary atmospheric compound generated via photochemical reactions under intense heat and sunlight solar rays."
        }

    def execute_diagnostic_cycle(self, telemetry: Dict[str, float]) -> DiagnosticReport:
        """
        Processes real-time telemetry against the configured regulatory rules.
        Calculates maximum variance steps to spot anomalies dynamically.
        """
        logger.info("🔄 Analyzer Agent: Booting analytical validation matrix pipeline...")
        report = DiagnosticReport()
        
        max_deviation_ratio = 0.0
        dominant_driver = "None"
        
        # Iterating systematically across atmospheric matrices
        for pollutant, safe_limit in self.regulatory_thresholds.items():
            current_val = telemetry.get(pollutant, 0.0)
            
            # Mathematical calculation of standard deviation ratios
            deviation_ratio = current_val / safe_limit
            
            if current_val > safe_limit:
                report.is_anomaly_detected = True
                excess_percentage = ((current_val - safe_limit) / safe_limit) * 100
                
                anomaly_entry = {
                    "parameter": pollutant.upper(),
                    "observed_value": current_val,
                    "permissible_limit": safe_limit,
                    "variance_pct": round(excess_percentage, 1),
                    "root_cause_vector": self.source_knowledge_base.get(pollutant)
                }
                report.anomaly_logs.append(anomaly_entry)
                
                # Track down which pollutant crossed the safe limits by the largest margin
                if deviation_ratio > max_deviation_ratio:
                    max_deviation_ratio = deviation_ratio
                    dominant_driver = pollutant.upper()

        # If thresholds are breached, dynamically compute core tracking weights
        if report.is_anomaly_detected:
            report.primary_contributor = dominant_driver
            # Convert deviation metrics to clear architectural importance weights
            total_ratio_sum = sum([telemetry.get(p, 0.0)/lim for p, lim in self.regulatory_thresholds.items()])
            report.severity_contribution_pct = round((max_deviation_ratio / total_ratio_sum) * 100, 1)
            logger.warning(f"⚠️ Anomaly Isolated: Primary driver detected as {dominant_driver}")
        else:
            logger.info("✅ Analyzer Agent: Ingested telemetry vector settles within baseline standard deviations.")
            
        return report