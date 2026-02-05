"""Agent modules for scam intelligence extraction"""

from .language import LanguageDetectionAgent
from .normalizer import TextNormalizationAgent
from .extractor import FeatureExtractionAgent
from .intent import IntentInferenceAgent
from .confidence import ConfidenceEstimationAgent

# Transformer-powered agents
from .detector import MLSpamDetector, get_ml_detector
from .scorer import ThreatScoringAgent
from .classifier import ScamClassificationAgent

__all__ = [
    "LanguageDetectionAgent",
    "TextNormalizationAgent",
    "FeatureExtractionAgent",
    "IntentInferenceAgent",
    "ConfidenceEstimationAgent",
    # ML versions
    "MLSpamDetector",
    "get_ml_detector",
    "ThreatScoringAgent",
    "ScamClassificationAgent",
]
