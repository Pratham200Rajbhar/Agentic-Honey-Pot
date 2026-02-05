"""
Intent Inference Agent
Determines attacker motivation from message analysis.
"""
import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


class IntentInferenceAgent:
    """Agent for inferring attacker intent."""
    
    # Intent taxonomy
    INTENTS = [
        "Financial Fraud",
        "Identity Theft",
        "Credential Harvesting",
        "Malware Distribution",
        "Social Engineering",
        "Information Gathering"
    ]
    
    # Category to primary intent mapping
    CATEGORY_INTENT_MAP = {
        "Bank/Financial Scam": "Financial Fraud",
        "Lottery/Prize Scam": "Financial Fraud",
        "Job/Employment Scam": "Financial Fraud",
        "Crypto/Investment Scam": "Financial Fraud",
        "Phishing/Credential Theft": "Credential Harvesting",
        "Romance/Dating Scam": "Social Engineering",
        "Tech Support Scam": "Credential Harvesting",
        "Delivery/Package Scam": "Financial Fraud",
        "Government/Tax Scam": "Identity Theft",
        "General Spam": "Information Gathering"
    }
    
    # Intent-indicative keywords
    INTENT_KEYWORDS = {
        "Financial Fraud": [
            "payment", "transfer", "money", "fee", "charge", "pay", "send",
            "wire", "deposit", "withdraw", "transaction", "cash", "fund"
        ],
        "Identity Theft": [
            "ssn", "social security", "id", "identity", "passport", "license",
            "dob", "date of birth", "address", "personal information", "kyc",
            "aadhar", "aadhaar", "pan card", "pan number"
        ],
        "Credential Harvesting": [
            "password", "login", "username", "account", "verify", "credential",
            "authentication", "sign in", "log in", "otp", "pin", "cvv",
            "security code", "2fa", "two factor"
        ],
        "Malware Distribution": [
            "download", "install", "attachment", "file", "software", "app",
            "update", "patch", "executable", "run", "open", "click here"
        ],
        "Social Engineering": [
            "trust", "help", "friend", "relationship", "emergency", "urgent",
            "confidential", "secret", "personal", "favor", "assist"
        ],
        "Information Gathering": [
            "survey", "feedback", "opinion", "information", "details", "data",
            "confirm", "verify", "provide", "share", "update"
        ]
    }
    
    def __init__(self):
        """Initialize the intent inference agent."""
        pass
    
    def _check_keywords(self, text_lower: str, keywords: list) -> int:
        """Count matching keywords in text."""
        return sum(1 for kw in keywords if kw in text_lower)
    
    def infer_intent(
        self, 
        text: str,
        scam_type: str,
        features: Optional[Dict] = None
    ) -> str:
        """
        Infer the primary intent from the message.
        
        Args:
            text: The message text
            scam_type: The classified scam type
            features: Extracted features (optional)
            
        Returns:
            The inferred intent
        """
        text_lower = text.lower()
        
        # Start with category-based mapping
        primary_intent = self.CATEGORY_INTENT_MAP.get(scam_type, "Information Gathering")
        
        # Check for intent overrides based on entity composition
        if features:
            flags = features.get("flags", {})
            entities = features.get("entities", {})
            
            # URL-only with click request -> likely Malware Distribution
            if flags.get("has_url") and not flags.get("has_phone") and not flags.get("has_amount"):
                urls = entities.get("urls", [])
                for url in urls:
                    url_lower = url.lower()
                    if any(s in url_lower for s in [".exe", ".zip", ".apk", "download", "install"]):
                        return "Malware Distribution"
            
            # Credential keywords present -> Credential Harvesting
            cred_count = self._check_keywords(text_lower, self.INTENT_KEYWORDS["Credential Harvesting"])
            if cred_count >= 2:
                return "Credential Harvesting"
            
            # Identity-related keywords -> Identity Theft
            id_count = self._check_keywords(text_lower, self.INTENT_KEYWORDS["Identity Theft"])
            if id_count >= 2:
                return "Identity Theft"
        
        # Keyword-based scoring for refinement
        intent_scores = {}
        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = self._check_keywords(text_lower, keywords)
            intent_scores[intent] = score
        
        # If a different intent has significantly higher score, override
        max_intent = max(intent_scores, key=intent_scores.get)
        max_score = intent_scores[max_intent]
        primary_score = intent_scores.get(primary_intent, 0)
        
        if max_score > primary_score + 2:  # Significant difference threshold
            return max_intent
        
        return primary_intent
    
    def process(
        self, 
        text: str,
        scam_type: str,
        features: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process text and return intent inference results.
        
        Args:
            text: The message text
            scam_type: The classified scam type
            features: Extracted features (optional)
            
        Returns:
            Dictionary with intent inference results
        """
        text_lower = text.lower()
        
        # Compute all intent scores
        intent_scores = {}
        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = self._check_keywords(text_lower, keywords)
            intent_scores[intent] = score
        
        primary_intent = self.infer_intent(text, scam_type, features)
        
        return {
            "intent": primary_intent,
            "intent_scores": intent_scores,
            "category_based_intent": self.CATEGORY_INTENT_MAP.get(scam_type, "Information Gathering")
        }
