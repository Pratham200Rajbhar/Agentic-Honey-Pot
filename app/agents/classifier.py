"""
Scam Classification Agent (100% ML-Powered)

This agent classifies messages into specific scam categories
using semantic similarity and ML predictions, avoiding hardcoded keywords.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class ScamClassificationAgent:
    """
    Robust ML-Powered Scam Classification Agent.

    Uses semantic similarity in a Vector Space Model (VSM) to categorize scams
    without relying on brittle keyword lists.
    """

    # Semantic descriptions of categories (Prototypes)
    # These represent the "meaning" of the category in high-dimensional space
    CATEGORY_DESCRIPTIONS = {
        "Bank/Financial Scam": "Banking fraud, unauthorized transactions, account suspension, card verification, bank transfers, and financial account alerts.",
        "Lottery/Prize Scam": "Winning a lottery, claiming a prize, luck draws, sweepstakes winners, and cash rewards for selected participants.",
        "Job/Employment Scam": "Work from home job offers, high salary positions, hiring for remote work with no experience, and part-time income opportunities.",
        "Crypto/Investment Scam": "Cryptocurrency investment, bitcoin trading, forex profits, guaranteed returns on stocks, and wallet mining schemes.",
        "Phishing": "Verifying account credentials, clicking links to reset passwords, unauthorized login attempts, and urgent security updates.",
        "Romance/Dating Scam": "Soulmate searches, romantic companionship, attractive singles wanting to meet, and relationship-based schemes.",
        "Tech Support Scam": "Malware infections, viruses detected on computer, Microsoft or Apple support calls, and remote access for technical fixes.",
        "Delivery/Package Scam": "Package tracking, failed delivery attempts, customs fees for shipments, and courier service notifications.",
        "Government/Tax Scam": "IRS tax audits, social security number issues, legal warrants for arrest, and federal agency compliance demands.",
        "General Spam": "Generic promotional offers, sales discounts, brand deals, and subscription-based advertising.",
    }

    def __init__(self):
        """Initialize the classification agent."""
        self._ml_detector = None
        self._category_vectors = {}
        self._load_ml_model()
        self._initialize_vsm()

    def _load_ml_model(self):
        """Load the shared ML detector."""
        try:
            from app.agents.detector import get_ml_detector

            self._ml_detector = get_ml_detector()
            if self._ml_detector.is_loaded:
                logger.info("Shared ML detector integrated into Classification Agent")
        except Exception as e:
            logger.error(f"Integrity error when loading ML detector: {e}")
            self._ml_detector = None

    def _initialize_vsm(self):
        """Create vector representations for each category based on descriptions."""
        if not self._ml_detector or not self._ml_detector.is_loaded:
            return

        try:
            for category, description in self.CATEGORY_DESCRIPTIONS.items():
                vector = self._ml_detector.get_embedding(description)
                if vector is not None:
                    self._category_vectors[category] = vector
            logger.info(
                f"Vector Space Model initialized on DistilBERT with {len(self._category_vectors)} categories"
            )
        except Exception as e:
            logger.error(f"VSM initialization failed: {e}")

    def _cosine_similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return np.dot(vec_a, vec_b) / (norm_a * norm_b)

    def _semantic_classify(self, text: str) -> Tuple[str, float]:
        """
        Classify text by finding the closest category in vector space.
        """
        if not self._category_vectors:
            return "General Spam", 0.5

        try:
            target_vector = self._ml_detector.get_embedding(text)
            if target_vector is None:
                return "General Spam", 0.4

            best_category = "General Spam"
            max_sim = -1.0

            for category, cat_vector in self._category_vectors.items():
                sim = self._cosine_similarity(target_vector, cat_vector)
                if sim > max_sim:
                    max_sim = sim
                    best_category = category

            # Normalize confidence based on similarity (VSM scores are usually low for sparse TF-IDF)
            # We use a non-linear mapping to bring typical scores into 0-1 range
            confidence = min(0.95, float(max_sim * 5))

            return best_category, confidence
        except Exception as e:
            logger.warning(f"Semantic classification failed: {e}")
            return "General Spam", 0.3

    def classify(self, text: str, features: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Classify text using the robust ML-VSM pipeline.
        """
        # 1. Primary Spam Check
        ml_result = {"is_spam": False, "spam_probability": 0.5}
        if self._ml_detector and self._ml_detector.is_loaded:
            ml_result = self._ml_detector.predict(text)

        is_spam = ml_result.get("is_spam", False)
        spam_prob = ml_result.get("spam_probability", 0.5)

        # 2. Categorization
        if is_spam or spam_prob > 0.4:
            scam_type, type_confidence = self._semantic_classify(text)

            # Combine signals
            overall_confidence = (spam_prob + type_confidence) / 2

            return {
                "scam_type": scam_type,
                "is_scam": True,
                "confidence": float(overall_confidence),
                "spam_probability": float(spam_prob),
                "semantic_confidence": float(type_confidence),
                "method": "VectorSpaceModel",
            }
        else:
            return {
                "scam_type": "Not Scam",
                "is_scam": False,
                "confidence": float(1.0 - spam_prob),
                "spam_probability": float(spam_prob),
                "method": "MLPrediction",
            }

    def process(self, text: str, features: Optional[Dict] = None) -> Dict[str, Any]:
        """Process text and return classification results."""
        return self.classify(text, features)
