"""
Agent Orchestrator
Coordinates the multi-agent processing pipeline with ML-powered detection.
"""

import logging
import uuid
from typing import Dict, Any, Optional

from .agents import (
    LanguageDetectionAgent,
    TextNormalizationAgent,
    FeatureExtractionAgent,
    IntentInferenceAgent,
    ConfidenceEstimationAgent,
    # Transformer-powered agents
    ThreatScoringAgent,
    ScamClassificationAgent,
)
from .schemas import ScamResponse, ExtractedEntities

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates the multi-agent analysis pipeline with ML models."""

    def __init__(self):
        """
        Initialize the orchestrator with all agents.
        """
        # Initialize all agents
        self.language_agent = LanguageDetectionAgent()
        self.normalizer_agent = TextNormalizationAgent()
        self.extractor_agent = FeatureExtractionAgent()
        # Use ML-powered agents
        self.classifier_agent = ScamClassificationAgent()
        self.scorer_agent = ThreatScoringAgent()
        self.intent_agent = IntentInferenceAgent()
        self.confidence_agent = ConfidenceEstimationAgent()

        logger.info("Agent orchestrator initialized with ML models")

    def analyze(self, message: str) -> ScamResponse:
        """
        Run the full analysis pipeline on a message.

        Args:
            message: The message to analyze

        Returns:
            ScamResponse with complete analysis results
        """
        analysis_id = str(uuid.uuid4())
        logger.info(f"Starting analysis {analysis_id}")

        try:
            # Stage 1: Language Detection
            language_result = self.language_agent.process(message)
            language = language_result["language"]
            logger.debug(f"Language detected: {language}")

            # Stage 2: Text Normalization
            norm_result = self.normalizer_agent.process(message)
            normalized_text = norm_result["normalized"]
            normalized_lower = norm_result["normalized_lower"]
            logger.debug(f"Text normalized, length: {len(normalized_text)}")

            # Stage 3: Feature Extraction
            features = self.extractor_agent.process(normalized_text)
            logger.debug(f"Features extracted: {features['flags']}")

            # Stage 4: Classification (ML-powered)
            classification = self.classifier_agent.process(
                normalized_text, features=features
            )
            scam_type = classification["scam_type"]
            logger.debug(f"Classified as: {scam_type}")

            # Stage 5: Threat Scoring (ML-powered)
            scoring = self.scorer_agent.process(normalized_text, features)
            threat_score = scoring["threat_score"]
            threat_level = scoring["threat_level"]
            logger.debug(f"Threat score: {threat_score} ({threat_level})")

            # Stage 6: Intent Inference
            intent_result = self.intent_agent.process(
                normalized_text, scam_type=scam_type, features=features
            )
            intent = intent_result["intent"]
            logger.debug(f"Intent inferred: {intent}")

            # Stage 7: Confidence Estimation
            confidence_result = self.confidence_agent.process(
                text=message,
                threat_score=threat_score,
                classification_scores=classification.get("scores"),
                features=features,
            )
            confidence_score = confidence_result["confidence_score"]
            logger.debug(f"Confidence: {confidence_score}")

            # Build response
            entities = features.get("entities", {})
            extracted_entities = ExtractedEntities(
                emails=entities.get("emails", []),
                phones=entities.get("phones", []),
                urls=entities.get("urls", []),
                amounts=entities.get("amounts", []),
            )

            response = ScamResponse(
                analysis_id=analysis_id,
                scam_type=scam_type,
                threat_level=threat_level,
                threat_score=threat_score,
                intent=intent,
                confidence_score=confidence_score,
                language=language,
                extracted_entities=extracted_entities,
            )

            logger.info(
                f"Analysis {analysis_id} completed: {scam_type}, score={threat_score}"
            )
            return response

        except Exception as e:
            logger.error(f"Analysis {analysis_id} failed: {str(e)}")
            raise

    def process(self, message: str) -> Dict[str, Any]:
        """
        Run the full analysis pipeline and return as dictionary.

        Args:
            message: The message to analyze

        Returns:
            Dictionary with complete analysis results
        """
        response = self.analyze(message)
        return response.model_dump()


# Singleton instance for reuse
_orchestrator_instance: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """Get or create the orchestrator singleton."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = AgentOrchestrator()
    return _orchestrator_instance
