from typing import Dict, Any, List, Optional
from ..models.api_models import AgentType
import numpy as np

class DecisionAgent:
    agent_type = AgentType.decision

    def __init__(self, human_threshold: float = 0.7):
        # Below this confidence, trigger human-in-the-loop
        self.human_threshold = human_threshold

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesizes research/analysis results to recommend an action.
        """
        try:
            research = input_data.get("research", {})
            analysis = input_data.get("analysis", {})
            # Confidence aggregation: take minimum, or weighted mean if available
            conf_research = research.get("confidence", 0)
            conf_analysis = analysis.get("confidence", 0)
            confidence = self.get_confidence([conf_research, conf_analysis])

            # Synthesize recommendations
            recommendations = []
            if conf_analysis >= 0.6 and analysis.get("insights"):
                recommendations.extend([f"Data insight: {msg}" for msg in analysis["insights"]])
            if conf_research >= 0.6 and research.get("results"):
                recommendations.extend([f"Research: {str(r)}" for r in research["results"]])
            
            # Basic logic: if both above threshold, auto decision; else, require human
            decision_status = (
                "auto_approved" if confidence >= self.human_threshold else "human_verification_required"
            )
            next_action = (
                "Proceed automatically."
                if decision_status == "auto_approved"
                else "Escalate to human review for low confidence."
            )
            return {
                "recommendations": recommendations or ["Insufficient data for automated decision."],
                "confidence": confidence,
                "status": decision_status,
                "next_action": next_action,
            }
        except Exception as e:
            return self.handle_error(str(e))

    def get_confidence(self, confidences: List[float]) -> float:
        """Multi-factor aggregation for confidence."""
        confidences = [c for c in confidences if isinstance(c, (float, int))]
        if not confidences:
            return 0.0
        # Use geometric mean for conservative aggregation
        confidence = float(np.prod(confidences) ** (1/len(confidences)))
        return round(confidence, 2)

    def handle_error(self, error: str) -> Dict[str, Any]:
        return {
            "recommendations": [],
            "confidence": 0.0,
            "status": "error",
            "next_action": "Escalate to human review due to system error.",
            "error": error,
        }
