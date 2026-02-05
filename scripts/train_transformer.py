"""
Ultimate Transformer Training Pipeline (v4)

Fine-tunes DistilBERT on all consolidated datasets using PyTorch and GPU-acceleration.
Implements robust label validation and data consolidation.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from torch.optim import AdamW
from pathlib import Path
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.detector import preprocess_text

# Device configuration
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_NAME = "distilbert-base-uncased"
OUTPUT_DIR = Path("models/distilbert_spam")


class SpamDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]

        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding="max_length",
            truncation=True,
            return_attention_mask=True,
            return_tensors="pt",
        )

        return {
            "text": text,
            "input_ids": encoding["input_ids"].flatten(),
            "attention_mask": encoding["attention_mask"].flatten(),
            "labels": torch.tensor(label, dtype=torch.long),
        }


def validate_labels(df, text_col, label_col):
    """Detect if labels are flipped."""
    spam_keywords = [
        "free",
        "won",
        "lottery",
        "prize",
        "claim",
        "urgent",
        "verify",
        "account",
        "cash",
        "money",
    ]
    sample = df.sample(min(200, len(df)), random_state=42)
    counts = {0: 0, 1: 0}
    for _, row in sample.iterrows():
        text = str(row[text_col]).lower()
        label = 1 if str(row[label_col]).lower() in ["spam", "1", "yes", "true"] else 0
        matches = sum(1 for kw in spam_keywords if kw in text)
        counts[label] += matches
    if counts[0] > counts[1] * 1.5 and counts[0] > 10:
        return True  # flipped
    return False


def load_all_data():
    """Consolidate all available CSV datasets."""
    all_texts, all_labels = [], []
    csv_files = list(Path("dataset").glob("*.csv")) + [
        Path("spam_and_ham_classification.csv")
    ]

    for path in csv_files:
        if not path.exists():
            continue
        try:
            df = pd.read_csv(path, encoding="latin-1", on_bad_lines="skip")
            text_col = next(
                (
                    c
                    for c in df.columns
                    if any(k in c.lower() for k in ["text", "v2", "body"])
                ),
                None,
            )
            label_col = next(
                (
                    c
                    for c in df.columns
                    if any(k in c.lower() for k in ["label", "v1", "class"])
                ),
                None,
            )

            if not text_col or not label_col:
                continue

            should_flip = validate_labels(df, text_col, label_col)

            for _, row in df.iterrows():
                text = str(row[text_col])
                label_raw = str(row[label_col]).lower()
                label = (
                    1
                    if any(k in label_raw for k in ["spam", "1", "yes", "smishing"])
                    else 0
                )
                if should_flip:
                    label = 1 - label

                if len(text) > 3:
                    # We store preprocessed text for training too
                    all_texts.append(preprocess_text(text))
                    all_labels.append(label)
            print(f"Loaded {path.name} ({'Flipped' if should_flip else 'OK'})")
        except Exception as e:
            print(f"Error loading {path.name}: {e}")

    return all_texts, all_labels


def train():
    print(f"Setting up training on: {DEVICE}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load Data
    texts, labels = load_all_data()
    print(f"Total samples: {len(texts)} (Spam: {sum(labels)})")

    X_train, X_val, y_train, y_val = train_test_split(
        texts, labels, test_size=0.1, random_state=42
    )

    # 2. Tokenizer & Model
    tokenizer = DistilBertTokenizer.from_pretrained(MODEL_NAME)
    model = DistilBertForSequenceClassification.from_pretrained(
        MODEL_NAME, num_labels=2
    )
    model.to(DEVICE)

    # 3. DataLoaders
    train_dataset = SpamDataset(X_train, y_train, tokenizer)
    val_dataset = SpamDataset(X_val, y_val, tokenizer)

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32)

    # 4. Optimizer
    optimizer = AdamW(model.parameters(), lr=2e-5)

    # 5. Training Loop
    epochs = 3
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        loop = tqdm(train_loader, leave=True)
        for batch in loop:
            optimizer.zero_grad()
            input_ids = batch["input_ids"].to(DEVICE)
            attention_mask = batch["attention_mask"].to(DEVICE)
            labels_tensor = batch["labels"].to(DEVICE)

            outputs = model(
                input_ids, attention_mask=attention_mask, labels=labels_tensor
            )
            loss = outputs.loss
            total_loss += loss.item()

            loss.backward()
            optimizer.step()

            loop.set_description(f"Epoch {epoch+1}")
            loop.set_postfix(loss=loss.item())

    # 6. Final Evaluation
    model.eval()
    preds, actuals = [], []
    with torch.no_grad():
        for batch in val_loader:
            input_ids = batch["input_ids"].to(DEVICE)
            attention_mask = batch["attention_mask"].to(DEVICE)
            outputs = model(input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            preds.extend(torch.argmax(logits, dim=1).cpu().numpy())
            actuals.extend(batch["labels"].numpy())

    print(f"\nFinal Validation Accuracy: {accuracy_score(actuals, preds):.4%}")
    print(classification_report(actuals, preds))

    # 7. Save
    print(f"Saving model to {OUTPUT_DIR}")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    metadata = {
        "model_type": "DistilBERT",
        "accuracy": accuracy_score(actuals, preds),
        "f1": f1_score(actuals, preds),
        "samples": len(texts),
        "timestamp": pd.Timestamp.now().isoformat(),
    }
    with open(OUTPUT_DIR / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)


if __name__ == "__main__":
    train()
