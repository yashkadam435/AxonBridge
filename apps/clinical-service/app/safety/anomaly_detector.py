import uuid
from app.models.schemas import AnomalyAlert

class AnomalyDetector:
    """
    Detects anomalous clinical patterns that may indicate errors.
    """
    
    ANOMALY_RULES = {
        "systolic_bp": {"min": 90, "max": 180, "critical_min": 70, "critical_max": 220},
        "diastolic_bp": {"min": 60, "max": 110, "critical_min": 40, "critical_max": 130},
        "heart_rate": {"min": 50, "max": 120, "critical_min": 40, "critical_max": 150},
        "temperature": {"min": 97.0, "max": 100.5, "critical_min": 95.0, "critical_max": 104.0},
        "spo2": {"min": 92, "max": 100, "critical_min": 85, "critical_max": 100},
    }
    
    async def check_vitals(self, vitals: dict) -> list[AnomalyAlert]:
        alerts = []
        for vital, value in vitals.items():
            if vital in self.ANOMALY_RULES:
                rules = self.ANOMALY_RULES[vital]
                val = float(value)
                
                if val >= rules.get("critical_max", 999) or val <= rules.get("critical_min", -999):
                    alerts.append(AnomalyAlert(
                        id=str(uuid.uuid4()),
                        type="vital_sign",
                        field=vital,
                        value=val,
                        expected_range=f"{rules['min']}-{rules['max']}",
                        severity="critical",
                        message=f"{vital} of {val} is critically abnormal.",
                        suggested_action="Recheck immediately and notify physician."
                    ))
                elif val > rules["max"] or val < rules["min"]:
                    alerts.append(AnomalyAlert(
                        id=str(uuid.uuid4()),
                        type="vital_sign",
                        field=vital,
                        value=val,
                        expected_range=f"{rules['min']}-{rules['max']}",
                        severity="warning",
                        message=f"{vital} of {val} is outside normal limits.",
                        suggested_action="Monitor closely."
                    ))
        return alerts
