"""
Text Normalization Agent
Standardizes input text for consistent feature extraction.
"""
import re
import unicodedata
import logging
from typing import Tuple, List

logger = logging.getLogger(__name__)


class TextNormalizationAgent:
    """Agent for normalizing text input."""
    
    # Patterns to preserve during normalization
    URL_PATTERN = re.compile(
        r'https?://[^\s<>"{}|\\^`\[\]]+|'
        r'www\.[^\s<>"{}|\\^`\[\]]+'
    )
    EMAIL_PATTERN = re.compile(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    )
    PHONE_PATTERN = re.compile(
        r'\+?[0-9]{1,4}[-.\s]?(\(?\d{1,4}\)?[-.\s]?)?[\d\s.-]{5,15}'
    )
    
    def __init__(self):
        """Initialize the text normalization agent."""
        # Pre-compile whitespace pattern
        self._whitespace_pattern = re.compile(r'\s+')
        self._control_char_pattern = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]')
    
    def _extract_preservables(self, text: str) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Extract URLs, emails, and phones to preserve during normalization.
        
        Returns:
            Tuple of (modified text with placeholders, list of (placeholder, original))
        """
        preservables = []
        modified_text = text
        
        # Extract and replace URLs
        for i, match in enumerate(self.URL_PATTERN.finditer(text)):
            placeholder = f"__URL_{i}__"
            preservables.append((placeholder, match.group()))
            modified_text = modified_text.replace(match.group(), placeholder, 1)
        
        # Extract and replace emails
        for i, match in enumerate(self.EMAIL_PATTERN.finditer(modified_text)):
            if not match.group().startswith("__"):
                placeholder = f"__EMAIL_{i}__"
                preservables.append((placeholder, match.group()))
                modified_text = modified_text.replace(match.group(), placeholder, 1)
        
        return modified_text, preservables
    
    def _restore_preservables(self, text: str, preservables: List[Tuple[str, str]]) -> str:
        """Restore preserved entities in text."""
        for placeholder, original in preservables:
            text = text.replace(placeholder, original)
        return text
    
    def normalize(self, text: str) -> str:
        """
        Normalize text while preserving important entities.
        
        Args:
            text: The text to normalize
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Extract preservable entities
        modified_text, preservables = self._extract_preservables(text)
        
        # Unicode normalization (NFC form)
        normalized = unicodedata.normalize('NFC', modified_text)
        
        # Remove control characters
        normalized = self._control_char_pattern.sub('', normalized)
        
        # Normalize whitespace (collapse multiple spaces, trim)
        normalized = self._whitespace_pattern.sub(' ', normalized).strip()
        
        # Restore preserved entities
        normalized = self._restore_preservables(normalized, preservables)
        
        return normalized
    
    def normalize_for_analysis(self, text: str) -> str:
        """
        Normalize text for analysis (includes lowercase).
        
        Args:
            text: The text to normalize
            
        Returns:
            Normalized lowercase text for analysis
        """
        normalized = self.normalize(text)
        return normalized.lower()
    
    def process(self, text: str) -> dict:
        """
        Process text and return normalization results.
        
        Args:
            text: The text to process
            
        Returns:
            Dictionary with normalized text variants
        """
        return {
            "normalized": self.normalize(text),
            "normalized_lower": self.normalize_for_analysis(text),
            "original_length": len(text),
            "normalized_length": len(self.normalize(text))
        }
