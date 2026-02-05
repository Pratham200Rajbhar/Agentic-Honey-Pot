# Project Overview

## Agentic Honey-Pot: Scam Intelligence Extraction API

**Version:** 3.0  
**Date:** February 4, 2026  
**Status:** Production-Ready (ML-Powered)

---

## 1. Product Summary

### 1.1 Vision Statement

An intelligent API honeypot that analyzes scam and phishing messages using a **Deep Learning Transformer model (DistilBERT)** fine-tuned on 31,000+ labeled messages, achieving **99.1% accuracy** while extracting structured threat intelligence through a multi-agent processing architecture.

### 1.2 Value Proposition

| Traditional Approach     | Our Approach                                  |
| ------------------------ | --------------------------------------------- |
| Binary spam detection    | Multi-dimensional threat analysis             |
| Opaque classification    | Context-aware semantic reasoning              |
| Static rule matching     | **Transformer-based adaptive classification** |
| Single-pass processing   | Multi-agent sequential reasoning              |
| Moderate accuracy (~80%) | **99.11% accuracy**                           |

### 1.3 Key Capabilities

- **Classification:** 10 scam category taxonomy
- **Entity Extraction:** URLs, phones, emails, monetary values
- **Threat Quantification:** Normalized severity scoring (0-100)
- **Intent Analysis:** Attacker motivation inference
- **Confidence Estimation:** Model certainty quantification

---

## 2. Architecture Overview

### 2.1 Processing Pipeline

```
Request → Authentication → Validation → Agent Pipeline → Response
```

### 2.2 Agent Architecture

| Agent                 | Function                        | Output            |
| --------------------- | ------------------------------- | ----------------- |
| Language Detection    | Message language identification | ISO 639-1 code    |
| Text Normalization    | Input standardization           | Normalized text   |
| Feature Extraction    | Entity and indicator extraction | Feature vector    |
| Classification        | Scam category prediction        | Category + scores |
| Threat Scoring        | Severity quantification         | Score (0-100)     |
| Intent Inference      | Motivation classification       | Intent category   |
| Confidence Estimation | Certainty calculation           | Probability (0-1) |

### 2.3 Technology Foundation

**Core Stack:**

- FastAPI (API framework)
- Pydantic (Data validation)
- **PyTorch/Transformers (Deep Learning)**
- Custom NLP pipeline (Text processing)
- Uvicorn (ASGI server)

**Design Principles:**

- Stateless request handling
- No external API dependencies
- Sub-second processing latency
- Horizontal scalability

---

## 3. Machine Learning Model Design

### 3.1 ML Pipeline Components

The system employs a **fine-tuned DistilBERT** model with the following stages:

**Text Preprocessing:**

- Semantic marker preservation (URLs, Phones, Money)
- Unicode and Case normalization

**Architecture:**

- **Transformer:** DistilBERT (distilbert-base-uncased)
- **Vocabulary:** 30,522 WordPiece tokens
- **Inference:** GPU-Accelerated (CUDA) with CPU fallback

**Performance:**

- **Accuracy:** 99.11%
- **Recall:** 99.70%
- **Precision:** 98.42%

### 3.2 Model Training Results

The model was trained on a consolidated corpus:

| Dataset                | Samples | Purpose                             |
| ---------------------- | ------- | ----------------------------------- |
| Consolidated SMS/Email | 31,705  | Broad coverage of modern scam types |

**Model Performance:**
| Metric | Score |
|--------|-------|
| Accuracy | 99.11% |
| F1 Score | 99.06% |
| Training Mode | GPU-Accelerated (NVIDIA) |
| Architecture | Deep Transformer (DistilBERT) |

---

## 4. Intelligence Output

### 4.1 Response Structure

| Field                | Type    | Description                            |
| -------------------- | ------- | -------------------------------------- |
| `analysis_id`        | UUID    | Unique request identifier              |
| `scam_type`          | String  | Classification category                |
| `threat_level`       | Enum    | Categorical severity (Low/Medium/High) |
| `threat_score`       | Integer | Numeric severity (0-100)               |
| `intent`             | String  | Inferred attacker motivation           |
| `confidence_score`   | Float   | Model certainty (0.0-1.0)              |
| `language`           | String  | Detected language code                 |
| `extracted_entities` | Object  | Structured entity collection           |

### 4.2 Entity Extraction

| Entity Type     | Pattern Source                    |
| --------------- | --------------------------------- |
| Email addresses | RFC 5322 compliant patterns       |
| Phone numbers   | International format variations   |
| URLs            | URI specification patterns        |
| Monetary values | Multi-currency format recognition |

---

## 5. Security Architecture

### 5.1 Authentication

- API key-based access control
- Header-based key transmission (`X-API-Key`)
- Stateless validation (no session management)

### 5.2 Data Privacy

- No message content persistence
- No PII logging
- Request-scoped data lifecycle

### 5.3 Input Security

- Schema-based validation
- Length constraints (1-5000 characters)
- Injection prevention via sanitization

---

## 6. Performance Characteristics

| Metric        | Target       | Method                   |
| ------------- | ------------ | ------------------------ |
| Latency (P50) | < 200ms      | Optimized pipeline       |
| Latency (P95) | < 2s         | Graceful degradation     |
| Throughput    | 100+ req/min | Async processing         |
| Memory        | < 512MB      | Lightweight dependencies |

---

## 7. Deployment Model

### 7.1 Infrastructure Requirements

- Python 3.9+ runtime
- 512MB RAM minimum
- HTTPS termination capability
- Environment variable support

### 7.2 Platform Compatibility

- Container-based deployment (Docker)
- PaaS platforms (Render, Railway)
- Traditional VM/server deployment

---

## 8. Quality Assurance

### 8.1 Accuracy Metrics

| Metric                   | Target |
| ------------------------ | ------ |
| Classification Accuracy  | > 85%  |
| False Positive Rate      | < 5%   |
| Entity Extraction Recall | > 90%  |

### 8.2 Validation Strategy

- Test corpus derived from held-out dataset samples
- Cross-validation against multiple dataset sources
- Edge case coverage for boundary conditions

---

**Document Status:** Final  
**Next Phase:** Implementation
