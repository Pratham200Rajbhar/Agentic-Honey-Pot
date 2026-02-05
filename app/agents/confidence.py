"""
Confidence Estimation Agent
Quantifies classification certainty.
"""
import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


class ConfidenceEstimationAgent:
    """Agent for estimating classification confidence."""
    
    # Minimum and maximum message lengths for optimal confidence
    MIN_OPTIMAL_LENGTH = 20
    MAX_OPTIMAL_LENGTH = 500
    
    def __init__(self):
        """Initialize the confidence estimation agent."""
        pass
    
    def estimate_confidence(
        self,
        text: str,
        threat_score: int,
        classification_scores: Optional[Dict[str, float]] = None,
        features: Optional[Dict] = None
    ) -> float:
        """
        Estimate confidence in the analysis results.
        
        Args:
            text: The analyzed text
            threat_score: The computed threat score
            classification_scores: Scores for each category
            features: Extracted features
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence = 0.5  # Base confidence
        adjustments = []
        
        # Factor 1: Message length (adequate length -> higher confidence)
        text_length = len(text.strip())
        if text_length >= self.MIN_OPTIMAL_LENGTH:
            if text_length <= self.MAX_OPTIMAL_LENGTH:
                length_factor = 0.15
            else:
                # Slightly lower confidence for very long messages
                length_factor = 0.10
            confidence += length_factor
            adjustments.append(("adequate_length", length_factor))
        else:
            # Short messages have lower confidence
            length_factor = -0.1
            confidence += length_factor
            adjustments.append(("short_message", length_factor))
        
        # Factor 2: Classification score margin
        if classification_scores:
            sorted_scores = sorted(classification_scores.values(), reverse=True)
            if len(sorted_scores) >= 2:
                margin = sorted_scores[0] - sorted_scores[1]
                if margin > 2.0:
                    margin_factor = 0.15
                elif margin > 1.0:
                    margin_factor = 0.10
                elif margin > 0.5:
                    margin_factor = 0.05
                else:
                    margin_factor = -0.05  # Low margin means uncertain
                
                confidence += margin_factor
                adjustments.append(("score_margin", margin_factor))
            
            # Top score magnitude
            top_score = sorted_scores[0] if sorted_scores else 0
            if top_score > 3.0:
                score_factor = 0.10
            elif top_score > 1.5:
                score_factor = 0.05
            else:
                score_factor = -0.05
            
            confidence += score_factor
            adjustments.append(("top_score_magnitude", score_factor))
        
        # Factor 3: Entity presence (entities increase confidence)
        if features:
            flags = features.get("flags", {})
            entity_count = flags.get("entity_count", 0)
            
            if entity_count >= 3:
                entity_factor = 0.12
            elif entity_count >= 2:
                entity_factor = 0.08
            elif entity_count >= 1:
                entity_factor = 0.05
            else:
                entity_factor = 0.0
            
            confidence += entity_factor
            adjustments.append(("entity_presence", entity_factor))
            
            # Multiple entity types
            entity_types = sum([
                flags.get("has_url", False),
                flags.get("has_phone", False),
                flags.get("has_email", False),
                flags.get("has_amount", False)
            ])
            if entity_types >= 2:
                diversity_factor = 0.05
                confidence += diversity_factor
                adjustments.append(("entity_diversity", diversity_factor))
        
        # Factor 4: Threat score (very high or very low scores are more confident)
        if threat_score >= 80:
            threat_factor = 0.10
        elif threat_score >= 60:
            threat_factor = 0.05
        elif threat_score <= 20:
            threat_factor = 0.08  # Clear ham/benign
        elif threat_score <= 40:
            threat_factor = 0.03
        else:
            threat_factor = -0.02  # Middle scores are less certain
        
        confidence += threat_factor
        adjustments.append(("threat_score_clarity", threat_factor))
        
        # Factor 5: Word count
        if features:
            structural = features.get("structural", {})
            word_count = structural.get("word_count", 0)
            
            if 10 <= word_count <= 100:
                word_factor = 0.05
            elif word_count > 100:
                word_factor = 0.02
            else:
                word_factor = -0.05
            
            confidence += word_factor
            adjustments.append(("word_count", word_factor))
        
        # Ensure bounds [0.0, 1.0]
        confidence = max(0.0, min(1.0, confidence))
        
        # Round to 2 decimal places
        confidence = round(confidence, 2)
        
        return confidence
    
    def process(
        self,
        text: str,
        threat_score: int,
        classification_scores: Optional[Dict[str, float]] = None,
        features: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process and return confidence estimation results.
        
        Args:
            text: The analyzed text
            threat_score: The computed threat score
            classification_scores: Scores for each category
            features: Extracted features
            
        Returns:
            Dictionary with confidence estimation results
        """
        confidence = self.estimate_confidence(
            text, threat_score, classification_scores, features
        )
        
        # Determine confidence level
        if confidence >= 0.8:
            confidence_level = "High"
        elif confidence >= 0.6:
            confidence_level = "Medium"
        else:
            confidence_level = "Low"
        
        return {
            "confidence_score": confidence,
            "confidence_level": confidence_level
        }
