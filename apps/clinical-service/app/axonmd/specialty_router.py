from app.axonmd.bot_definitions import BOT_DEFINITIONS

class SpecialtyRouter:
    @staticmethod
    def route_by_context(symptoms: list[str], department: str = None, diagnosis: str = None) -> str:
        """Rule-based router based on triggers."""
        symptoms_str = " ".join(symptoms).lower()
        if diagnosis:
            symptoms_str += f" {diagnosis.lower()}"
            
        # Check emergency priority first
        for word in ["cardiac arrest", "stroke", "trauma", "unconscious", "gsw", "severe bleeding"]:
            if word in symptoms_str:
                return "emergency_medicine"
                
        # Check specific triggers
        best_match = "general_medicine"
        max_matches = 0
        
        for spec, details in BOT_DEFINITIONS.items():
            triggers = details.get("triggers", [])
            matches = sum(1 for t in triggers if t.lower() in symptoms_str or t.lower() == (department or "").lower())
            if matches > max_matches:
                max_matches = matches
                best_match = spec
                
        return best_match
