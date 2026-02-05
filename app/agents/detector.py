"""
Transformer-Based Robust Spam Detector

Uses fine-tuned DistilBERT for state-of-the-art spam and scam detection.
Leverages GPU acceleration (CUDA) if available.
"""

import os
import re
import logging
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path

import torch
import numpy as np
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

logger = logging.getLogger(__name__)

# Device configuration
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def preprocess_text(text: str) -> str:
    """
    Standard preprocessing for both training and inference.
    """
    if not isinstance(text, str):
        text = str(text)
    text = text.lower()
    text = re.sub(r"https?://\S+|www\.\S+", " [url] ", text)
    text = re.sub(r"\S+@\S+", " [email] ", text)
    text = re.sub(r"\b\d{10,}\b", " [phone] ", text)
    text = re.sub(r"\b\d{3,4}[\s-]?\d{3,4}[\s-]?\d{4}\b", " [phone] ", text)
    text = re.sub(r"\b\d{4,6}\b", " [shortcode] ", text)
    text = re.sub(r"[$£€]\s*\d+[,\d]*\.?\d*", " [money] ", text)
    text = re.sub(
        r"\d+[,\d]*\.?\d*\s*(?:dollars?|pounds?|euros?|rs|inr)", " [money] ", text
    )
    text = re.sub(r"[^a-z0-9\s\[\]]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


class MLSpamDetector:
    """
    Production-ready Transformer based spam detector.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, model_dir: str = "models/distilbert_spam"):
        if MLSpamDetector._initialized:
            return

        self.model_dir = Path(model_dir)
        self.tokenizer = None
        self.model = None
        self.metadata = None
        self._loaded = False

        self._load_model()
        MLSpamDetector._initialized = True

    def _load_model(self):
        """Load the fine-tuned DistilBERT model."""
        try:
            if self.model_dir.exists():
                self.tokenizer = DistilBertTokenizer.from_pretrained(self.model_dir)
                self.model = DistilBertForSequenceClassification.from_pretrained(
                    self.model_dir
                )
                self.model.to(DEVICE)
                self.model.eval()

                metadata_path = self.model_dir / "metadata.json"
                if metadata_path.exists():
                    import json

                    with open(metadata_path) as f:
                        self.metadata = json.load(f)

                self._loaded = True
                logger.info(f"Transformer model loaded on {DEVICE}")
            else:
                logger.warning(
                    f"Transformer model directory not found: {self.model_dir}"
                )
        except Exception as e:
            logger.error(f"Failed to load Transformer model: {e}")
            self._loaded = False

    def transform(self, text: str) -> Optional[Dict[str, torch.Tensor]]:
        """Tokenize text for Transformer input."""
        if not self._loaded:
            return None
        processed = preprocess_text(text)
        return self.tokenizer.encode_plus(
            processed,
            add_special_tokens=True,
            max_length=128,
            padding="max_length",
            truncation=True,
            return_attention_mask=True,
            return_tensors="pt",
        )

    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Extract the embedding ([CLS] token) for semantic similarity."""
        if not self._loaded:
            return None
        try:
            inputs = self.transform(text)
            input_ids = inputs["input_ids"].to(DEVICE)
            attention_mask = inputs["attention_mask"].to(DEVICE)

            with torch.no_grad():
                outputs = self.model(
                    input_ids, attention_mask=attention_mask, output_hidden_states=True
                )
                # Use the last hidden state of the [CLS] token as the embedding
                embedding = outputs.hidden_states[-1][0][0].cpu().numpy()
            return embedding
        except Exception as e:
            logger.error(f"Embedding extraction error: {e}")
            return None

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Classify text using the Transformer model.
        """
        if not self._loaded:
            return {"is_spam": False, "confidence": 0, "available": False}

        try:
            inputs = self.transform(text)
            input_ids = inputs["input_ids"].to(DEVICE)
            attention_mask = inputs["attention_mask"].to(DEVICE)

            with torch.no_grad():
                outputs = self.model(input_ids, attention_mask=attention_mask)
                logits = outputs.logits
                probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
                prediction = torch.argmax(logits, dim=1).item()

            # Correct mapping: Index 0 is SPAM, Index 1 is HAM
            spam_prob = float(probs[0])
            confidence = abs(spam_prob - 0.5) * 2

            return {
                "is_spam": bool(prediction == 0),
                "spam_probability": spam_prob,
                "confidence": confidence,
                "available": True,
                "model_type": "DistilBERT",
            }
        except Exception as e:
            logger.error(f"Transformer prediction error: {e}")
            return {"is_spam": False, "error": str(e), "available": False}

    def get_threat_score(self, text: str) -> Tuple[int, str]:
        """Convert prediction to threat score (0-100)."""
        result = self.predict(text)
        if not result.get("available", False):
            return 50, "Medium"

        spam_prob = result["spam_probability"]
        score = int(spam_prob * 100)

        if score >= 70:
            level = "High"
        elif score >= 30:
            level = "Medium"
        else:
            level = "Low"

        return score, level

    @property
    def is_loaded(self) -> bool:
        return self._loaded


# Global singleton
_detector = None


def get_ml_detector(force_reload: bool = False) -> MLSpamDetector:
    global _detector
    if force_reload or _detector is None:
        _detector = MLSpamDetector()
    return _detector
