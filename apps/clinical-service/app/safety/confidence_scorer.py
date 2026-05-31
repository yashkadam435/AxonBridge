import uuid
from app.models.schemas import ConfidenceScore, EncounterConfidence

class ConfidenceScorer:
    """
    Scores confidence of agent-generated clinical actions.
    """
    SCORING_FACTORS = {
        "model_confidence": 0.35,
        "data_completeness": 0.25,
        "historical_accuracy": 0.20,
        "guideline_alignment": 0.15,
        "input_quality": 0.05
    }
    
    DEFAULT_THRESHOLD = 0.85
    
    async def score_action(self, action_type: str, model_confidence: float, context_keys_present: int) -> ConfidenceScore:
        # Simulate data completeness based on how many context keys are present
        data_completeness = min(1.0, context_keys_present / 10.0) 
        historical_accuracy = 0.82  # Mock baseline
        guideline_alignment = 0.90   # Mock alignment
        input_quality = 0.88         # Mock audio/text quality
        
        overall = (
            model_confidence * self.SCORING_FACTORS["model_confidence"] +
            data_completeness * self.SCORING_FACTORS["data_completeness"] +
            historical_accuracy * self.SCORING_FACTORS["historical_accuracy"] +
            guideline_alignment * self.SCORING_FACTORS["guideline_alignment"] +
            input_quality * self.SCORING_FACTORS["input_quality"]
        )
        
        escalated = overall < self.DEFAULT_THRESHOLD
        
        return ConfidenceScore(
            action_id=str(uuid.uuid4()),
            action_type=action_type,
            overall_score=round(overall, 2),
            factor_scores={
                "model_confidence": round(model_confidence, 2),
                "data_completeness": round(data_completeness, 2),
                "historical_accuracy": historical_accuracy,
                "guideline_alignment": guideline_alignment,
                "input_quality": input_quality
            },
            threshold=self.DEFAULT_THRESHOLD,
            escalated=escalated,
            escalation_reason="Confidence below clinical threshold" if escalated else None,
            recommended_action="review_required" if escalated else "proceed"
        )
