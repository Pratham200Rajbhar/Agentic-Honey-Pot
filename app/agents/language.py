"""
Language Detection Agent
Identifies the language of incoming messages.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class LanguageDetectionAgent:
    """Agent for detecting message language."""
    
    DEFAULT_LANGUAGE = "en"
    
    def __init__(self):
        """Initialize the language detection agent."""
        self._detector = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """Lazy initialization of langdetect."""
        if not self._initialized:
            try:
                from langdetect import detect, DetectorFactory
                # Set seed for consistent results
                DetectorFactory.seed = 0
                self._detector = detect
                self._initialized = True
            except ImportError:
                logger.warning("langdetect not installed, using default language")
                self._detector = None
                self._initialized = True
    
    def detect(self, text: str) -> str:
        """
        Detect the language of the given text.
        
        Args:
            text: The text to analyze
            
        Returns:
            ISO 639-1 language code (e.g., 'en', 'hi', 'es')
        """
        self._ensure_initialized()
        
        if not text or len(text.strip()) < 3:
            return self.DEFAULT_LANGUAGE
        
        if self._detector is None:
            return self.DEFAULT_LANGUAGE
        
        try:
            language = self._detector(text)
            logger.debug(f"Detected language: {language}")
            return language
        except Exception as e:
            logger.debug(f"Language detection failed: {e}, using default")
            return self.DEFAULT_LANGUAGE
    
    def process(self, text: str) -> dict:
        """
        Process text and return language detection results.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary with language detection results
        """
        language = self.detect(text)
        return {
            "language": language,
            "is_english": language == "en"
        }
