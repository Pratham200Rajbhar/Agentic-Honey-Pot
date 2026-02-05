"""
Feature Extraction Agent
Extracts entities and linguistic features from messages.
"""
import re
import logging
from typing import Dict, List, Set, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ExtractedFeatures:
    """Container for extracted features."""
    emails: List[str] = field(default_factory=list)
    phones: List[str] = field(default_factory=list)
    urls: List[str] = field(default_factory=list)
    amounts: List[str] = field(default_factory=list)
    tokens: List[str] = field(default_factory=list)
    
    # Structural features
    capitalization_ratio: float = 0.0
    punctuation_density: float = 0.0
    digit_ratio: float = 0.0
    word_count: int = 0
    char_count: int = 0
    
    # Entity flags
    has_url: bool = False
    has_email: bool = False
    has_phone: bool = False
    has_amount: bool = False
    entity_count: int = 0


class FeatureExtractionAgent:
    """Agent for extracting features from text."""
    
    # RFC 5322 compliant email pattern
    EMAIL_PATTERN = re.compile(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        re.IGNORECASE
    )
    
    # ITU-T E.164 compatible phone patterns
    PHONE_PATTERNS = [
        re.compile(r'\+?[1-9]\d{9,14}'),  # International format
        re.compile(r'\+?[0-9]{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}'),  # Various formats
        re.compile(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'),  # US format
        re.compile(r'\b\d{5}[-.\s]?\d{5}\b'),  # Indian mobile
        re.compile(r'\b\d{10,12}\b'),  # Plain digits
    ]
    
    # RFC 3986 URI pattern
    URL_PATTERN = re.compile(
        r'https?://[^\s<>"{}|\\^`\[\]]+|'
        r'www\.[^\s<>"{}|\\^`\[\]]+|'
        r'[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}(?:/[^\s]*)?',
        re.IGNORECASE
    )
    
    # Multi-currency amount patterns
    AMOUNT_PATTERNS = [
        re.compile(r'\$\s?[\d,]+(?:\.\d{2})?'),  # USD
        re.compile(r'£\s?[\d,]+(?:\.\d{2})?'),  # GBP
        re.compile(r'€\s?[\d,]+(?:\.\d{2})?'),  # EUR
        re.compile(r'₹\s?[\d,]+(?:\.\d{2})?'),  # INR
        re.compile(r'Rs\.?\s?[\d,]+(?:\.\d{2})?', re.IGNORECASE),  # INR text
        re.compile(r'\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s?(?:USD|GBP|EUR|INR|dollars?|pounds?|euros?|rupees?)\b', re.IGNORECASE),
        re.compile(r'\b(?:USD|GBP|EUR|INR)\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b', re.IGNORECASE),
    ]
    
    # Token pattern
    TOKEN_PATTERN = re.compile(r'\b[a-zA-Z]+\b')
    
    def __init__(self):
        """Initialize the feature extraction agent."""
        pass
    
    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text."""
        matches = self.EMAIL_PATTERN.findall(text)
        return list(set(matches))
    
    def extract_phones(self, text: str) -> List[str]:
        """Extract phone numbers from text."""
        phones = set()
        for pattern in self.PHONE_PATTERNS:
            matches = pattern.findall(text)
            for match in matches:
                # Clean and validate phone number
                cleaned = re.sub(r'[^\d+]', '', match)
                if len(cleaned) >= 7 and len(cleaned) <= 15:
                    phones.add(match.strip())
        return list(phones)
    
    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text."""
        matches = self.URL_PATTERN.findall(text)
        urls = []
        for url in set(matches):
            # Basic validation
            if '.' in url and len(url) > 4:
                urls.append(url)
        return urls
    
    def extract_amounts(self, text: str) -> List[str]:
        """Extract monetary amounts from text."""
        amounts = set()
        for pattern in self.AMOUNT_PATTERNS:
            matches = pattern.findall(text)
            amounts.update(matches)
        return list(amounts)
    
    def extract_tokens(self, text: str) -> List[str]:
        """Extract word tokens from text."""
        return self.TOKEN_PATTERN.findall(text.lower())
    
    def compute_structural_features(self, text: str) -> Dict[str, float]:
        """Compute structural features from text."""
        if not text:
            return {
                "capitalization_ratio": 0.0,
                "punctuation_density": 0.0,
                "digit_ratio": 0.0,
                "word_count": 0,
                "char_count": 0
            }
        
        char_count = len(text)
        alpha_chars = sum(1 for c in text if c.isalpha())
        upper_chars = sum(1 for c in text if c.isupper())
        punct_chars = sum(1 for c in text if c in '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')
        digit_chars = sum(1 for c in text if c.isdigit())
        words = text.split()
        
        return {
            "capitalization_ratio": upper_chars / alpha_chars if alpha_chars > 0 else 0.0,
            "punctuation_density": punct_chars / char_count if char_count > 0 else 0.0,
            "digit_ratio": digit_chars / char_count if char_count > 0 else 0.0,
            "word_count": len(words),
            "char_count": char_count
        }
    
    def extract(self, text: str) -> ExtractedFeatures:
        """
        Extract all features from text.
        
        Args:
            text: The text to analyze
            
        Returns:
            ExtractedFeatures with all extracted data
        """
        features = ExtractedFeatures()
        
        # Extract entities
        features.emails = self.extract_emails(text)
        features.phones = self.extract_phones(text)
        features.urls = self.extract_urls(text)
        features.amounts = self.extract_amounts(text)
        features.tokens = self.extract_tokens(text)
        
        # Set entity flags
        features.has_email = len(features.emails) > 0
        features.has_phone = len(features.phones) > 0
        features.has_url = len(features.urls) > 0
        features.has_amount = len(features.amounts) > 0
        features.entity_count = (
            len(features.emails) + 
            len(features.phones) + 
            len(features.urls) + 
            len(features.amounts)
        )
        
        # Compute structural features
        structural = self.compute_structural_features(text)
        features.capitalization_ratio = structural["capitalization_ratio"]
        features.punctuation_density = structural["punctuation_density"]
        features.digit_ratio = structural["digit_ratio"]
        features.word_count = structural["word_count"]
        features.char_count = structural["char_count"]
        
        return features
    
    def process(self, text: str) -> Dict[str, Any]:
        """
        Process text and return feature extraction results.
        
        Args:
            text: The text to process
            
        Returns:
            Dictionary with extracted features
        """
        features = self.extract(text)
        return {
            "entities": {
                "emails": features.emails,
                "phones": features.phones,
                "urls": features.urls,
                "amounts": features.amounts
            },
            "tokens": features.tokens,
            "structural": {
                "capitalization_ratio": features.capitalization_ratio,
                "punctuation_density": features.punctuation_density,
                "digit_ratio": features.digit_ratio,
                "word_count": features.word_count,
                "char_count": features.char_count
            },
            "flags": {
                "has_url": features.has_url,
                "has_email": features.has_email,
                "has_phone": features.has_phone,
                "has_amount": features.has_amount,
                "entity_count": features.entity_count
            }
        }
