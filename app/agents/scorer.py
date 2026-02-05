"""
Threat Scoring Agent (ML-Powered)

This agent computes threat scores using a trained machine learning model
combined with heuristic feature analysis for comprehensive scoring.
"""

import os
import re
import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ThreatScoringAgent:
    """
    ML-Powered Threat Scoring Agent.

    Combines machine learning predictions with heuristic analysis
    to compute comprehensive threat scores.
    """

    # Threat level thresholds
    THREAT_THRESHOLDS = {
        "high": 70,
        "medium": 30,
    }

    # Additional heuristic weights for feature boosting
    FEATURE_WEIGHTS = {
        "url_presence": 5,
        "multiple_urls": 8,
        "suspicious_url": 12,
        "phone_presence": 5,
        "email_presence": 5,
        "monetary_reference": 8,
        "large_amount": 10,
        "urgency_indicator": 8,
        "threat_language": 10,
        "credential_request": 15,
    }

    # Urgency keywords
    URGENCY_KEYWORDS = [
        "urgent",
        "immediately",
        "asap",
        "now",
        "expires",
        "limited",
        "act now",
        "don't delay",
        "last chance",
        "final notice",
    ]

    # Threat keywords
    THREAT_KEYWORDS = [
        "blocked",
        "suspended",
        "terminated",
        "disabled",
        "locked",
        "compromised",
        "hacked",
        "unauthorized",
        "illegal",
    ]

    # Credential request keywords
    CREDENTIAL_KEYWORDS = [
        "password",
        "pin",
        "cvv",
        "ssn",
        "social security",
        "account number",
        "login",
        "credentials",
        "verify your",
    ]

    def __init__(self):
        """Initialize the threat scoring agent."""
        self._thresholds = self.THREAT_THRESHOLDS.copy()
        self._ml_detector = None
        self._load_ml_model()

    def _load_ml_model(self):
        """Load the ML detector."""
        try:
            from app.agents.detector import get_ml_detector

            self._ml_detector = get_ml_detector()
            if self._ml_detector.is_loaded:
                logger.info("ML detector loaded for threat scoring")
            else:
                logger.warning("ML detector not available, using heuristics only")
        except Exception as e:
            logger.warning(f"Failed to load ML detector: {e}")
            self._ml_detector = None

    def _check_keywords(self, text_lower: str, keywords: list) -> bool:
        """Check if any keywords are present in text."""
        return any(kw in text_lower for kw in keywords)

    def _count_keywords(self, text_lower: str, keywords: list) -> int:
        """Count how many keywords are present in text."""
        return sum(1 for kw in keywords if kw in text_lower)

    def _compute_heuristic_boost(
        self, text: str, features: Optional[Dict] = None
    ) -> tuple:
        """
        Compute additional heuristic boost to ML score.

        Returns tuple of (boost_score, factors)
        """
        text_lower = text.lower()
        boost = 0
        factors = []

        # Feature-based boosts
        if features:
            flags = features.get("flags", {})
            entities = features.get("entities", {})

            # URL presence
            if flags.get("has_url"):
                urls = entities.get("urls", [])
                if len(urls) > 1:
                    boost += self.FEATURE_WEIGHTS["multiple_urls"]
                    factors.append(
                        ("multiple_urls", self.FEATURE_WEIGHTS["multiple_urls"])
                    )

                # Check for suspicious URLs
                for url in urls:
                    url_lower = url.lower()
                    if any(
                        s in url_lower for s in ["bit.ly", "tinyurl", "goo.gl", "t.co"]
                    ):
                        boost += self.FEATURE_WEIGHTS["suspicious_url"]
                        factors.append(
                            ("suspicious_url", self.FEATURE_WEIGHTS["suspicious_url"])
                        )
                        break

            # Large monetary amounts
            if flags.get("has_amount"):
                amounts = entities.get("amounts", [])
                for amount in amounts:
                    nums = re.findall(r"[\d,]+", amount)
                    for num in nums:
                        try:
                            val = float(num.replace(",", ""))
                            if val >= 10000:
                                boost += self.FEATURE_WEIGHTS["large_amount"]
                                factors.append(
                                    (
                                        "large_amount",
                                        self.FEATURE_WEIGHTS["large_amount"],
                                    )
                                )
                                break
                        except:
                            pass

        # Urgency indicators
        if self._check_keywords(text_lower, self.URGENCY_KEYWORDS):
            boost += self.FEATURE_WEIGHTS["urgency_indicator"]
            factors.append(
                ("urgency_indicator", self.FEATURE_WEIGHTS["urgency_indicator"])
            )

        # Threat language
        if self._check_keywords(text_lower, self.THREAT_KEYWORDS):
            boost += self.FEATURE_WEIGHTS["threat_language"]
            factors.append(("threat_language", self.FEATURE_WEIGHTS["threat_language"]))

        # Credential requests
        if self._check_keywords(text_lower, self.CREDENTIAL_KEYWORDS):
            boost += self.FEATURE_WEIGHTS["credential_request"]
            factors.append(
                ("credential_request", self.FEATURE_WEIGHTS["credential_request"])
            )

        return boost, factors

    def compute_score(
        self, text: str, features: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Compute threat score for text using ML model + heuristics.

        Args:
            text: The text to analyze
            features: Pre-extracted features (optional)

        Returns:
            Dictionary with score and contributing factors
        """
        factors = []

        # Get ML-based score
        if self._ml_detector and self._ml_detector.is_loaded:
            ml_result = self._ml_detector.predict(text)

            # Use spam probability directly scaled to 0-100
            spam_prob = ml_result.get("spam_probability", 0.5)

            # Direct linear scaling: probability 0.5+ -> score 30+
            # probability 0.7+ -> score 70+
            base_score = spam_prob * 100

            factors.append(("ml_spam_probability", int(base_score)))
        else:
            # Fallback to medium score
            base_score = 30
            factors.append(("ml_unavailable_default", 30))

        # Add heuristic boost
        boost, boost_factors = self._compute_heuristic_boost(text, features)
        factors.extend(boost_factors)

        # Combine scores
        score = base_score + (boost * 0.5)  # Heuristics add up to 50% boost

        # Normalize to 0-100
        score = min(100, max(0, int(score)))

        # Determine threat level
        if score >= self._thresholds["high"]:
            threat_level = "High"
        elif score >= self._thresholds["medium"]:
            threat_level = "Medium"
        else:
            threat_level = "Low"

        return {"threat_score": score, "threat_level": threat_level, "factors": factors}

    def process(self, text: str, features: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process text and return threat scoring results.

        Args:
            text: The text to analyze
            features: Pre-extracted features (optional)

        Returns:
            Dictionary with threat scoring results
        """
        return self.compute_score(text, features)
