import logging
from typing import Dict, Any, List, Optional

# Setting up structural system logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AQIExplanationAgent")

class AQIExplanationAgent:
    """
    Autonomous Linguistic Core Agent. Consumes structured computational streams 
    and synthesizes high-fidelity semantic summaries and contextual public health 
    advisories based on composite air quality matrices.
    """
    def __init__(self):
        # Operational Action Vector Matrix mapping metrics to institutional health guidelines
        self.health_action_matrix = {
            "GOOD": {
                "badge": "🟢 Good (Healthy Baseline)",
                "action_protocol": "Air quality is highly optimal for all outdoor cardiovascular training and public activities."
            },
            "MODERATE": {
                "badge": "🟡 Moderate (Acceptable Monitoring Window)",
                "action_protocol": "Extremely hypersensitive individuals should track fine baseline metrics and monitor subtle respiratory changes."
            },
            "UNHEALTHY_SENSITIVE": {
                "badge": "🟠 Unhealthy for Sensitive Groups (Active Risk)",
                "action_protocol": "People with active asthma, seniors, and children must minimize high-intensity outdoor exposure cycles."
            },
            "UNHEALTHY": {
                "badge": "🔴 Unhealthy (Critical Threshold Breach)",
                "action_protocol": "Mandatory respiratory mask protocols enforced. General population should significantly reduce prolonged outdoor tasks."
            },
            "HAZARDOUS": {
                "badge": "⚫ Hazardous (Emergency Atmospheric Stagnation)",
                "action_protocol": "CRITICAL HEALTH ALERT: Evacuate external open zones. Seal all indoor ventilation networks and deploy active air purifiers."
            }
        }

    def _resolve_evaluation_key(self, scalar_aqi: float) -> str:
        """Maps scalar variables directly to corresponding structural severity keys."""
        if scalar_aqi <= 50.0: return "GOOD"
        elif scalar_aqi <= 100.0: return "MODERATE"
        elif scalar_aqi <= 150.0: return "UNHEALTHY_SENSITIVE"
        elif scalar_aqi <= 200.0: return "UNHEALTHY"
        else: return "HAZARDOUS"

    def execute_explanation_cycle(self, zone_name: str, estimation_payload: Dict[str, Any], diagnostic_logs: List[Dict[str, Any]]) -> str:
        """
        Assembles continuous variable payloads and anomaly arrays into an 
        enterprise-grade, context-aware markdown analysis report.
        """
        logger.info(f"🔄 Explainer Agent: Compiling semantic telemetry matrix for zone: '{zone_name}'")
        
        try:
            scalar_aqi = float(estimation_payload.get("scalar_aqi", 0.0))
        except (ValueError, TypeError):
            logger.error("❌ Explainer Agent: Invalid quantitative numeric data received.")
            return "### ❌ Extraction Failure\nUnable to compile narrative string due to schema conversion anomalies."

        # Extract dynamic severity coordinates matching continuous variables array
        severity_key = self._resolve_evaluation_key(scalar_aqi)
        meta_protocol = self.health_action_matrix[severity_key]
        
        dominant_catalyst = estimation_payload.get("dominant_driver", "N/A")

        # Compile professional analytical structural layout using markdown templates
        markdown_report = f"""### 🛡️ Environmental Intelligence Brief: {zone_name} Regional Grid

---

#### 📊 Integrated Air Quality Coordinates
* **Calculated Continuous Scaled Index ($AQI_{{US}}$):** `{scalar_aqi}`
* **Regulatory Classification Status:** {meta_protocol['badge']}
* **Dominant Critical Pollutant Catalyst:** `{dominant_catalyst}`

#### 🔬 Dynamic Diagnostic Vector Breakdowns
"""
        # Parse through anomaly arrays passed from the Analyzer Agent node
        if diagnostic_logs and isinstance(diagnostic_logs, list):
            for log in diagnostic_logs:
                # If logs are fully structured dictionary layers
                if isinstance(log, dict) and "parameter" in log:
                    markdown_report += f"* **Parameter `{log['parameter']}` Variance:** Observed `{log['observed_value']}` µg/m³ against safe regulatory limit `{log['permissible_limit']}` µg/m³ (Breached by **+{log['variance_pct']}%**).\n"
                    markdown_report += f"  - *Causal Root Vector:* {log['root_cause_vector']}\n"
                else:
                    # Fallback string parsing loop logic
                    markdown_report += f"* {log}\n"
        else:
            markdown_report += "* Baseline stability verified. No critical feature anomalies detected within this temporal monitoring grid.\n"

        markdown_report += f"""
#### ⚡ Real-Time Automated Public Health Advisory Protocol
> **Enforced Safety Directives:** {meta_protocol['action_protocol']}

---
*Generated autonomously via distributed multi-agent context evaluation frames.*
"""
        logger.info("✅ Explainer Agent: Narrative reporting matrix successfully generated.")
        return markdown_report