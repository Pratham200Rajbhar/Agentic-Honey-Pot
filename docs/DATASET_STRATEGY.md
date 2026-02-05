# Dataset Strategy Document

## Agentic Honey-Pot: Scam Intelligence Extraction API

**Version:** 3.0  
**Date:** February 4, 2026

---

## 1. Dataset Philosophy

### 1.1 Core Principle

Datasets serve as the **fine-tuning corpus** for the deep learning Transformer model. The production system uses a **fine-tuned DistilBERT** model achieving **99.11% accuracy**.

### 1.2 Usage Paradigm

| Phase       | Dataset Role                                   |
| ----------- | ---------------------------------------------- |
| Development | Training corpus for ML model training          |
| Production  | No dataset access; uses trained ML models only |

---

## 2. Dataset Inventory

### 2.1 Consolidated Corpus

The model is trained on a massive consolidated corpus of **31,705 messages** from 5+ premium sources, including UCI, Mendeley, and Kaggle.

### 2.2 Dataset Characteristics

**SMS Spam Collection:**

- Distribution: 13% spam, 87% ham
- Language: English
- Format: CSV (label, message)
- Coverage: General spam, promotional content

**SMS Phishing Dataset:**

- Labels: ham, spam, smishing
- Language: English
- Focus: Banking, delivery, credential harvesting
- Coverage: Modern phishing tactics

**Balanced Dataset:**

- Distribution: Even spam/ham ratio
- Purpose: Prevent majority class bias
- Use: Weight calibration, validation

---

## 3. Feature Extraction Pipeline

### 3.1 Pipeline Overview

```
Consolidated Corpus (31,705 messages)
      │
      ▼
┌──────────────────┐
│ Automated Validation│
│ • Label check       │
│ • Flip detection    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Transformer Fine-tuning
│ • DistilBERT Base   │
│ • GPU-Accelerated   │
│ • AdamW Optimizer   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Model Deployment    │
│ • PyTorch Model     │
│ • Tokenizer config  │
│ • ~260MB total      │
└──────────────────┘
```

### 3.2 Data Preparation

**Loading:**

- Parse CSV format with appropriate encoding (UTF-8, Latin-1)
- Handle missing values and malformed records
- Normalize label encoding across datasets

**Cleaning:**

- Remove duplicate messages
- Filter invalid entries (empty, non-text)
- Standardize label format

**Normalization:**

- Unicode normalization (NFC form)
- Whitespace standardization
- Case normalization for analysis

### 3.3 Feature Categories

| Category   | Features Extracted                         |
| ---------- | ------------------------------------------ |
| Lexical    | Token frequencies, vocabulary sets         |
| Structural | Length distributions, punctuation patterns |
| Entity     | URL, phone, email presence rates           |
| Semantic   | Category-indicative term clusters          |

---

## 4. Statistical Analysis Methods

### 4.1 Frequency Analysis

**Token Frequency Computation:**

- Extract all tokens from labeled messages
- Compute per-class frequency distributions
- Identify discriminative tokens (high ratio between classes)

**N-gram Analysis:**

- Unigram frequencies for vocabulary building
- Bigram frequencies for phrase detection
- Trigram frequencies for pattern identification

### 4.2 Category Profiling

For each scam category, compute:

- Characteristic token set
- Entity presence probability
- Structural feature distribution
- Discriminative feature ranking

### 4.3 Weight Optimization

**Discriminative Power Calculation:**

For each feature $f$ and category $c$:

- Compute presence rate in category: $P(f|c)$
- Compute presence rate outside category: $P(f|\neg c)$
- Discriminative score: $D(f,c) = P(f|c) / P(f|\neg c)$

**Weight Assignment:**

- Higher discriminative score → Higher weight
- Normalize weights to prevent score explosion
- Apply domain knowledge adjustments

### 4.4 Threshold Calibration

**Threat Score Thresholds:**

- Analyze score distributions on labeled data
- Optimize thresholds for precision/recall balance
- Validate on held-out test set

**Confidence Thresholds:**

- Map score ranges to confidence levels
- Calibrate for realistic probability estimates

---

## 5. Category-Specific Analysis

### 5.1 Category Feature Profiles

| Category          | Key Discriminative Features                              |
| ----------------- | -------------------------------------------------------- |
| Bank/Financial    | Account references, OTP mentions, verification requests  |
| Lottery/Prize     | Winning announcements, claim instructions, large amounts |
| Job/Employment    | Work offers, salary mentions, application requests       |
| Crypto/Investment | Trading terms, return promises, wallet references        |
| Phishing          | URL presence, verification requests, account alerts      |
| Romance/Dating    | Relationship language, emotional appeals                 |
| Tech Support      | Computer issues, support offers, remote access           |
| Delivery/Package  | Shipment status, tracking requests, customs mentions     |
| Government/Tax    | Authority names, refund claims, legal threats            |
| General Spam      | Promotional content without specific category markers    |

### 5.2 Cross-Category Disambiguation

Features that appear across multiple categories require:

- Context-dependent weighting
- Combination rules for disambiguation
- Fallback to General Spam when ambiguous

---

## 6. Threat Scoring Model

### 6.1 Feature Weight Matrix

| Feature              | Weight Range   | Rationale                 |
| -------------------- | -------------- | ------------------------- |
| URL presence         | High (25-35)   | Primary attack vector     |
| Monetary reference   | High (20-30)   | Financial fraud indicator |
| Urgency language     | Medium (15-25) | Social engineering tactic |
| Contact information  | Medium (10-20) | Engagement solicitation   |
| Threat language      | Medium (15-25) | Coercion signal           |
| Multiple entities    | Low (5-15)     | Compound indicator        |
| Structural anomalies | Low (5-15)     | Obfuscation attempt       |

### 6.2 Weight Derivation Process

1. **Initial Assignment:** Domain knowledge baseline
2. **Dataset Validation:** Test on labeled corpus
3. **Iterative Refinement:** Adjust based on performance
4. **Cross-Validation:** Verify on held-out data

### 6.3 Threshold Optimization

Optimize thresholds to achieve:

- High threat: High precision (minimize false positives)
- Low threat: High recall (capture benign messages)
- Medium threat: Balanced trade-off

---

## 7. Validation Strategy

### 7.1 Coverage Validation

**Metric:** Pattern coverage rate

**Target:** > 90% of spam messages match at least one pattern

**Method:**

- Apply compiled weights to spam corpus
- Measure percentage with non-zero scores
- Identify uncovered message types

### 7.2 Accuracy Validation

**Metric:** Classification accuracy

**Target:** > 98% correct classification  
**Achieved:** **99.11%** ✅

**Method:**

- Deep learning train/val split
- Cross-dataset evaluation
- Real-world "adversarial" testing

**Results:**
| Metric | Score |
|--------|-------|
| Accuracy | 99.11% |
| Precision | 98.42% |
| Recall | 99.70% |
| F1 Score | 99.06% |

### 7.3 False Positive Validation

**Metric:** False positive rate

**Target:** < 5% of ham messages classified as high threat

**Method:**

- Apply scoring to ham corpus
- Measure percentage exceeding high threshold
- Analyze false positive characteristics

---

## 8. Artifact Specification

### 8.1 ML Model Artifacts

**Trained Transformer:** `models/distilbert_spam/`

- Architecture: DistilBERT
- Precision: FP32
- Size: ~260MB

**Model Metadata:** `models/distilbert_spam/metadata.json`

```json
{
  "model_type": "DistilBERT",
  "accuracy": 0.9911,
  "total_samples": 31705,
  "timestamp": "2026-02-04"
}
```

### 8.2 Artifact Characteristics

| Property   | Specification   |
| ---------- | --------------- |
| Format     | joblib (pickle) |
| Total Size | ~5MB            |
| Load time  | < 2 seconds     |
| Accuracy   | 99.95%          |

---

## 9. Privacy and Compliance

### 9.1 Data Handling

| Principle          | Implementation                       |
| ------------------ | ------------------------------------ |
| No message storage | Only statistical aggregates retained |
| No PII extraction  | Features are anonymous indicators    |
| Dataset isolation  | Training data never in production    |

### 9.2 Attribution

All datasets used require proper attribution:

- SMS Spam Collection: UCI Machine Learning Repository
- SMS Phishing Dataset: Mendeley Data (CC BY 4.0)

---

## 10. Continuous Improvement

### 10.1 Model Updates

Feature weights may be updated when:

- New scam patterns emerge
- Accuracy metrics decline
- Additional training data available

### 10.2 Update Process

1. Collect new labeled data
2. Re-run feature extraction pipeline
3. Validate new weights on test corpus
4. Deploy updated weights.json artifact

---

**Document Status:** Final  
**Last Updated:** February 4, 2026
